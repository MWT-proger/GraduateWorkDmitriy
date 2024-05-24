class ServiceException(Exception):
    def __init__(self, msg: str, status_code: int = None):
        self.msg = msg
        self.status_code = status_code if status_code else 400
