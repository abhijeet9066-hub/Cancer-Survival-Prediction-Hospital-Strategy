# Data Provenance

## Official source

UCI Machine Learning Repository:

**HCC Survival — dataset 423**

- Dataset page: `https://archive.ics.uci.edu/dataset/423/hcc+survival`
- DOI: `10.24432/C5TS4S`
- License: CC BY 4.0
- Dataset creators: Miriam Santos, Pedro Abreu, Pedro Garcia-Laencina, Adelia Simao, Armando Carvalho

UCI describes the source as real clinical data for 165 patients diagnosed with hepatocellular carcinoma at a University Hospital in Portugal.

## Extraction

The extractor first downloads the official UCI ZIP distribution and reads:

`hcc-survival/hcc-data.txt`

The canonical 50-column table is then written to:

`data/raw/hcc_survival_uci.csv`

The first 49 columns are clinical predictors, in the published UCI order. The final column is the binary one-year survival target.

The extraction metadata records:

- retrieval timestamp;
- official source URL;
- dataset ID and DOI;
- raw ZIP SHA-256;
- raw `hcc-data.txt` SHA-256;
- canonical CSV SHA-256;
- row count;
- feature count;
- target class counts;
- `synthetic_data: false`.

If the UCI ZIP endpoint is unavailable, the script can fall back to the official `ucimlrepo` dataset interface and records that retrieval mode explicitly.

## Fixed source checks

The pipeline expects the published dataset characteristics:

- 165 patients;
- 49 features;
- 102 one-year survivors;
- 63 deaths within one year.

A mismatch fails extraction rather than silently changing the analytical cohort.

## Privacy

This public UCI dataset contains clinical variables but does not expose names, addresses, phone numbers or patient identifiers in the analytical table.

The Power BI export contains aggregate tables only.

## Synthetic data

No synthetic patient rows, labels or clinical measurements are generated.
