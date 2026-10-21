import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

CSV_DATASETS = [
    ("parcels", 23, 2),
    ("weather", 717, 3),
    ("harvest_sales", 21, 2),
]


def count_csv(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def count_jsonl(path: Path) -> int:
    with path.open(encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


@pytest.mark.parametrize("name,valid,rejected", CSV_DATASETS)
def test_csv_datasets_are_consistent(name, valid, rejected):
    raw = count_csv(ROOT / "data" / "raw" / f"{name}.csv")
    quarantine = count_csv(ROOT / "data" / "quarantine" / f"{name}_rejected.csv")
    unfiltered = count_csv(ROOT / "data" / "samples" / "unfiltered" / f"{name}.csv")
    assert raw == valid
    assert quarantine == rejected
    assert unfiltered == raw + quarantine


def test_irrigation_dataset_is_consistent():
    raw = count_jsonl(ROOT / "data" / "raw" / "irrigation.jsonl")
    quarantine = count_jsonl(ROOT / "data" / "quarantine" / "irrigation_rejected.jsonl")
    unfiltered = count_jsonl(ROOT / "data" / "samples" / "unfiltered" / "irrigation.jsonl")
    assert raw == 6910
    assert quarantine == 4
    assert unfiltered == raw + quarantine
