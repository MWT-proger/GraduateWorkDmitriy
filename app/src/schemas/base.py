from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SuccessSchema(BaseModel):
    msg: str = Field(example="Операция прошла успешно")


class TimeseriesSchema(BaseModel):
    data: Optional[dict[str, Any]]
    index: List[datetime]


class ParamsAlgorithmSchema(BaseModel):
    parametr: str = Field(example="max_forecast_steps")
    value: Any = Field(example="None")
