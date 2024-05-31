from fastapi import Request, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.manager_ws import ManagerWebSocket
from exceptions.auth import AuthJWTException
from schemas.auth import AuthJWTSchema
from services.auth import get_auth_service


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.service = get_auth_service()

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthJWTException(
                    status_code=403, msg="Invalid authentication scheme."
                )
            user_id = self.service.get_user_id_from_jwt(
                credentials.credentials
            )
            if not user_id:
                raise AuthJWTException(
                    status_code=403, msg="Invalid token or expired token."
                )
            return AuthJWTSchema(
                user_id=user_id, token=credentials.credentials
            )
        else:
            raise AuthJWTException(
                status_code=403, msg="Invalid authorization code."
            )


class JWTRefreshBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTRefreshBearer, self).__init__(auto_error=auto_error)
        self.service = get_auth_service()

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTRefreshBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthJWTException(
                    status_code=403, msg="Invalid authentication scheme."
                )
            user_id = self.service.get_user_id_from_refresh_jwt(
                credentials.credentials
            )
            if not user_id:
                raise AuthJWTException(
                    status_code=403, msg="Invalid token or expired token."
                )
            return AuthJWTSchema(
                user_id=user_id, token=credentials.credentials
            )
        else:
            raise AuthJWTException(
                status_code=403, msg="Invalid authorization code."
            )


async def get_current_user_from_ws(websocket: WebSocket):
    manager_ws = ManagerWebSocket(ws=websocket)
    await manager_ws.ws.accept()

    token = manager_ws.ws.query_params.get("token")
    if not token:
        exc = AuthJWTException(
            status_code=403, msg="Не указан токен авторизации."
        )
        await manager_ws.send_exception(exc)
        await manager_ws.close(code=1008)
        raise exc

    service = get_auth_service()
    user_id = service.get_user_id_from_jwt(token)

    if not user_id:
        exc = AuthJWTException(
            status_code=403, msg="Токен авторизации не валидный или истек."
        )
        await manager_ws.send_exception(exc)
        await manager_ws.close(code=1008)
        raise exc

    return AuthJWTSchema(user_id=user_id, token=token)
