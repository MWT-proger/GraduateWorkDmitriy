from datetime import datetime

from bson import ObjectId
from pydantic import Field, field_serializer

from .base import BaseObjectIDModel, PydanticObjectId, datetime_now


class Auth(BaseObjectIDModel):
    user_id: PydanticObjectId
    user_agent: str
    refresh_token: str
    created_at: datetime = Field(default_factory=datetime_now)

    @field_serializer("user_id")
    def serialize_dt(self, user_id: PydanticObjectId, _info):
        return ObjectId(user_id)
