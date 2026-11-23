from typing import Any, Optional, Sequence

from bson import ObjectId

from app.models.mongo_employee import Employee
from app.repositories.mongo_base import MongoBaseRepository


class MongoEmployeeRepository(MongoBaseRepository):
    """MongoDB repository for Employee operations."""

    def __init__(self) -> None:
        super().__init__("employees")

    @staticmethod
    def _user_id_values(user_ids: Sequence[str]) -> list[Any]:
        values: list[Any] = []
        for user_id in user_ids:
            if user_id not in values:
                values.append(user_id)
            if ObjectId.is_valid(user_id):
                object_id = ObjectId(user_id)
                if object_id not in values:
                    values.append(object_id)
        return values

    async def get_by_user_id(self, user_id: str) -> Optional[dict]:
        """Get the employee record linked to a user account."""
        return await self.find_one(
            {"user_id": {"$in": self._user_id_values([user_id])}}
        )

    async def get_by_user_ids(self, user_ids: Sequence[str]) -> list[dict]:
        """Get employee records linked to the provided user accounts."""
        if not user_ids:
            return []
        return await self.find_many(
            {"user_id": {"$in": self._user_id_values(user_ids)}},
            limit=len(user_ids),
        )

    async def get_all_employees(
        self, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Get employees with pagination."""
        return await self.get_all(skip=skip, limit=limit)

    async def create(self, **kwargs) -> dict:
        """Create an employee record."""
        employee = Employee.model_validate(kwargs)
        return await super().create(employee.to_mongo())

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get an employee by its document ID."""
        return await super().get_by_id(id)

    async def update(self, id: str, **kwargs) -> Optional[dict]:
        """Update an employee record."""
        employee = Employee.model_validate(kwargs)
        update_data = employee.model_dump(
            exclude_unset=True,
            exclude={"id", "created_at", "updated_at", "is_deleted", "deleted_at"},
        )
        return await super().update(id, update_data)

    async def delete(self, id: str) -> bool:
        """Delete an employee record."""
        return await super().delete(id)
