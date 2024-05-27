from typing import Any, List, Optional

from pydantic import BaseModel, Field

from models.base import PydanticObjectId


class ParamsAlgorithmSchema(BaseModel):
    parametr: str = Field(example="max_forecast_steps")
    value: str = Field(example="None")


class TrainTestDataSchema(BaseModel):
    file_id: PydanticObjectId
    target_col: str = Field(example="temp_max")
    algorithm: str = Field(example="DefaultForecaster")
    algorithm_params: List[ParamsAlgorithmSchema] = Field
    train_percentage: int = Field(example=80)
    file_mode: str = Field(default="single")
    feature_cols: List[str] = None
    exog_cols: List[str] = None
    test_filename: str = None


class MetricTable(BaseModel):
    data: Any
    columns: Any
    editable: bool
    style_table: dict
    style_data: dict
    style_header: dict
    style_cell_conditional: Any
    style_header_conditional: Any


class ResultForecastSchema(BaseModel):
    train_metric_table: Optional[MetricTable]
    test_metric_table: Optional[MetricTable]
    figure_json: Optional[str]
