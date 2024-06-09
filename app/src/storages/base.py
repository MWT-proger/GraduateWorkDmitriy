from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from models import Profile, User
from models.anomaly import ResultAnomalyModel
from models.auth import Auth
from models.dataset import Dataset
from models.forecast import ResultForecastModel


class BaseStorage(ABC):

    def __init__(self, db) -> None:
        self.db = db


class BaseUserStorage(BaseStorage):
    @abstractmethod
    async def create_user_and_profile(self, user: User, profile: Profile): ...

    @abstractmethod
    async def get_by_email(self, email: str): ...

    @abstractmethod
    async def activate_user(self, user_id: str): ...

    @abstractmethod
    async def get_by_email_and_otp(
        self, email: str, otp_code: str
    ) -> User: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User: ...

    @abstractmethod
    async def delete_by_id(self, user_id: str): ...

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str): ...


class BaseProfileStorage(BaseStorage):

    @abstractmethod
    async def create(self, profile: Profile, session=None): ...

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Profile: ...

    @abstractmethod
    async def update(self, user_id: str, data: dict): ...


class BaseAuthStorage(BaseStorage):

    @abstractmethod
    async def create(self, auth: Auth): ...

    @abstractmethod
    async def upsert(
        self, user_id: str, user_agent: str, new_refresh_token: str
    ): ...

    @abstractmethod
    async def get_by_user_id_and_user_agent(
        self, user_id: str, user_agent: str
    ) -> Optional[Auth]: ...


class BaseForecastStorage(BaseStorage):

    @abstractmethod
    async def save_result(self, data: ResultForecastModel): ...

    @abstractmethod
    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[ResultForecastModel, None]: ...

    @abstractmethod
    async def get_documents_by_user_and_id(
        self, user_id: str, forecast_id: str
    ) -> ResultForecastModel: ...


class BaseDatasetStorage(BaseStorage):

    @abstractmethod
    async def create_document(self, document: Dataset): ...

    @abstractmethod
    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[Dataset, None]: ...

    @abstractmethod
    async def get_document_by_user_and_id(
        self, user_id: str, doc_id: str
    ) -> Dataset: ...


class BaseAnomalyStorage(BaseStorage):

    @abstractmethod
    async def save_result(self, data: ResultAnomalyModel): ...

    @abstractmethod
    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[ResultAnomalyModel, None]: ...

    @abstractmethod
    async def get_documents_by_user_and_id(
        self, user_id: str, anomaly_id: str
    ) -> ResultAnomalyModel: ...
