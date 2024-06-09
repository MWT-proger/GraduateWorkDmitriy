from datetime import datetime
from functools import lru_cache

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models import Profile

from .base import BaseProfileStorage


class ProfileStorageMongoDB(BaseProfileStorage):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(
            settings.MONGODB.COLLECTIONS.PROFILES
        )

    async def create(self, profile: Profile, session=None):
        data = profile.model_dump(by_alias=True)
        await self.collection.insert_one(data, session=session)

    async def get_by_user_id(self, user_id: str) -> Profile:
        print(user_id)
        print("@@@@@@@@@@@@@@@@@@@@")
        user_doc = await self.collection.find_one(
            {"user_id": ObjectId(user_id)}
        )
        return Profile(**user_doc) if user_doc else None

    async def update(self, user_id: str, data: dict):
        await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"updated_at": datetime.now(), **data}},
        )


@lru_cache()
def get_profile_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ProfileStorageMongoDB:
    return ProfileStorageMongoDB(db=db)
