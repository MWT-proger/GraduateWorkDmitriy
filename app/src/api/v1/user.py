from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer
from schemas import (
    ChangePasswordUserSchema,
    ConfirmEmailSchema,
    CreateUserSchema,
    SuccessSchema,
)
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
    dependencies=[Depends(JWTBearer())],
    response_model=SuccessSchema,
)
async def change_password(
    data: ChangePasswordUserSchema,
    service: BaseUserService = Depends(get_user_service),
):
    user = service.create(data)
    return user


@router.post("/confirm_email", response_model=SuccessSchema)
async def confirm_email(
    data: ConfirmEmailSchema,
    service: BaseUserService = Depends(get_user_service),
):
    user = service.create(data)
    return user


@router.delete(
    "", dependencies=[Depends(JWTBearer())], response_model=SuccessSchema
)
async def remove(service: BaseUserService = Depends(get_user_service)):
    user = service.create()
    return user
