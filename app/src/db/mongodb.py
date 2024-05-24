from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import settings

mongodb: Optional[AsyncIOMotorClient] = None


async def get_mongodb():
    return mongodb


def get_db() -> AsyncIOMotorDatabase:
    return mongodb[settings.MONGODB.NAME]
