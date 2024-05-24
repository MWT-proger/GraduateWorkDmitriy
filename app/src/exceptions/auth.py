from .base import ServiceException


class AuthServiceException(ServiceException):
    def __init__(self, msg: str, status_code: int = None):
        super().__init__(msg, status_code)
        self.status_code = status_code if status_code else 401


class AuthJWTException(ServiceException):
    def __init__(self, msg: str, status_code: int = None):
        super().__init__(msg, status_code)
        self.status_code = status_code if status_code else 403
