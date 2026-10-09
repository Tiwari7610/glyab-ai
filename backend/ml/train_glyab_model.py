from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "glof_training_dataset.csv"
)

MODEL_DIR = BASE_DIR / "trained_models"

MODEL_FILE = MODEL_DIR / "glyab_glof_model.joblib"
METRICS_FILE = MODEL_DIR / "model_metrics.json"
FEATURE_FILE = MODEL_DIR / "feature_schema.json"


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "historical_glof"

# These columns must NOT be used for training because
# they are directly involved in constructing the target.
LEAKAGE_COLUMNS = {
    TARGET,
    "nearest_glof_km",
    "historical_event_year",
    "historical_event_count_proxy",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_training_data():

    print("\n==========================================")
    print("        GLYAB GLOF MODEL TRAINING")
    print("==========================================\n")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        low_memory=False,
    )

    print(f"[DATA] Dataset: {DATA_FILE.name}")
    print(f"[DATA] Rows: {len(df):,}")
    print(f"[DATA] Columns: {len(df.columns)}")

    if TARGET not in df.columns:
        raise ValueError(
            f"Target column '{TARGET}' not found."
        )

    return df


# ============================================================
# CLEAN DATA
# ============================================================

def clean_dataset(df):

    df = df.copy()

    # Remove duplicate records
    before = len(df)

    df = df.drop_duplicates()

    print(
        f"[CLEAN] Removed duplicates: "
        f"{before - len(df):,}"
    )

    # Convert numeric columns
    for column in df.columns:

        if column == TARGET:
            continue

        if df[column].dtype == "object":

            converted = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.80:
                df[column] = converted

    # Clean target
    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    df = df.dropna(
        subset=[TARGET]
    )

    df[TARGET] = df[TARGET].astype(int)

    return df


# ============================================================
# FEATURE SELECTION
# ============================================================

def select_features(df):

    excluded = set(LEAKAGE_COLUMNS)

    candidate_columns = [
        column
        for column in df.columns
        if column not in excluded
    ]

    # Keep only numeric features for first production model
    numeric_columns = []

    for column in candidate_columns:

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):
            numeric_columns.append(column)

    if not numeric_columns:
        raise ValueError(
            "No numeric features available."
        )

    X = df[numeric_columns].copy()
    y = df[TARGET].copy()

    print("\n[FEATURES]")
    print(
        f"Total usable features: "
        f"{len(numeric_columns)}"
    )

    for feature in numeric_columns:
        print(f"  ✓ {feature}")

    print("\n[LEAKAGE PROTECTION]")
    for column in sorted(LEAKAGE_COLUMNS):
        if column in df.columns:
            print(f"  ✗ Excluded: {column}")

    return X, y, numeric_columns


# ============================================================
# PREPROCESSOR
# ============================================================

def create_preprocessor(feature_columns):

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                feature_columns,
            )
        ],
        remainder="drop",
    )

    return preprocessor


# ============================================================
# MODELS
# ============================================================

def create_models(preprocessor):

    models = {

        "logistic_regression": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=2000,
                        C=1.0,
                        random_state=42,
                    ),
                ),
            ]
        ),

        "random_forest": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        max_depth=18,
                        min_samples_leaf=3,
                        class_weight="balanced_subsample",
                        n_jobs=-1,
                        random_state=42,
                    ),
                ),
            ]
        ),

        "extra_trees": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=500,
                        max_depth=20,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        n_jobs=-1,
                        random_state=42,
                    ),
                ),
            ]
        ),

        "hist_gradient_boosting": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        max_iter=300,
                        learning_rate=0.05,
                        max_leaf_nodes=31,
                        l2_regularization=1.0,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }

    return models


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    name,
    model,
    X_train,
    X_test,
    y_train,
    y_test,
):

    print(
        f"\n{'=' * 55}"
    )
    print(
        f"MODEL: {name.upper()}"
    )
    print(
        f"{'=' * 55}"
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    cm = confusion_matrix(
        y_test,
        predictions,
    )

    print(
        f"Accuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )

    print(
        f"ROC-AUC   : {auc:.4f}"
    )

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Background",
                "Historical GLOF Associated",
            ],
            zero_division=0,
        )
    )

    return {
        "name": name,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(auc),
        "confusion_matrix": cm.tolist(),
        "model": model,
    }


