from typing import Any, Optional

from app.repositories.mongo_employee_repository import MongoEmployeeRepository


class MongoEmployeeService:
    """MongoDB-based employee service."""

    def __init__(self) -> None:
        self.repository = MongoEmployeeRepository()

    async def get_by_id(self, employee_id: str) -> Optional[dict]:
        """Get an employee by its document ID."""
        return await self.repository.get_by_id(employee_id)

    async def get_by_user_id(self, user_id: str) -> Optional[dict]:
        """Get the employee record linked to a user account."""
        return await self.repository.get_by_user_id(user_id)

    async def get_by_user_ids(self, user_ids: list[str]) -> list[dict]:
        """Get employee records linked to the provided user accounts."""
        return await self.repository.get_by_user_ids(user_ids)

    async def get_all_employees(
        self, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Get employees with pagination."""
        return await self.repository.get_all_employees(skip=skip, limit=limit)

    async def create_employee(self, data: dict[str, Any]) -> dict:
        """Create an employee record."""
        return await self.repository.create(**data)

    async def update_employee(
        self, employee_id: str, data: dict[str, Any]
    ) -> Optional[dict]:
        """Update an employee record."""
        return await self.repository.update(employee_id, **data)

    async def delete_employee(self, employee_id: str) -> bool:
        """Delete an employee record."""
        return await self.repository.delete(employee_id)
