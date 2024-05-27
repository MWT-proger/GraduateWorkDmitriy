from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .base import BaseUUIDModel, PydanticObjectId, datetime_now


class Dataset(BaseUUIDModel):
    file_path: Optional[str] = None
    file_name: str
    user_id: PydanticObjectId
    columns: Optional[List[str]] = None

    created_at: datetime = Field(default_factory=datetime_now)
