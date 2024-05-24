from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
