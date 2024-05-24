from abc import ABC, abstractmethod

from models import Profile, User


class BaseStorage(ABC):

    def __init__(self, db) -> None:
        self.db = db


class BaseUserStorage(BaseStorage):
    @abstractmethod
    async def create_user_and_profile(self, user: User, profile: Profile): ...

    @abstractmethod
    async def get_by_email(self, email: str): ...

    @abstractmethod
    async def activate_user(self, email: str, otp_code: str): ...

    @abstractmethod
    async def get_by_email_and_otp(self, email: str, otp_code: str): ...

    @abstractmethod
    async def get_by_username(self, username: str): ...

    @abstractmethod
    async def get_by_id(self, user_id: str): ...

    @abstractmethod
    async def delete_by_id(self, user_id: str): ...

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str): ...


class BaseProfileStorage(BaseStorage):

    @abstractmethod
    async def create(self, profile: Profile, session=None): ...
