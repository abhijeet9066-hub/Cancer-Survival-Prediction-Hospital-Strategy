# HCC One-Year Survival Analytics

A reproducible **UCI + Python + scikit-learn + SQL + Power BI** oncology analytics project based on real clinical data from patients diagnosed with hepatocellular carcinoma (HCC).

The GitHub repository keeps its historical name `Cancer-Survival-Prediction-Hospital-Strategy` for continuity. The analytical project is deliberately titled **HCC One-Year Survival Analytics** because the public source provides a binary **1-year survival outcome**, not exact patient-level survival times suitable for Kaplan-Meier or Cox proportional-hazards analysis.

> **Clinical-use warning:** This is a retrospective educational portfolio analysis. It is not a validated clinical decision-support system, does not provide individual treatment advice, and must not be used to predict prognosis for a real patient.

## Public Dataset

Source:

**HCC Survival — UCI Machine Learning Repository, dataset 423**

The UCI repository describes the dataset as real clinical data from **165 patients diagnosed with HCC** at a University Hospital in Portugal.

Published source characteristics:

```text
Patients: 165
Clinical features: 49
1-year survivors: 102
Deaths within 1 year: 63
Missing data: approximately 10.22% overall
Complete cases: 8 patients
Target:
    1 = survived 1 year
    0 = died within 1 year
```

The 49 features cover demographic factors, HCC/liver-disease risk factors, clinical status, tumour characteristics and laboratory measurements.

Dataset citation:

> Santos M, Abreu P, Garcia-Laencina P, Simao A, Carvalho A. HCC Survival. UCI Machine Learning Repository. DOI: 10.24432/C5TS4S.

License: **CC BY 4.0**.

## Why This Is Survival Analytics — Not Time-to-Event Modelling

The UCI target is **survival status at one year**.

The dataset does not provide a reliable individual event/censoring time required for:

- Kaplan-Meier curves;
- Cox proportional-hazards modelling;
- hazard ratios;
- median survival time.

Those methods are therefore intentionally **not fabricated**.

This project instead analyses:

- observed 1-year survival proportion;
- clinical-feature completeness;
- subgroup outcome composition;
- repeated cross-validated classification performance;
- model coefficients as descriptive model signals;
- hospital-facing data-quality and cohort insights.

## Data Pipeline

```text
UCI HCC Survival ZIP
        ↓
src/01_extract_uci_hcc.py
        ↓
canonical 165-row snapshot + SHA-256 provenance
        ↓
src/02_build_analytics.py
        ↓
cohort / missingness / subgroup analytics
        ↓
src/03_train_validate_model.py
        ↓
repeated stratified 5-fold cross-validation
        ↓
src/04_build_sqlite.py
        ↓
SQLite analytical warehouse
        ↓
src/05_export_powerbi.py
        ↓
Power BI-ready aggregate tables
```

## Modelling Design

The model is intentionally simple:

**L2-regularized logistic regression**

All 49 UCI features are numeric-coded in the source data. Within every cross-validation training fold the pipeline performs:

1. median imputation;
2. missingness-indicator generation;
3. standardization;
4. L2 logistic regression.

Evaluation uses:

```text
RepeatedStratifiedKFold
5 folds × 10 repeats = 50 held-out folds
random_state = 42
```

The pipeline reports fold-level and aggregate:

- ROC-AUC;
- average precision / PR-AUC;
- Brier score;
- accuracy;
- balanced accuracy;
- precision;
- recall for 1-year survival;
- specificity for death within 1 year;
- F1 score.

No train/test metric is described as prospective clinical performance.

## Why Repeated Cross-Validation?

There are only 165 patients.

A single train/test split would make performance highly dependent on which small set of patients happened to land in the test set. Repeated stratified cross-validation gives a more transparent view of metric variability, but it does **not** solve the fundamental small-sample and single-centre limitations.

## Outputs

```text
data/raw/
  hcc_survival_uci.csv
  source_metadata.json

data/processed/
  cohort_summary.csv
  feature_missingness.csv
  subgroup_outcomes.csv
  model_cv_fold_metrics.csv
  model_cv_summary.csv
  model_coefficients.csv
  cancer_survival.sqlite

data/powerbi/
  cohort_summary.csv
  feature_missingness.csv
  subgroup_outcomes.csv
  model_cv_summary.csv
  model_coefficients.csv
```

Patient-level rows are not exported to the Power BI layer.

## Hospital Strategy Interpretation

This project can support a **hospital analytics discussion** around:

- which clinical variables have high missingness;
- which features should be captured consistently in an oncology registry;
- how outcome composition differs across documented clinical groups;
- how uncertain model performance becomes in a small cohort;
- why external validation is required before operational deployment.

It does **not** claim that the dataset identifies a hospital's treatment quality, staffing requirement, causal treatment effect or current HCC survival rate.

## Run

```bash
python -m pip install -r requirements.txt
python src/01_extract_uci_hcc.py
python src/02_build_analytics.py
python src/03_train_validate_model.py
python src/04_build_sqlite.py
python src/05_export_powerbi.py
python src/validate_repo.py
```

GitHub Actions does not call UCI. CI rebuilds analytics and model evaluation from the committed canonical source snapshot.

## Power BI Pages

1. HCC Cohort Overview
2. One-Year Outcome Composition
3. Clinical Feature Missingness
4. Subgroup Outcome Explorer
5. Model Validation & Metric Variability
6. Model Coefficient Explorer
7. Provenance, Limitations & Hospital Data Strategy

## Interview Summary

> I built a reproducible HCC one-year survival analytics project from the UCI HCC Survival dataset. I preserve a canonical source snapshot and SHA-256 provenance, audit missingness across 49 clinical variables, create aggregate subgroup outcome tables, and evaluate an L2 logistic-regression pipeline using repeated stratified 5-fold cross-validation rather than relying on one small holdout split. I explicitly distinguish binary one-year survival classification from true time-to-event survival analysis and avoid presenting the model as clinically validated.

## Author

**Abhijeet Vasantrao Patil**  
GitHub: https://github.com/abhijeet9066-hub
