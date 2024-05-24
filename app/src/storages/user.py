from datetime import datetime
from functools import lru_cache

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models import Profile, User

from .base import BaseProfileStorage, BaseUserStorage
from .profile import get_profile_storage


class UserStorageMongoDB(BaseUserStorage):
    db: AsyncIOMotorDatabase

    def __init__(
        self, db: AsyncIOMotorDatabase, profile_storage: BaseProfileStorage
    ) -> None:
        self.profile_storage = profile_storage
        self.collection = db.get_collection(settings.MONGODB.COLLECTIONS.USERS)
        self.db = db

    async def _find_user(self, query: dict):
        query["is_active"] = True
        user_doc = await self.collection.find_one(query)
        return User(**user_doc) if user_doc else None

    async def create_user_and_profile(self, user: User, profile: Profile):
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                user_data = user.model_dump(
                    exclude=["id", "email", "username"]
                )

                user_data.update(
                    {
                        "email": user.email.lower(),
                        "username": user.username.lower(),
                        "_id": user.id,
                    }
                )
                await self.collection.insert_one(user_data, session=session)
                await self.profile_storage.create(
                    profile=profile, session=session
                )

    async def activate_user(self, user_id: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True, "updated_at": datetime.now()}},
        )

    async def get_by_email_and_otp(self, email: str, otp_code: str):
        user_doc = await self.collection.find_one(
            {"email": email.lower(), "otp_code": otp_code}
        )
        return User(**user_doc) if user_doc else None

    async def get_by_email(self, email: str):
        user_doc = await self.collection.find_one({"email": email.lower()})
        return User(**user_doc) if user_doc else None

    async def get_by_username(self, username: str):
        user_doc = await self.collection.find_one(
            {"username": username.lower()}
        )
        return User(**user_doc) if user_doc else None

    async def get_by_id(self, user_id: str):
        return await self._find_user({"_id": ObjectId(user_id)})

    async def delete_by_id(self, user_id: str):
        await self.collection.delete_one({"_id": ObjectId(user_id)})

    async def change_password(self, user_id: str, new_password: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": new_password, "updated_at": datetime.now()}},
        )


@lru_cache()
def get_user_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
    profile_storage: BaseProfileStorage = Depends(get_profile_storage),
) -> UserStorageMongoDB:
    return UserStorageMongoDB(db=db, profile_storage=profile_storage)
