# app/agent/graph.py
import os
from typing import List, TypedDict, Annotated
from collections import deque
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.tools import create_rag_tools
from app.agent.parsers import TASK_PARSER_MAP, ParsedRevenue, ParsedNetIncome, ParsedEPS, ParsedSegmentContribution, ParsedUtilization, ParsedKeyRisks
from app.schemas.extraction import (
    FinancialReportData, ConsolidatedRevenue, ConsolidatedNetIncome, DilutedEPS,
    SegmentContribution, EmployeeUtilization, KeyManagementRisk
)
from app.db.crud import add_trace_log, update_extraction_run_task # <--- Add the new import

# --- 1. Define Agent State (Revised) ---
# This class represents the data that flows through the graph at each step.
class AgentState(TypedDict):
    task_queue: deque
    current_task: str
    extracted_data: FinancialReportData
    tool_names: List[str] # List of tool names instead of Tool objects
    planner_prompt: str
    # The 'str' is the output of the planner, which is the tool call string
    # We use Annotated to tell LangGraph that this is a special field
    tool_choice: Annotated[str, "tool_choice"]
    tool_output: str
    
    # --- ADD THESE FOR AUDITING ---
    run_id: int
    # Note: We'll access db_session from a global variable instead of passing it through state

# --- 2. Define Pydantic models for the Planner's output ---
# The planner's job is to decide which tool to use and what query to send it.
class ToolCall(BaseModel):
    tool_name: str = Field(description="The name of the tool to use from the available tools.")
    query: str = Field(description="The precise, detailed question to ask the tool.")

# --- 3. Define the Graph Nodes ---
# Each node is a function that performs an action and modifies the agent's state.

def planner_node(state: AgentState):
    """
    The 'brain' of the agent. Decides what to do next and logs its plan.
    """
    print("--- PLANNER ---")
    global _GLOBAL_DB_SESSION
    db = _GLOBAL_DB_SESSION
    run_id = state['run_id']
    
    # Pop the next task from the left of the queue
    task_queue = state.get("task_queue", deque())
    if not task_queue:
        log_message = "Task queue is empty. Agent is finishing."
        print(log_message)
        add_trace_log(db, run_id, "Planner", log_message)
        return {"tool_choice": "FINISH"}
        
    current_task = task_queue.popleft()
    print(f"Current task: {current_task}")
    
    # --- ADD THIS LINE TO UPDATE THE DATABASE ---
    update_extraction_run_task(db, run_id, f"Processing: {current_task}")

    # Create tool descriptions from tool names
    tool_descriptions = []
    for tool_name in state['tool_names']:
        if tool_name == "TextSearchTool":
            tool_descriptions.append("- TextSearchTool: Use this tool to find qualitative information, narrative summaries, or data points mentioned in prose within the annual report.")
        elif tool_name == "TableSearchTool":
            tool_descriptions.append("- TableSearchTool: Use this tool to find quantitative data that is likely to be in a structured table. This is the best tool for extracting specific financial figures.")
    
    tool_descriptions_str = "\n".join(tool_descriptions)
    prompt = state['planner_prompt'].format(
        task=current_task,
        tools=tool_descriptions_str
    )

    # Initialize the planner LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    ).with_structured_output(ToolCall) # Force the LLM to output a ToolCall object

    # Invoke the planner and get the chosen tool call
    tool_call = llm.invoke(prompt)
    
    log_message = (
        f"Task: '{current_task}'.\n"
        f"Decision: Use tool '{tool_call.tool_name}'.\n"
        f"Query: '{tool_call.query}'"
    )
    print(f"Planner decided: {log_message}")
    add_trace_log(db, run_id, "Planner", log_message)
    
    return {
        "current_task": current_task,
        "task_queue": task_queue,
        "tool_choice": tool_call # Pass the structured tool call
    }

async def tool_node(state: AgentState):
    """
    Executes the chosen tool and logs the raw output.
    """
    print("--- TOOL EXECUTOR ---")
    global _GLOBAL_DB_SESSION
    db = _GLOBAL_DB_SESSION
    run_id = state['run_id']
    tool_call = state['tool_choice']
    
    # Access tools from global storage
    global _GLOBAL_TOOLS
    chosen_tool = _GLOBAL_TOOLS.get(tool_call.tool_name)
    
    output = "NOT FOUND"
    if chosen_tool:
        print(f"Executing tool: {tool_call.tool_name}")
        # We use ainvoke for asynchronous execution
        output = await chosen_tool.func(tool_call.query)
        log_message = f"Executed tool '{tool_call.tool_name}'.\nRaw Output:\n---\n{output}\n---"
    else:
        log_message = f"Error: Tool '{tool_call.tool_name}' not found."
    
    print("Tool execution complete.")
    add_trace_log(db, run_id, "ToolExecutor", log_message)
    return {"tool_output": output}


