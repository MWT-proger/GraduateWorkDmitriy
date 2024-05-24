from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from exceptions.user import UserServiceException
from models import Profile, User
from schemas import CreateUserSchema
from storages import get_user_storage

from .base import BaseUserService


class UserService(BaseUserService):

    async def check_exist_email(self, email: str):
        is_existed_email = self.storage.get_by_email(email)
        if is_existed_email:
            return UserServiceException(
                "Пользователь с указанным адресом электронной почты уже существует."
            )

    async def create(self, data: CreateUserSchema):
        # Можно еще почту и username приводить к одному регистру
        # Проверка Что такая почта не используется
        # Проверка Что такой username не используется

        await self.check_exist_email(data.email)

        # Создание хеша для пароля
        user = User(
            username=data.username,
            email=data.email,
            password=data.password,
        )
        profile = Profile(
            user_id=user.id,
            full_name=data.full_name,
            phone_number=data.phone_number,
        )

        await self.storage.create_user_and_profile(user=user, profile=profile)


@lru_cache()
def get_user_service(
    storage: AsyncIOMotorDatabase = Depends(get_user_storage),
) -> UserService:
    return UserService(storage=storage)
