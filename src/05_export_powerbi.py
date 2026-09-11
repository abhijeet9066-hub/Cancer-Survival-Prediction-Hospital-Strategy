from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
POWERBI = ROOT / "data" / "powerbi"
POWERBI.mkdir(parents=True, exist_ok=True)

FILES = [
    "cohort_summary.csv",
    "feature_missingness.csv",
    "subgroup_outcomes.csv",
    "model_cv_summary.csv",
    "model_coefficients.csv",
]


def main():
    for name in FILES:
        src = PROCESSED / name
        if not src.exists():
            raise FileNotFoundError(src)
        dst = POWERBI / name
        shutil.copy2(src, dst)
        print(f"Exported {dst}")


if __name__ == "__main__":
    main()
