# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import the new router
from app.api.v1 import endpoints

# --- ADD THESE IMPORTS ---
from app.db.database import engine
from app.db import models
# --- END IMPORTS ---


# --- ADD THIS STARTUP EVENT ---
# This command ensures that the database tables are created if they don't exist
# every time the application starts up.
models.Base.metadata.create_all(bind=engine)
# --- END STARTUP EVENT ---


app = FastAPI(
    title="TCS Annual Report Extraction Agent API",
    description="An API for an autonomous agent that extracts structured data from TCS annual reports.",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing) middleware setup
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router from our endpoints file
app.include_router(endpoints.router)

@app.get("/api/health")
def read_health():
    """Health check endpoint required by the Dockerfile."""
    return {"status": "ok"}

@app.get("/")
def read_root():
    """A root endpoint to confirm the API is running."""
    return {"message": "Welcome to the TCS Extraction Agent API"}