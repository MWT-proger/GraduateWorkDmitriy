from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import Field

from schemas.forecast import TimeseriesSchema, TrainTestDataSchema

from .base import BaseUUIDModel, PydanticObjectId, datetime_now


class StatusForecastEnum(str, Enum):
    process = "in_process"
    success = "success"
    error = "error"


class ResultForecastModel(BaseUUIDModel):
    user_id: PydanticObjectId

    params: TrainTestDataSchema
    message: Optional[str] = None
    status: StatusForecastEnum = StatusForecastEnum.success

    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None
    test_ts: Optional[TimeseriesSchema] = None
    train_ts: Optional[TimeseriesSchema] = None
    exog_ts: Optional[TimeseriesSchema] = None
    test_pred: Optional[TimeseriesSchema] = None

    created_at: datetime = Field(default_factory=datetime_now)
