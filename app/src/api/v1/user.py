from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer
from schemas import (
    ChangePasswordUserSchema,
    ConfirmEmailSchema,
    CreateUserSchema,
    SuccessSchema,
)
from schemas.auth import AuthJWTSchema
from services import BaseUserService, get_user_service

router = APIRouter(
    tags=[
        "User",
    ]
)


@router.post("", response_model=SuccessSchema, status_code=201)
async def create(
    data: CreateUserSchema,
    service: BaseUserService = Depends(get_user_service),
):
    await service.create(data)
    return SuccessSchema(msg="Успешно. Необходимо подтвердить почту.")


@router.post(
    "/change_password",
    response_model=SuccessSchema,
)
async def change_password(
    data: ChangePasswordUserSchema,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseUserService = Depends(get_user_service),
):
    await service.change_password(user_id=auth_data.user_id, data=data)

    return SuccessSchema(msg="Успешно")


@router.post("/confirm_email", response_model=SuccessSchema)
async def confirm_email(
    data: ConfirmEmailSchema,
    service: BaseUserService = Depends(get_user_service),
):
    await service.confirm_email(data)

    return SuccessSchema(msg="Успешно")


@router.delete("", response_model=SuccessSchema)
async def remove(
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseUserService = Depends(get_user_service),
):

    await service.remove(user_id=auth_data.user_id)

    return SuccessSchema(msg="Успешно")
