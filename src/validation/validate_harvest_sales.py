"""Valide les événements de récolte/vente générés, avec vérification
référentielle contre les parcelles déjà validées.
"""

import csv
from pathlib import Path

from pydantic import ValidationError

from src.validation.harvest_sale import HarvestSale

INPUT_FILE = Path("data/generated/harvest_sales.csv")
PARCELS_FILE = Path("data/raw/parcels.csv")
VALIDATED_FILE = Path("data/raw/harvest_sales.csv")
QUARANTINE_FILE = Path("data/quarantine/harvest_sales_rejected.csv")

FIELDNAMES = ["parcel_id", "harvest_date", "harvest_kg", "sold_kg", "unit_price_fcfa"]
QUARANTINE_FIELDNAMES = FIELDNAMES + ["validation_error"]


def load_known_parcel_ids() -> set[str]:
    with PARCELS_FILE.open(encoding="utf-8") as f:
        return {row["parcel_id"] for row in csv.DictReader(f)}


def validate_and_quarantine() -> None:
    VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)

    known_parcel_ids = load_known_parcel_ids()

    with INPUT_FILE.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    valid_rows = []
    quarantine_rows = []

    for row in rows:
        try:
            record = HarvestSale.model_validate(row)

            if record.parcel_id not in known_parcel_ids:
                raise ValueError(
                    f"parcel_id '{record.parcel_id}' inconnu (absent des parcelles validées)"
                )

            valid_rows.append(record.model_dump(mode="json"))

        except (ValidationError, ValueError) as error:
            quarantine_row = dict(row)
            quarantine_row["validation_error"] = str(error)
            quarantine_rows.append(quarantine_row)

    with VALIDATED_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(valid_rows)

    with QUARANTINE_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUARANTINE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(quarantine_rows)

    print("Validation récolte/vente terminée.")
    print(f"Nombre total : {len(rows)}")
    print(f"Données conformes : {len(valid_rows)}")
    print(f"Données rejetées : {len(quarantine_rows)}")
    print(f"Fichier conforme : {VALIDATED_FILE}")
    print(f"Fichier quarantine : {QUARANTINE_FILE}")


if __name__ == "__main__":
    validate_and_quarantine()