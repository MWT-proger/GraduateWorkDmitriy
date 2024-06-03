#
# Copyright (c) 2023 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#
import asyncio

import pandas as pd
from merlion.dashboard.models.forecast import ForecastModel as _ForecastModel
from merlion.evaluate.forecast import ForecastEvaluator
from merlion.models.factory import ModelFactory
from merlion.utils.time_series import TimeSeries

from schemas.forecast import ForecastProgressEnum


class ForecastModel(_ForecastModel):

    async def train(
        self,
        algorithm,
        train_df,
        test_df,
        target_column,
        feature_columns,
        exog_columns,
        params,
        set_progress,
    ):
        if target_column not in train_df:
            target_column = int(target_column)
        assert (
            target_column in train_df
        ), f"The target variable {target_column} is not in the time series."
        try:
            feature_columns = [
                int(c) if c not in train_df else c for c in feature_columns
            ]
        except ValueError:
            feature_columns = []
        try:
            exog_columns = [
                int(c) if c not in train_df else c for c in exog_columns
            ]
        except ValueError:
            exog_columns = []
        for exog_column in exog_columns:
            assert (
                exog_column in train_df
            ), f"Exogenous variable {exog_column} is not in the time series."

        # Re-arrange dataframe so that the target column is first, and exogenous columns are last
        columns = [target_column] + feature_columns + exog_columns
        train_df = train_df.loc[:, columns]
        test_df = test_df.loc[:, columns]

        # Get the target_seq_index & initialize the model
        params["target_seq_index"] = columns.index(target_column)
        model_class = ModelFactory.get_model_class(algorithm)
        model = model_class(model_class.config_class(**params))
        await set_progress(ForecastProgressEnum.model_initialized)
        await asyncio.sleep(0.01)
        # Handle exogenous regressors if they are supported by the model
        if model.supports_exog and len(exog_columns) > 0:
            exog_ts = TimeSeries.from_pd(
                pd.concat(
                    (
                        train_df.loc[:, exog_columns],
                        test_df.loc[:, exog_columns],
                    )
                )
            )
            train_df = train_df.loc[:, [target_column] + feature_columns]
            test_df = test_df.loc[:, [target_column] + feature_columns]
        else:
            exog_ts = None

        self.logger.info(f"Training the forecasting model: {algorithm}...")
        await set_progress(ForecastProgressEnum.training_started)
        await asyncio.sleep(0.01)
        train_ts = TimeSeries.from_pd(train_df)
        predictions = model.train(train_ts, exog_data=exog_ts)
        if isinstance(predictions, tuple):
            predictions = predictions[0]

        self.logger.info("Computing training performance metrics...")
        await set_progress(ForecastProgressEnum.training_completed)
        await asyncio.sleep(0.01)
        evaluator = ForecastEvaluator(
            model, config=ForecastEvaluator.config_class()
        )
        train_metrics = ForecastModel._compute_metrics(
            evaluator, train_ts, predictions
        )
        await set_progress(ForecastProgressEnum.train_metrics_computed)
        await asyncio.sleep(0.01)
        test_ts = TimeSeries.from_pd(test_df)
        if (
            "max_forecast_steps" in params
            and params["max_forecast_steps"] is not None
        ):
            n = min(len(test_ts) - 1, int(params["max_forecast_steps"]))
            test_ts, _ = test_ts.bisect(t=test_ts.time_stamps[n])

        self.logger.info("Computing test performance metrics...")
        test_pred, test_err = model.forecast(
            time_stamps=test_ts.time_stamps, exog_data=exog_ts
        )
        test_metrics = ForecastModel._compute_metrics(
            evaluator, test_ts, test_pred
        )
        await set_progress(ForecastProgressEnum.test_metrics_computed)
        await asyncio.sleep(0.01)
        self.logger.info("Finished.")
        return (
            model,
            train_metrics,
            test_metrics,
            test_ts,
            train_ts,
            exog_ts,
            test_pred,
        )
