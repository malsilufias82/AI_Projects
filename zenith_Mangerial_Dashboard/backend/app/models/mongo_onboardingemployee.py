from datetime import date
from typing import Optional

from pydantic import Field

from app.models.mongo_base import MongoBaseModel, TimestampMixin


class OnboardingEmployee(MongoBaseModel, TimestampMixin):
    """MongoDB document for employee onboarding progress."""

    # Fields
    employee_id: str = Field(..., index=True, max_length=50)

    # Credential
    credential_received_date: Optional[date] = Field(None)
    credential_status: Optional[str] = Field(None, max_length=50)


       # Background verification
    bgv_initiated_date: Optional[str] = Field(None, max_length=50)
    bgv_completed_date: Optional[str] = Field(None, max_length=50)
    bgv_status: Optional[str] = Field(None, max_length=50)

    # VCF
    vcf_sent_date: Optional[str] = Field(None, max_length=50)
    client_credential_received_date: Optional[str] = Field(None, max_length=50)
    vcf_status: Optional[str] = Field(None, max_length=50)

    # Overall
    primaryskill: Optional[str] = Field(None, max_length=255)
    onboarding_status: Optional[str] = Field(None, max_length=50)
    remarks: Optional[str] = Field(None, max_length=1000)

    # Audit
    created_by: Optional[str] = Field(None, max_length=255)

    class Config:
        collection_name = "onboarding_employees"
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                
                "credential_received_date": "2026-08-03",
                "credential_status": "Completed",
                "bgv_initiated_date": "2026-08-02",
                "bgv_completed_date": "2026-08-05",
                "bgv_status": "Completed",
                "vcf_sent_date": "2026-08-06",
                "client_credential_received_date": "2026-08-07",
                "vcf_status": "Completed",
                "primaryskill": "Java",
                "onboarding_status": "Completed",
                "remarks": "Onboarding completed successfully.",
                "created_by": "admin@example.com"
            }
        }
