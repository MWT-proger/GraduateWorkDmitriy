from pydantic import EmailStr, Field

from .base import BaseUUIDModel


class User(BaseUUIDModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password: str = Field(min_length=8, example="securepassword123")
    email: EmailStr = Field(example="user@example.com")


class Profile(BaseUUIDModel):
    full_name: str = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: str = Field(
        min_length=10, max_length=15, example="+79990000000"
    )
    user: User
