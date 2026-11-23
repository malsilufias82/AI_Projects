from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager for async operations."""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize MongoDB connection."""
        if cls.client is not None:
            return

        try:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            )
            cls.database = cls.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(
                "Connected to MongoDB",
                database=settings.MONGODB_DATABASE,
                url=settings.MONGODB_URL,
            )
        except Exception as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            raise

    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.database = None
            logger.info("Disconnected from MongoDB")

    @classmethod
    def get_database(cls):
        """Get the MongoDB database instance."""
        if cls.database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection from the database."""
        database = cls.get_database()
        return database[collection_name]


async def get_mongodb():
    """Dependency to get MongoDB database instance."""
    database = MongoDB.get_database()
    return database
