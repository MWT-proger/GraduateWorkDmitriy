from functools import lru_cache
from abc import abstractmethod

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from exceptions.user import UserServiceException
from schemas import CreateUserSchema
from db.mongodb import get_db

from .base import BaseUserService


class UserService(BaseUserService):
    
    def create(self, data: CreateUserSchema):
       raise UserServiceException(name="222")
    
    def login(self, data: CreateUserSchema):
       raise UserServiceException(name="222")
    
    def logout(self, data: CreateUserSchema):
       raise UserServiceException(name="222")
    
    def refresh(self, data: CreateUserSchema):
       raise UserServiceException(name="222")


@lru_cache()
def get_user_service(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> UserService:
    return UserService(db=db)
