from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument

from app.core.mongodb import MongoDB
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoBaseRepository:
    """Base repository for MongoDB operations with flexible schema support."""

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
        self._collection = None

    @property
    def collection(self):
        """Lazy load the collection."""
        if self._collection is None:
            self._collection = MongoDB.get_collection(self.collection_name)
        return self._collection

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new document."""
        if "_id" not in data:
            data["_id"] = str(uuid4())
        
        data["created_at"] = datetime.now(timezone.utc)
        data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        logger.info(
            f"Created document in {self.collection_name}",
            document_id=str(result.inserted_id),
        )
        return self._serialize_mongo_doc(created_doc)

    async def get_by_id(self, id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        # Try to convert to ObjectId if it looks like one
        try:
            object_id = ObjectId(id)
            doc = await self.collection.find_one({"_id": object_id})
        except:
            # If not a valid ObjectId, try as string
            doc = await self.collection.find_one({"_id": str(id)})
        return self._serialize_mongo_doc(doc) if doc else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all documents with optional filters and pagination."""
        query = filters or {}
        if "is_deleted" not in query:
            query["is_deleted"] = {"$ne": True}
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        docs = await cursor.to_list(length=limit)
        return [self._serialize_mongo_doc(doc) for doc in docs]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching filters."""
        query = filters or {}
        if "is_deleted" not in query:
            query["is_deleted"] = {"$ne": True}
        return await self.collection.count_documents(query)

    async def update(
        self,
        id: Union[str, UUID],
        data: Dict[str, Any],
        upsert: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Update a document by ID."""
        data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.find_one_and_update(
            {"_id": str(id), "is_deleted": {"$ne": True}},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
            upsert=upsert,
        )
        
        if result:
            logger.info(
                f"Updated document in {self.collection_name}",
                document_id=str(id),
            )
            return self._serialize_mongo_doc(result)
        return None

    async def delete(self, id: Union[str, UUID]) -> bool:
        """Hard delete a document by ID."""
        result = await self.collection.delete_one({"_id": str(id)})
        deleted = result.deleted_count > 0
        if deleted:
            logger.info(
                f"Deleted document from {self.collection_name}",
                document_id=str(id),
            )
        return deleted

    async def soft_delete(self, id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """Soft delete a document by ID."""
        return await self.update(
            id,
            {"is_deleted": True, "deleted_at": datetime.now(timezone.utc)},
        )

    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if a document matching filters exists."""
        if "is_deleted" not in filters:
            filters["is_deleted"] = {"$ne": True}
        count = await self.collection.count_documents(filters)
        return count > 0

    async def find_one(
        self, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find a single document matching filters."""
        if "is_deleted" not in filters:
            filters["is_deleted"] = {"$ne": True}
        doc = await self.collection.find_one(filters)
        return self._serialize_mongo_doc(doc) if doc else None

    async def find_many(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents matching filters."""
        if "is_deleted" not in filters:
            filters["is_deleted"] = {"$ne": True}
        
        cursor = self.collection.find(filters).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        docs = await cursor.to_list(length=limit)
        return [self._serialize_mongo_doc(doc) for doc in docs]

    async def upsert(
        self,
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a document if it exists, otherwise create it."""
        data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            filters,
            {"$set": data},
            upsert=True,
        )
        
        if result.upserted_id:
            # Document was inserted
            created_doc = await self.collection.find_one({"_id": result.upserted_id})
            logger.info(
                f"Upserted (created) document in {self.collection_name}",
                document_id=str(result.upserted_id),
            )
            return self._serialize_mongo_doc(created_doc)
        else:
            # Document was updated
            updated_doc = await self.collection.find_one(filters)
            logger.info(
                f"Upserted (updated) document in {self.collection_name}",
                filters=str(filters),
            )
            return self._serialize_mongo_doc(updated_doc)

    async def aggregate(
        self, pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline."""
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        return [self._serialize_mongo_doc(doc) for doc in docs]

    async def bulk_insert(
        self, documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Insert multiple documents in bulk."""
        for doc in documents:
            if "_id" not in doc:
                doc["_id"] = str(uuid4())
            doc["created_at"] = datetime.now(timezone.utc)
            doc["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_many(documents)
        logger.info(
            f"Bulk inserted {len(result.inserted_ids)} documents into {self.collection_name}",
        )
        return [str(id) for id in result.inserted_ids]

    async def bulk_update(
        self, updates: List[Dict[str, Any]]
    ) -> int:
        """Update multiple documents in bulk."""
        # updates should be a list of dicts with 'filter' and 'update' keys
        operations = []
        for update in updates:
            update["update"]["updated_at"] = datetime.now(timezone.utc)
            operations.append(
                {
                    "filter": update["filter"],
                    "update": {"$set": update["update"]},
                    "upsert": False,
                }
            )
        
        result = await self.collection.bulk_write(
            [
                {"update_one": op}
                for op in operations
            ]
        )
        logger.info(
            f"Bulk updated {result.modified_count} documents in {self.collection_name}",
        )
        return result.modified_count

    def _serialize_mongo_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to JSON-serializable format."""
        if doc is None:
            return None
        
        # Convert ObjectId to string
        if "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])
        
        # Convert datetime objects to ISO format strings
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif isinstance(value, dict):
                doc[key] = self._serialize_mongo_doc(value)
            elif isinstance(value, list):
                doc[key] = [
                    self._serialize_mongo_doc(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return doc

    async def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
    ) -> tuple[List[Dict[str, Any]], int]:
        """Paginate documents."""
        skip = (page - 1) * page_size
        items = await self.get_all(skip=skip, limit=page_size, filters=filters, sort=sort)
        total = await self.count(filters=filters)
        return items, total
