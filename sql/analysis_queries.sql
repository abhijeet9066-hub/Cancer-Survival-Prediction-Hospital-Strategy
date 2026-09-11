-- HCC One-Year Survival Analytics
-- Historical descriptive/educational analytics only; not clinical decision support.

-- 1. Cohort summary
SELECT metric, value
FROM cohort_summary;

-- 2. Highest missingness features
SELECT feature,
       missing_count,
       ROUND(missing_pct, 2) AS missing_pct,
       non_missing_count
FROM feature_missingness
ORDER BY missing_pct DESC, feature
LIMIT 20;

-- 3. Descriptive subgroup outcomes
SELECT group_variable,
       group_value,
       patients,
       survived_1yr,
       died_within_1yr,
       ROUND(observed_survival_pct, 1) AS observed_survival_pct
FROM subgroup_outcomes
WHERE patients >= 5
ORDER BY group_variable, observed_survival_pct DESC;

-- 4. Repeated-CV validation summary
SELECT metric,
       ROUND(mean, 4) AS mean,
       ROUND(std, 4) AS std,
       ROUND(min, 4) AS min,
       ROUND(max, 4) AS max,
       fold_evaluations
FROM model_cv_summary;

-- 5. Largest absolute standardized model coefficients
SELECT model_feature,
       ROUND(standardized_coefficient, 4) AS standardized_coefficient,
       direction_for_survival_class
FROM model_coefficients
ORDER BY abs_standardized_coefficient DESC
LIMIT 20;
