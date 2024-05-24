from datetime import datetime

from pydantic import Field

from .base import BaseUUIDModel, datetime_now


class Auth(BaseUUIDModel):
    user_id: str
    user_agent: str
    refresh_token: str
    created_at: datetime = Field(default_factory=datetime_now)
