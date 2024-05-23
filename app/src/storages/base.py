from abc import ABC, abstractmethod

class BaseStorage(ABC):

    def __init__(self, db) -> None:
        self.db = db
    
    
    @abstractmethod
    def create(self):
        ...

class BaseUserStorage(BaseStorage):
    pass
