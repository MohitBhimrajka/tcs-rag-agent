# app/db/crud.py
from sqlalchemy.orm import Session, joinedload
import datetime
from . import models
from app.schemas.extraction import FinancialReportData

def create_extraction_run(db: Session, filename: str) -> models.ExtractionRun:
    """Creates a new record for an extraction job in the database."""
    db_run = models.ExtractionRun(filename=filename, status="in_progress")
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

def add_trace_log(db: Session, run_id: int, node_name: str, log_message: str):
    """Adds a detailed log entry for a specific step in an extraction run."""
    db_log = models.TraceLog(
        run_id=run_id,
        node_name=node_name,
        log_message=log_message
    )
    db.add(db_log)
    db.commit()

def update_extraction_run_status(db: Session, run_id: int, status: str):
    """Updates the status and end_time of an extraction run."""
    db_run = db.query(models.ExtractionRun).filter(models.ExtractionRun.id == run_id).first()
    if db_run:
        db_run.status = status
        if status in ["completed", "failed"]:
            db_run.end_time = datetime.datetime.utcnow()
        db.commit()

# --- ADD THE FOLLOWING FUNCTIONS ---

def update_extraction_run_task(db: Session, run_id: int, task: str):
    """Updates the current task being processed for a given run."""
    db_run = db.query(models.ExtractionRun).filter(models.ExtractionRun.id == run_id).first()
    if db_run:
        db_run.current_task = task
        db.commit()

def update_extraction_run_results(db: Session, run_id: int, results: FinancialReportData):
    """Saves the final JSON results of an extraction run to the database."""
    db_run = db.query(models.ExtractionRun).filter(models.ExtractionRun.id == run_id).first()
    if db_run:
        db_run.results = results.dict()
        db.commit()

def get_extraction_run(db: Session, run_id: int) -> models.ExtractionRun:
    """Fetches a single extraction run by its ID."""
    return db.query(models.ExtractionRun).filter(models.ExtractionRun.id == run_id).first()

def get_extraction_run_with_logs(db: Session, run_id: int) -> models.ExtractionRun:
    """
    Fetches an extraction run and eagerly loads its associated logs to prevent
    lazy loading issues.
    """
    return db.query(models.ExtractionRun).options(joinedload(models.ExtractionRun.logs)).filter(models.ExtractionRun.id == run_id).first()
