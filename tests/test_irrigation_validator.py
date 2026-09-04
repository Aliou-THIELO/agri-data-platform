from datetime import datetime

import pytest
from pydantic import ValidationError

from src.validation.irrigation import IrrigationRecord


VALID_PARCEL_ID = "81be1926"  # 8 caractères, cohérent avec le format généré


def test_valid_irrigation_record():
    record = IrrigationRecord.model_validate(
        {
            "parcel_id": VALID_PARCEL_ID,
            "timestamp": "2026-02-02T08:31:22",
            "water_volume_m3": 4.72,
            "soil_humidity_pct": 37.15,
        },
        context={"known_parcel_ids": {VALID_PARCEL_ID}},
    )
    assert record.parcel_id == VALID_PARCEL_ID
    assert record.timestamp == datetime(2026, 2, 2, 8, 31, 22)
    assert record.water_volume_m3 == 4.72
    assert record.soil_humidity_pct == 37.15


def test_invalid_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": VALID_PARCEL_ID,
                "timestamp": "timestamp_invalide",
                "water_volume_m3": 4.72,
                "soil_humidity_pct": 37.15,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )


def test_humidity_above_100_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": VALID_PARCEL_ID,
                "timestamp": "2026-02-02T08:31:22",
                "water_volume_m3": 4.72,
                "soil_humidity_pct": 114.2,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )


def test_water_volume_below_minimum_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": VALID_PARCEL_ID,
                "timestamp": "2026-02-02T08:31:22",
                "water_volume_m3": 0.49,
                "soil_humidity_pct": 37.15,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )


def test_water_volume_above_maximum_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": VALID_PARCEL_ID,
                "timestamp": "2026-02-02T08:31:22",
                "water_volume_m3": 8.01,
                "soil_humidity_pct": 37.15,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )


def test_parcel_id_wrong_length_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": "P001",  # trop court, doit faire 8 caractères
                "timestamp": "2026-02-02T08:31:22",
                "water_volume_m3": 4.72,
                "soil_humidity_pct": 37.15,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )


def test_unknown_parcel_id_is_rejected():
    with pytest.raises(ValidationError):
        IrrigationRecord.model_validate(
            {
                "parcel_id": "ffffffff",  # 8 caractères, mais absent de known_parcel_ids
                "timestamp": "2026-02-02T08:31:22",
                "water_volume_m3": 4.72,
                "soil_humidity_pct": 37.15,
            },
            context={"known_parcel_ids": {VALID_PARCEL_ID}},
        )