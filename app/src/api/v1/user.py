from fastapi import APIRouter, Depends

from schemas import ChangePasswordUserSchema, CreateUserSchema, TokenJWTSchema
from services import BaseUserService, get_user_service

router = APIRouter()


@router.post("", response_model=TokenJWTSchema)
async def create(
    data: CreateUserSchema,
    service: BaseUserService = Depends(get_user_service),
):
    user = await service.create(data)
    return user


# @router.post("/change_password", response_model=None)
# async def change_password(
#     data: ChangePasswordUserSchema,
#     service: BaseUserService = Depends(get_user_service),
# ):
#     user = service.create(data)
#     return user


# @router.post("/confirm_email", response_model=TokenJWTSchema)
# async def confirm_email(
#     data: CreateUserSchema,
#     service: BaseUserService = Depends(get_user_service),
# ):
#     user = service.create(data)
#     return user


# @router.delete("", response_model=TokenJWTSchema)
# async def remove(service: BaseUserService = Depends(get_user_service)):
#     user = service.create()
#     return user
