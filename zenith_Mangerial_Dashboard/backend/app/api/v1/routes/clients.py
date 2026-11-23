from typing import List
from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.exceptions import NotFoundException
from app.core.mongodb import MongoDB
from app.schemas.base import MessageResponse, PaginatedResponse
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate

router = APIRouter()


def convert_datetime_fields(doc: dict) -> dict:
    """Convert datetime fields to ISO format strings."""
    doc_copy = doc.copy()
    for field in ["created_at", "updated_at"]:
        if field in doc_copy and isinstance(doc_copy[field], datetime):
            doc_copy[field] = doc_copy[field].isoformat()
    return doc_copy


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    _: dict = Depends(require_permission("clients", "add")),
) -> ClientResponse:
    """Create a new client."""
    try:
        await MongoDB.connect()
        clients_collection = MongoDB.get_collection("clients")
        
        # Convert to dict and insert
        client_dict = data.model_dump()
        client_dict["status"] = client_dict.get("status", "active")
        
        result = await clients_collection.insert_one(client_dict)
        client_dict["id"] = str(result.inserted_id)
        
        # Convert datetime fields to strings
        client_dict = convert_datetime_fields(client_dict)
        
        return ClientResponse(**client_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    status: str = Query(default=None),
    _: dict = Depends(require_permission("clients", "view")),
) -> PaginatedResponse[ClientResponse]:
    """List all clients with pagination."""
    try:
        await MongoDB.connect()
        clients_collection = MongoDB.get_collection("clients")
        
        # Build query
        query = {"deleted_at": None}
        if status:
            query["status"] = status
        
        skip = (page - 1) * page_size
        
        # Get clients
        cursor = clients_collection.find(query).skip(skip).limit(page_size)
        clients = await cursor.to_list(length=page_size)
        
        # Get total count
        total = await clients_collection.count_documents(query)
        
        # Convert to response format
        items = []
        for client in clients:
            client_dict = client.copy()
            client_dict["id"] = str(client_dict["_id"])
            client_dict = convert_datetime_fields(client_dict)
            items.append(ClientResponse(**client_dict))
        
        return PaginatedResponse[ClientResponse].create(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    _: dict = Depends(require_permission("clients", "view")),
) -> ClientResponse:
    """Get a specific client by ID."""
    try:
        await MongoDB.connect()
        clients_collection = MongoDB.get_collection("clients")
        
        client = await clients_collection.find_one({
            "_id": ObjectId(client_id),
            "deleted_at": None
        })
        
        if not client:
            raise NotFoundException(f"Client '{client_id}' not found.")
        
        client_dict = client.copy()
        client_dict["id"] = str(client_dict["_id"])
        client_dict = convert_datetime_fields(client_dict)
        
        return ClientResponse(**client_dict)
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    _: dict = Depends(require_permission("clients", "modify")),
) -> ClientResponse:
    """Update a client."""
    try:
        await MongoDB.connect()
        clients_collection = MongoDB.get_collection("clients")
        
        # Check if client exists
        existing = await clients_collection.find_one({
            "_id": ObjectId(client_id),
            "deleted_at": None
        })
        
        if not existing:
            raise NotFoundException(f"Client '{client_id}' not found.")
        
        # Build update dict with only provided fields
        update_data = data.model_dump(exclude_unset=True)
        
        if update_data:
            await clients_collection.update_one(
                {"_id": ObjectId(client_id)},
                {"$set": update_data}
            )
        
        # Get updated client
        updated = await clients_collection.find_one({
            "_id": ObjectId(client_id),
            "deleted_at": None
        })
        
        updated_dict = updated.copy()
        updated_dict["id"] = str(updated_dict["_id"])
        updated_dict = convert_datetime_fields(updated_dict)
        
        return ClientResponse(**updated_dict)
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}", response_model=MessageResponse)
async def delete_client(
    client_id: str,
    _: dict = Depends(require_permission("clients", "delete")),
) -> MessageResponse:
    """Soft delete a client."""
    try:
        await MongoDB.connect()
        clients_collection = MongoDB.get_collection("clients")
        
        # Check if client exists
        existing = await clients_collection.find_one({
            "_id": ObjectId(client_id),
            "deleted_at": None
        })
        
        if not existing:
            raise NotFoundException(f"Client '{client_id}' not found.")
        
        # Soft delete
        await clients_collection.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": {"deleted_at": "now"}}
        )
        
        return MessageResponse(message=f"Client '{client_id}' deleted successfully.")
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