# ============================================================
# CROSS VALIDATION
# ============================================================

def cross_validate_best(
    model,
    X,
    y,
):

    print(
        "\n[CV] Running 5-fold "
        "stratified cross-validation..."
    )

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scores = cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1,
    )

    print(
        "\n[CV] ROC-AUC scores:"
    )

    for i, score in enumerate(
        scores,
        start=1,
    ):
        print(
            f"Fold {i}: {score:.4f}"
        )

    print(
        f"\n[CV] Mean ROC-AUC: "
        f"{scores.mean():.4f}"
    )

    print(
        f"[CV] Std: "
        f"{scores.std():.4f}"
    )

    return scores


# ============================================================
# MAIN TRAINING
# ============================================================

def main():

    df = load_training_data()

    df = clean_dataset(
        df
    )

    X, y, features = select_features(
        df
    )

    print("\n[TARGET]")
    print(
        y.value_counts()
        .sort_index()
        .to_string()
    )

    # ----------------------------------------
    # Train/Test split
    # ----------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            stratify=y,
            random_state=42,
        )
    )

    print(
        f"\n[SPLIT]"
    )

    print(
        f"Training: {len(X_train):,}"
    )

    print(
        f"Testing : {len(X_test):,}"
    )

    # ----------------------------------------
    # Models
    # ----------------------------------------

    preprocessor = create_preprocessor(
        features
    )

    models = create_models(
        preprocessor
    )

    results = []

    # ----------------------------------------
    # Train + evaluate
    # ----------------------------------------

    for name, model in models.items():

        result = evaluate_model(
            name,
            model,
            X_train,
            X_test,
            y_train,
            y_test,
        )

        results.append(result)

    # ----------------------------------------
    # Select best
    # ----------------------------------------

    results_sorted = sorted(
        results,
        key=lambda x: (
            x["roc_auc"],
            x["f1"],
        ),
        reverse=True,
    )

    best = results_sorted[0]

    best_model = best["model"]

    print(
        "\n=========================================="
    )

    print(
        f"BEST MODEL: "
        f"{best['name'].upper()}"
    )

    print(
        f"ROC-AUC: "
        f"{best['roc_auc']:.4f}"
    )

    print(
        f"F1: "
        f"{best['f1']:.4f}"
    )

    print(
        "=========================================="
    )

    # ----------------------------------------
    # Cross validation
    # ----------------------------------------

    cross_validate_best(
        best_model,
        X,
        y,
    )

    # ----------------------------------------
    # Save model
    # ----------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        best_model,
        MODEL_FILE,
    )

    # ----------------------------------------
    # Save metrics
    # ----------------------------------------

    metrics = {
        "project": "GLYAB",
        "model_type": best["name"],
        "target": TARGET,
        "dataset_rows": int(len(df)),
        "positive_samples": int(y.sum()),
        "negative_samples": int((y == 0).sum()),
        "features": features,
        "metrics": {
            key: value
            for key, value in best.items()
            if key != "model"
        },
        "leakage_columns_excluded": sorted(
            LEAKAGE_COLUMNS
        ),
    }

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
        )

    # ----------------------------------------
    # Save feature schema
    # ----------------------------------------

    schema = {
        "project": "GLYAB",
        "target": TARGET,
        "features": features,
        "excluded_features": sorted(
            LEAKAGE_COLUMNS
        ),
    }

    with open(
        FEATURE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            schema,
            file,
            indent=4,
        )

    print(
        "\n[SAVED]"
    )

    print(
        f"Model   : {MODEL_FILE}"
    )

    print(
        f"Metrics : {METRICS_FILE}"
    )

    print(
        f"Schema  : {FEATURE_FILE}"
    )

    print(
        "\n✓ GLYAB MODEL TRAINING COMPLETE"
    )


if __name__ == "__main__":
    main()