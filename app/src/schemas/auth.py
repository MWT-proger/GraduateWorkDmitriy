from pydantic import BaseModel, Field

from models.base import PydanticObjectId


class TokenJWTSchema(BaseModel):
    access_token: str
    refresh_token: str


class AuthJWTSchema(BaseModel):
    user_id: PydanticObjectId
    token: str


class LoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password: str = Field(min_length=8, example="securepassword123")
