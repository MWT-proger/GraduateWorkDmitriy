#
# Copyright (c) 2023 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#

import asyncio
from functools import lru_cache
from typing import Any, List

from fastapi import Depends

from exceptions.forecast import ForecastServiceException
from models.forecast import ResultForecastModel, StatusForecastEnum
from schemas.forecast import ForecastProgressEnum, TrainTestDataSchema
from services.base import BaseForecastService
from services.merlion.models import ForecastModel
from storages.base import BaseDatasetStorage, BaseForecastStorage
from storages.dataset import get_dataset_storage
from storages.forecast import get_forecast_storage
from utils import serializer_timeseries_to_pydantic


class ForecastService(BaseForecastService):

    def __init__(
        self, storage: BaseForecastStorage, dataset_storage: BaseDatasetStorage
    ) -> None:
        self.storage = storage
        self.dataset_storage = dataset_storage

    models_storage = "data"  # Папка где хранятся модели

    async def get_users_history(
        self, user_id: str
    ) -> List[ResultForecastModel]:
        return self.storage.get_documents_by_user(user_id=user_id)

    async def get_train_test_result(
        self, data: TrainTestDataSchema, user_id: str, set_progress: Any
    ) -> ResultForecastModel:
        result_in_db = ResultForecastModel(user_id=user_id, params=data)
        file = await self.dataset_storage.get_document_by_user_and_id(
            user_id=user_id, doc_id=str(data.file_id)
        )

        if not file:
            raise ForecastServiceException(
                msg="Файл с датасетом временного ряда не существует."
            )
        await set_progress(ForecastProgressEnum.file_exist)
        await asyncio.sleep(0.01)
        try:
            (
                train_metrics,
                test_metrics,
                test_ts,
                train_ts,
                exog_ts,
                test_pred,
            ) = await self._train_test(
                file_path=file.file_path,
                target_col=data.target_col,
                algorithm=data.algorithm,
                algorithm_params=data.algorithm_params,
                train_percentage=data.train_percentage,
                file_mode=data.file_mode,
                feature_cols=data.feature_cols,
                exog_cols=data.exog_cols,
                test_filename=data.test_filename,
                set_progress=set_progress,
            )

        except ForecastServiceException as e:
            raise e
        except Exception as e:
            result_in_db.status = StatusForecastEnum.error
            result_in_db.message = str(e)
            raise ForecastServiceException(
                msg="Не удалось произвести вычисления."
            )

        else:
            await set_progress(ForecastProgressEnum.full_process_success)
            await asyncio.sleep(0.01)
            result_in_db.train_metrics = train_metrics
            result_in_db.test_metrics = test_metrics
            result_in_db.test_ts = serializer_timeseries_to_pydantic(test_ts)
            result_in_db.train_ts = serializer_timeseries_to_pydantic(
                test_pred
            )
            result_in_db.exog_ts = serializer_timeseries_to_pydantic(exog_ts)
            # result_in_db.test_pred = serializer_timeseries_to_pydantic(test_pred)

        finally:
            await self.storage.save_result(data=result_in_db)

        await set_progress(ForecastProgressEnum.save_to_db_success)
        await asyncio.sleep(0.01)

        return result_in_db

    async def _train_test(
        self,
        file_path,
        target_col,
        algorithm,
        algorithm_params,
        train_percentage,
        set_progress: Any,
        file_mode="single",
        feature_cols=None,
        exog_cols=None,
        test_filename=None,
    ):
        """
        Функция для обучения и тестирования модели прогнозирования временных рядов.

        Параметры:
        - file_path (str): Путь к файлу с датасетом временного ряда в формате CSV.
        - target_col (str): Имя колонки, содержащей целевую переменную для прогнозирования.
        - algorithm (str): Имя алгоритма прогнозирования, который будет использоваться для моделирования.
        - algorithm_params (dict): Словарь параметров для настройки выбранного алгоритма.
        - train_percentage (int): Процент данных, который будет использоваться для обучения модели.
        - file_mode (str, optional): Режим работы с файлами. Может быть "single" (один файл) или "double" (два файла).
        По умолчанию "single".
        - feature_cols (list[str], optional): Список имен колонок, используемых в качестве признаков модели.
        По умолчанию None.
        - exog_cols (list[str], optional): Список имен колонок, содержащих экзогенные переменные.
        По умолчанию None.
        - test_filename (str, optional): Имя файла для тестовых данных, используется только в режиме "double".
        По умолчанию None.

        Возвращает:
        - train_metrics (dict): Метрики для обучающей выборки.
        - test_metrics (dict): Метрики для тестовой выборки.
        - test_ts (pd.DataFrame): Тестовые данные с прогнозируемыми значениями.
        - train_ts (pd.DataFrame): Обучающие данные с прогнозируемыми значениями.
        - exog_ts (pd.DataFrame): Данные экзогенных переменных.
        """

        if not file_path:
            raise ForecastServiceException(msg="Файл обучающих данных пуст!")
        if not target_col:
            raise ForecastServiceException(
                msg="Пожалуйста, выберите целевую колонку для прогнозирования."
            )
        if not algorithm:
            raise ForecastServiceException(
                msg="Пожалуйста, выберите алгоритм прогнозирования."
            )

        feature_cols = feature_cols or []
        exog_cols = exog_cols or []
        params = {p.parametr: p.value for p in algorithm_params}

        df = ForecastModel().load_data(file_path=file_path)

        if len(df) <= 20:
            raise ForecastServiceException(
                msg=f"Длина входного временного ряда ({len(df)}) слишком мала."
            )

        if file_mode == "single":
            n = int(int(train_percentage) * len(df) / 100)
            train_df, test_df = df.iloc[:n], df.iloc[n:]
        else:
            if not test_filename:
                raise ForecastServiceException(msg="Тестовый файл пуст!")
            test_df = ForecastModel().load_data(file_path=test_filename)
            train_df = df

        await set_progress(ForecastProgressEnum.data_loaded)
        await asyncio.sleep(0.01)

        (
            model,
            train_metrics,
            test_metrics,
            test_ts,
            train_ts,
            exog_ts,
            test_pred,
        ) = await ForecastModel().train(
            algorithm,
            train_df,
            test_df,
            target_col,
            feature_cols,
            exog_cols,
            params,
            set_progress=set_progress,
        )
        await set_progress(ForecastProgressEnum.save_model_train)
        await asyncio.sleep(0.01)
        ForecastModel.save_model(self.models_storage, model, algorithm)

        return (
            train_metrics,
            test_metrics,
            test_ts,
            train_ts,
            exog_ts,
            test_pred,
        )


@lru_cache()
def get_forecast_service(
    storage: BaseForecastStorage = Depends(get_forecast_storage),
    dataset_storage: BaseDatasetStorage = Depends(get_dataset_storage),
) -> ForecastService:
    return ForecastService(storage=storage, dataset_storage=dataset_storage)
