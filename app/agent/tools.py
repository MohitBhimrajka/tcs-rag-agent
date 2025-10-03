# app/agent/tools.py
import os
from typing import List

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

# The strict prompt template remains crucial for both tools.
RAG_PROMPT_TEMPLATE = """
You are a precise financial data extraction assistant. Your task is to find the exact answer to the user's question using ONLY the context provided below.

- Look for the specific data point asked in the question.
- Do not use any prior knowledge or external information.
- Do not make up, infer, or calculate any figures.
- If the answer is present in the context, return only the answer and nothing else.
- If the answer is not explicitly stated in the context, you MUST return the single phrase "NOT FOUND".

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

def _create_rag_chain(retriever: VectorStoreRetriever) -> Runnable:
    """A helper function to create a standard RAG chain with a given retriever."""
    
    prompt = PromptTemplate(template=RAG_PROMPT_TEMPLATE, input_variables=["context", "question"])
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
        convert_system_message_to_human=True
    )
    
    def format_docs(docs):
        # Helper to format retrieved documents, including metadata.
        return "\n\n".join(
            f"--- Snippet from Page {doc.metadata.get('page', 'N/A')} ---\n{doc.page_content}"
            for doc in docs
        )

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def create_rag_tools(
    text_retriever: VectorStoreRetriever, 
    table_retriever: VectorStoreRetriever | None
) -> List[Tool]:
    """
    Creates a list of specialized RAG tools for the agent to use.
    One tool for searching text, and another for searching tables.
    """
    tools = []

    # 1. Text Search Tool
    text_rag_chain = _create_rag_chain(text_retriever)
    text_search_tool = Tool(
        name="TextSearchTool",
        func=text_rag_chain.ainvoke, # Use async invocation
        description=(
            "Use this tool to find qualitative information, narrative summaries, or data points "
            "mentioned in prose within the annual report. This is best for things like "
            "management risks, business outlook, or employee utilization rates if they are "
            "described in paragraphs."
        )
    )
    tools.append(text_search_tool)

    # 2. Table Search Tool (only if the retriever exists)
    if table_retriever:
        table_rag_chain = _create_rag_chain(table_retriever)
        table_search_tool = Tool(
            name="TableSearchTool",
            func=table_rag_chain.ainvoke,
            description=(
                "Use this tool to find quantitative data that is likely to be in a structured table. "
                "This is the best tool for extracting specific financial figures like Consolidated Revenue, "
                "Net Income, Earnings Per Share (EPS), or segment-wise revenue breakdowns."
            )
        )
        tools.append(table_search_tool)

    return tools

# The simple tool is no longer needed for the agent, but we can keep it for direct testing if desired.
def create_simple_rag_tool(retriever: VectorStoreRetriever):
    """DEPRECATED: Creates a simple, single-purpose RAG chain."""
    return _create_rag_chain(retriever)