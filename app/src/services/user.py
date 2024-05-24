from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from models import User, Profile
from storages import get_user_storage
from exceptions.user import UserServiceException
from schemas import CreateUserSchema

from .base import BaseUserService


class UserService(BaseUserService):

    async def create(self, data: CreateUserSchema):
        user = User(
            username=data.username,
            email=data.email,
            password=data.password,
        )
        profile = Profile(user_id=user.id, full_name=data.full_name, phone_number=data.phone_number)
        await self.storage.create_user_and_profile(user=user, profile=profile)
        


@lru_cache()
def get_user_service(
    storage: AsyncIOMotorDatabase = Depends(get_user_storage),
) -> UserService:
    return UserService(storage=storage)
