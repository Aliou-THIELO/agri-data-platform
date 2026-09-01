import csv
import random
import uuid
from datetime import date, timedelta
from pathlib import Path


OUTPUT_FILE = Path("data/raw/parcels.csv")
NUMBER_OF_PARCELS = 25

ZONES = [
    "Niayes",
    "Vallée du Fleuve",
    "Casamance",
    "Sine-Saloum",
]

CROPS = [
    "Tomate",
    "Oignon",
    "Chou",
    "Piment",
    "Aubergine",
    "Gombo",
    "Carotte",
    "Laitue",
    "Poivron",
    "Concombre",
]

MANAGERS = [
    "Coopérative A",
    "Coopérative B",
    "Exploitant indépendant",
    None,
]

FIELDNAMES = [
    "parcel_id",
    "zone",
    "crop",
    "surface_m2",
    "planting_date",
    "latitude",
    "longitude",
    "manager",
]


def random_date(start: date, end: date) -> date:
    """Génère une date aléatoire entre deux dates incluses."""
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def generate_parcel() -> dict:
    """Génère une parcelle respectant le contrat de données."""
    planting_date = random_date(
        date(2026, 1, 1),
        date(2026, 3, 1),
    )

    return {
        "parcel_id": uuid.uuid4().hex[:8],
        "zone": random.choice(ZONES),
        "crop": random.choice(CROPS),
        "surface_m2": round(random.uniform(200, 5000), 2),
        "planting_date": planting_date.isoformat(),
        "latitude": round(random.uniform(14.6, 16.5), 6),
        "longitude": round(random.uniform(-17.5, -13.0), 6),
        "manager": random.choice(MANAGERS),
    }


def generate_parcels() -> list[dict]:
    """Génère l'ensemble des parcelles."""
    parcels = [
        generate_parcel()
        for _ in range(NUMBER_OF_PARCELS)
    ]

    # Une parcelle sans coordonnées pour tester les données incomplètes.
    parcels[2]["latitude"] = None
    parcels[2]["longitude"] = None

    # Anomalies volontaires destinées aux tests de validation.
    parcels[0]["surface_m2"] = -500
    parcels[1]["surface_m2"] = 0

    return parcels


def save_to_csv(parcels: list[dict]) -> None:
    """Écrit les parcelles dans le fichier CSV de sortie."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(parcels)


def main() -> None:
    """Point d'entrée du générateur."""
    parcels = generate_parcels()
    save_to_csv(parcels)

    print(f"{len(parcels)} parcelles générées.")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

