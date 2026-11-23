"""
MongoDB model for daily report data.
Stores daily status reports with completed, in-progress, blockers, next plan, and notes.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.mongo_base import MongoBaseModel, TimestampMixin


class DailyReport(MongoBaseModel, TimestampMixin):
    """Model for daily report data."""
    
    user_id: str = Field(..., description="ID of the user who created/updated the report")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    completed: str = Field(default="", description="Completed tasks")
    inProgress: str = Field(default="", description="Tasks in progress")
    blockers: str = Field(default="", description="Blockers or issues")
    nextPlan: str = Field(default="", description="Next plan of action")
    notes: str = Field(default="", description="Additional notes")
    
    class Config:
        collection_name = "daily_reports"
        json_schema_extra = {
            "example": {
                "date": "2026-07-27",
                "completed": "Completed task X",
                "inProgress": "Working on task Y",
                "blockers": "Waiting for API access",
                "nextPlan": "Start task Z",
                "notes": "Meeting at 2pm"
            }
        }
