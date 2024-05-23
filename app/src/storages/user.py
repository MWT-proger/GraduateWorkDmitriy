from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings

from .base import BaseUserStorage


class UserStorageMongoDB(BaseUserStorage):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(settings.MONGODB.COLLECTIONS.USERS)
