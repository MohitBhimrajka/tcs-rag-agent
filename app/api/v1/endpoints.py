# app/api/v1/endpoints.py
import os
import shutil # <--- ADD THIS
from typing import List # <--- ADD THIS
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File # <--- UPDATE THIS
from pydantic import BaseModel
from collections import deque
import uuid
from sqlalchemy.orm import Session # <--- Add Session

from app.core.document_processor import DocumentProcessor
from app.agent.tools import create_rag_tools
# --- REMOVE THE GRAPH IMPORTS ---
# from app.agent.graph import create_agent_graph, set_global_db_session

# --- ADD THESE NEW IMPORTS ---
from app.agent.rag_chain import create_rag_chain
from app.agent.parsers import TASK_PARSER_MAP, ParsedRevenue, ParsedNetIncome, ParsedEPS, ParsedSegmentContribution, ParsedUtilization, ParsedKeyRisks

from app.schemas.extraction import FinancialReportData, ConsolidatedRevenue, ConsolidatedNetIncome, DilutedEPS, SegmentContribution, EmployeeUtilization, KeyManagementRisk
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

@router.post("/extract")
async def extract_data_with_agent(
    request: ExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Runs the new, high-accuracy RAG chain for a pre-defined list of financial data points.
    """
    run = crud.create_extraction_run(db=db, filename=request.filename)
    run_id = run.id
    print(f"--- STARTING EXTRACTION RUN ID: {run_id} FOR FILE: {request.filename} ---")
    
    try:
        pdf_path = os.path.join("documents", request.filename)
        store_name = os.path.splitext(request.filename)[0]
        text_store_path = os.path.join("app/data/vector_stores", f"{store_name}_text")
        table_store_path = os.path.join("app/data/vector_stores", f"{store_name}_tables")
        
        if not os.path.exists(text_store_path) or not os.path.exists(table_store_path):
            crud.update_extraction_run_task(db, run_id, "Processing Document...")
            processor = DocumentProcessor(pdf_path=pdf_path)
            processor.process_and_store(text_store_path, table_store_path)

        text_retriever, table_retriever = DocumentProcessor.load_retrievers(
            text_store_path=text_store_path,
            table_store_path=table_store_path
        )
        
        task_queue = deque([
            "Consolidated Revenue (USD Billion)",
            "Consolidated Net Income (Profit After Tax)",
            "Diluted Earnings Per Share (EPS in INR)",
            "Percentage contribution of the top 3 operating segments (e.g., BFSI, Retail)",
            "Employee Utilization Rate (excluding trainees)",
            "Top 2-3 most critical risks from the Management Discussion & Analysis",
        ])
        
        final_results = FinancialReportData()

        # Loop through each task and execute the powerful RAG chain
        for task in task_queue:
            crud.update_extraction_run_task(db, run_id, f"Processing: {task}")
            print(f"--- RUN {run_id}: Starting task: {task} ---")

            try:
                parser_model = TASK_PARSER_MAP.get(task)
                if not parser_model:
                    print(f"--- RUN {run_id}: Skipping task '{task}' - no parser defined.")
                    continue

                rag_chain = create_rag_chain(text_retriever, table_retriever, parser_model)
                parsed_result = await rag_chain.ainvoke({"task": task})

                log_msg = f"Task: '{task}'.\nSuccess.\nResult: {parsed_result.dict()}"
                crud.add_trace_log(db, run_id, "RAGChain", log_msg)
                print(f"--- RUN {run_id}: SUCCESS for task: {task} ---")

                # Map the parsed data back to our final schema
                if isinstance(parsed_result, ParsedRevenue):
                    final_results.consolidated_revenue = ConsolidatedRevenue(**parsed_result.dict())
                elif isinstance(parsed_result, ParsedNetIncome):
                    final_results.consolidated_net_income = ConsolidatedNetIncome(**parsed_result.dict())
                elif isinstance(parsed_result, ParsedEPS):
                    data = parsed_result.dict()
                    data['unit'] = 'INR'
                    final_results.diluted_eps = DilutedEPS(**data)
                elif isinstance(parsed_result, ParsedSegmentContribution):
                    for seg in parsed_result.top_segments:
                        final_results.top_3_segment_contributions.append(SegmentContribution(**seg.dict()))
                elif isinstance(parsed_result, ParsedUtilization):
                    final_results.employee_utilization = EmployeeUtilization(**parsed_result.dict())
                elif isinstance(parsed_result, ParsedKeyRisks):
                     for risk in parsed_result.key_risks:
                        final_results.key_management_risks.append(KeyManagementRisk(**risk.dict()))

            except Exception as e:
                # Log failures for individual tasks but continue the process
                error_msg = f"Task: '{task}'.\nFailed.\nError: {str(e)}"
                crud.add_trace_log(db, run_id, "RAGChain", error_msg)
                print(f"--- RUN {run_id}: FAILED task: {task}. Error: {e} ---")
                continue

        crud.update_extraction_run_results(db, run_id, final_results)
        crud.update_extraction_run_status(db, run_id, "completed")
        crud.update_extraction_run_task(db, run_id, "Completed")
        
        print(f"--- RUN {run_id} COMPLETED SUCCESSFULLY ---")
        return {"run_id": run_id, "status": "processing_started"}

    except FileNotFoundError as e:
        error_detail = f"Document not found: {str(e)}"
        print(f"--- FILE NOT FOUND FOR RUN {run_id}: {error_detail} ---")
        crud.update_extraction_run_status(db=db, run_id=run_id, status="failed")
        crud.update_extraction_run_task(db, run_id, "Failed - Document not found")
        raise HTTPException(status_code=404, detail=error_detail)
    except Exception as e:
        error_detail = f"An internal error occurred: {str(e)}"
        print(f"--- CATASTROPHIC FAILURE FOR RUN {run_id}: {error_detail} ---")
        crud.update_extraction_run_status(db=db, run_id=run_id, status="failed")
        crud.update_extraction_run_task(db, run_id, "Failed")
        raise HTTPException(status_code=500, detail=error_detail)

# --- ADD THE FOLLOWING NEW ENDPOINTS ---

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Handles uploading of a new PDF document.
    """
    upload_dir = "documents"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = os.path.join(upload_dir, file.filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' already exists.")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "status": "uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")


@router.get("/documents", response_model=dict)
async def get_available_documents():
    """
    Returns a list of PDF filenames available in the documents directory.
    """
    doc_dir = "documents"
    if not os.path.exists(doc_dir):
        return {"filenames": []}
    
    try:
        filenames = [f for f in os.listdir(doc_dir) if f.endswith(".pdf")]
        return {"filenames": filenames}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read documents directory: {e}")


@router.get("/extractions/{run_id}/status")
async def get_extraction_status(run_id: int, db: Session = Depends(get_db)):
    """
    Polls for the status of a specific extraction run.
    """
    run = crud.get_extraction_run(db, run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Extraction run not found")
    return {
        "run_id": run.id,
        "status": run.status,
        "current_task": run.current_task,
        "start_time": run.start_time,
        "end_time": run.end_time
    }


@router.get("/extractions/{run_id}/results")
async def get_extraction_results(run_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the final results and trace logs for a completed extraction run.
    """
    run = crud.get_extraction_run_with_logs(db, run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Extraction run not found")
    
    # Manually format logs to avoid circular reference issues with Pydantic
    trace_logs = [{
        "timestamp": log.timestamp.isoformat(),
        "node_name": log.node_name,
        "log_message": log.log_message
    } for log in run.logs]

    return {
        "run_id": run.id,
        "status": run.status,
        "filename": run.filename,
        "results": run.results,
        "trace_logs": trace_logs
    }

# --- END OF NEW ENDPOINTS ---

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