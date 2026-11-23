from typing import Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class Employee(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB Employee model for storing detailed employee information from VLink Team Details."""
    
    # Link to user account
    user_id: Optional[str] = Field(None, index=True)

    # Basic employee info
    employee_id: Optional[str] = Field(None, max_length=50)

    # Project and team details
    department: Optional[str] = Field(None, max_length=100)
    client: Optional[str] = Field(None, max_length=255)
    project: Optional[str] = Field(None, max_length=255)
    pillar: Optional[str] = Field(None, max_length=255)
    blk_team_sub_project: Optional[str] = Field(None, max_length=255)
    vlinker: Optional[str] = Field(None, max_length=255)
    team_lead: Optional[str] = Field(None, max_length=255)
    team_lead_id: Optional[str] = Field(None, index=True)
    active_inactive: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    active_pw_io: Optional[str] = Field(None, max_length=50)
    billed: Optional[str] = Field(None, max_length=50)
    dev_qa: Optional[str] = Field(None, max_length=50)
    role_description: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    onboarding: Optional[str] = Field(None, max_length=200)
    skill_set: Optional[str] = Field(None, max_length=255)
    work_location: Optional[str] = Field(None, max_length=255)
    kras: Optional[str] = Field(None, max_length=255)
    ai_level: Optional[str] = Field(None, max_length=50)
    ai_lead: Optional[str] = Field(None, max_length=255)
    
    # Management details
    account_manager: Optional[str] = Field(None, max_length=255)
    am_poc_in_blackrock: Optional[str] = Field(None, max_length=255)
    hr1_rm: Optional[str] = Field(None, max_length=255)
    fm_id: Optional[str] = Field(None, max_length=50)
    hr1_fm: Optional[str] = Field(None, max_length=255)
    
    # Onboarding details
    onboarding_vlink: Optional[str] = Field(None, max_length=50)
    bgv_start: Optional[str] = Field(None, max_length=50)
    bgv_clear: Optional[str] = Field(None, max_length=50)
    vcf_sent: Optional[str] = Field(None, max_length=50)
    client_credential_received: Optional[str] = Field(None, max_length=50)
    billing_start_date: Optional[str] = Field(None, max_length=50)
    buffer: Optional[str] = Field(None, max_length=50)
    
    # Offboarding details
    offboarded_from_client: Optional[str] = Field(None, max_length=50)
    new_project: Optional[str] = Field(None, max_length=255)
    resignation_date: Optional[str] = Field(None, max_length=50)
    lwd_in_vlink: Optional[str] = Field(None, max_length=50)
    offboarding_reason: Optional[str] = Field(None, max_length=255)
    offboarding_decision_date: Optional[str] = Field(None, max_length=50)
    renewal: Optional[str] = Field(None, max_length=50)
    expected_due_date: Optional[str] = Field(None, max_length=50)
    filler: Optional[str] = Field(None, max_length=255)
    filler_1: Optional[str] = Field(None, max_length=255)
    
    # BlackRock management
    country: Optional[str] = Field(None, max_length=100)
    blk_tl: Optional[str] = Field(None, max_length=255)
    poc_project_reporting_mgr_at_blk: Optional[str] = Field(None, max_length=255)
    blk_buddy: Optional[str] = Field(None, max_length=255)
    blk_manager: Optional[str] = Field(None, max_length=255)
    blk_manager_level_2: Optional[str] = Field(None, max_length=255)
    blk_manager_level_3: Optional[str] = Field(None, max_length=255)
    blk_manager_level_4: Optional[str] = Field(None, max_length=255)
    blk_manager_level_5: Optional[str] = Field(None, max_length=255)
    blk_manager_level_6: Optional[str] = Field(None, max_length=255)
    
    # Employment details
    fte_contractor: Optional[str] = Field(None, max_length=50)
    contract_type: Optional[str] = Field(None, max_length=50)
    vendor: Optional[str] = Field(None, max_length=255)
    employment_status: Optional[str] = Field(None, max_length=50)
    exp_in_emp_details: Optional[str] = Field(None, max_length=50)
    email_id: Optional[str] = Field(None, max_length=255)
    replacement_details: Optional[str] = Field(None, max_length=255)
    
    # Location details
    commute: Optional[str] = Field(None, max_length=50)
    current_city: Optional[str] = Field(None, max_length=100)
    current_state: Optional[str] = Field(None, max_length=100)
    home_town: Optional[str] = Field(None, max_length=100)
    permanent_city: Optional[str] = Field(None, max_length=100)
    permanent_state: Optional[str] = Field(None, max_length=100)
    location_as_per_hr: Optional[str] = Field(None, max_length=255)
    
    # Other details
    h_o_v: Optional[str] = Field(None, max_length=50)
    bf_bl: Optional[str] = Field(None, max_length=50)
    alias: Optional[str] = Field(None, max_length=100)
    comments: Optional[str] = Field(None, max_length=500)
    renewal_1: Optional[str] = Field(None, max_length=50)
    filler_lowercase: Optional[str] = Field(None, max_length=255)

    class Config:
        collection_name = "employees"
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "employee_id": "VIPL000944",
                "project": "AABB",
                "team_lead": "Jane Smith",
                "role_description": "Software Engineer",
                "status": "Onboarded"
            }
        }
