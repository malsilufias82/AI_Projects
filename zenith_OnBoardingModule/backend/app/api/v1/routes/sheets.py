"""
API endpoints for Excel sheet processing.

Each endpoint calls file-specific processor modules that use the helper functions.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import os
from pathlib import Path

from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.engine.sheets.helper import get_sheet_summary
from app.tasks.sheet_tasks import process_status_sheet, process_multiple_sheets, weekly_status_check

logger = get_logger(__name__)
router = APIRouter()


class SheetProcessRequest(BaseModel):
    """Request model for sheet processing"""
    file_path: str
    processor_module: str  # e.g., 'app.engine.sheets.plateformteam'
    du_file_path: Optional[str] = "DU.xlsx"
    async_processing: bool = False
    kwargs: Optional[Dict[str, Any]] = {}


class MultipleSheetsRequest(BaseModel):
    """Request model for processing multiple sheets"""
    file_configs: List[Dict[str, Any]]  # Each dict: {'file_path': str, 'processor_module': str, 'kwargs': dict}
    du_file_path: Optional[str] = "DU.xlsx"
    async_processing: bool = False


class SheetInfoRequest(BaseModel):
    """Request model for getting sheet information"""
    file_path: str


@router.post("/process")
async def process_sheet(
    file: UploadFile = File(...),
    processor_module: str = Form(...),
    du_file_path: str = Form("DU.xlsx"),
    async_processing: bool = Form(False)
):
    """
    Process a single Excel status sheet using a file-specific processor.
    
    - **file**: Uploaded Excel file
    - **processor_module**: Module path to the file-specific processor (e.g., 'app.engine.sheets.plateformteam')
    - **du_file_path**: Path to DU.xlsx for offboarded vlinkers (default: "DU.xlsx")
    - **async_processing**: If True, process in background and return task ID
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path("backend/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file to temp directory
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_path_str = str(file_path)
        
        # Handle du_file_path - if it's just a filename, look in temp directory
        du_path = Path(du_file_path)
        if not du_path.is_absolute() and not du_path.exists():
            # Try to find it in temp directory
            temp_du_path = temp_dir / du_file_path
            if temp_du_path.exists():
                du_file_path = str(temp_du_path)
            else:
                # Try with common variations
                for du_name in ["DU.xlsx", "DU Teams.xlsx", "du.xlsx", "du teams.xlsx"]:
                    temp_du_path = temp_dir / du_name
                    if temp_du_path.exists():
                        du_file_path = str(temp_du_path)
                        break
        
        if async_processing:
            # Process asynchronously via Celery
            task = process_status_sheet.delay(
                file_path=file_path_str,
                processor_module=processor_module,
                du_file_path=du_file_path
            )
            return {
                "status": "queued",
                "task_id": task.id,
                "message": "Sheet processing started in background"
            }
        else:
            # Process synchronously by importing the processor module
            module = __import__(processor_module, fromlist=['process_file'])
            result = await module.process_file(
                file_path_str, 
                du_file_path=du_file_path
            )
            return {
                "status": "completed",
                "result": result
            }
    except Exception as e:
        logger.error("Sheet processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-multiple")
async def process_multiple(request: MultipleSheetsRequest, background_tasks: BackgroundTasks):
    """
    Process multiple Excel files using their respective processors.
    
    - **file_configs**: List of dicts with 'file_path', 'processor_module', and optional 'kwargs' keys
    - **du_file_path**: Path to DU.xlsx for offboarded vlinkers (default: "DU.xlsx")
    - **async_processing**: If True, process in background and return task ID
    """
    try:
        if request.async_processing:
            # Process asynchronously via Celery
            task = process_multiple_sheets.delay(
                file_configs=request.file_configs,
                du_file_path=request.du_file_path
            )
            return {
                "status": "queued",
                "task_id": task.id,
                "message": "Multiple sheets processing started in background"
            }
        else:
            # Process synchronously
            results = []
            for config in request.file_configs:
                file_path = config.get('file_path')
                processor_module = config.get('processor_module')
                kwargs = config.get('kwargs', {})
                
                try:
                    module = __import__(processor_module, fromlist=['process_file'])
                    result = await module.process_file(file_path, du_file_path=request.du_file_path, **kwargs)
                    result['file_path'] = file_path
                    results.append(result)
                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'error': str(e),
                        'status': 'failed'
                    })
            
            total_unfilled = sum(
                result.get('total_unfilled', 0) 
                for result in results 
                if 'total_unfilled' in result
            )
            return {
                "status": "completed",
                "files_processed": len(results),
                "total_unfilled": total_unfilled,
                "results": results
            }
    except Exception as e:
        logger.error("Multiple sheets processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/info")
