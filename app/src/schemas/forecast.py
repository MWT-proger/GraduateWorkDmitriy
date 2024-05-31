from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from merlion.dashboard.models.forecast import ForecastModel
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_serializer,
    model_validator,
)
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
    process = "in_process"
    success = "success"
    error = "error"


class ResultForecastSchema(BaseModel):
    id: Optional[str] = None
    message: Optional[str] = None
    status: StatusForecastEnum = StatusForecastEnum.success
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None
    test_ts: Optional[TimeseriesSchema] = None
    train_ts: Optional[TimeseriesSchema] = None
    exog_ts: Optional[TimeseriesSchema] = None


class ResultForecastDataListSchema(BaseModel):
    id: Optional[str]
    message: Optional[str] = None
    status: StatusForecastEnum = StatusForecastEnum.success
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None


class ResultForecastListSchema(BaseModel):
    data: List[ResultForecastDataListSchema] = []


class ForecastProgressEnum(Enum):
    start = ("Запрос получен.", 5)
    file_exist = (
        "Файл с датасетом найден. Запускается процесс прогнозирования.",
        10,
    )
    data_loaded = ("Данные из файла загружены.", 20)
    model_initialized = ("Модель инициализирована.", 25)
    training_started = ("Обучение модели началось.", 30)
    training_completed = ("Обучение модели завершено.", 70)
    train_metrics_computed = ("Обучающие метрики вычислены.", 75)
    test_metrics_computed = ("Тестовые метрики вычислены.", 80)
    save_model_train = ("Происходит сохранение модели.", 85)
    full_process_success = (
        "Процесс прогнозирование успешно произведен. Идет сохранение в БД.",
        90,
    )
    save_to_db_success = (
        "Сохранение в БД успешно произведено. Ждите результат.",
        95,
    )
    finish = ("Завершено", 100)

    def __init__(self, stage, percent):
        self.stage = stage
        self.percent = percent


class ResultWebSocketForecastDataSchema(BaseModel):
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None
    test_ts: Optional[TimeseriesSchema] = None
    train_ts: Optional[TimeseriesSchema] = None
    exog_ts: Optional[TimeseriesSchema] = None


class ResultWebSocketForecastSchema(BaseModel):
    status: StatusForecastEnum = StatusForecastEnum.success
    progress: Optional[ForecastProgressEnum] = None
    detail: Optional[List[dict[str, Any]]] = None

    message: Optional[str] = None
    data: Optional[ResultWebSocketForecastDataSchema] = None

    @field_serializer("progress")
    def serialize_progress(self, value: ForecastProgressEnum, _info):
        if value is None:
            return None
        return {"percent": value.percent, "stage": value.stage}
