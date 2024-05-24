from abc import ABC, abstractmethod

from schemas import CreateUserSchema
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


class BaseAuthService(BaseService): ...
