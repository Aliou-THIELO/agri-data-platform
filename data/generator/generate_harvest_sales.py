"""Génère les événements de récolte/vente (1 par parcelle validée).

Lit data/raw/parcels.csv (parcelles DÉJÀ VALIDÉES, pas les brutes générées)
et écrit data/generated/harvest_sales.csv.

Injecte volontairement 1-2 anomalies (sold_kg > harvest_kg) pour tester
la validation Pydantic en aval.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

PARCELS_FILE = Path("data/raw/parcels.csv")
OUTPUT_FILE = Path("data/generated/harvest_sales.csv")

SEED = 42
HARVEST_START = date(2026, 4, 1)
HARVEST_END = date(2026, 5, 1)


def load_validated_parcel_ids() -> list[str]:
    if not PARCELS_FILE.exists():
        raise FileNotFoundError(
            f"{PARCELS_FILE} introuvable — valider les parcelles avant de générer les récoltes."
        )
    with PARCELS_FILE.open(encoding="utf-8") as f:
        return [row["parcel_id"] for row in csv.DictReader(f)]


def generate_harvest_sales(seed: int = SEED) -> list[dict]:
    random.seed(seed)
    parcel_ids = load_validated_parcel_ids()

    delta_days = (HARVEST_END - HARVEST_START).days
    records = []

    for parcel_id in parcel_ids:
        harvest_date = HARVEST_START + timedelta(days=random.randint(0, delta_days))
        harvest_kg = round(random.uniform(50, 2000), 1)
        taux_perte = random.uniform(0.05, 0.25)
        sold_kg = round(harvest_kg * (1 - taux_perte), 1)

        records.append(
            {
                "parcel_id": parcel_id,
                "harvest_date": harvest_date.isoformat(),
                "harvest_kg": harvest_kg,
                "sold_kg": sold_kg,
                "unit_price_fcfa": random.randint(150, 600),
            }
        )

    # Anomalie volontaire : sold_kg > harvest_kg sur 1-2 lignes, pour tester
    # la validation Pydantic (cas de rejet démontrable en quarantine).
    if len(records) >= 2:
        for idx in random.sample(range(len(records)), k=min(2, len(records))):
            records[idx]["sold_kg"] = round(records[idx]["harvest_kg"] * 1.15, 1)

    return records


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    records = generate_harvest_sales()

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["parcel_id", "harvest_date", "harvest_kg", "sold_kg", "unit_price_fcfa"],
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"{len(records)} événements de récolte/vente générés.")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()