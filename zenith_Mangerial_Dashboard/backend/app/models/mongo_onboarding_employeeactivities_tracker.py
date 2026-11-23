from pydantic import BaseModel, Field


class OnboardingEmployeeActivityTracker(BaseModel):
    """MongoDB document for a completed employee onboarding activity."""

    employee_id: str = Field(default="", description="Employee identifier")
    activityid: str = Field(default="", description="Tracker activity identifier")
    activity: str = Field(default="", description="Activity name")
    status: str = Field(default="Pending", description="Activity status")
    comment: str = Field(default="", description="Activity comment")
    blocker: str = Field(default="", description="Legacy blocker/comment value")
    day: str = Field(default="", description="Day associated with the activity")

    class Config:
        populate_by_name = True
