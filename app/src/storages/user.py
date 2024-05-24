from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from models import Profile, User
from core.config import settings
from db.mongodb import get_db

from .base import BaseUserStorage, BaseProfileStorage
from .profile import get_profile_storage


class UserStorageMongoDB(BaseUserStorage):
    db: AsyncIOMotorDatabase

    def __init__(self, db: AsyncIOMotorDatabase, profile_storage: BaseProfileStorage) -> None:
        self.profile_storage = profile_storage
        self.collection = db.get_collection(settings.MONGODB.COLLECTIONS.USERS)
        self.db = db

    async def create_user_and_profile(self, user: User, profile: Profile):
        
        # async with await self.db.client.start_session() as session:
        #     async with session.start_transaction():
        session = None
        await self.collection.insert_one(user.model_dump(), session=session)
        await self.profile_storage.create(profile=profile, session=session)


@lru_cache()
def get_user_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
    profile_storage: BaseProfileStorage = Depends(get_profile_storage),
) -> UserStorageMongoDB:
    return UserStorageMongoDB(db=db, profile_storage=profile_storage)
