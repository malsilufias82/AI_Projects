import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            if isinstance(v, str) and ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")
        return v

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SoftDeleteMixin(BaseModel):
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def to_mongo(self) -> dict[str, Any]:
        """Convert Pydantic model to MongoDB document."""
        excluded = {"id"}
        data = self.model_dump(exclude=excluded, by_alias=True, exclude_none=True)
        if "_id" not in data and self.id:
            data["_id"] = self.id
        return data

    @classmethod
    def from_mongo(cls, data: dict[str, Any]) -> "MongoBaseModel":
        """Create Pydantic model from MongoDB document."""
        if not data:
            return None
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)
