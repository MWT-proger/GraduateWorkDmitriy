from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, example="user123")
    password: str = Field(min_length=8, example="securepassword123")
    email: EmailStr = Field(example="user@example.com")
    full_name: str = Field(
        min_length=3, max_length=100, example="Иванов Иван Иванович"
    )
    phone_number: str = Field(
        min_length=10, max_length=15, example="+79990000000"
    )


class ChangePasswordUserSchema(BaseModel):
    current_password: str = Field(min_length=8, example="securepassword123")
    new_password: str = Field(min_length=8, example="newsecurepassword123")
    confirm_new_password: str = Field(
        min_length=8, example="newsecurepassword123"
    )


class ConfirmEmailSchema(BaseModel):
    email: EmailStr
    otp_code: str
