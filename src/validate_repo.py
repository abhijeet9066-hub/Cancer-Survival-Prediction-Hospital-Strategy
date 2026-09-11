from pathlib import Path
import hashlib
import json
import re
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "config" / "feature_names.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
POWERBI = ROOT / "data" / "powerbi"

required = [
    ROOT / "README.md",
    ROOT / "config" / "config.json",
    ROOT / "config" / "feature_names.json",
    RAW / "hcc_survival_uci.csv",
    RAW / "source_metadata.json",
    PROCESSED / "cohort_summary.csv",
    PROCESSED / "feature_missingness.csv",
    PROCESSED / "subgroup_outcomes.csv",
    PROCESSED / "model_cv_fold_metrics.csv",
    PROCESSED / "model_cv_summary.csv",
    PROCESSED / "model_coefficients.csv",
    PROCESSED / "cancer_survival.sqlite",
    POWERBI / "cohort_summary.csv",
    POWERBI / "feature_missingness.csv",
    POWERBI / "subgroup_outcomes.csv",
    POWERBI / "model_cv_summary.csv",
    POWERBI / "model_coefficients.csv",
    ROOT / "docs" / "data_provenance.md",
    ROOT / "docs" / "methodology.md",
    ROOT / "docs" / "data_dictionary.md",
    ROOT / "docs" / "limitations.md",
    ROOT / "sql" / "analysis_queries.sql",
    ROOT / "powerbi" / "dashboard_blueprint.md",
    ROOT / "powerbi" / "measures.dax",
    ROOT / ".github" / "workflows" / "ci.yml",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

meta = json.loads((RAW / "source_metadata.json").read_text(encoding="utf-8"))
if meta.get("synthetic_data") is not False:
    raise SystemExit("Source metadata must record synthetic_data=false.")
if int(meta.get("uci_dataset_id", -1)) != 423:
    raise SystemExit("Unexpected UCI dataset ID.")
if meta.get("doi") != "10.24432/C5TS4S":
    raise SystemExit("Unexpected UCI DOI.")
if meta.get("license") != "CC BY 4.0":
    raise SystemExit("Unexpected source license.")
if not re.fullmatch(r"[0-9a-f]{64}", str(meta.get("canonical_csv_sha256", ""))):
    raise SystemExit("Missing/invalid canonical CSV SHA-256.")

raw = pd.read_csv(RAW / "hcc_survival_uci.csv")
target = CONFIG["target"]

expected_columns = FEATURES + [target]
if list(raw.columns) != expected_columns:
    raise SystemExit("Canonical source columns do not match fixed feature order.")
if raw.shape != (165, 50):
    raise SystemExit(f"Expected 165x50 canonical table; found {raw.shape}.")
if int((raw[target] == 1).sum()) != 102:
    raise SystemExit("Expected 102 one-year survivors.")
if int((raw[target] == 0).sum()) != 63:
    raise SystemExit("Expected 63 deaths within one year.")
if raw[target].isna().any():
    raise SystemExit("Target cannot contain missing values.")

with (RAW / "hcc_survival_uci.csv").open("rb") as f:
    actual_hash = hashlib.sha256(f.read()).hexdigest()
if actual_hash != meta["canonical_csv_sha256"]:
    raise SystemExit("Canonical source SHA-256 does not match metadata.")

missingness = pd.read_csv(PROCESSED / "feature_missingness.csv")
subgroups = pd.read_csv(PROCESSED / "subgroup_outcomes.csv")
folds = pd.read_csv(PROCESSED / "model_cv_fold_metrics.csv")
summary = pd.read_csv(PROCESSED / "model_cv_summary.csv")
coefs = pd.read_csv(PROCESSED / "model_coefficients.csv")

if len(missingness) != 49:
    raise SystemExit("Feature missingness table must contain 49 rows.")
if len(folds) != 50:
    raise SystemExit(f"Expected 50 held-out fold evaluations; found {len(folds)}.")
if set(summary["metric"]) != {
    "roc_auc", "average_precision", "brier_score", "accuracy",
    "balanced_accuracy", "precision_survival", "recall_survival",
    "specificity_death", "f1_survival"
}:
    raise SystemExit("Model summary metric set is incomplete.")
if len(subgroups) < 20:
    raise SystemExit("Subgroup analytical table unexpectedly small.")
if len(coefs) < 49:
    raise SystemExit("Coefficient table unexpectedly small.")

bounded_metrics = [
    "roc_auc", "average_precision", "brier_score", "accuracy",
    "balanced_accuracy", "precision_survival", "recall_survival",
    "specificity_death", "f1_survival"
]
for c in bounded_metrics:
    if folds[c].lt(0).any() or folds[c].gt(1).any():
        raise SystemExit(f"{c} contains values outside [0,1].")

conn = sqlite3.connect(PROCESSED / "cancer_survival.sqlite")
try:
    db_counts = {
        "cohort_summary": conn.execute("SELECT COUNT(*) FROM cohort_summary").fetchone()[0],
        "feature_missingness": conn.execute("SELECT COUNT(*) FROM feature_missingness").fetchone()[0],
        "subgroup_outcomes": conn.execute("SELECT COUNT(*) FROM subgroup_outcomes").fetchone()[0],
        "model_cv_fold_metrics": conn.execute("SELECT COUNT(*) FROM model_cv_fold_metrics").fetchone()[0],
        "model_cv_summary": conn.execute("SELECT COUNT(*) FROM model_cv_summary").fetchone()[0],
        "model_coefficients": conn.execute("SELECT COUNT(*) FROM model_coefficients").fetchone()[0],
    }
finally:
    conn.close()

expected_db = {
    "cohort_summary": len(pd.read_csv(PROCESSED / "cohort_summary.csv")),
    "feature_missingness": len(missingness),
    "subgroup_outcomes": len(subgroups),
    "model_cv_fold_metrics": len(folds),
    "model_cv_summary": len(summary),
    "model_coefficients": len(coefs),
}
if db_counts != expected_db:
    raise SystemExit("SQLite row counts do not match processed outputs.")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
norm = readme.replace("**", "").replace("`", "").lower()
phrases = [
    "not exact patient-level survival times",
    "kaplan-meier",
    "not a validated clinical decision-support system",
    "165 patients",
    "repeated stratified 5-fold cross-validation",
    "external validation",
]
for phrase in phrases:
    if phrase not in norm:
        raise SystemExit(f"Required limitation/methodology statement missing: {phrase}")

print("PASS: real UCI HCC Survival dataset provenance and SHA-256 captured")
print("PASS: UCI dataset ID 423 / DOI 10.24432/C5TS4S / CC BY 4.0")
print("PASS: canonical cohort rows = 165")
print("PASS: clinical features = 49")
print("PASS: one-year survivors = 102; deaths within one year = 63")
print(f"PASS: feature missingness rows = {len(missingness)}")
print(f"PASS: subgroup analytical rows = {len(subgroups)}")
print("PASS: repeated stratified CV held-out fold evaluations = 50")
print("PASS: all validation metrics are bounded within [0,1]")
print("PASS: SQLite warehouse matches processed outputs")
print("PASS: binary-outcome vs time-to-event and clinical-use limitations documented")
