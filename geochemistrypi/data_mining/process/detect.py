# -*- coding: utf-8 -*-
import os

import pandas as pd

from ..constants import MLFLOW_ARTIFACT_DATA_PATH
from ..model.detection import AbnormalDetectionWorkflowBase, IsolationForestAbnormalDetection
from ._base import ModelSelectionBase


class AbnormalDetectionModelSelection(ModelSelectionBase):
    """Simulate the normal way of invoking scikit-learn abnormal detection algorithms."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.ad_workflow = AbnormalDetectionWorkflowBase()
        self.transformer_config = {}

    def activate(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.DataFrame,
        y_test: pd.DataFrame,
    ) -> None:
        """Train by Scikit-learn framework."""

        self.ad_workflow.data_upload(X=X, y=y, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)

        # Model option
        if self.model_name == "Isolation Forest":
            hyper_parameters = IsolationForestAbnormalDetection.manual_hyper_parameters()
            self.ad_workflow = IsolationForestAbnormalDetection(
                n_estimators=hyper_parameters["n_estimators"],
                contamination=hyper_parameters["contamination"],
                max_features=hyper_parameters["max_features"],
                bootstrap=hyper_parameters["bootstrap"],
                max_samples=hyper_parameters["max_samples"],
            )

        self.ad_workflow.show_info()

        # Use Scikit-learn style API to process input data
        self.ad_workflow.fit(X)
        y_predict = self.ad_workflow.predict(X)
        X_abnormal_detection, X_normal, X_abnormal = self.ad_workflow._detect_data(X, y_predict)

        self.ad_workflow.data_upload(X=X, y=y, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)

        # Save the model hyper-parameters
        self.ad_workflow.save_hyper_parameters(hyper_parameters, self.model_name, os.getenv("GEOPI_OUTPUT_PARAMETERS_PATH"))

        # Common components for every abnormal detection algorithm
        self.ad_workflow.common_components()

        # special components of different algorithms
        self.ad_workflow.special_components()

        # Save abnormal detection result
        self.ad_workflow.data_save(X_abnormal_detection, "X Abnormal Detection", os.getenv("GEOPI_OUTPUT_ARTIFACTS_DATA_PATH"), MLFLOW_ARTIFACT_DATA_PATH, "Abnormal Detection Data")
        self.ad_workflow.data_save(X_normal, "X Normal", os.getenv("GEOPI_OUTPUT_ARTIFACTS_DATA_PATH"), MLFLOW_ARTIFACT_DATA_PATH, "Normal Data")
        self.ad_workflow.data_save(X_abnormal, "X Abnormal", os.getenv("GEOPI_OUTPUT_ARTIFACTS_DATA_PATH"), MLFLOW_ARTIFACT_DATA_PATH, "Abnormal Data")

        # Save the trained model
        self.ad_workflow.model_save()
