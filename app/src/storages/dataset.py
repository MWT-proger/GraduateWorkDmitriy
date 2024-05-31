from functools import lru_cache
from typing import AsyncGenerator

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.mongodb import get_db
from models.base import PydanticObjectId
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
        documents = await self.collection.find(
            {"user_id": ObjectId(user_id)}
        ).to_list(length)
        for doc in documents:
            yield Dataset(**doc)

    async def get_document_by_user_and_id(
        self, user_id: str, doc_id: PydanticObjectId
    ) -> Dataset:
        user_doc = await self.collection.find_one(
            {"_id": ObjectId(doc_id), "user_id": ObjectId(user_id)}
        )
        return Dataset(**user_doc) if user_doc else None


@lru_cache()
def get_dataset_storage(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> DatasetStorageMongoDB:
    return DatasetStorageMongoDB(db=db)
