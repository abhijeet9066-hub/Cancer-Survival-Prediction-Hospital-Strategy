# Power BI Dashboard Blueprint

## Page 1 — HCC Cohort Overview

Cards:

- patients;
- one-year survivors;
- deaths within one year;
- observed one-year survival percentage;
- complete patient rows.

Mandatory note:

> Historical single-centre cohort of 165 patients. Not a current population survival estimate.

## Page 2 — One-Year Outcome Composition

Visuals:

- survivor vs death count;
- survivor vs death percentage;
- age-band outcome composition.

Use the wording **observed outcome composition**, not predicted life expectancy.

## Page 3 — Clinical Feature Missingness

Visuals:

- top missingness fields;
- missing vs observed count;
- complete-case count.

Hospital analytics angle:

> Which registry variables require stronger structured-data capture?

## Page 4 — Subgroup Outcome Explorer

Use `subgroup_outcomes.csv`.

Show only groups with an adequate displayed count and always display `patients`.

Mandatory note:

> Unadjusted descriptive subgroup proportions; not causal treatment effects.

## Page 5 — Model Validation

Show:

- mean repeated-CV ROC-AUC;
- ROC-AUC standard deviation;
- average precision;
- Brier score;
- balanced accuracy;
- recall/specificity.

Mandatory note:

> Repeated cross-validation is internal validation on a 165-patient dataset, not prospective or external clinical validation.

## Page 6 — Model Coefficient Explorer

Show standardized coefficients ranked by absolute magnitude.

Mandatory note:

> Coefficients are descriptive model signals after imputation/scaling. They are not causal effects or clinical risk multipliers.

## Page 7 — Provenance & Limitations

Include:

- UCI dataset ID 423;
- DOI `10.24432/C5TS4S`;
- CC BY 4.0;
- source SHA-256;
- 165 patients / 49 features;
- binary 1-year target;
- no event/censor time;
- no Kaplan-Meier/Cox claims;
- no clinical deployment.
