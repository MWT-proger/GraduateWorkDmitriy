from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import Field, field_serializer

from .base import BaseUUIDModel, PydanticObjectId, datetime_now


class Dataset(BaseUUIDModel):
    file_path: Optional[str] = None
    file_name: str
    user_id: PydanticObjectId
    columns: Optional[List[str]] = None

    created_at: datetime = Field(default_factory=datetime_now)

    @field_serializer("user_id")
    def serialize_dt(self, user_id: PydanticObjectId, _info):
        return ObjectId(user_id)
