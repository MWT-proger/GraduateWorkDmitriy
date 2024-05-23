from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from db.mongodb import get_db
from exceptions.user import UserServiceException
from schemas import CreateUserSchema
from services.base import BaseAuthService


class AuthService(BaseAuthService):

    def login(self, data: CreateUserSchema):
        raise UserServiceException(name="222")

    def logout(self, data: CreateUserSchema):
        raise UserServiceException(name="222")

    def refresh(self, data: CreateUserSchema):
        raise UserServiceException(name="222")


@lru_cache()
def get_auth_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AuthService:
    return AuthService(db=db)
