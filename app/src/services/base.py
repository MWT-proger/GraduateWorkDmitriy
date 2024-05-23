from abc import ABC, abstractmethod

from schemas import CreateUserSchema

class BaseService(ABC):

    def __init__(self, db) -> None:
        self.db = db
    
    
    @abstractmethod
    def create(self):
        ...

class BaseUserService(BaseService):
    
    @abstractmethod
    def create(self, data: CreateUserSchema):
        ...

class BaseAuthService(BaseService): ...
