from typing import List
from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.exceptions import NotFoundException
from app.core.mongodb import MongoDB
from app.schemas.base import MessageResponse, PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


def convert_datetime_fields(doc: dict) -> dict:
    """Convert datetime fields to ISO format strings."""
    doc_copy = doc.copy()
    for field in ["created_at", "updated_at"]:
        if field in doc_copy and isinstance(doc_copy[field], datetime):
            doc_copy[field] = doc_copy[field].isoformat()
    return doc_copy


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    _: dict = Depends(require_permission("projects", "add")),
) -> ProjectResponse:
    """Create a new project."""
    try:
        await MongoDB.connect()
        projects_collection = MongoDB.get_collection("projects")
        clients_collection = MongoDB.get_collection("clients")
        
        # Verify client exists
        client = await clients_collection.find_one({
            "_id": ObjectId(data.client_id),
            "deleted_at": None
        })
        
        if not client:
            raise HTTPException(status_code=400, detail=f"Client '{data.client_id}' not found.")
        
        # Convert to dict and insert
        project_dict = data.model_dump()
        project_dict["status"] = project_dict.get("status", "active")
        
        result = await projects_collection.insert_one(project_dict)
        project_dict["id"] = str(result.inserted_id)
        project_dict = convert_datetime_fields(project_dict)
        
        return ProjectResponse(**project_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    status: str = Query(default=None),
    client_id: str = Query(default=None),
    _: dict = Depends(require_permission("projects", "view")),
) -> PaginatedResponse[ProjectResponse]:
    """List all projects with pagination."""
    try:
        await MongoDB.connect()
        projects_collection = MongoDB.get_collection("projects")
        
        # Build query
        query = {"deleted_at": None}
        if status:
            query["status"] = status
        if client_id:
            query["client_id"] = client_id
        
        skip = (page - 1) * page_size
        
        # Get projects
        cursor = projects_collection.find(query).skip(skip).limit(page_size)
        projects = await cursor.to_list(length=page_size)
        
        # Get total count
        total = await projects_collection.count_documents(query)
        
        # Convert to response format
        items = []
        for project in projects:
            project_dict = project.copy()
            project_dict["id"] = str(project_dict["_id"])
            project_dict = convert_datetime_fields(project_dict)
            items.append(ProjectResponse(**project_dict))
        
        return PaginatedResponse[ProjectResponse].create(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    _: dict = Depends(require_permission("projects", "view")),
) -> ProjectResponse:
    """Get a specific project by ID."""
    try:
        await MongoDB.connect()
        projects_collection = MongoDB.get_collection("projects")
        
        project = await projects_collection.find_one({
            "_id": ObjectId(project_id),
            "deleted_at": None
        })
        
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")
        
        project_dict = project.copy()
        project_dict["id"] = str(project_dict["_id"])
        project_dict = convert_datetime_fields(project_dict)
        
        return ProjectResponse(**project_dict)
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    _: dict = Depends(require_permission("projects", "modify")),
) -> ProjectResponse:
    """Update a project."""
    try:
        await MongoDB.connect()
        projects_collection = MongoDB.get_collection("projects")
        clients_collection = MongoDB.get_collection("clients")
        
        # Check if project exists
        existing = await projects_collection.find_one({
            "_id": ObjectId(project_id),
            "deleted_at": None
        })
        
        if not existing:
            raise NotFoundException(f"Project '{project_id}' not found.")
        
        # If client_id is being updated, verify new client exists
        if data.client_id:
            client = await clients_collection.find_one({
                "_id": ObjectId(data.client_id),
                "deleted_at": None
            })
            
            if not client:
                raise HTTPException(status_code=400, detail=f"Client '{data.client_id}' not found.")
        
        # Build update dict with only provided fields
        update_data = data.model_dump(exclude_unset=True)
        
        if update_data:
            await projects_collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_data}
            )
        
        # Get updated project
        updated = await projects_collection.find_one({
            "_id": ObjectId(project_id),
            "deleted_at": None
        })
        
        updated_dict = updated.copy()
        updated_dict["id"] = str(updated_dict["_id"])
        updated_dict = convert_datetime_fields(updated_dict)
        
        return ProjectResponse(**updated_dict)
    except NotFoundException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    _: dict = Depends(require_permission("projects", "delete")),
) -> MessageResponse:
    """Soft delete a project."""
    try:
        await MongoDB.connect()
        projects_collection = MongoDB.get_collection("projects")
        
        # Check if project exists
        existing = await projects_collection.find_one({
            "_id": ObjectId(project_id),
            "deleted_at": None
        })
        
        if not existing:
            raise NotFoundException(f"Project '{project_id}' not found.")
        
        # Soft delete
        await projects_collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"deleted_at": "now"}}
        )
        
        return MessageResponse(message=f"Project '{project_id}' deleted successfully.")
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
