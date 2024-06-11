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

    async def _find_user(self, query: dict) -> User:
        query["is_active"] = True
        user_doc = await self.collection.find_one(query)
        return User(**user_doc) if user_doc else None

    async def create_user_and_profile(self, user: User, profile: Profile):
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                user_data = user.model_dump(
                    exclude=["email", "username"], by_alias=True
                )
                user_data.update(
                    {
                        "email": user.email.lower(),
                        "username": user.username.lower(),
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

    async def get_by_email_and_otp(self, email: str, otp_code: str) -> User:
        user_doc = await self.collection.find_one(
            {"email": email.lower(), "otp_code": otp_code}
        )
        return User(**user_doc) if user_doc else None

    async def get_by_email(self, email: str) -> User:
        user_doc = await self.collection.find_one({"email": email.lower()})
        return User(**user_doc) if user_doc else None

    async def get_by_username(
        self, username: str, is_active: bool = None
    ) -> User:
        query = {"username": username.lower()}

        if is_active:
            query["is_active"] = True

        user_doc = await self.collection.find_one(filter=query)

        return User(**user_doc) if user_doc else None

    async def get_by_id(self, user_id: str) -> User:
        return await self._find_user({"_id": ObjectId(user_id)})

    async def delete_by_id(self, user_id: str):
        await self.collection.delete_one({"_id": ObjectId(user_id)})

    async def change_password(self, user_id: str, new_password: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": new_password,
                    "updated_at": datetime.now(),
                }
            },
        )

    async def update(self, user_id: str, data: dict):
        doc = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"updated_at": datetime.now(), **data}},
        )


@lru_cache()
def get_user_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
    profile_storage: BaseProfileStorage = Depends(get_profile_storage),
) -> UserStorageMongoDB:
    return UserStorageMongoDB(db=db, profile_storage=profile_storage)
