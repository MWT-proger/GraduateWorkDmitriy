from enum import Enum
from typing import Any, List, Optional, Self

from merlion.dashboard.models.anomaly import AnomalyModel
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_serializer,
    model_validator,
)
from pydantic_core import InitErrorDetails, PydanticCustomError

from models.base import PydanticObjectId
from schemas.base import ParamsAlgorithmSchema, TimeseriesSchema


class StatusAnomalyEnum(str, Enum):
    process = "in_process"
    success = "success"
    error = "error"


class AlgorithmAnomaly(str, Enum):
    DefaultDetector = "DefaultDetector"
    ArimaDetector = "ArimaDetector"
    DynamicBaseline = "DynamicBaseline"
    IsolationForest = "IsolationForest"
    ETSDetector = "ETSDetector"
    MSESDetector = "MSESDetector"
    ProphetDetector = "ProphetDetector"
    RandomCutForest = "RandomCutForest"
    SarimaDetector = "SarimaDetector"
    WindStats = "WindStats"
    SpectralResidual = "SpectralResidual"
    ZMS = "ZMS"
    DeepPointAnomalyDetector = "DeepPointAnomalyDetector"


class AnomalyProgressEnum(Enum):
    start = ("Запрос получен.", 5)
    file_exist = ("Файл с датасетом временного ряда найден", 5)

    data_loaded = ("Данные из файла загружены.", 20)

    start_anomaly_detector_training = ("Обучение детектора аномалий ...", 20)
    training_completed = ("Обучение завершено.", 60)
    get_train_metrics = (
        "Вычисление показателей эффективности обучения...",
        70,
    )
    sget_test_pred = ("Получение результатов во время тестирования...", 80)

    save_model_train = ("Происходит сохранение модели.", 85)

    full_process_success = (
        "Формирование данных для ответа.",
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


class AnomalyTrainTestDataSchema(BaseModel):
    file_id: PydanticObjectId
    columns: List[str] = Field(
        example=[
            "temp_max",
        ]
    )
    algorithm: AlgorithmAnomaly = Field(
        example=AlgorithmAnomaly.DefaultDetector
    )
    algorithm_params: List[ParamsAlgorithmSchema] = []
    label_column: Optional[str] = None
    train_percentage: int = Field(example=80, le=100, ge=10)
    file_mode: str = Field(default="single")
    test_filename: Optional[str] = None
    threshold_class: Optional[str] = None
    threshold_params: Optional[List[ParamsAlgorithmSchema]] = None

    @model_validator(mode="after")
    def check_parametrs_by_algorithm(self) -> Self:

        params_info = AnomalyModel.get_parameter_info(algorithm=self.algorithm)
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


class ResultWebSocketAnomalyDataSchema(BaseModel):
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None

    test_ts: Optional[TimeseriesSchema] = None
    test_pred: Optional[TimeseriesSchema] = None
    test_labels: Optional[TimeseriesSchema] = None


class ResultWebSocketAnomalySchema(BaseModel):
    status: StatusAnomalyEnum = StatusAnomalyEnum.success
    progress: Optional[AnomalyProgressEnum] = None
    detail: Optional[List[dict[str, Any]]] = None

    message: Optional[str] = None
    data: Optional[ResultWebSocketAnomalyDataSchema] = None

    @field_serializer("progress")
    def serialize_progress(self, value: AnomalyProgressEnum, _info):
        if value is None:
            return None
        return {"percent": value.percent, "stage": value.stage}


class ResultAnomalySchema(BaseModel):
    id: Optional[str] = None
    message: Optional[str] = None
    status: StatusAnomalyEnum = StatusAnomalyEnum.success
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None

    test_ts: Optional[TimeseriesSchema] = None
    test_pred: Optional[TimeseriesSchema] = None
    test_labels: Optional[TimeseriesSchema] = None


class ResultAnomalyDataListSchema(BaseModel):
    id: Optional[str]
    message: Optional[str] = None
    status: StatusAnomalyEnum = StatusAnomalyEnum.success
    train_metrics: Optional[dict[str, Any]] = None
    test_metrics: Optional[dict[str, Any]] = None


class ResultAnomalyListSchema(BaseModel):
    data: List[ResultAnomalyDataListSchema] = []
