from pathlib import Path
import json

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "trained_models"
    / "glyab_glof_model.joblib"
)

SCHEMA_PATH = (
    BASE_DIR
    / "trained_models"
    / "feature_schema.json"
)


class GLYABPredictor:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(
                f"Feature schema not found: {SCHEMA_PATH}"
            )

        self.model = joblib.load(
            MODEL_PATH
        )

        with open(
            SCHEMA_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            schema = json.load(file)

        self.features = schema["features"]

    # --------------------------------------------------
    # Prepare input
    # --------------------------------------------------

    def prepare_input(
        self,
        data: dict,
    ) -> pd.DataFrame:

        row = {}

        for feature in self.features:

            value = data.get(
                feature,
                None,
            )

            row[feature] = value

        frame = pd.DataFrame(
            [row],
            columns=self.features,
        )

        return frame

    # --------------------------------------------------
    # Risk classification
    # --------------------------------------------------

    @staticmethod
    def risk_level(
        probability: float,
    ) -> str:

        if probability >= 0.75:
            return "HIGH"

        if probability >= 0.45:
            return "MODERATE"

        return "LOW"

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    def predict(
        self,
        data: dict,
    ) -> dict:

        X = self.prepare_input(
            data
        )

        probability = float(
            self.model.predict_proba(X)[0][1]
        )

        prediction = int(
            probability >= 0.50
        )

        risk = self.risk_level(
            probability
        )

        return {
            "prediction": prediction,
            "risk_level": risk,
            "risk_probability": round(
                probability,
                4,
            ),
            "risk_percentage": round(
                probability * 100,
                2,
            ),
            "model": "GLYAB GLOF Risk Model",
        }


_predictor = None


def get_predictor():

    global _predictor

    if _predictor is None:
        _predictor = GLYABPredictor()

    return _predictor