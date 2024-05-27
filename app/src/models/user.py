from datetime import datetime

from pydantic import EmailStr, Field

from .base import BaseUUIDModel, PydanticObjectId, datetime_now


class User(BaseUUIDModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password_hash: str
    email: EmailStr = Field(example="user@example.com")
    is_active: bool = False
    updated_at: datetime = Field(default_factory=datetime_now)
    created_at: datetime = Field(default_factory=datetime_now)
    otp_code: str = None


class Profile(BaseUUIDModel):
    full_name: str = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: str = Field(
        min_length=10, max_length=15, example="+79990000000"
    )
    user_id: PydanticObjectId
    updated_at: datetime = Field(default_factory=datetime_now)
    created_at: datetime = Field(default_factory=datetime_now)
