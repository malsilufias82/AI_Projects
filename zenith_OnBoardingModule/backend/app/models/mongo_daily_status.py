"""
MongoDB model for daily status data.
Stores daily status updates for each user across different sheets and dates.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DailyStatus(BaseModel):
    """Model for daily status data."""
    
    user_name: str = Field(..., description="Name of the user/vlinker")
    team_lead: Optional[str] = Field(None, description="Team lead name")
    sheet_name: str = Field(..., description="Name of the sheet")
    sheet_date: str = Field(..., description="Date associated with the sheet (from sheet name)")
    day_of_week: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    date: Optional[str] = Field(None, description="Actual date for this day")
    status_content: str = Field(..., description="The status update content")
    is_leave: bool = Field(default=False, description="Whether the user is on leave")
    is_filled: bool = Field(default=True, description="Whether the status is filled")
    team_name: Optional[str] = Field(None, description="Team name (e.g., Platform, Product, PMI, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when record was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when record was last updated")
    
    class Config:
        collection_name = "daily_status"
        json_schema_extra = {
            "example": {
                "user_name": "John Doe",
                "team_lead": "Jane Smith",
                "sheet_name": "Week Ending 19-07-2026",
                "sheet_date": "19-07-2026",
                "day_of_week": "Monday",
                "date": "2026-07-13",
                "status_content": "Completed task X, working on task Y",
                "is_leave": False,
                "is_filled": True,
                "team_name": "Platform Team"
            }
        }
