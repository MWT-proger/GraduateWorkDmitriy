from abc import ABC, abstractmethod
from typing import Optional

from models import Profile, User
from models.auth import Auth


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
    async def get_by_id(self, user_id: str): ...

    @abstractmethod
    async def delete_by_id(self, user_id: str): ...

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str): ...


class BaseProfileStorage(BaseStorage):

    @abstractmethod
    async def create(self, profile: Profile, session=None): ...


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