def validation_node(state: AgentState):
    """
    Parses the tool's output, validates it, and logs the outcome.
    """
    print("--- VALIDATOR ---")
    global _GLOBAL_DB_SESSION
    db = _GLOBAL_DB_SESSION
    run_id = state['run_id']
    raw_output = state.get('tool_output', '')
    task = state.get('current_task', '')
    extracted_data = state.get('extracted_data')

    if "NOT FOUND" in raw_output or not task:
        log_message = f"Task: '{task}'. Skipping validation as no information was found."
        print(log_message)
        add_trace_log(db, run_id, "Validator", log_message)
        return {} # No changes to the state

    # 1. Select the appropriate parser for the current task
    parser_model = TASK_PARSER_MAP.get(task)
    if not parser_model:
        log_message = f"Error: No parser defined for task '{task}'."
        print(log_message)
        add_trace_log(db, run_id, "Validator", log_message)
        return {}

    # 2. Create a dedicated parsing LLM with structured output
    # This LLM's only job is to accurately fill our Pydantic parser model.
    parsing_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    ).with_structured_output(parser_model)

    # 3. Create the prompt for the parsing LLM
    parsing_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert data extraction and parsing assistant. Your job is to take raw text and accurately populate the provided structured data model. It is critical that you extract all fields, including the value, its unit (e.g., 'INR Crores', 'USD Billion'), and the source_page number from the context. Do not make up information; if a field is not present, omit it."),
        ("human", "Based on the following raw text, please extract the required information.\n\nRaw Text:\n---\n{raw_text}\n---"),
    ])
    
    parsing_chain = parsing_prompt | parsing_llm

    print(f"Attempting to parse output for task: {task}")
    try:
        # 4. Invoke the chain to get the structured, parsed data
        parsed_result = parsing_chain.invoke({"raw_text": raw_output})
        print(f"Successfully parsed data: {parsed_result}")

        log_message = f"Task: '{task}'.\nSuccessfully parsed raw output.\nParsed Data: {parsed_result.dict()}"
        add_trace_log(db, run_id, "Validator", log_message)

        # 5. Update the main `FinancialReportData` state object
        # This is where we map the parsed data back to our final schema.
        if isinstance(parsed_result, ParsedRevenue):
            extracted_data.consolidated_revenue = ConsolidatedRevenue(**parsed_result.dict())
        elif isinstance(parsed_result, ParsedNetIncome):
            extracted_data.consolidated_net_income = ConsolidatedNetIncome(**parsed_result.dict())
        elif isinstance(parsed_result, ParsedEPS):
            # The schema for DilutedEPS requires a 'unit' field, which our parser doesn't provide.
            # We add it here, as it's a fixed value for this specific task.
            data = parsed_result.dict()
            data['unit'] = 'INR'
            extracted_data.diluted_eps = DilutedEPS(**data)
        elif isinstance(parsed_result, ParsedSegmentContribution):
            page = parsed_result.source_page
            for seg in parsed_result.top_segments:
                extracted_data.top_3_segment_contributions.append(SegmentContribution(**seg.dict()))
            # A bit of a hack to get the page number onto the parent object
            if extracted_data.top_3_segment_contributions:
                print(f"Note: Page number for segments is {page} but not stored in the final schema.")
        elif isinstance(parsed_result, ParsedUtilization):
            extracted_data.employee_utilization = EmployeeUtilization(**parsed_result.dict())
        elif isinstance(parsed_result, ParsedKeyRisks):
             for risk in parsed_result.key_risks:
                extracted_data.key_management_risks.append(KeyManagementRisk(**risk.dict()))

        return {"extracted_data": extracted_data}

    except Exception as e:
        log_message = f"Task: '{task}'.\nFailed to parse or validate data.\nError: {e}"
        print(log_message)
        add_trace_log(db, run_id, "Validator", log_message)
        # Even if parsing fails, we don't want to halt the entire process.
        # We just move on to the next task.
        return {}


# --- 4. Define the Conditional Edge ---
# This function determines the next step after the validator runs.
def should_continue(state: AgentState):
    if not state.get("task_queue"):
        return "end" # If the queue is empty, we're done
    else:
        return "continue" # Otherwise, loop back to the planner

# --- 5. Assemble the Graph ---

# Global variable to store tools (since we can't serialize them in state)
_GLOBAL_TOOLS = {}
# Global variable to store database session (since we can't serialize it in state)
_GLOBAL_DB_SESSION = None

def set_global_db_session(db_session: Session):
    """Set the global database session for logging."""
    global _GLOBAL_DB_SESSION
    _GLOBAL_DB_SESSION = db_session

def create_agent_graph(planner_prompt: str, tools: list):
    """
    Builds the LangGraph agent workflow.
    """
    global _GLOBAL_TOOLS
    # Store tools globally so we can access them in nodes
    _GLOBAL_TOOLS = {tool.name: tool for tool in tools}
    
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("tool_executor", tool_node)
    graph.add_node("validator", validation_node)

    # Define the graph's flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "tool_executor")
    graph.add_edge("tool_executor", "validator")
    graph.add_conditional_edges(
        "validator",
        should_continue,
        {
            "continue": "planner",
            "end": END
        }
    )

    # Compile the graph into a runnable application
    # MemorySaver is used to keep track of the state at each step.
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
