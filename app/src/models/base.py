from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class BaseUUIDModel(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)
