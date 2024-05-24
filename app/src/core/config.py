import os
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING


class MongoCollections:
    USERS = "users"
    PROFILES = "profiles"


class MongoDB(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONGODB_")

    NAME: str
    PORT: str
    HOST: str
    USER: str
    PASSWORD: str
    COLLECTIONS: MongoCollections = MongoCollections()

    @property
    def DSN(self):
        return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}"


class Settings(BaseSettings):
    DEBUG: bool = False
    PROJECT_NAME: str = "app"
    PORT: str = "8000"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    MONGODB: MongoDB = MongoDB()


settings = Settings()

if settings.DEBUG:
    LOGGING["root"]["level"] = "DEBUG"

logging_config.dictConfig(LOGGING)
