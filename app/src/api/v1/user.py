from fastapi import APIRouter, Depends, File, UploadFile

from auth.auth_bearer import JWTBearer
from schemas import (
    ChangePasswordUserSchema,
    ConfirmEmailSchema,
    CreateUserSchema,
    SuccessSchema,
)
from schemas.auth import AuthJWTSchema
from schemas.user import GetUserProfileSchema, UpdateUserSchema
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


@router.patch("", response_model=GetUserProfileSchema, status_code=200)
async def update(
    data: UpdateUserSchema,
    service: BaseUserService = Depends(get_user_service),
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
):
    result = await service.update(data, user_id=auth_data.user_id)
    return result


@router.post("/img", response_model=GetUserProfileSchema)
async def upload_image(
    image: UploadFile = File(...),
    service: BaseUserService = Depends(get_user_service),
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
):
    result = await service.upload_image(image, user_id=auth_data.user_id)
    return result


@router.get("", response_model=GetUserProfileSchema, status_code=200)
async def get_user(
    service: BaseUserService = Depends(get_user_service),
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
):
    result = await service.get_profile(user_id=auth_data.user_id)
    return result


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
