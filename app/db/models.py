# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON # <--- ADD THIS IMPORT
import datetime

Base = declarative_base()

class ExtractionRun(Base):
    """
    Represents a single, complete extraction job. This is the parent record
    for all associated trace logs.
    """
    __tablename__ = "extraction_runs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="in_progress") # e.g., in_progress, completed, failed
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # --- ADD THIS COLUMN ---
    results = Column(JSON, nullable=True)
    current_task = Column(String, nullable=True, default="Initializing...")

    # This creates a one-to-many relationship with the TraceLog model
    logs = relationship("TraceLog", back_populates="run", cascade="all, delete-orphan")

class TraceLog(Base):
    """
    Represents a single step or observation in the agent's reasoning process.
    Each log is linked to a specific ExtractionRun.
    """
    __tablename__ = "trace_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("extraction_runs.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    node_name = Column(String, nullable=False) # e.g., Planner, ToolExecutor, Validator
    log_message = Column(Text, nullable=False)

    # This defines the many-to-one relationship back to the ExtractionRun
    run = relationship("ExtractionRun", back_populates="logs")
