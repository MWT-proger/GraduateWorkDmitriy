from datetime import datetime
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel, Field

from models.base import PydanticObjectId


class DatasetSchema(BaseModel):
    id: PydanticObjectId = Field(example="665271bff4546cdc3faa2719")
    file_name: str = Field(example="example.csv")
    columns: List[str] = Field(example=["date", "max", "min"])
    created_at: datetime


class ListDatasetsSchema(BaseModel):
    data: List[DatasetSchema]


class DatasetFile(UploadFile):
    pass
