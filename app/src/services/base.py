from abc import ABC, abstractmethod

from schemas import ConfirmEmailSchema, CreateUserSchema, LoginSchema
from schemas.forecast import ResultForecastSchema, TrainTestDataSchema
from schemas.user import ChangePasswordUserSchema
from storages import BaseUserStorage
from storages.base import BaseAuthStorage


class BaseService(ABC):

    def __init__(self, storage) -> None:
        self.storage = storage


class BaseUserService(BaseService):
    storage: BaseUserStorage

    @abstractmethod
    async def create(self, data: CreateUserSchema): ...

    @abstractmethod
    async def confirm_email(self, data: ConfirmEmailSchema): ...

    @abstractmethod
    async def remove(self, user_id): ...

    @abstractmethod
    async def change_password(
        self, user_id: str, data: ChangePasswordUserSchema
    ): ...


class BaseAuthService(BaseService):

    def __init__(
        self, storage: BaseAuthStorage, user_storage: BaseUserStorage
    ) -> None:
        self.storage = storage
        self.user_storage = user_storage

    @abstractmethod
    async def login(self, data: LoginSchema, user_agent: str): ...

    @abstractmethod
    async def logout(self, user_id: str, user_agent: str, access: str): ...

    @abstractmethod
    async def refresh(self, user_agent: str, refresh: str): ...


class BaseForecastService(ABC):

    @abstractmethod
    async def get_train_test_result(
        self, data: TrainTestDataSchema, user_id: str
    ) -> ResultForecastSchema: ...
