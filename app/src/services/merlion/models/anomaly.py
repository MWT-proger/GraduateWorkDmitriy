#
# Copyright (c) 2023 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#
import asyncio
import importlib
import logging

from merlion.dashboard.models.anomaly import AnomalyModel as _AnomalyModel
from merlion.evaluate.anomaly import TSADMetric
from merlion.models.factory import ModelFactory
from merlion.plot import MTSFigure, plot_anoms_plotly
from merlion.utils.time_series import TimeSeries

from schemas.anomaly import AnomalyProgressEnum


class AnomalyModel(_AnomalyModel):
    univariate_algorithms = [
        "DefaultDetector",
        "ArimaDetector",
        "DynamicBaseline",
        "IsolationForest",
        "ETSDetector",
        "MSESDetector",
        "ProphetDetector",
        "RandomCutForest",
        "SarimaDetector",
        "WindStats",
        "SpectralResidual",
        "ZMS",
        "DeepPointAnomalyDetector",
    ]
    multivariate_algorithms = [
        "IsolationForest",
        "AutoEncoder",
        "VAE",
        "DAGMM",
        "LSTMED",
    ]
    thresholds = ["Threshold", "AggregateAlarms"]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def get_available_algorithms(num_input_metrics):
        if num_input_metrics <= 0:
            return []
        elif num_input_metrics == 1:
            return AnomalyModel.univariate_algorithms
        else:
            return AnomalyModel.multivariate_algorithms

    @staticmethod
    def get_available_thresholds():
        return AnomalyModel.thresholds

    @staticmethod
    def get_threshold_info(threshold):
        module = importlib.import_module("merlion.post_process.threshold")
        model_class = getattr(module, threshold)
        param_info = AnomalyModel._param_info(model_class.__init__)
        if not param_info["alm_threshold"]["default"]:
            param_info["alm_threshold"]["default"] = 3.0
        return param_info

    @staticmethod
    def _compute_metrics(labels, predictions):
        metrics = {}
        for metric in [
            TSADMetric.Precision,
            TSADMetric.Recall,
            TSADMetric.F1,
            TSADMetric.MeanTimeToDetect,
        ]:
            m = metric.value(ground_truth=labels, predict=predictions)
            metrics[metric.name] = (
                round(m, 5) if metric.name != "MeanTimeToDetect" else str(m)
            )
        return metrics

    @staticmethod
    def _plot_anomalies(model, ts, scores, labels=None):
        title = f"{type(model).__name__}: Anomalies in Time Series"
        fig = MTSFigure(y=ts, y_prev=None, anom=scores)
        return plot_anoms_plotly(
            fig=fig.plot_plotly(title=title), anomaly_labels=labels
        )

    @staticmethod
    def _check(df, columns, label_column, is_train):
        kind = "train" if is_train else "test"
        if label_column and label_column not in df:
            label_column = int(label_column)
            assert (
                label_column in df
            ), f"The label column {label_column} is not in the {kind} time series."
        for i in range(len(columns)):
            if columns[i] not in df:
                columns[i] = int(columns[i])
            assert (
                columns[i] in df
            ), f"The variable {columns[i]} is not in the time {kind} series."
        return columns, label_column

    async def train(
        self,
        algorithm,
        train_df,
        test_df,
        columns,
        label_column,
        params,
        threshold_params,
        set_progress,
    ):
        columns, label_column = AnomalyModel._check(
            train_df, columns, label_column, is_train=True
        )
        columns, label_column = AnomalyModel._check(
            test_df, columns, label_column, is_train=False
        )

        if threshold_params is not None:
            thres_class, thres_params = threshold_params
            module = importlib.import_module("merlion.post_process.threshold")
            model_class = getattr(module, thres_class)
            params["threshold"] = model_class(**thres_params)

        model_class = ModelFactory.get_model_class(algorithm)
        model = model_class(model_class.config_class(**params))
        train_ts, train_labels = TimeSeries.from_pd(train_df[columns]), None
        test_ts, test_labels = TimeSeries.from_pd(test_df[columns]), None
        if label_column is not None and label_column != "":
            train_labels = TimeSeries.from_pd(train_df[label_column])
            test_labels = TimeSeries.from_pd(test_df[label_column])

        self.logger.info(f"Training the anomaly detector: {algorithm}...")
        await set_progress(AnomalyProgressEnum.start_anomaly_detector_training)
        await asyncio.sleep(0.01)

        scores = model.train(train_data=train_ts)
        await set_progress(AnomalyProgressEnum.training_completed)
        await asyncio.sleep(0.01)

        await set_progress(AnomalyProgressEnum.get_train_metrics)
        await asyncio.sleep(0.01)
        self.logger.info("Computing training performance metrics...")
        train_pred = (
            model.post_rule(scores) if model.post_rule is not None else scores
        )
        train_metrics = (
            AnomalyModel._compute_metrics(train_labels, train_pred)
            if train_labels is not None
            else None
        )

        await set_progress(AnomalyProgressEnum.get_train_metrics)
        await asyncio.sleep(0.01)
        self.logger.info("Getting test-time results...")
        test_pred = model.get_anomaly_label(test_ts)
        test_metrics = (
            AnomalyModel._compute_metrics(test_labels, test_pred)
            if test_labels is not None
            else None
        )

        return (
            model,
            train_metrics,
            test_metrics,
            test_ts,
            test_pred,
            test_labels,
        )

    def test(
        self, model, df, columns, label_column, threshold_params, set_progress
    ):
        columns, label_column = AnomalyModel._check(
            df, columns, label_column, is_train=False
        )

        threshold = None
        if threshold_params is not None:
            thres_class, thres_params = threshold_params
            module = importlib.import_module("merlion.post_process.threshold")
            model_class = getattr(module, thres_class)
            threshold = model_class(**thres_params)
        if threshold is not None:
            model.threshold = threshold

        self.logger.info("Detecting anomalies...")
        set_progress(("2", "10"))

        test_ts, label_ts = TimeSeries.from_pd(df[columns]), None
        if label_column is not None and label_column != "":
            label_ts = TimeSeries.from_pd(df[[label_column]])
        predictions = model.get_anomaly_label(time_series=test_ts)
        set_progress(("7", "10"))

        self.logger.info("Computing test performance metrics...")
        metrics = (
            AnomalyModel._compute_metrics(label_ts, predictions)
            if label_ts is not None
            else None
        )
        set_progress(("8", "10"))

        self.logger.info("Plotting anomaly labels...")
        figure = AnomalyModel._plot_anomalies(
            model, test_ts, predictions, label_ts
        )
        self.logger.info("Finished.")
        set_progress(("10", "10"))

        return metrics, figure
