from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import io
import json
import zipfile

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

FEATURES = json.loads((ROOT / "config" / "feature_names.json").read_text(encoding="utf-8"))
COLUMNS = FEATURES + [CONFIG["target"]]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_official_zip() -> tuple[pd.DataFrame, dict]:
    r = requests.get(
        CONFIG["uci_zip_url"],
        timeout=(30, 180),
        headers={"User-Agent": UA, "Accept": "application/zip,*/*;q=0.8"},
    )
    r.raise_for_status()
    raw_zip = r.content

    if not raw_zip.startswith(b"PK"):
        raise RuntimeError("UCI download did not return a ZIP archive.")

    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        candidates = [
            name for name in z.namelist()
            if name.lower().endswith("hcc-data.txt")
            and "__macosx" not in name.lower()
        ]
        if len(candidates) != 1:
            raise RuntimeError(f"Could not uniquely locate hcc-data.txt: {candidates}")
        member = candidates[0]
        raw_data = z.read(member)

    frame = pd.read_csv(
        io.BytesIO(raw_data),
        header=None,
        names=COLUMNS,
        na_values=["?"],
        skipinitialspace=True,
    )

    meta = {
        "retrieval_mode": "official UCI ZIP",
        "zip_sha256": sha256_bytes(raw_zip),
        "raw_hcc_data_sha256": sha256_bytes(raw_data),
        "zip_bytes": len(raw_zip),
        "raw_member": member,
    }
    return frame, meta


def fetch_via_ucimlrepo() -> tuple[pd.DataFrame, dict]:
    from ucimlrepo import fetch_ucirepo

    ds = fetch_ucirepo(id=int(CONFIG["uci_dataset_id"]))
    X = ds.data.features.copy()
    y = ds.data.targets.copy()

    if X.shape[1] != len(FEATURES):
        raise RuntimeError(
            f"UCI interface returned {X.shape[1]} features; expected {len(FEATURES)}."
        )
    if y.shape[1] != 1:
        raise RuntimeError(f"Expected one target column; found {y.shape[1]}.")

    X.columns = FEATURES
    y.columns = [CONFIG["target"]]
    frame = pd.concat([X, y], axis=1)

    meta = {
        "retrieval_mode": "ucimlrepo fallback",
        "zip_sha256": None,
        "raw_hcc_data_sha256": None,
        "zip_bytes": None,
        "raw_member": None,
    }
    return frame, meta


def main() -> None:
    retrieval_error = None
    try:
        print("Downloading official UCI HCC Survival ZIP...")
        df, retrieval = download_official_zip()
    except Exception as exc:
        retrieval_error = f"{type(exc).__name__}: {exc}"
        print("Official ZIP retrieval failed; trying ucimlrepo fallback...")
        df, retrieval = fetch_via_ucimlrepo()

    # Canonical numeric conversion; UCI missing values are retained as NaN.
    for c in COLUMNS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    expected_rows = int(CONFIG["expected_rows"])
    expected_features = int(CONFIG["expected_features"])
    target = CONFIG["target"]

    if df.shape != (expected_rows, expected_features + 1):
        raise RuntimeError(
            f"Expected {(expected_rows, expected_features + 1)} table shape; "
            f"found {df.shape}."
        )

    if df[target].isna().any():
        raise RuntimeError("Target contains missing values after parsing.")

    classes = set(df[target].astype(int).unique())
    if classes != {0, 1}:
        raise RuntimeError(f"Unexpected target values: {classes}")

    survivors = int((df[target] == 1).sum())
    deaths = int((df[target] == 0).sum())

    if survivors != int(CONFIG["expected_survived_1yr"]):
        raise RuntimeError(
            f"Expected {CONFIG['expected_survived_1yr']} survivors; found {survivors}."
        )
    if deaths != int(CONFIG["expected_died_within_1yr"]):
        raise RuntimeError(
            f"Expected {CONFIG['expected_died_within_1yr']} deaths; found {deaths}."
        )

    out = RAW / "hcc_survival_uci.csv"
    df.to_csv(out, index=False)

    metadata = {
        "project": CONFIG["project"],
        "uci_dataset_id": CONFIG["uci_dataset_id"],
        "uci_dataset_name": CONFIG["uci_dataset_name"],
        "uci_dataset_page": CONFIG["uci_dataset_page"],
        "uci_zip_url": CONFIG["uci_zip_url"],
        "doi": CONFIG["uci_doi"],
        "license": CONFIG["license"],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "retrieval_mode": retrieval["retrieval_mode"],
        "official_zip_error_if_fallback": retrieval_error,
        "zip_sha256": retrieval["zip_sha256"],
        "raw_hcc_data_sha256": retrieval["raw_hcc_data_sha256"],
        "canonical_csv_sha256": sha256_file(out),
        "rows": len(df),
        "features": expected_features,
        "survived_1yr": survivors,
        "died_within_1yr": deaths,
        "total_feature_missing_cells": int(df[FEATURES].isna().sum().sum()),
        "total_feature_cells": int(df[FEATURES].size),
        "synthetic_data": False,
        "interpretation": (
            "Binary one-year survival outcome in a historical 165-patient HCC cohort. "
            "Not a time-to-event dataset and not clinically validated for real-patient use."
        ),
    }

    (RAW / "source_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Rows: {len(df)}")
    print(f"Clinical features: {len(FEATURES)}")
    print(f"Survived 1 year: {survivors}")
    print(f"Died within 1 year: {deaths}")
    print(f"Missing feature cells: {metadata['total_feature_missing_cells']}")
    print(f"Retrieval mode: {retrieval['retrieval_mode']}")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
