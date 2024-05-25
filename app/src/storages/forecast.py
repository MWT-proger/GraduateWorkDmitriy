from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db

from .base import BaseForecastStorage


class ForecastStorageMongoDB(BaseForecastStorage):
    db: AsyncIOMotorDatabase

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(
            settings.MONGODB.COLLECTIONS.FORECAST
        )
        self.db = db

    async def save_result(self, result_data: dict):
        # TODO: Исправить result_data
        await self.collection.insert_one(result_data)


@lru_cache()
def get_forecast_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ForecastStorageMongoDB:
    return ForecastStorageMongoDB(db=db)
