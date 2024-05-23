from abc import ABC, abstractmethod

class BaseService(ABC):

    def __init__(self, db) -> None:
        self.db = db
    
    
    @abstractmethod
    def create(self):
        ...

class BaseUserService(BaseService):
    pass
