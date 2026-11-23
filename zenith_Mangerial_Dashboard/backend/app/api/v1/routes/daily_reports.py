"""
API endpoints for daily status reports.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import date, datetime, timezone, timedelta
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
    team_lead_id: Optional[str] = None
    total_team_members: int
    completed_count: int
    pending_count: int
    completion_percentage: float
    is_complete: bool
    pending_members: List[str] = Field(default_factory=list)
    completed_members: List[str] = Field(default_factory=list)
    pending_member_details: List[Dict[str, Optional[str]]] = Field(default_factory=list)
    completed_member_details: List[Dict[str, Optional[str]]] = Field(default_factory=list)


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


@router.get("/status-details")
async def get_status_details(
    start: str,
    end: str,
    user_id: Optional[str] = None,
    team_lead_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Return read-only daily reports for one employee or a team lead's team."""
    if bool(user_id) == bool(team_lead_id):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of user_id or team_lead_id",
        )

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Dates must use YYYY-MM-DD format") from exc

    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be on or after start date")

    try:
        await MongoDB.connect()
        employees_collection = MongoDB.get_collection("employees")
        users_collection = MongoDB.get_collection("users")
        daily_reports_collection = MongoDB.get_collection("daily_reports")

        employees = await employees_collection.find({
            "active_inactive": {"$ne": "Inactive"},
            "is_deleted": {"$ne": True},
        }).to_list(length=None)
        users = await users_collection.find({}).to_list(length=None)
        users_by_id = {str(user.get("_id")): user for user in users if user.get("_id") is not None}
        employees_by_user_id = {
            str(employee.get("user_id")): employee
            for employee in employees
            if employee.get("user_id") is not None
        }
        team_leads_by_id = {
            str(record.get("_id")): record
            for record in [*users, *employees]
            if record.get("_id") is not None
        }

        if user_id:
            target_user_ids = [user_id]
        else:
            target_user_ids = list(dict.fromkeys(
                str(employee["user_id"])
                for employee in employees
                if employee.get("user_id") is not None
                and str(employee.get("team_lead_id") or "") == team_lead_id
            ))

        if not target_user_ids:
            return []

        reports = await daily_reports_collection.find({
            "user_id": {"$in": target_user_ids},
            "date": {"$gte": start, "$lte": end},
        }).to_list(length=None)
        reports_by_user_and_date = {
            (str(report.get("user_id") or ""), report.get("date")): report
            for report in reports
        }

        result = []
        current_date = start_date
        while current_date <= end_date:
            report_date = current_date.isoformat()
            for report_user_id in target_user_ids:
                report = reports_by_user_and_date.get((report_user_id, report_date), {})
                employee = employees_by_user_id.get(report_user_id, {})
                user = users_by_id.get(report_user_id, {})
                name = " ".join(
                    part for part in (
                        str(user.get("first_name") or "").strip(),
                        str(user.get("last_name") or "").strip(),
                    ) if part
                ) or user.get("email") or employee.get("full_name") or employee.get("employee_id") or report_user_id
                lead_id = str(employee.get("team_lead_id") or team_lead_id or "")
                team_lead = team_leads_by_id.get(lead_id, {})
                lead_name = " ".join(
                    part for part in (
                        str(team_lead.get("first_name") or "").strip(),
                        str(team_lead.get("last_name") or "").strip(),
                    ) if part
                ) or team_lead.get("full_name") or team_lead.get("email") or employee.get("team_lead") or ""
                result.append({
                    "id": f"{report_user_id}:{report_date}",
                    "user_id": report_user_id,
                    "employee_name": name,
                    "email": user.get("email") or employee.get("email") or employee.get("email_id") or "",
                    "team_lead": lead_name,
                    "date": report_date,
                    "leaveType": report.get("leaveType", ""),
                    "completed": report.get("completed", ""),
                    "completedNoUpdates": report.get("completedNoUpdates", False),
                    "inProgress": report.get("inProgress", ""),
                    "inProgressNoUpdates": report.get("inProgressNoUpdates", False),
                    "blockers": report.get("blockers", ""),
                    "blockersNoUpdates": report.get("blockersNoUpdates", False),
                    "nextPlan": report.get("nextPlan", ""),
                    "nextPlanNoUpdates": report.get("nextPlanNoUpdates", False),
                    "notes": report.get("notes", ""),
                    "notesNoUpdates": report.get("notesNoUpdates", False),
                })
            current_date += timedelta(days=1)

        return sorted(result, key=lambda item: (item["date"] or "", item["employee_name"].lower()))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get daily status details", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to get daily status details") from exc


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
        
        # Get all active employees (including team leads)
        employees = await employees_collection.find({
            "active_inactive": {"$ne": "Inactive"},
            "is_deleted": {"$ne": True}
        }).to_list(length=None)
        
        # Also load users to resolve team lead names when team_lead_id points to a user record
        users_collection = MongoDB.get_collection("users")
        users = await users_collection.find({}).to_list(length=None)
        
        # Create a mapping of user_id / _id -> record for team lead lookup
        team_lead_employees = {}
        for emp in employees:
            emp_user_id = str(emp.get("user_id", ""))
            emp_id = str(emp.get("_id", ""))
            if emp_user_id:
                team_lead_employees[emp_user_id] = emp
            if emp_id:
                team_lead_employees[emp_id] = emp
        for user in users:
            user_id = str(user.get("_id", ""))
            if user_id:
                team_lead_employees[user_id] = user
        
        # Create a user lookup map keyed by user _id for member name resolution
        users_map = {}
        for user in users:
            user_id_str = str(user.get("_id", ""))
            if user_id_str:
                users_map[user_id_str] = user
        
        # Group employees by team_lead_id relation
        team_groups = {}
        for emp in employees:
            team_lead_id = str(emp.get("team_lead_id") or "")
            if team_lead_id:
                if team_lead_id not in team_groups:
                    team_groups[team_lead_id] = []
                team_groups[team_lead_id].append(emp)

        current_user_ids = {
            str(value)
            for value in (current_user.get("_id"), current_user.get("id"))
            if value is not None
        }
        for employee in employees:
            if str(employee.get("user_id") or "") in current_user_ids and employee.get("_id") is not None:
                current_user_ids.add(str(employee["_id"]))

        current_user_teams = current_user_ids.intersection(team_groups)
        if current_user_teams:
            team_groups = {
                team_lead_id: members
                for team_lead_id, members in team_groups.items()
                if team_lead_id in current_user_teams
            }
        
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
        for team_lead_id, team_members in team_groups.items():
            total_members = len(team_members)
            completed_count = 0
            pending_members = []
            completed_members = []
            pending_member_details = []
            completed_member_details = []
            
            for member in team_members:
                user_id = str(member.get("user_id", ""))
                # Resolve member name from users collection via user_id
                user_record = users_map.get(user_id)
                if user_record:
                    first_name = user_record.get("first_name", "") or ""
                    last_name = user_record.get("last_name", "") or ""
                    member_name = (first_name + " " + last_name).strip() or user_record.get("email", "") or user_id
                else:
                    member_name = member.get("full_name") or member.get("employee_id") or member.get("email") or user_id or "Unknown"
                
                # Check if user has reports for all dates in the range
                if user_id and user_id in user_report_dates:
                    user_dates = user_report_dates[user_id]
                    if all_dates_in_range.issubset(user_dates):
                        all_sections_filled = True
                        for date in all_dates_in_range:
                            report = next((r for r in reports if r.get("date") == date and str(r.get("user_id")) == user_id), None)
                            if report:
                                leave_type = report.get("leaveType", "")
                                completed = report.get("completed", "").strip()
                                completed_no_updates = report.get("completedNoUpdates", False)
                                
                                # Report is complete if completed section is filled or checkbox checked
                                if not (completed or completed_no_updates):
                                    all_sections_filled = False
                                    break
                                
                                # For non-Working leave types, require all sections
                                if leave_type != 'Working':
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
                            completed_member_details.append({
                                "id": user_id or None,
                                "name": member_name,
                            })
                        else:
                            pending_members.append(member_name)
                            pending_member_details.append({
                                "id": user_id or None,
                                "name": member_name,
                            })
                    else:
                        pending_members.append(member_name)
                        pending_member_details.append({
                            "id": user_id or None,
                            "name": member_name,
                        })
                else:
                    pending_members.append(member_name)
                    pending_member_details.append({
                        "id": user_id or None,
                        "name": member_name,
                    })
            
            # Resolve team lead name by team_lead_id relation
            team_lead_name = None
            # First try users collection (team_lead_id references user _id)
            team_lead_user = users_map.get(team_lead_id)
            if team_lead_user:
                first = team_lead_user.get("first_name", "") or ""
                last = team_lead_user.get("last_name", "") or ""
                team_lead_name = (first + " " + last).strip() or team_lead_user.get("email", "") or team_lead_id
            if not team_lead_name:
                team_lead_emp = team_lead_employees.get(team_lead_id)
                if team_lead_emp:
                    team_lead_name = team_lead_emp.get("full_name")
                    if not team_lead_name:
                        first = team_lead_emp.get("first_name", "")
                        last = team_lead_emp.get("last_name", "")
                        if first or last:
                            team_lead_name = f"{first} {last}".strip()
                    if not team_lead_name:
                        team_lead_name = team_lead_emp.get("employee_id") or team_lead_emp.get("user_id") or team_lead_emp.get("email") or team_lead_id
            if not team_lead_name:
                team_lead_name = team_lead_id
            
            pending_count = total_members - completed_count
            completion_percentage = (completed_count / total_members * 100) if total_members > 0 else 0
            is_complete = completed_count == total_members and total_members > 0
            
            team_status_list.append(TeamCompletionStatus(
                team_lead=team_lead_name,
                team_lead_id=team_lead_id,
                total_team_members=total_members,
                completed_count=completed_count,
                pending_count=pending_count,
                completion_percentage=round(completion_percentage, 2),
                is_complete=is_complete,
                pending_members=pending_members,
                completed_members=completed_members,
                pending_member_details=pending_member_details,
                completed_member_details=completed_member_details,
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
