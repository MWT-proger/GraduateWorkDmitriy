import os
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MongoCollections:
    USERS = "users"
    PROFILES = "profiles"
    AUTH = "auth"
    FORECAST = "forecast"


class JWTConfig:
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")
    TEMPLATES: str = os.path.dirname(BASE_DIR) + "/src/template/"
    HOST: str = ""
    PORT: int = 465
    HOST_USER: str = ""
    HOST_PASSWORD: str = ""
    DEFAULT_FROM_EMAIL: str = ""


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
    SECRET_KEY: str
    DEBUG: bool = False
    PROJECT_NAME: str = "app"
    PORT: str = "8000"
    BASE_DIR: str = BASE_DIR

    MONGODB: MongoDB = MongoDB()
    EMAIL: EmailConfig = EmailConfig()
    JWT: JWTConfig = JWTConfig()


settings = Settings()

if settings.DEBUG:
    LOGGING["root"]["level"] = "DEBUG"

logging_config.dictConfig(LOGGING)
