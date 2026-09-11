from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB = PROCESSED / "cancer_survival.sqlite"

TABLES = {
    "cohort_summary": "cohort_summary.csv",
    "feature_missingness": "feature_missingness.csv",
    "subgroup_outcomes": "subgroup_outcomes.csv",
    "model_cv_fold_metrics": "model_cv_fold_metrics.csv",
    "model_cv_summary": "model_cv_summary.csv",
    "model_coefficients": "model_coefficients.csv",
}


def main():
    conn = sqlite3.connect(DB)
    counts = {}
    try:
        for table, filename in TABLES.items():
            path = PROCESSED / filename
            if not path.exists():
                raise FileNotFoundError(path)
            df = pd.read_csv(path)
            df.to_sql(table, conn, if_exists="replace", index=False)
            counts[table] = len(df)
        conn.commit()
    finally:
        conn.close()

    print(f"SQLite database: {DB}")
    for table, count in counts.items():
        print(f"{table} rows: {count}")


if __name__ == "__main__":
    main()
