# Data Dictionary

## Target

| Field | Meaning |
|---|---|
| `survival_1yr` | 1 = survived one year; 0 = died within one year |

## Clinical predictors

| Field | Meaning |
|---|---|
| `gender` | UCI HCC clinical feature in published source order |
| `symptoms` | UCI HCC clinical feature in published source order |
| `alcohol` | UCI HCC clinical feature in published source order |
| `hepatitis_b_surface_antigen` | UCI HCC clinical feature in published source order |
| `hepatitis_b_e_antigen` | UCI HCC clinical feature in published source order |
| `hepatitis_b_core_antibody` | UCI HCC clinical feature in published source order |
| `hepatitis_c_virus_antibody` | UCI HCC clinical feature in published source order |
| `cirrhosis` | UCI HCC clinical feature in published source order |
| `endemic_countries` | UCI HCC clinical feature in published source order |
| `smoking` | UCI HCC clinical feature in published source order |
| `diabetes` | UCI HCC clinical feature in published source order |
| `obesity` | UCI HCC clinical feature in published source order |
| `hemochromatosis` | UCI HCC clinical feature in published source order |
| `arterial_hypertension` | UCI HCC clinical feature in published source order |
| `chronic_renal_insufficiency` | UCI HCC clinical feature in published source order |
| `hiv` | UCI HCC clinical feature in published source order |
| `nonalcoholic_steatohepatitis` | UCI HCC clinical feature in published source order |
| `esophageal_varices` | UCI HCC clinical feature in published source order |
| `splenomegaly` | UCI HCC clinical feature in published source order |
| `portal_hypertension` | UCI HCC clinical feature in published source order |
| `portal_vein_thrombosis` | UCI HCC clinical feature in published source order |
| `liver_metastasis` | UCI HCC clinical feature in published source order |
| `radiological_hallmark` | UCI HCC clinical feature in published source order |
| `age_at_diagnosis` | UCI HCC clinical feature in published source order |
| `alcohol_grams_per_day` | UCI HCC clinical feature in published source order |
| `cigarette_packs_per_year` | UCI HCC clinical feature in published source order |
| `performance_status` | UCI HCC clinical feature in published source order |
| `encephalopathy_degree` | UCI HCC clinical feature in published source order |
| `ascites_degree` | UCI HCC clinical feature in published source order |
| `inr` | UCI HCC clinical feature in published source order |
| `alpha_fetoprotein_ng_ml` | UCI HCC clinical feature in published source order |
| `haemoglobin_g_dl` | UCI HCC clinical feature in published source order |
| `mean_corpuscular_volume_fl` | UCI HCC clinical feature in published source order |
| `leukocytes_g_l` | UCI HCC clinical feature in published source order |
| `platelets_g_l` | UCI HCC clinical feature in published source order |
| `albumin_mg_dl` | UCI HCC clinical feature in published source order |
| `total_bilirubin_mg_dl` | UCI HCC clinical feature in published source order |
| `alt_u_l` | UCI HCC clinical feature in published source order |
| `ast_u_l` | UCI HCC clinical feature in published source order |
| `ggt_u_l` | UCI HCC clinical feature in published source order |
| `alkaline_phosphatase_u_l` | UCI HCC clinical feature in published source order |
| `total_proteins_g_dl` | UCI HCC clinical feature in published source order |
| `creatinine_mg_dl` | UCI HCC clinical feature in published source order |
| `number_of_nodules` | UCI HCC clinical feature in published source order |
| `major_nodule_dimension_cm` | UCI HCC clinical feature in published source order |
| `direct_bilirubin_mg_dl` | UCI HCC clinical feature in published source order |
| `iron_mcg_dl` | UCI HCC clinical feature in published source order |
| `oxygen_saturation_pct` | UCI HCC clinical feature in published source order |
| `ferritin_ng_ml` | UCI HCC clinical feature in published source order |

## Processed outputs

`cohort_summary.csv` contains cohort and target counts.

`feature_missingness.csv` contains missing count and missing percentage for every predictor.

`subgroup_outcomes.csv` contains aggregate observed one-year outcome composition for selected clinical grouping fields.

`model_cv_fold_metrics.csv` contains one row per held-out cross-validation fold.

`model_cv_summary.csv` contains aggregate mean / standard deviation / minimum / maximum for each validation metric.

`model_coefficients.csv` contains full-cohort standardized logistic-regression coefficients. These are descriptive model signals, not causal effect estimates.
