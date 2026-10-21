import csv

import pytest
from pydantic import ValidationError

from src.validation import validate_parcels as vp
from src.validation.parcel import Parcel

VALID_PARCEL = {
    "parcel_id": "a1b2c3d4",
    "zone": "Niayes",
    "crop": "Aubergine",
    "surface_m2": 500.0,
    "planting_date": "2026-02-10",
    "latitude": 14.865122,
    "longitude": -17.038772,
    "manager": "Coopérative A",
}


def test_valid_parcel_is_accepted():
    parcel = Parcel(**VALID_PARCEL)
    assert parcel.surface_m2 == 500.0


@pytest.mark.parametrize("surface", [-500.0, 0.0])
def test_non_positive_surface_is_rejected(surface):
    with pytest.raises(ValidationError):
        Parcel(**{**VALID_PARCEL, "surface_m2": surface})


def test_validate_parcels_splits_valid_and_rejected(tmp_path, monkeypatch):
    input_file = tmp_path / "generated" / "parcels.csv"
    input_file.parent.mkdir()
    rows = [
        VALID_PARCEL,
        {**VALID_PARCEL, "parcel_id": "b2c3d4e5", "manager": ""},
        {**VALID_PARCEL, "parcel_id": "c3d4e5f6", "surface_m2": -500.0},
    ]
    with input_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(VALID_PARCEL.keys()))
        writer.writeheader()
        writer.writerows(rows)

    validated = tmp_path / "raw" / "parcels.csv"
    quarantine = tmp_path / "quarantine" / "parcels_rejected.csv"
    monkeypatch.setattr(vp, "INPUT_FILE", input_file)
    monkeypatch.setattr(vp, "VALIDATED_FILE", validated)
    monkeypatch.setattr(vp, "QUARANTINE_FILE", quarantine)

    vp.validate_parcels()

    with validated.open(newline="", encoding="utf-8") as f:
        valid_rows = list(csv.DictReader(f))
    with quarantine.open(newline="", encoding="utf-8") as f:
        rejected_rows = list(csv.DictReader(f))

    assert len(valid_rows) == 2
    assert len(rejected_rows) == 1
    assert rejected_rows[0]["parcel_id"] == "c3d4e5f6"
    assert "validation_error" in rejected_rows[0]
