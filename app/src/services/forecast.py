#
# Copyright (c) 2023 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#

from functools import lru_cache

from fastapi import Depends
from merlion.dashboard.models.forecast import ForecastModel
from merlion.dashboard.pages.utils import (
    create_empty_figure,
    create_metric_table,
)

from exceptions.forecast import ForecastServiceException
from schemas.forecast import (
    MetricTable,
    ResultForecastSchema,
    TrainTestDataSchema,
)
from services.base import BaseForecastService
from storages.base import BaseForecastStorage
from storages.forecast import get_forecast_storage


def stub_set_progress(stub):
    # TODO: тоже решим
    print(stub)
    pass


class ForecastService(BaseForecastService):

    def __init__(self, storage: BaseForecastStorage) -> None:
        self.storage = storage

    models_storage = "data"  # Папка где хранятся модели

    async def get_train_test_result(
        self, data: TrainTestDataSchema, user_id: str
    ) -> ResultForecastSchema:
        train_metric_table, test_metric_table, figure_json = None, None, None
        # status = "success"
        # msg = None

        # file = await self.storage.get_file_path_by_id(data.file_id, user_id)
        # TODO: временно
        class TempStruct:
            path: str = "data/seattle-weather.csv"

        file = TempStruct()

        if not file:
            raise ForecastServiceException(
                msg="Файл с датасетом временного ряда не существует."
            )
        else:
            try:
                train_metric_table, test_metric_table, figure_json = (
                    self._train_test(
                        file_path=file.path,
                        target_col=data.target_col,
                        algorithm=data.algorithm,
                        algorithm_params=[
                            {"Parameter": param.parametr, "Value": param.value}
                            for param in data.algorithm_params
                        ],
                        train_percentage=data.train_percentage,
                        file_mode=data.file_mode,
                        feature_cols=data.feature_cols,
                        exog_cols=data.exog_cols,
                        test_filename=data.test_filename,
                    )
                )
            except Exception as e:
                # status = "fail"
                # msg = str(e)
                print(e)
                raise ForecastServiceException(
                    msg="Не удалось произвести вычисления."
                )

            finally:
                pass
                # result_data = {
                #     "user_id": user_id,
                #     "train_metric_table": train_metric_table,
                #     "test_metric_table": test_metric_table,
                #     "figure_json": figure_json,
                #     "status": status,
                #     "msg": msg,
                #     "request_params": data.model_dump(),
                # }

                # await self.storage.save_result(result_data)

        return ResultForecastSchema(
            train_metric_table=train_metric_table,
            test_metric_table=test_metric_table,
            figure_json=figure_json,
        )

    def _train_test(
        self,
        file_path,
        target_col,
        algorithm,
        algorithm_params,
        train_percentage,
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
        - train_metric_table: Метрики для обучающей выборки.
        - test_metric_table: Метрики для тестовой выборки.
        - figure_json: Фигура (график) в json, отображающая результаты прогнозирования.
        """

        train_metric_table = create_metric_table()
        test_metric_table = create_metric_table()
        figure = create_empty_figure()

        assert file_path, "The training data file is empty!"
        assert (
            target_col
        ), "Please select a target variable/metric for forecasting."
        assert algorithm, "Please select a forecasting algorithm."
        feature_cols = feature_cols or []
        exog_cols = exog_cols or []

        df = ForecastModel().load_data(file_path=file_path)
        assert (
            len(df) > 20
        ), f"The input time series length ({len(df)}) is too small."
        if file_mode == "single":
            n = int(int(train_percentage) * len(df) / 100)
            train_df, test_df = df.iloc[:n], df.iloc[n:]
        else:
            assert test_filename, "The test file is empty!"
            test_df = ForecastModel().load_data(file_path=file_path)
            train_df = df

        params = ForecastModel.parse_parameters(
            param_info=ForecastModel.get_parameter_info(algorithm),
            params={
                p["Parameter"]: p["Value"]
                for p in algorithm_params
                if p["Parameter"]
            },
        )
        model, train_metrics, test_metrics, figure = ForecastModel().train(
            algorithm,
            train_df,
            test_df,
            target_col,
            feature_cols,
            exog_cols,
            params,
            stub_set_progress,
        )
        ForecastModel.save_model(self.models_storage, model, algorithm)
        train_metric_table = create_metric_table(train_metrics)
        test_metric_table = create_metric_table(test_metrics)

        train_metric_table_new = MetricTable(
            data=train_metric_table.data,
            columns=train_metric_table.columns,
            editable=train_metric_table.editable,
            style_table=train_metric_table.style_table,
            style_data=train_metric_table.style_data,
            style_header=train_metric_table.style_header,
            style_cell_conditional=train_metric_table.style_cell_conditional,
            style_header_conditional=train_metric_table.style_header_conditional,
        )

        test_metric_table_new = MetricTable(
            data=test_metric_table.data,
            columns=test_metric_table.columns,
            editable=test_metric_table.editable,
            style_table=test_metric_table.style_table,
            style_data=test_metric_table.style_data,
            style_header=test_metric_table.style_header,
            style_cell_conditional=test_metric_table.style_cell_conditional,
            style_header_conditional=test_metric_table.style_header_conditional,
        )

        figure_json = figure.to_json()

        return train_metric_table_new, test_metric_table_new, figure_json


@lru_cache()
def get_forecast_service(
    storage: BaseForecastStorage = Depends(get_forecast_storage),
) -> ForecastService:
    return ForecastService(storage=storage)
