from functools import lru_cache
from typing import Optional

from bson import ObjectId
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
        data = auth.model_dump(by_alias=True)

        await self.collection.insert_one(data)

    async def upsert(
        self, user_id: str, user_agent: str, new_refresh_token: str
    ):
        await self.collection.update_one(
            {"user_id": ObjectId(user_id), "user_agent": user_agent},
            {"$set": {"refresh_token": new_refresh_token}},
            upsert=True,
        )

    async def get_by_user_id_and_user_agent(
        self, user_id: str, user_agent: str
    ) -> Optional[Auth]:
        auth_doc = await self.collection.find_one(
            {"user_id": ObjectId(user_id), "user_agent": user_agent}
        )
        return Auth(**auth_doc) if auth_doc else None

    async def delete_by_id(self, obj_id: str):
        await self.collection.delete_one({"_id": ObjectId(obj_id)})

    async def get_by_refresh_token_and_user_agent(
        self, refresh_token: str, user_agent: str
    ) -> Optional[Auth]:
        auth_doc = await self.collection.find_one(
            {"refresh_token": refresh_token, "user_agent": user_agent}
        )
        return Auth(**auth_doc) if auth_doc else None


@lru_cache()
def get_auth_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_storage: BaseUserStorage = Depends(get_user_storage),
) -> AuthStorageMongoDB:
    return AuthStorageMongoDB(db=db, user_storage=user_storage)
