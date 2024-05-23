from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import settings


mongodb: Optional[AsyncIOMotorClient] = None

def get_db() -> AsyncIOMotorDatabase:
    return mongodb[settings.MONGODB.NAME]
