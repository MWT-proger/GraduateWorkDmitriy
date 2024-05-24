from fastapi import APIRouter, Depends

from schemas import LoginSchema, TokenJWTSchema
from services.base import BaseUserService
from services.user import get_user_service

router = APIRouter()


# @router.post("/login", response_model=TokenJWTSchema)
# async def login(
#     data: LoginSchema, service: BaseUserService = Depends(get_user_service)
# ):
#     user = service.login(data)
#     return user


# @router.post("/logout", response_model=None)
# async def logout(service: BaseUserService = Depends(get_user_service)):
#     service.logout()


# @router.post("/refresh", response_model=TokenJWTSchema)
# async def refresh(service: BaseUserService = Depends(get_user_service)):
#     user = service.refresh()
#     return user
