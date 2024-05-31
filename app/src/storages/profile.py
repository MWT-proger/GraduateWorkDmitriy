from functools import lru_cache

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


@lru_cache()
def get_profile_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ProfileStorageMongoDB:
    return ProfileStorageMongoDB(db=db)
