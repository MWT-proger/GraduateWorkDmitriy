from datetime import datetime

from bson import ObjectId
from pydantic import EmailStr, Field, field_serializer

from .base import BaseObjectIDModel, PydanticObjectId, datetime_now


class User(BaseObjectIDModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password_hash: str
    email: EmailStr = Field(example="user@example.com")
    is_active: bool = False
    updated_at: datetime = Field(default_factory=datetime_now)
    created_at: datetime = Field(default_factory=datetime_now)
    otp_code: str = None


class Profile(BaseObjectIDModel):
    full_name: str = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: str = Field(
        min_length=10, max_length=15, example="+79990000000"
    )
    user_id: PydanticObjectId
    updated_at: datetime = Field(default_factory=datetime_now)
    created_at: datetime = Field(default_factory=datetime_now)

    @field_serializer("user_id")
    def serialize_dt(self, user_id: PydanticObjectId, _info):
        return ObjectId(user_id)
