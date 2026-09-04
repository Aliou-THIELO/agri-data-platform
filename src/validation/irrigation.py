"""Validation Pydantic des relevés d'irrigation — contrôle de conformité
avant intégration dans le pipeline NiFi.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, ValidationError

INPUT_FILE = Path("data/generated/irrigation.jsonl")
VALID_FILE = Path("data/raw/irrigation.jsonl")
QUARANTINE_FILE = Path("data/quarantine/irrigation_rejected.jsonl")
KNOWN_PARCELS_FILE = Path("data/raw/parcels.csv")


def load_known_parcel_ids() -> set[str]:
    """Charge les parcel_id déjà validés, pour la vérification référentielle."""
    if not KNOWN_PARCELS_FILE.exists():
        raise FileNotFoundError(
            f"{KNOWN_PARCELS_FILE} introuvable — valider les parcelles avant l'irrigation."
        )
    with KNOWN_PARCELS_FILE.open(encoding="utf-8") as f:
        return {row["parcel_id"] for row in csv.DictReader(f)}


class IrrigationRecord(BaseModel):
    parcel_id: str = Field(min_length=8, max_length=8)
    timestamp: datetime
    water_volume_m3: float = Field(ge=0.5, le=8.0)
    soil_humidity_pct: float = Field(ge=0.0, le=100.0)

    @field_validator("parcel_id")
    @classmethod
    def parcel_must_exist(cls, v: str, info) -> str:
        known_ids = info.context.get("known_parcel_ids") if info.context else None
        if known_ids is not None and v not in known_ids:
            raise ValueError(f"parcel_id '{v}' inconnu (absent des parcelles validées)")
        return v


def validate_and_quarantine() -> None:
    VALID_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)

    known_parcel_ids = load_known_parcel_ids()

    valid_count = 0
    invalid_count = 0

    with (
        INPUT_FILE.open("r", encoding="utf-8") as input_file,
        VALID_FILE.open("w", encoding="utf-8") as valid_file,
        QUARANTINE_FILE.open("w", encoding="utf-8") as quarantine_file,
    ):
        for line_number, line in enumerate(input_file, start=1):
            raw_data = None
            try:
                raw_data = json.loads(line)
                record = IrrigationRecord.model_validate(
                    raw_data, context={"known_parcel_ids": known_parcel_ids}
                )
                valid_file.write(
                    json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n"
                )
                valid_count += 1

            except (json.JSONDecodeError, ValidationError) as error:
                invalid_count += 1
                quarantine_file.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "data": raw_data,
                            "error": str(error),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    print(f"Relevés valides   : {valid_count}")
    print(f"Relevés rejetés   : {invalid_count}")
    print(f"Fichier validé    : {VALID_FILE}")
    print(f"Fichier quarantine: {QUARANTINE_FILE}")


if __name__ == "__main__":
    validate_and_quarantine()