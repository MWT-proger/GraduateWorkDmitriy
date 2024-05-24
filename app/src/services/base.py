from abc import ABC, abstractmethod

from schemas import ConfirmEmailSchema, CreateUserSchema
from storages import BaseUserStorage


class BaseService(ABC):

    def __init__(self, storage) -> None:
        self.storage = storage

    @abstractmethod
    async def create(self): ...


class BaseUserService(BaseService):
    storage: BaseUserStorage

    @abstractmethod
    async def create(self, data: CreateUserSchema): ...

    @abstractmethod
    async def confirm_email(self, data: ConfirmEmailSchema): ...


class BaseAuthService(BaseService): ...
