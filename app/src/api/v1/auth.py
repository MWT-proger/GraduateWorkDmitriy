from fastapi import APIRouter, Depends, Request

from auth.auth_bearer import JWTBearer, JWTRefreshBearer
from schemas import LoginSchema, SuccessSchema, TokenJWTSchema
from schemas.auth import AuthJWTSchema
from services.auth import get_auth_service
from services.base import BaseAuthService

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
    response_model=SuccessSchema,
)
async def logout(
    request: Request,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseAuthService = Depends(get_auth_service),
):
    user_agent = request.headers.get("user-agent")

    await service.logout(
        user_id=auth_data.user_id,
        user_agent=user_agent,
        access=auth_data.token,
    )

    return SuccessSchema(msg="Успешно")


@router.post(
    "/refresh",
    response_model=TokenJWTSchema,
)
async def refresh(
    request: Request,
    auth_data: AuthJWTSchema = Depends(JWTRefreshBearer()),
    service: BaseAuthService = Depends(get_auth_service),
):
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token = await service.refresh(
        user_agent=user_agent,
        refresh=auth_data.token,
    )

    return TokenJWTSchema(
        access_token=access_token, refresh_token=refresh_token
    )
