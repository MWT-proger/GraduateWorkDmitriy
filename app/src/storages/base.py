from abc import ABC, abstractmethod

from models import Profile, User


class BaseStorage(ABC):

    def __init__(self, db) -> None:
        self.db = db


class BaseUserStorage(BaseStorage):
    
    @abstractmethod
    async def create_user_and_profile(self, user: User, profile: Profile):
        pass

class BaseProfileStorage(BaseStorage):

    @abstractmethod
    async def create(self, profile: Profile, session = None):
        ...
