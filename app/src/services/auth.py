from datetime import datetime, timedelta
from functools import lru_cache

import jwt
from fastapi import Depends

from auth.password_manager import get_password_manager
from core.config import settings
from exceptions.auth import AuthServiceException
from schemas import CreateUserSchema, LoginSchema
from services.base import BaseAuthService
from storages import BaseAuthStorage
from storages.auth import get_auth_storage
from storages.base import BaseUserStorage
from storages.user import get_user_storage


class AuthService(BaseAuthService):

    ALGORITHM = "HS256"

    def __init__(
        self, storage: BaseAuthStorage, user_storage: BaseUserStorage
    ) -> None:
        self.storage = storage
        self.user_storage = user_storage

    async def login(self, data: LoginSchema, user_agent: str):
        user = await self.user_storage.get_by_username(
            username=data.username, is_active=True
        )

        if not user:
            raise AuthServiceException(
                msg="Неверное имя пользователя или пароль"
            )

        password_manager = get_password_manager()
        is_verify = password_manager.verify_password(
            password=data.password, hash_str=user.password_hash
        )

        if not is_verify:
            raise AuthServiceException(
                msg="Неверное имя пользователя или пароль"
            )

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        await self.storage.upsert(
            user_id=str(user.id),
            user_agent=user_agent,
            new_refresh_token=refresh_token,
        )

        return access_token, refresh_token

    async def logout(self, data: CreateUserSchema):
        pass

    async def refresh(self, data: CreateUserSchema):
        pass

    def _create_access_token(self, user):
        to_encode = {
            "sub": str(user.id),
            "exp": datetime.now()
            + timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_jwt

    def _create_refresh_token(self, user):
        to_encode = {
            "sub": str(user.id),
            "exp": datetime.now()
            + timedelta(days=settings.JWT.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_jwt


@lru_cache()
def get_auth_service(
    storage: BaseAuthStorage = Depends(get_auth_storage),
    user_storage: BaseUserStorage = Depends(get_user_storage),
) -> AuthService:
    return AuthService(storage=storage, user_storage=user_storage)
