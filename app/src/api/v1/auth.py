from fastapi import APIRouter, Depends, Request

from auth.auth_bearer import JWTBearer
from schemas import LoginSchema, SuccessSchema, TokenJWTSchema
from services.auth import get_auth_service
from services.base import BaseAuthService, BaseUserService
from services.user import get_user_service

router = APIRouter(
    tags=[
        "Auth",
    ]
)


@router.post("/login", response_model=TokenJWTSchema)
async def login(
    data: LoginSchema,
    request: Request,
    service: BaseAuthService = Depends(get_auth_service),
):
    user_agent = request.headers.get("user-agent")
    access_token, refresh_token = await service.login(data, user_agent)
    return TokenJWTSchema(
        access_token=access_token, refresh_token=refresh_token
    )


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
    access_token, refresh_token = await service.refresh()
    return TokenJWTSchema(
        access_token=access_token, refresh_token=refresh_token
    )
