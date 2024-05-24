from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.password_manager import get_password_manager
from core.utils import create_otp
from exceptions.user import UserServiceException
from models import Profile, User
from schemas import CreateUserSchema
from services.email import get_email_service
from storages import get_user_storage

from .base import BaseUserService


class UserService(BaseUserService):

    async def check_exist_email(self, email: str):
        if await self.storage.get_by_email(email):
            raise UserServiceException(
                "Пользователь с указанным адресом электронной почты уже существует."
            )

    async def check_exist_username(self, username: str):
        if await self.storage.get_by_username(username):
            raise UserServiceException(
                "Пользователь с указанным именем пользователя уже существует."
            )

    async def create(self, data: CreateUserSchema):
        await self.check_exist_email(data.email)
        await self.check_exist_username(data.username)

        password_manager = get_password_manager()
        email_service = get_email_service()
        hashed_password = password_manager.generate_hash(data.password)
        otp_code = create_otp()

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            otp_code=otp_code,
        )
        profile = Profile(
            user_id=user.id,
            full_name=data.full_name,
            phone_number=data.phone_number,
        )

        try:
            await self.storage.create_user_and_profile(
                user=user, profile=profile
            )
            await email_service.send_email_confirm(
            to=[
                data.email,
            ],
            otp_code=otp_code,
        )
        except Exception as e:
            raise UserServiceException(
                "Ошибка при создании пользователя"
            ) from e


@lru_cache()
def get_user_service(
    storage: AsyncIOMotorDatabase = Depends(get_user_storage),
) -> UserService:
    return UserService(storage=storage)
