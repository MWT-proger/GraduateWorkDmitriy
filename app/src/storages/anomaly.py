from functools import lru_cache
from typing import AsyncGenerator

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models.anomaly import ResultAnomalyModel

from .base import BaseAnomalyStorage


class AnomalyStorageMongoDB(BaseAnomalyStorage):
    db: AsyncIOMotorDatabase

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(
            settings.MONGODB.COLLECTIONS.ANOMALY
        )
        self.db = db

    async def save_result(self, data: ResultAnomalyModel):
        doc = data.model_dump(by_alias=True)
        await self.collection.insert_one(document=doc)

    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[ResultAnomalyModel, None]:
        documents = await self.collection.find(
            {"user_id": ObjectId(user_id)}
        ).to_list(length)
        for doc in documents:
            yield ResultAnomalyModel(**doc)

    async def get_documents_by_user_and_id(
        self, user_id: str, anomaly_id: str
    ) -> ResultAnomalyModel:

        doc = await self.collection.find_one(
            {"_id": ObjectId(anomaly_id), "user_id": ObjectId(user_id)}
        )
        return ResultAnomalyModel(**doc) if doc else None


@lru_cache()
def get_anomaly_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AnomalyStorageMongoDB:
    return AnomalyStorageMongoDB(db=db)
