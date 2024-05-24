from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models.auth import Auth
from storages.user import get_user_storage

from .base import BaseAuthStorage, BaseUserStorage


class AuthStorageMongoDB(BaseAuthStorage):
    db: AsyncIOMotorDatabase

    def __init__(
        self, db: AsyncIOMotorDatabase, user_storage: BaseUserStorage
    ) -> None:
        self.user_storage = user_storage
        self.collection = db.get_collection(settings.MONGODB.COLLECTIONS.AUTH)
        self.db = db

    async def create(self, auth: Auth):
        data = auth.model_dump(exclude=["id"])
        data["_id"] = auth.id

        await self.collection.insert_one(data)

    async def upsert(
        self, user_id: str, user_agent: str, new_refresh_token: str
    ):
        await self.collection.update_one(
            {"user_id": user_id, "user_agent": user_agent},
            {"$set": {"refresh_token": new_refresh_token}},
            upsert=True,
        )


@lru_cache()
def get_auth_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_storage: BaseUserStorage = Depends(get_user_storage),
) -> AuthStorageMongoDB:
    return AuthStorageMongoDB(db=db, user_storage=user_storage)
