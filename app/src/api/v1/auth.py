from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer
from schemas import LoginSchema, SuccessSchema, TokenJWTSchema
from services.base import BaseUserService
from services.user import get_user_service

router = APIRouter(
    tags=[
        "Auth",
    ]
)


@router.post("/login", response_model=TokenJWTSchema)
async def login(
    data: LoginSchema, service: BaseUserService = Depends(get_user_service)
):
    user = service.login(data)
    return user


@router.post(
    "/logout",
    dependencies=[Depends(JWTBearer())],
    response_model=SuccessSchema,
)
async def logout(service: BaseUserService = Depends(get_user_service)):
    service.logout()


@router.post(
    "/refresh",
    dependencies=[Depends(JWTBearer())],
    response_model=TokenJWTSchema,
)
async def refresh(service: BaseUserService = Depends(get_user_service)):
    user = service.refresh()
    return user
