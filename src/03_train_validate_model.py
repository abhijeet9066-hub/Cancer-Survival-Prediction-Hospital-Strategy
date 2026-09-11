from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "config" / "feature_names.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

TARGET = CONFIG["target"]


def make_pipeline():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scaler", StandardScaler()),
        (
            "model",
            LogisticRegression(
                penalty="l2",
                C=1.0,
                solver="liblinear",
                max_iter=5000,
                random_state=int(CONFIG["random_state"]),
            ),
        ),
    ])


def fold_metrics(y_true, prob):
    pred = (prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else np.nan

    return {
        "roc_auc": roc_auc_score(y_true, prob),
        "average_precision": average_precision_score(y_true, prob),
        "brier_score": brier_score_loss(y_true, prob),
        "accuracy": accuracy_score(y_true, pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "precision_survival": precision_score(y_true, pred, zero_division=0),
        "recall_survival": recall_score(y_true, pred, zero_division=0),
        "specificity_death": specificity,
        "f1_survival": f1_score(y_true, pred, zero_division=0),
        "test_patients": len(y_true),
        "test_survivors": int((y_true == 1).sum()),
        "test_deaths": int((y_true == 0).sum()),
    }


def main() -> None:
    df = pd.read_csv(RAW / "hcc_survival_uci.csv")
    X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="raise").astype(int).to_numpy()

    cv = RepeatedStratifiedKFold(
        n_splits=int(CONFIG["cv_folds"]),
        n_repeats=int(CONFIG["cv_repeats"]),
        random_state=int(CONFIG["random_state"]),
    )

    rows = []
    for fold_index, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        pipe = make_pipeline()
        pipe.fit(X.iloc[train_idx], y[train_idx])
        prob = pipe.predict_proba(X.iloc[test_idx])[:, 1]
        metrics = fold_metrics(y[test_idx], prob)
        metrics["fold_index"] = fold_index
        metrics["repeat_index"] = (fold_index - 1) // int(CONFIG["cv_folds"]) + 1
        metrics["fold_within_repeat"] = (fold_index - 1) % int(CONFIG["cv_folds"]) + 1
        rows.append(metrics)

    folds = pd.DataFrame(rows)
    ordered = [
        "fold_index", "repeat_index", "fold_within_repeat",
        "test_patients", "test_survivors", "test_deaths",
        "roc_auc", "average_precision", "brier_score", "accuracy",
        "balanced_accuracy", "precision_survival", "recall_survival",
        "specificity_death", "f1_survival",
    ]
    folds = folds[ordered]
    folds.to_csv(PROCESSED / "model_cv_fold_metrics.csv", index=False)

    metric_cols = [
        "roc_auc",
        "average_precision",
        "brier_score",
        "accuracy",
        "balanced_accuracy",
        "precision_survival",
        "recall_survival",
        "specificity_death",
        "f1_survival",
    ]

    summary_rows = []
    for metric in metric_cols:
        s = folds[metric].astype(float)
        summary_rows.append({
            "metric": metric,
            "mean": float(s.mean()),
            "std": float(s.std(ddof=1)),
            "min": float(s.min()),
            "max": float(s.max()),
            "fold_evaluations": len(s),
        })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(PROCESSED / "model_cv_summary.csv", index=False)

    # Full-cohort fit is for a descriptive coefficient table only.
    full = make_pipeline()
    full.fit(X, y)

    imputer = full.named_steps["imputer"]
    transformed_names = list(FEATURES)
    indicator = getattr(imputer, "indicator_", None)
    if indicator is not None and len(indicator.features_) > 0:
        transformed_names += [
            f"missing_indicator__{FEATURES[i]}"
            for i in indicator.features_
        ]

    coef = full.named_steps["model"].coef_[0]
    if len(coef) != len(transformed_names):
        raise RuntimeError(
            f"Coefficient/name mismatch: {len(coef)} vs {len(transformed_names)}"
        )

    coefficients = pd.DataFrame({
        "model_feature": transformed_names,
        "standardized_coefficient": coef,
        "abs_standardized_coefficient": np.abs(coef),
    }).sort_values("abs_standardized_coefficient", ascending=False)

    coefficients["direction_for_survival_class"] = np.where(
        coefficients["standardized_coefficient"] > 0,
        "positive model association",
        np.where(
            coefficients["standardized_coefficient"] < 0,
            "negative model association",
            "zero"
        )
    )
    coefficients.to_csv(PROCESSED / "model_coefficients.csv", index=False)

    print(f"Cross-validation fold evaluations: {len(folds)}")
    for _, row in summary.iterrows():
        print(
            f"{row['metric']}: mean={row['mean']:.4f}, "
            f"sd={row['std']:.4f}"
        )
    print(f"Coefficient rows: {len(coefficients)}")


if __name__ == "__main__":
    main()
