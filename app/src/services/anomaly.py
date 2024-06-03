#
# Copyright (c) 2023 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#

import asyncio
from functools import lru_cache
from typing import Any, AsyncGenerator, List

from fastapi import Depends

from exceptions.anomaly import AnomalyServiceException
from models.anomaly import ResultAnomalyModel, StatusAnomalyEnum
from schemas.anomaly import AnomalyProgressEnum, AnomalyTrainTestDataSchema
from services.base import BaseAnomalyService
from services.merlion.models import AnomalyModel
from storages.anomaly import get_anomaly_storage
from storages.base import BaseAnomalyStorage, BaseDatasetStorage
from storages.dataset import get_dataset_storage
from utils import serializer_timeseries_to_pydantic


class AnomalyService(BaseAnomalyService):

    def __init__(
        self, storage: BaseAnomalyStorage, dataset_storage: BaseDatasetStorage
    ) -> None:
        self.storage = storage
        self.dataset_storage = dataset_storage

    models_storage = "data"  # Папка где хранятся модели

    async def get_users_history(
        self, user_id: str
    ) -> List[ResultAnomalyModel]:
        return self.storage.get_documents_by_user(user_id=user_id)

    async def get_users_history_by_id(
        self, user_id: str, anomaly_id: str
    ) -> AsyncGenerator[ResultAnomalyModel, None]:
        obj = await self.storage.get_documents_by_user_and_id(
            user_id=user_id, anomaly_id=anomaly_id
        )
        if not obj:
            raise AnomalyServiceException("Объект не найден", status_code=404)
        return obj

    async def get_train_test_result(
        self, data: AnomalyTrainTestDataSchema, user_id: str, set_progress: Any
    ) -> ResultAnomalyModel:

        result_in_db = ResultAnomalyModel(user_id=user_id, params=data)

        file = await self.dataset_storage.get_document_by_user_and_id(
            user_id=user_id, doc_id=str(data.file_id)
        )
        if not file:
            raise AnomalyServiceException(
                msg="Файл с датасетом временного ряда не существует."
            )
        await set_progress(AnomalyProgressEnum.file_exist)
        await asyncio.sleep(0.01)

        try:
            train_metrics, test_metrics, test_ts, test_pred, test_labels = (
                await self._train(
                    set_progress=set_progress,
                    file_path=file.file_path,
                    columns=data.columns,
                    algorithm=data.algorithm,
                    algorithm_params=data.algorithm_params,
                    label_column=data.label_column,
                    train_percentage=data.train_percentage,
                    file_mode=data.file_mode,
                    test_filename=data.test_filename,
                    threshold_class=data.threshold_class,
                    threshold_params=data.threshold_params,
                )
            )

        except AnomalyServiceException as e:
            raise e
        except Exception as e:
            result_in_db.status = StatusAnomalyEnum.error
            result_in_db.message = str(e)
            raise AnomalyServiceException(
                msg="Не удалось произвести вычисления."
            )

        else:

            await set_progress(AnomalyProgressEnum.full_process_success)
            await asyncio.sleep(0.01)
            result_in_db.train_metrics = train_metrics
            result_in_db.test_metrics = test_metrics
            result_in_db.test_ts = serializer_timeseries_to_pydantic(test_ts)
            result_in_db.test_pred = serializer_timeseries_to_pydantic(
                test_pred
            )
            result_in_db.test_labels = serializer_timeseries_to_pydantic(
                test_labels
            )

        finally:
            await self.storage.save_result(data=result_in_db)

        await set_progress(AnomalyProgressEnum.save_to_db_success)
        await asyncio.sleep(0.01)

        return result_in_db

    async def _train(
        self,
        set_progress: Any,
        file_path,
        columns,
        algorithm,
        algorithm_params,
        label_column,
        train_percentage,
        file_mode="single",
        test_filename=None,
        threshold_class=None,
        threshold_params=None,
    ):

        if not file_path:
            raise AnomalyServiceException(msg="Файл данных пуст!")
        if not columns:
            raise AnomalyServiceException(
                msg="Пожалуйста, выберите переменные/показатели для анализа."
            )
        if not algorithm:
            raise AnomalyServiceException(
                msg="Пожалуйста, выберите детектор аномалий для обучения."
            )

        df = AnomalyModel().load_data(file_path=file_path)

        if len(df) <= 20:
            raise AnomalyServiceException(
                msg=f"Длина входного временного ряда ({len(df)}) слишком мала."
            )

        if file_mode == "single":
            n = int(int(train_percentage) * len(df) / 100)
            train_df, test_df = df.iloc[:n], df.iloc[n:]
        else:
            if not test_filename:
                raise AnomalyServiceException(msg="Тестовый файл пуст!")
            test_df = AnomalyModel().load_data(file_path=test_filename)
            train_df = df

        await set_progress(AnomalyProgressEnum.data_loaded)
        await asyncio.sleep(0.01)

        alg_params = {p.parametr: p.value for p in algorithm_params}

        if threshold_class:
            threshold_class_and_params = (
                threshold_class,
                {p.parametr: p.value for p in threshold_params},
            )
        else:
            threshold_class_and_params = None

        (
            model,
            train_metrics,
            test_metrics,
            test_ts,
            test_pred,
            test_labels,
        ) = await AnomalyModel().train(
            algorithm,
            train_df,
            test_df,
            columns,
            label_column,
            alg_params,
            threshold_class_and_params,
            set_progress,
        )

        await set_progress(AnomalyProgressEnum.save_model_train)
        await asyncio.sleep(0.01)
        AnomalyModel.save_model(self.models_storage, model, algorithm)

        return (train_metrics, test_metrics, test_ts, test_pred, test_labels)


@lru_cache()
def get_anomaly_service(
    storage: BaseAnomalyStorage = Depends(get_anomaly_storage),
    dataset_storage: BaseDatasetStorage = Depends(get_dataset_storage),
) -> AnomalyService:
    return AnomalyService(storage=storage, dataset_storage=dataset_storage)
