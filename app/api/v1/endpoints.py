# app/api/v1/endpoints.py
import os
from fastapi import APIRouter, HTTPException, Depends # <--- Add Depends
from pydantic import BaseModel
from collections import deque
import uuid
from sqlalchemy.orm import Session # <--- Add Session

from app.core.document_processor import DocumentProcessor
from app.agent.tools import create_rag_tools
from app.agent.graph import create_agent_graph, set_global_db_session
from app.schemas.extraction import FinancialReportData
from app.db.database import get_db # <--- Add get_db
from app.db import crud # <--- Add crud

# Define the router for this module
router = APIRouter(
    prefix="/api/v1",
    tags=["Extraction Agent"]
)

# Define the request body model
class ExtractionRequest(BaseModel):
    filename: str
    question: str = "What is the final reported Consolidated Revenue for the group in USD Billion?"

# This is the prompt that instructs our planner agent.
# It's a critical piece of the agent's intelligence.
PLANNER_PROMPT_TEMPLATE = """
You are an expert financial analyst agent. Your goal is to extract specific data points from a financial report.
For the given task, you must choose the best tool and formulate a precise, detailed query to send to that tool.

Available tools:
{tools}

Current Task: "{task}"

Based on the task, what is the single most appropriate tool to use?
And what is the best, most specific query to ask it to get a clear, unambiguous answer? For example, for "Consolidated Revenue", a good query would be "What is the Consolidated Revenue from operations for the most recent financial year?".
"""

@router.post("/extract", response_model=FinancialReportData) # <--- Add response_model for clarity
async def extract_data_with_agent(
    request: ExtractionRequest,
    db: Session = Depends(get_db) # <--- Use FastAPI's dependency injection to get a DB session
):
    """
    The main endpoint to run the full, multi-modal agentic extraction process with auditing.
    """
    # --- AUDIT START ---
    # Create a record for this extraction run in the database
    run = crud.create_extraction_run(db=db, filename=request.filename)
    run_id = run.id
    print(f"--- STARTING EXTRACTION RUN ID: {run_id} FOR FILE: {request.filename} ---")
    
    try:
        pdf_path = os.path.join("documents", request.filename)
        store_name = os.path.splitext(request.filename)[0]
        text_store_path = os.path.join("app/data/vector_stores", f"{store_name}_text")
        table_store_path = os.path.join("app/data/vector_stores", f"{store_name}_tables")
        
        # 1. Process document if necessary
        if not os.path.exists(text_store_path) or not os.path.exists(table_store_path):
            print("Processing document for agent...")
            processor = DocumentProcessor(pdf_path=pdf_path)
            processor.process_and_store(
                text_store_path=text_store_path,
                table_store_path=table_store_path
            )

        # 2. Load retrievers and create tools
        text_retriever, table_retriever = DocumentProcessor.load_retrievers(
            text_store_path=text_store_path,
            table_store_path=table_store_path
        )
        tools = create_rag_tools(text_retriever, table_retriever)
        
        # 3. Define the deterministic task list (the agent's "to-do" list)
        task_queue = deque([
            "Consolidated Revenue (USD Billion)",
            "Consolidated Net Income (Profit After Tax)",
            "Diluted Earnings Per Share (EPS in INR)",
            "Percentage contribution of the top 3 operating segments (e.g., BFSI, Retail)",
            "Employee Utilization Rate (excluding trainees)",
            "Top 2-3 most critical risks from the Management Discussion & Analysis",
        ])

        # 4. Create and run the agent graph
        agent_graph = create_agent_graph(PLANNER_PROMPT_TEMPLATE, tools)
        
        # Set the global database session for the agent to use
        set_global_db_session(db)
        
        # The initial state for the agent
        initial_state = {
            "task_queue": task_queue,
            "current_task": "",
            "extracted_data": FinancialReportData(),
            "tool_names": [tool.name for tool in tools], # Pass tool names instead of objects
            "planner_prompt": PLANNER_PROMPT_TEMPLATE,
            "tool_output": "",
            # --- PASS RUN ID TO AGENT ---
            "run_id": run_id,
        }

        # A unique ID for this specific run
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        print("\n--- INVOKING AGENT ---")
        # --- MODIFICATION START ---
        final_run_state = {}
        async for step in agent_graph.astream(initial_state, config=config):
            node_name = list(step.keys())[0]
            print(f"--- Finished Node: {node_name} ---")
            # Store the state from the very last step. LangGraph ensures the final
            # state is comprehensive.
            final_run_state = step
        
        # After the loop, the final state is in the value of the last dictionary entry.
        # We add multiple checks to prevent crashes.
        last_node_name = list(final_run_state.keys())[0] if final_run_state else None
        if last_node_name:
            final_data = final_run_state.get(last_node_name, {}).get('extracted_data')
        else:
            final_data = FinancialReportData() # Return an empty object if the run fails completely
        
        print(f"\n--- AGENT RUN {run_id} COMPLETE ---")
        crud.update_extraction_run_status(db=db, run_id=run_id, status="completed")
        
        return final_data

    except FileNotFoundError as e:
        crud.update_extraction_run_status(db=db, run_id=run_id, status="failed")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"An unexpected error occurred during run {run_id}: {e}")
        crud.update_extraction_run_status(db=db, run_id=run_id, status="failed")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# Keep the older endpoints for backward compatibility and testing
