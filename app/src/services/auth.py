from datetime import datetime, timedelta
from functools import lru_cache

import jwt
from fastapi import Depends

from auth.password_manager import get_password_manager
from core.config import settings
from exceptions.auth import AuthServiceException
from schemas import LoginSchema
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

        access_token = self._create_access_token(user.id)
        refresh_token = self._create_refresh_token(user.id)

        await self.storage.upsert(
            user_id=str(user.id),
            user_agent=user_agent,
            new_refresh_token=refresh_token,
        )

        return access_token, refresh_token

    async def logout(self, user_id: str, user_agent: str, access: str):
        auth = await self.storage.get_by_user_id_and_user_agent(
            user_id, user_agent
        )

        if auth:
            await self.storage.delete_by_id(obj_id=auth.id)
        print("Отзываем Access", access)

    async def refresh(self, user_agent: str, refresh: str):
        auth = await self.storage.get_by_refresh_token_and_user_agent(
            refresh, user_agent
        )
        if not auth:
            raise AuthServiceException("Токен не валидный")

        access_token = self._create_access_token(auth.user_id)
        refresh_token = self._create_refresh_token(auth.user_id)

        await self.storage.upsert(
            user_id=str(auth.user_id),
            user_agent=user_agent,
            new_refresh_token=refresh_token,
        )

        return access_token, refresh_token

    def _create_access_token(self, user_id):
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now()
            + timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_jwt

    def _create_refresh_token(self, user_id):
        to_encode = {
            "sub": str(user_id),
            "refresh": True,
            "exp": datetime.now()
            + timedelta(days=settings.JWT.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_jwt

    def get_user_id_from_jwt(self, jwtoken: str) -> dict:
        try:
            payload = jwt.decode(
                jwtoken, settings.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
        except Exception:
            return None

        if payload.get("refresh"):
            return None
        return payload.get("sub")

    def get_user_id_from_refresh_jwt(self, jwtoken: str) -> dict:
        try:
            payload = jwt.decode(
                jwtoken, settings.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
        except Exception:
            return None
        if not payload.get("refresh"):
            return None
        return payload.get("sub")


@lru_cache()
def get_auth_service(
    storage: BaseAuthStorage = Depends(get_auth_storage),
    user_storage: BaseUserStorage = Depends(get_user_storage),
) -> AuthService:
    return AuthService(storage=storage, user_storage=user_storage)
