from functools import lru_cache
from typing import AsyncGenerator

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models.forecast import ResultForecastModel

from .base import BaseForecastStorage


class ForecastStorageMongoDB(BaseForecastStorage):
    db: AsyncIOMotorDatabase

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(
            settings.MONGODB.COLLECTIONS.FORECAST
        )
        self.db = db

    async def save_result(self, data: ResultForecastModel):
        doc = data.model_dump(by_alias=True)
        await self.collection.insert_one(document=doc)

    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[ResultForecastModel, None]:
        documents = await self.collection.find({"user_id": user_id}).to_list(
            length
        )
        for doc in documents:
            yield ResultForecastModel(**doc)

    async def get_documents_by_user_and_id(
        self, user_id: str, forecast_id: str
    ) -> ResultForecastModel:

        doc = await self.collection.find_one(
            {"_id": ObjectId(forecast_id), "user_id": user_id}
        )
        return ResultForecastModel(**doc) if doc else None


@lru_cache()
def get_forecast_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ForecastStorageMongoDB:
    return ForecastStorageMongoDB(db=db)