@router.post("/extract-simple")
async def extract_simple_data(request: ExtractionRequest):
    """
    DEPRECATED: A simple endpoint to test the core RAG pipeline on TEXT ONLY.
    """
    try:
        pdf_path = os.path.join("documents", request.filename)
        store_name = os.path.splitext(request.filename)[0]
        vector_store_path = os.path.join("app/data/vector_stores", f"{store_name}_text_only")

        if not os.path.exists(vector_store_path):
            print(f"Vector store not found for {request.filename}. Processing document...")
            processor = DocumentProcessor(pdf_path=pdf_path)
            # Note: This calls the OLD method which only did text.
            # We are leaving this as-is and building new logic for the agent.
            processor.process_and_store(vector_store_path) # Only text processing
        else:
            print(f"Found existing vector store for {request.filename}.")
        
        retriever = DocumentProcessor.load_retriever(vector_store_path)
        from app.agent.tools import create_simple_rag_tool
        rag_chain = create_simple_rag_tool(retriever=retriever)

        # Step 3: Use the provided question and invoke the chain
        print(f"Invoking RAG chain with question: '{request.question}'")
        
        result = await rag_chain.ainvoke(request.question)

        # Step 4: Return the result
        return {
            "question": request.question,
            "answer": result
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@router.post("/initiate-agent-processing")
async def initiate_agent_processing(request: ExtractionRequest):
    """
    Initiates the multi-modal document processing required for the agent.
    This endpoint ensures the text and table vector stores are created and ready for querying.
    """
    try:
        pdf_path = os.path.join("documents", request.filename)
        store_name = os.path.splitext(request.filename)[0]
        
        # Define separate, clearer paths for text and table vector stores
        text_store_path = os.path.join("app/data/vector_stores", f"{store_name}_text")
        table_store_path = os.path.join("app/data/vector_stores", f"{store_name}_tables")
        
        # Step 1: Process the document if either vector store is missing
        if not os.path.exists(text_store_path) or not os.path.exists(table_store_path):
            print(f"One or more vector stores not found for {request.filename}. Starting multi-modal processing...")
            processor = DocumentProcessor(pdf_path=pdf_path)
            processor.process_and_store(
                text_store_path=text_store_path,
                table_store_path=table_store_path
            )
        else:
            print(f"Found existing text and table vector stores for {request.filename}.")

        # Step 2: Load the retrievers to confirm they are ready for the agent
        text_retriever, table_retriever = DocumentProcessor.load_retrievers(
            text_store_path=text_store_path,
            table_store_path=table_store_path
        )
        
        response_message = "Multi-modal processing complete. Text and table retrievers are ready."
        if not table_retriever:
            response_message = "Text processing complete. Table processing was skipped or failed. Text retriever is ready."
            
        return {"status": "success", "message": response_message}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")