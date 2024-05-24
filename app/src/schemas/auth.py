from pydantic import BaseModel, Field


class TokenJWTSchema(BaseModel):
    access_token: str
    refresh_token: str


class AuthJWTSchema(BaseModel):
    user_id: str
    token: str


class LoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password: str = Field(min_length=8, example="securepassword123")