async def get_sheet_info(request: SheetInfoRequest):
    """
    Get summary information about sheets in an Excel file.
    
    - **file_path**: Path to the Excel file
    """
    try:
        summary = get_sheet_summary(request.file_path)
        return summary
    except Exception as e:
        logger.error("Failed to get sheet information", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly-check")
async def weekly_check(request: MultipleSheetsRequest, background_tasks: BackgroundTasks):
    """
    Run weekly status check across all team sheets.
    This is designed for scheduled execution (e.g., every Friday evening).
    
    - **file_configs**: List of dicts with 'file_path', 'processor_module', and optional 'kwargs' keys
    - **du_file_path**: Path to DU.xlsx for offboarded vlinkers (default: "DU.xlsx")
    """
    try:
        task = weekly_status_check.delay(
            file_configs=request.file_configs,
            du_file_path=request.du_file_path
        )
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Weekly status check started in background"
        }
    except Exception as e:
        logger.error("Weekly status check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a background task.
    
    - **task_id**: Celery task ID
    """
    try:
        from app.workers.celery_app import celery_app
        task_result = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "ready": task_result.ready()
        }
        
        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.result)
        else:
            response["info"] = str(task_result.info)
        
        return response
    except Exception as e:
        logger.error("Failed to get task status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-status")
async def get_team_status():
    """
    Get team status data from MongoDB for the status report page.
    Returns team structure with filled/unfilled counts for the current week.
    """
    try:
        await MongoDB.connect()
        daily_status_collection = MongoDB.get_collection("daily_status")
        
        # Get the most recent sheet date
        latest_sheet = await daily_status_collection.find_one(
            {}, sort=[("sheet_date", -1)]
        )
        
        if not latest_sheet:
            return {"teams": [], "message": "No status data found"}
        
        latest_sheet_date = latest_sheet.get("sheet_date")
        
        # Get all status records for the latest sheet
        status_records = await daily_status_collection.find({
            "sheet_date": latest_sheet_date
        }).to_list(length=None)
        
        # Group by team lead
        team_lead_data = {}
        
        for record in status_records:
            team_lead = record.get("team_lead")
            user_name = record.get("user_name")
            day_of_week = record.get("day_of_week")
            is_filled = record.get("is_filled", False)
            
            if not team_lead or not user_name:
                continue
            
            if team_lead not in team_lead_data:
                team_lead_data[team_lead] = {
                    "name": team_lead,
                    "teamSize": 0,
                    "unfilledCount": 0,
                    "filledCount": 0,
                    "members": {}
                }
            
            if user_name not in team_lead_data[team_lead]["members"]:
                team_lead_data[team_lead]["members"][user_name] = {
                    "name": user_name,
                    "unfilledCount": 0,
                    "mon": "filled",
                    "tue": "filled",
                    "wed": "filled",
                    "thu": "filled",
                    "fri": "filled"
                }
                team_lead_data[team_lead]["teamSize"] += 1
            
            # Map day of week to field name
            day_map = {
                "Monday": "mon",
                "Tuesday": "tue", 
                "Wednesday": "wed",
                "Thursday": "thu",
                "Friday": "fri"
            }
            
            day_field = day_map.get(day_of_week)
            if day_field:
                if is_filled:
                    team_lead_data[team_lead]["members"][user_name][day_field] = "filled"
                    team_lead_data[team_lead]["filledCount"] += 1
                else:
                    team_lead_data[team_lead]["members"][user_name][day_field] = "unfilled"
                    team_lead_data[team_lead]["members"][user_name]["unfilledCount"] += 1
        
        # Calculate unfilledCount as number of people with at least one unfilled day
        for tl_data in team_lead_data.values():
            people_with_unfilled = 0
            for member in tl_data["members"].values():
                if member["unfilledCount"] > 0:
                    people_with_unfilled += 1
            tl_data["unfilledCount"] = people_with_unfilled
        
        # Convert to array format
        teams = []
        for tl_data in team_lead_data.values():
            members_list = list(tl_data["members"].values())
            teams.append({
                "name": tl_data["name"],
                "teamSize": tl_data["teamSize"],
                "unfilledCount": tl_data["unfilledCount"],
                "filledCount": tl_data["filledCount"],
                "members": members_list
            })
        
        return {
            "sheet_date": latest_sheet_date,
            "teams": teams
        }
        
    except Exception as e:
        logger.error("Failed to get team status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly-status-breakdown")
async def get_weekly_status_breakdown():
    """
    Get weekly status breakdown from MongoDB for the productivity chart.
    Returns day-by-day breakdown of filled/unfilled/leave status for the current week.
    """
    try:
        await MongoDB.connect()
        daily_status_collection = MongoDB.get_collection("daily_status")
        
        # Get the most recent sheet date
        latest_sheet = await daily_status_collection.find_one(
            {}, sort=[("sheet_date", -1)]
        )
        
        if not latest_sheet:
            return {
                "sheet_date": None,
                "daily_breakdown": [],
                "summary": {
                    "total": 0,
                    "fill_rate": 0,
                    "unfilled": 0,
                    "leave": 0
                },
                "message": "No status data found"
            }
        
        latest_sheet_date = latest_sheet.get("sheet_date")
        
        # Get all status records for the latest sheet
        status_records = await daily_status_collection.find({
            "sheet_date": latest_sheet_date
        }).to_list(length=None)
        
        # Initialize day-wise counters
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_data = {day: {"filled": 0, "unfilled": 0, "leave": 0, "total": 0} for day in day_order}
        
        total_filled = 0
        total_unfilled = 0
        total_leave = 0
        total_entries = 0
        
        for record in status_records:
            day_of_week = record.get("day_of_week")
            is_filled = record.get("is_filled", False)
            is_leave = record.get("is_leave", False)
            
            if day_of_week in day_data:
                day_data[day_of_week]["total"] += 1
                total_entries += 1
                
                if is_leave:
                    day_data[day_of_week]["leave"] += 1
                    total_leave += 1
                elif is_filled:
                    day_data[day_of_week]["filled"] += 1
                    total_filled += 1
                else:
                    day_data[day_of_week]["unfilled"] += 1
                    total_unfilled += 1
        
        # Convert to array format for chart
        daily_breakdown = []
        for day in day_order:
            daily_breakdown.append({
                "day": day[:3],  # Mon, Tue, etc.
                "filled": day_data[day]["filled"],
                "unfilled": day_data[day]["unfilled"],
                "leave": day_data[day]["leave"],
                "total": day_data[day]["total"]
            })
        
        # Calculate summary
        fill_rate = (total_filled / total_entries * 100) if total_entries > 0 else 0
        
        return {
            "sheet_date": latest_sheet_date,
            "daily_breakdown": daily_breakdown,
            "summary": {
                "total": total_entries,
                "fill_rate": round(fill_rate, 1),
                "unfilled": total_unfilled,
                "leave": total_leave
            }
        }
        
    except Exception as e:
        logger.error("Failed to get weekly status breakdown", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
