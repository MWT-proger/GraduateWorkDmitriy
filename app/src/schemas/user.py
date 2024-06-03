from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from models.base import PydanticObjectId


class CreateUserSchema(BaseModel):
    """TODO: В будущем можно проверять:
    - правильную форму номера телефона
    - пароль на простоту и т.д.
    """

    username: str = Field(min_length=3, max_length=50, example="user123")
    password: str = Field(min_length=8, example="securepassword123")
    email: EmailStr = Field(example="user@example.com")
    full_name: str = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: str = Field(
        min_length=10, max_length=15, example="+79990000000"
    )


class UpdateUserSchema(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=50, example="user123")
    full_name: Optional[str] = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: Optional[str] = Field(
        min_length=10, max_length=15, example="+79990000000"
    )


class GetUserSchema(BaseModel):
    id: PydanticObjectId
    email: Optional[EmailStr] = None 
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None 


class ChangePasswordUserSchema(BaseModel):
    current_password: str = Field(min_length=8, example="securepassword123")
    new_password: str = Field(min_length=8, example="newsecurepassword123")
    confirm_new_password: str = Field(
        min_length=8, example="newsecurepassword123"
    )


class ConfirmEmailSchema(BaseModel):
    email: EmailStr
    otp_code: str
