from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models.dataset import Dataset

from .base import BaseDatasetStorage


class DatasetStorageMongoDB(BaseDatasetStorage):
    db: AsyncIOMotorDatabase

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.get_collection(
            settings.MONGODB.COLLECTIONS.DATASET
        )
        self.db = db

    async def create_document(self, document: Dataset):
        document_dict = document.model_dump(by_alias=True)
        await self.collection.insert_one(document_dict)

    async def get_documents_by_user(
        self, user_id: str, length: int = 100
    ) -> AsyncGenerator[Dataset, None]:
        documents = await self.collection.find({"user_id": user_id}).to_list(
            length
        )
        for doc in documents:
            yield Dataset(**doc)


@lru_cache()
def get_dataset_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> DatasetStorageMongoDB:
    return DatasetStorageMongoDB(db=db)
