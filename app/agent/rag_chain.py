# app/agent/rag_chain.py
import os
from typing import Type
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.vectorstores import VectorStoreRetriever

# This prompt turns a simple task into a detailed, self-contained question.
# This is the "Chain of Thought" part of the process.
CONTEXTUALIZER_PROMPT = """
Given a task from a user, you must rephrase it as a detailed, self-contained question to be answered by a financial document.
Your goal is to make the question as specific as possible to improve the accuracy of the search.

**Critical Instructions:**
1.  **Incorporate Constraints:** If the task mentions a specific constraint like a currency (e.g., "USD Billion"), the generated question **must** explicitly and strongly ask for the data in that specific unit.
2.  **Expand on Qualitative Tasks:** For qualitative tasks like finding "risks", expand the question to include common, alternative section titles. For example, a search for risks should also check for "Principal Risks and Uncertainties" or "Risk Management".

**Examples:**
- **User Task:** "Consolidated Revenue (USD Billion)"
- **Good Question:** "What is the total Consolidated Revenue from operations, specifically in USD Billion, for the most recent financial year reported in the document?"

- **User Task:** "Top 2-3 most critical risks from the Management Discussion & Analysis"
- **Good Question:** "What are the top 2-3 most critical risks identified in the 'Management Discussion & Analysis', 'Risk Management', or 'Principal Risks and Uncertainties' sections of the report?"

---
**Task:** {task}
**Question:**
"""

ANSWER_PROMPT = """
You are an expert financial analyst. Your job is to answer a question by synthesizing information from the provided context. You must be precise and adhere to all constraints.

**USER'S ORIGINAL TASK:** {task}
**DETAILED QUESTION FOR SEARCH:** {question}

**CONTEXT:**
---
{context}
---

**CRITICAL INSTRUCTIONS:**
1.  First, answer the **DETAILED QUESTION** based **only** on the provided **CONTEXT**.
2.  Second, cross-reference your answer with the **USER'S ORIGINAL TASK** to ensure all constraints (like currency, year, or specific metrics) are perfectly met.
3.  If the context contains the information but in the wrong unit (e.g., the context has a value in INR, but the task explicitly requires USD), you **MUST** state that the specific value was not found. Do not perform currency conversions. Your job is to find the data as it is written.
4.  If the answer is not present in the context at all, you **MUST** return "NOT FOUND".
5.  Extract the source page number from the metadata of the most relevant snippet.

**Final Answer:**
"""

def format_docs(docs):
    """Helper function to format retrieved documents, including their metadata."""
    return "\n\n".join(
        f"--- Snippet from Page {doc.metadata.get('page', 'N/A')} ---\n{doc.page_content}"
        for doc in docs
    )

def create_rag_chain(
    text_retriever: VectorStoreRetriever,
    table_retriever: VectorStoreRetriever,
    parser_model: Type[BaseModel]
):
    """
    Creates the complete, high-accuracy RAG chain.
    """
    # Get the API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    # 1. A lightweight LLM to contextualize the user's task into a detailed question
    contextualizer_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=api_key
    )
    
    # 2. A powerful, precise LLM to analyze the context and extract the final structured answer
    # NOTE: Ensure your API key has access to Gemini 2.5 Pro
    answer_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro", 
        temperature=0,
        google_api_key=api_key
    ).with_structured_output(parser_model)

    # 3. The chain to generate the detailed question
    contextualize_q_chain = (
        ChatPromptTemplate.from_template(CONTEXTUALIZER_PROMPT)
        | contextualizer_llm
        | StrOutputParser()
    )

    # 4. A function to retrieve and format contexts from both retrievers
    def retrieve_contexts(inputs):
        """
        Retrieves context and passes through the original task and detailed question.
        """
        question = inputs["question"]
        text_docs = text_retriever.invoke(question)
        table_docs = table_retriever.invoke(question)
        
        text_context = format_docs(text_docs)
        table_context = format_docs(table_docs)
        
        combined_context = (
            f"--- TEXTUAL CONTEXT ---\n{text_context}\n\n"
            f"--- TABULAR CONTEXT ---\n{table_context}"
        )
        
        # Pass all necessary variables to the final prompt
        return {"context": combined_context, "question": question, "task": inputs['task']}

    # 5. The final assembled RAG chain using LCEL
    rag_chain = (
        # Start with the original task and generate detailed question
        RunnablePassthrough.assign(question=contextualize_q_chain)
        # Retrieve contexts using the detailed question, while passing the task through
        | retrieve_contexts
        # Feed the combined context, detailed question, AND original task to the final prompt
        | ChatPromptTemplate.from_template(ANSWER_PROMPT)
        | answer_llm
    )
    
    return rag_chain
