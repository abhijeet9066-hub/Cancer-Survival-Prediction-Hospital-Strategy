# Methodology

## Target

`survival_1yr`

```text
1 = survived 1 year
0 = died within 1 year
```

This is a binary fixed-horizon outcome.

It is not an event-time/censoring variable.

## Clinical feature representation

The UCI source contains 49 numeric-coded clinical variables.

The project keeps the source coding instead of inventing undocumented category labels.

Published feature descriptions are used for canonical column names.

## Missing data

UCI reports substantial missingness in this dataset.

Missing data are preserved in the committed canonical source snapshot.

For model training only, imputation is performed **inside each training fold** using median imputation. Missingness indicators are also added inside the pipeline.

This prevents information from a held-out fold from being used to calculate imputation values.

## Model

L2-regularized logistic regression:

```text
SimpleImputer(strategy="median", add_indicator=True)
StandardScaler()
LogisticRegression(
    penalty="l2",
    C=1.0,
    solver="liblinear",
    max_iter=5000
)
```

No hyperparameter search is performed.

This limits researcher degrees of freedom in a very small dataset.

## Validation

```text
RepeatedStratifiedKFold
n_splits = 5
n_repeats = 10
random_state = 42
```

There are 50 held-out fold evaluations.

Metrics are summarized using mean, standard deviation, minimum and maximum.

## Reported metrics

Positive class = survived one year.

Reported metrics:

- ROC-AUC
- average precision
- Brier score
- accuracy
- balanced accuracy
- precision
- recall / sensitivity for one-year survival
- specificity for death within one year
- F1

## Full-cohort coefficient table

After cross-validation is complete, the same pipeline is fit to the full cohort only to create a descriptive coefficient table.

Those coefficients are **not** presented as causal effects or externally validated prognostic factors.

## Subgroup tables

Aggregate outcome composition is reported for selected clinical fields and derived age bands.

Subgroup tables are descriptive.

They do not adjust for confounding and should not be interpreted as treatment effects.
