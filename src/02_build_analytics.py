from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "config" / "feature_names.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

TARGET = CONFIG["target"]


def outcome_rows(df, group_col, display_name):
    temp = df[[group_col, TARGET]].copy()
    temp[group_col] = temp[group_col].where(temp[group_col].notna(), "Missing")

    rows = []
    for value, g in temp.groupby(group_col, dropna=False):
        n = len(g)
        survived = int((g[TARGET] == 1).sum())
        died = int((g[TARGET] == 0).sum())
        rows.append({
            "group_variable": display_name,
            "group_value": str(value),
            "patients": n,
            "survived_1yr": survived,
            "died_within_1yr": died,
            "observed_survival_pct": (survived / n * 100.0) if n else np.nan,
        })
    return rows


def main() -> None:
    src = RAW / "hcc_survival_uci.csv"
    if not src.exists():
        raise FileNotFoundError("Run src/01_extract_uci_hcc.py first.")

    df = pd.read_csv(src)

    summary = pd.DataFrame([
        {"metric": "patients", "value": len(df)},
        {"metric": "clinical_features", "value": len(FEATURES)},
        {"metric": "survived_1yr", "value": int((df[TARGET] == 1).sum())},
        {"metric": "died_within_1yr", "value": int((df[TARGET] == 0).sum())},
        {
            "metric": "observed_1yr_survival_pct",
            "value": float((df[TARGET] == 1).mean() * 100.0),
        },
        {
            "metric": "feature_missing_cells",
            "value": int(df[FEATURES].isna().sum().sum()),
        },
        {
            "metric": "feature_missing_pct",
            "value": float(df[FEATURES].isna().mean().mean() * 100.0),
        },
        {
            "metric": "complete_patient_rows",
            "value": int(df[FEATURES].notna().all(axis=1).sum()),
        },
    ])
    summary.to_csv(PROCESSED / "cohort_summary.csv", index=False)

    missing = pd.DataFrame({
        "feature": FEATURES,
        "missing_count": [int(df[c].isna().sum()) for c in FEATURES],
        "missing_pct": [float(df[c].isna().mean() * 100.0) for c in FEATURES],
        "non_missing_count": [int(df[c].notna().sum()) for c in FEATURES],
        "unique_non_missing_values": [int(df[c].nunique(dropna=True)) for c in FEATURES],
    }).sort_values(["missing_pct", "feature"], ascending=[False, True])
    missing.to_csv(PROCESSED / "feature_missingness.csv", index=False)

    subgroup_rows = []

    # Age bands are descriptive, not clinical staging thresholds.
    age = df["age_at_diagnosis"]
    df["age_band"] = pd.cut(
        age,
        bins=[-np.inf, 49, 59, 69, np.inf],
        labels=["<50", "50-59", "60-69", "70+"],
    )

    for col, label in [
        ("age_band", "Age band"),
        ("gender", "Gender (source code)"),
        ("symptoms", "Symptoms (source code)"),
        ("cirrhosis", "Cirrhosis (source code)"),
        ("portal_hypertension", "Portal hypertension (source code)"),
        ("portal_vein_thrombosis", "Portal vein thrombosis (source code)"),
        ("liver_metastasis", "Liver metastasis (source code)"),
        ("radiological_hallmark", "Radiological hallmark (source code)"),
        ("performance_status", "Performance status (source code)"),
        ("ascites_degree", "Ascites degree (source code)"),
        ("encephalopathy_degree", "Encephalopathy degree (source code)"),
        ("number_of_nodules", "Number of nodules (source value)"),
    ]:
        subgroup_rows.extend(outcome_rows(df, col, label))

    subgroup = pd.DataFrame(subgroup_rows)
    subgroup.to_csv(PROCESSED / "subgroup_outcomes.csv", index=False)

    print(f"Cohort rows: {len(df)}")
    print(f"Observed 1-year survival: {(df[TARGET] == 1).mean() * 100:.2f}%")
    print(f"Complete feature rows: {df[FEATURES].notna().all(axis=1).sum()}")
    print(f"Subgroup output rows: {len(subgroup)}")
    print(f"Feature missingness rows: {len(missing)}")


if __name__ == "__main__":
    main()
