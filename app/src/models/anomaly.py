from datetime import datetime
from enum import Enum
from typing import Any, Optional

from bson import ObjectId
from pydantic import Field, field_serializer

from schemas.anomaly import AnomalyTrainTestDataSchema
from schemas.base import TimeseriesSchema

from .base import BaseObjectIDModel, PydanticObjectId, datetime_now


class StatusAnomalyEnum(str, Enum):
    process = "in_process"
    success = "success"
    error = "error"


class ResultAnomalyModel(BaseObjectIDModel):
    user_id: PydanticObjectId

    params: AnomalyTrainTestDataSchema
    message: Optional[str] = None
    status: StatusAnomalyEnum = StatusAnomalyEnum.success

    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None

    test_ts: Optional[TimeseriesSchema] = None
    test_pred: Optional[TimeseriesSchema] = None
    test_labels: Optional[TimeseriesSchema] = None

    created_at: datetime = Field(default_factory=datetime_now)

    @field_serializer("user_id")
    def serialize_dt(self, user_id: PydanticObjectId, _info):
        return ObjectId(user_id)
