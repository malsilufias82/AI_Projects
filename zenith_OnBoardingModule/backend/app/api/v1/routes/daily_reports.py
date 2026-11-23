"""
API endpoints for daily status reports.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.auth.dependencies import get_current_user

logger = get_logger(__name__)
router = APIRouter()


class DailyReportData(BaseModel):
    """Daily report data model"""
    completed: str = ""
    inProgress: str = ""
    blockers: str = ""
    nextPlan: str = ""
    notes: str = ""
    leaveType: str = ""
    noAdditionalUpdates: bool = False
    completedNoUpdates: bool = False
    inProgressNoUpdates: bool = False
    blockersNoUpdates: bool = False
    nextPlanNoUpdates: bool = False
    notesNoUpdates: bool = False


class SaveReportsRequest(BaseModel):
    """Request model for saving daily reports"""
    reports: Dict[str, DailyReportData]  # Keyed by date (YYYY-MM-DD)


class TeamCompletionStatus(BaseModel):
    """Model for team completion status"""
    team_lead: str
    total_team_members: int
    completed_count: int
    pending_count: int
    completion_percentage: float
    is_complete: bool
    pending_members: List[str] = []  # List of member names who haven't completed
    completed_members: List[str] = []  # List of member names who have completed


@router.get("/")
async def get_reports(
    start: str,
    end: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get daily reports for a date range.
    
    - **start**: Start date in YYYY-MM-DD format
    - **end**: End date in YYYY-MM-DD format
    """
    try:
        await MongoDB.connect()
        daily_reports_collection = MongoDB.get_collection("daily_reports")

        # Get user ID from current user (use _id from MongoDB document)
        user_id = str(current_user.get("_id"))

        # Query reports within the date range for the current user
        query = {
            "user_id": user_id,
            "date": {
                "$gte": start,
                "$lte": end
            }
        }
        
        cursor = daily_reports_collection.find(query)
        reports = {}
        
        async for doc in cursor:
            date = doc.get("date")
            if date:
                reports[date] = {
                    "completed": doc.get("completed", ""),
                    "inProgress": doc.get("inProgress", ""),
                    "blockers": doc.get("blockers", ""),
                    "nextPlan": doc.get("nextPlan", ""),
                    "notes": doc.get("notes", ""),
                    "leaveType": doc.get("leaveType", ""),
                    "noAdditionalUpdates": doc.get("noAdditionalUpdates", False),
                    "completedNoUpdates": doc.get("completedNoUpdates", False),
                    "inProgressNoUpdates": doc.get("inProgressNoUpdates", False),
                    "blockersNoUpdates": doc.get("blockersNoUpdates", False),
                    "nextPlanNoUpdates": doc.get("nextPlanNoUpdates", False),
                    "notesNoUpdates": doc.get("notesNoUpdates", False)
                }
        
        return reports
        
    except Exception as e:
        logger.error("Failed to get daily reports", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def save_reports(
    request: SaveReportsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save daily reports for multiple dates.
    
    - **reports**: Dictionary of daily reports keyed by date (YYYY-MM-DD)
    """
    try:
        await MongoDB.connect()
        daily_reports_collection = MongoDB.get_collection("daily_reports")

        # Get user ID from current user (use _id from MongoDB document)
        user_id = str(current_user.get("_id"))

        # Upsert each report only if it has content
        for date, report_data in request.reports.items():
            # Check if any field has content (including leave type and checkbox states)
            has_content = (
                (report_data.completed and report_data.completed.strip()) or
                (report_data.inProgress and report_data.inProgress.strip()) or
                (report_data.blockers and report_data.blockers.strip()) or
                (report_data.nextPlan and report_data.nextPlan.strip()) or
                (report_data.notes and report_data.notes.strip()) or
                (report_data.leaveType and report_data.leaveType.strip()) or
                # Include checkbox states as content
                report_data.completedNoUpdates or
                report_data.inProgressNoUpdates or
                report_data.blockersNoUpdates or
                report_data.nextPlanNoUpdates or
                report_data.notesNoUpdates
            )

            # Only save if there's actual content
            if has_content:
                await daily_reports_collection.update_one(
                    {"user_id": user_id, "date": date},
                    {
                        "$set": {
                            "user_id": user_id,
                            "date": date,
                            "completed": report_data.completed,
                            "inProgress": report_data.inProgress,
                            "blockers": report_data.blockers,
                            "nextPlan": report_data.nextPlan,
                            "notes": report_data.notes,
                            "leaveType": report_data.leaveType,
                            "noAdditionalUpdates": report_data.noAdditionalUpdates,
                            "completedNoUpdates": report_data.completedNoUpdates,
                            "inProgressNoUpdates": report_data.inProgressNoUpdates,
                            "blockersNoUpdates": report_data.blockersNoUpdates,
                            "nextPlanNoUpdates": report_data.nextPlanNoUpdates,
                            "notesNoUpdates": report_data.notesNoUpdates,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    },
                    upsert=True
                )
            else:
                # If no content, delete the existing record if it exists
                await daily_reports_collection.delete_one(
                    {"user_id": user_id, "date": date}
                )
        
        return {"status": "success", "message": "Reports saved successfully"}

    except Exception as e:
        logger.error("Failed to save daily reports", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


def get_week_start_and_deadline():
    """
    Calculate current week's Monday and 5PM deadline for today.
    
    Returns:
        tuple: (week_start_date, deadline_datetime)
    """
    now = datetime.now(timezone.utc)
    
    # Calculate Monday of current week (Monday is weekday 0)
    days_since_monday = now.weekday()
    week_start = now - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Today's 5PM deadline (UTC)
    deadline = now.replace(hour=17, minute=0, second=0, microsecond=0)
    
    return week_start.strftime("%Y-%m-%d"), deadline


@router.get("/team-completion")
async def get_team_completion_status(
    start: str = None,
    end: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get team completion status for a date range.

    Returns a list of team leads with their team's daily report completion status
    from the start date to end date. If no dates provided, uses current week.
    """
    try:
        await MongoDB.connect()
        employees_collection = MongoDB.get_collection("employees")
        daily_reports_collection = MongoDB.get_collection("daily_reports")

        # Use provided date range or default to current week
        if start and end:
            week_start_date = start
            current_date = end
            deadline = datetime.fromisoformat(end).replace(hour=17, minute=0, second=0, microsecond=0)
        else:
            # Get current week's date range
            week_start_date, deadline = get_week_start_and_deadline()
            current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        logger.info(
            "Fetching team completion status",
            week_start=week_start_date,
            current_date=current_date,
            deadline=deadline.isoformat()
        )
        
        # Get all active employees (including team leads) - filter for Blackrock only
        employees = await employees_collection.find({
            "active_inactive": {"$ne": "Inactive"},
            "is_deleted": {"$ne": True},
            "full_name": {"$ne": "Nivedita"},  # Exclude Nivedita
            "$or": [
                {"client": {"$regex": "blackrock|blk", "$options": "i"}},
                {"project": {"$regex": "blackrock|phoenix", "$options": "i"}},
                {"blk_team_sub_project": {"$ne": "", "$exists": True}},
                {"blk_tl": {"$ne": "", "$exists": True}}
            ]
        }).to_list(length=None)
        
        # Create a mapping of team lead names to their employee records
        team_lead_employees = {}
        for emp in employees:
            emp_name = emp.get("full_name", emp.get("email", ""))
            if emp_name:
                team_lead_employees[emp_name] = emp
        
        # Group employees by team lead
        team_groups = {}
        for emp in employees:
            team_lead = emp.get("team_lead", "Unknown")
            if team_lead and team_lead != "Unknown":
                if team_lead not in team_groups:
                    team_groups[team_lead] = []
                team_groups[team_lead].append(emp)
        
        # Add team leads to their own teams
        for team_lead_name, team_members in team_groups.items():
            if team_lead_name in team_lead_employees:
                # Check if team lead is already in their team (they might have themselves as team_lead)
                team_lead_emp = team_lead_employees[team_lead_name]
                team_lead_id = str(team_lead_emp.get("_id", ""))
                already_in_team = any(
                    str(member.get("_id", "")) == team_lead_id 
                    for member in team_members
                )
                if not already_in_team:
                    team_groups[team_lead_name].append(team_lead_emp)
        
        # Get all daily reports for the current week (Monday to current date)
        reports_cursor = daily_reports_collection.find({
            "date": {"$gte": week_start_date, "$lte": current_date}
        })
        reports = await reports_cursor.to_list(length=None)
        
        # Create a dictionary mapping user_id to set of dates they have reports for
        user_report_dates = {}
        for report in reports:
            user_id = report.get("user_id")
            report_date = report.get("date")
            if user_id and report_date:
                user_id_str = str(user_id)
                if user_id_str not in user_report_dates:
                    user_report_dates[user_id_str] = set()
                user_report_dates[user_id_str].add(report_date)
        
        # Generate all dates from Monday to current date
        all_dates_in_range = set()
        current_dt = datetime.fromisoformat(week_start_date)
        end_dt = datetime.fromisoformat(current_date)
        while current_dt <= end_dt:
            all_dates_in_range.add(current_dt.strftime("%Y-%m-%d"))
            current_dt += timedelta(days=1)
        
        # Calculate completion status for each team
        team_status_list = []
        for team_lead, team_members in team_groups.items():
            total_members = len(team_members)
            completed_count = 0
            pending_members = []
            completed_members = []
            
            for member in team_members:
                user_id = member.get("user_id")
                member_name = member.get("full_name", member.get("email", "Unknown"))
                
                # Check if user has reports for ALL dates in the range with ALL sections filled
                if user_id and str(user_id) in user_report_dates:
                    user_dates = user_report_dates[str(user_id)]
                    # User is complete only if they have reports for all dates in range
                    # AND all sections are filled for each date
                    if all_dates_in_range.issubset(user_dates):
                        # Additional check: verify all sections are filled for each date
                        all_sections_filled = True
                        for date in all_dates_in_range:
                            # Find the report for this date
                            report = next((r for r in reports if r.get("date") == date and str(r.get("user_id")) == str(user_id)), None)
                            if report:
                                leave_type = report.get("leaveType", "")
                                completed = report.get("completed", "").strip()
                                completed_no_updates = report.get("completedNoUpdates", False)
                                
                                if leave_type == 'Working':
                                    # For 'Working', check each section: either has content OR checkbox is checked
                                    # Completed section is complete if it has content OR checkbox is checked
                                    if not (completed or completed_no_updates):
                                        all_sections_filled = False
                                        break
                                    
                                    in_progress = report.get("inProgress", "").strip()
                                    in_progress_no_updates = report.get("inProgressNoUpdates", False)
                                    blockers = report.get("blockers", "").strip()
                                    blockers_no_updates = report.get("blockersNoUpdates", False)
                                    next_plan = report.get("nextPlan", "").strip()
                                    next_plan_no_updates = report.get("nextPlanNoUpdates", False)
                                    
                                    # Each section is complete if it has content OR checkbox is checked
                                    if not (in_progress or in_progress_no_updates):
                                        all_sections_filled = False
                                        break
                                    if not (blockers or blockers_no_updates):
                                        all_sections_filled = False
                                        break
                                    if not (next_plan or next_plan_no_updates):
                                        all_sections_filled = False
                                        break
                                else:
                                    # For non-'Working' leave types, all sections are required
                                    if not completed:
                                        all_sections_filled = False
                                        break
                                    in_progress = report.get("inProgress", "").strip()
                                    blockers = report.get("blockers", "").strip()
                                    next_plan = report.get("nextPlan", "").strip()
                                    
                                    if not (in_progress and blockers and next_plan):
                                        all_sections_filled = False
                                        break
                            else:
                                all_sections_filled = False
                                break
                        
                        if all_sections_filled:
                            completed_count += 1
                            completed_members.append(member_name)
                        else:
                            pending_members.append(member_name)
                    else:
                        pending_members.append(member_name)
                else:
                    pending_members.append(member_name)
            
            pending_count = total_members - completed_count
            completion_percentage = (completed_count / total_members * 100) if total_members > 0 else 0
            is_complete = completed_count == total_members and total_members > 0
            
            team_status_list.append(TeamCompletionStatus(
                team_lead=team_lead,
                total_team_members=total_members,
                completed_count=completed_count,
                pending_count=pending_count,
                completion_percentage=round(completion_percentage, 2),
                is_complete=is_complete,
                pending_members=pending_members,
                completed_members=completed_members
            ))
        
        # Sort by completion percentage (descending) then by team lead name
        team_status_list.sort(
            key=lambda x: (-x.completion_percentage, x.team_lead)
        )
        
        logger.info(
            "Team completion status calculated",
            total_teams=len(team_status_list),
            teams_complete=sum(1 for t in team_status_list if t.is_complete)
        )
        
        return {
            "week_start": week_start_date,
            "current_date": current_date,
            "deadline": deadline.isoformat(),
            "team_status": team_status_list
        }
        
    except Exception as e:
        logger.error("Failed to get team completion status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
