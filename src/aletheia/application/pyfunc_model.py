"""Reviewed MLflow models-from-code adapter for the complete frozen callable."""

import mlflow
import pandas as pd

from aletheia.application.release import VerifiedRelease


class CalibratedModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.release = VerifiedRelease(
            __import__("pathlib").Path(context.artifacts["release"]),
            context.model_config["release_digest"],
        )

    def predict(self, context, model_input, params=None):
        if list(model_input.columns) != self.release.features or len(model_input) != 1:
            raise ValueError("only fixed synthetic case supported")
        if model_input.iloc[0].to_dict() != self.release.case:
            raise ValueError("editable input refused")
        return pd.DataFrame({"probability": [self.release.score()]})


mlflow.models.set_model(CalibratedModel())
