import csv
from pathlib import Path

from pydantic import ValidationError

from src.validation.parcel import Parcel


INPUT_FILE = Path("data/generated/parcels.csv") 
VALIDATED_FILE = Path("data/raw/parcels.csv")
QUARANTINE_FILE = Path("data/quarantine/parcels_rejected.csv")  # inchangé

NULLABLE_FIELDS = {
    "latitude",
    "longitude",
    "manager",
}


def normalize_row(row: dict) -> dict:
    """Convertit les cellules CSV vides en None pour les champs nullable."""

    normalized_row = row.copy()

    for field in NULLABLE_FIELDS:
        if normalized_row.get(field, "").strip() == "":
            normalized_row[field] = None

    return normalized_row


def validate_parcels() -> None:
    """Valide les parcelles et sépare les données conformes des rejets."""

    with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    valid_rows = []
    rejected_rows = []

    for row in rows:
        normalized_row = normalize_row(row)

        try:
            parcel = Parcel(**normalized_row)

            valid_rows.append(
                parcel.model_dump(mode="json")
            )

        except ValidationError as error:
            rejected_row = normalized_row.copy()
            rejected_row["validation_error"] = str(error)
            rejected_rows.append(rejected_row)

    VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if valid_rows:
        fieldnames = list(valid_rows[0].keys())

        with VALIDATED_FILE.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(valid_rows)

    if rejected_rows:
        fieldnames = list(rejected_rows[0].keys())

        with QUARANTINE_FILE.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rejected_rows)

    print("Validation terminée.")
    print(f"Nombre total : {len(rows)}")
    print(f"Données conformes : {len(valid_rows)}")
    print(f"Données rejetées : {len(rejected_rows)}")
    print(f"Fichier conforme : {VALIDATED_FILE}")
    print(f"Fichier quarantine : {QUARANTINE_FILE}")


if __name__ == "__main__":
    validate_parcels()