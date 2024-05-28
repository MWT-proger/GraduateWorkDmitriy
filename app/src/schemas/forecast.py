from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from merlion.dashboard.models.forecast import ForecastModel
from pydantic import BaseModel, Field, ValidationError, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError
from typing_extensions import Self

from models.base import PydanticObjectId


class ParamsAlgorithmSchema(BaseModel):
    parametr: str = Field(example="max_forecast_steps")
    value: Any = Field(example="None")


class AlgorithmForecast(str, Enum):
    DefaultForecaster = "DefaultForecaster"
    Arima = "Arima"
    LGBMForecaster = "LGBMForecaster"
    ETS = "ETS"
    AutoETS = "AutoETS"
    Prophet = "Prophet"
    AutoProphet = "AutoProphet"
    Sarima = "Sarima"
    VectorAR = "VectorAR"
    RandomForestForecaster = "RandomForestForecaster"
    ExtraTreesForecaster = "ExtraTreesForecaster"


class TrainTestDataSchema(BaseModel):
    file_id: PydanticObjectId
    target_col: str = Field(example="temp_max")
    algorithm: AlgorithmForecast = Field(
        example=AlgorithmForecast.DefaultForecaster
    )
    algorithm_params: List[ParamsAlgorithmSchema] = Field
    train_percentage: int = Field(example=80, le=100, ge=10)
    file_mode: str = Field(default="single")
    feature_cols: Optional[List[str]] = None
    exog_cols: Optional[List[str]] = None
    test_filename: Optional[str] = None

    @model_validator(mode="after")
    def check_parametrs_by_algorithm(self) -> Self:

        params_info = ForecastModel.get_parameter_info(
            algorithm=self.algorithm
        )
        errors = []
        for param in self.algorithm_params:
            info = params_info.get(param.parametr)
            if not info:
                errors.append(
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "algorithm_parameter_not_exists",
                            "Параметр {name} не существует",
                            dict(name=param.parametr),
                        ),
                        loc=tuple(
                            [
                                "algorithm_params",
                            ]
                        ),
                        input=param,
                    )
                )
                continue

            if param.value is not None and not isinstance(
                param.value, info["type"]
            ):
                errors.append(
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "algorithm_parameter_not_exists",
                            "Параметр {name} имеет не верный тип. Необходимый тип: {type}",
                            dict(
                                name=param.parametr, type=info["type"].__name__
                            ),
                        ),
                        loc=tuple(
                            [
                                "algorithm_params",
                            ]
                        ),
                        input=param,
                    )
                )

        if errors:
            raise ValidationError.from_exception_data(
                "Проверка параметров алгоритма", errors
            )
        return self


class TimeseriesSchema(BaseModel):
    data: Optional[dict[str, Any]]
    index: List[datetime]


class StatusForecastEnum(str, Enum):
    success = "успешно"
    error = "ошибка"


class ResultForecastSchema(BaseModel):
    message: Optional[str] = None
    status: StatusForecastEnum = StatusForecastEnum.success
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None
    test_ts: Optional[TimeseriesSchema] = None
    train_ts: Optional[TimeseriesSchema] = None
    exog_ts: Optional[TimeseriesSchema] = None
