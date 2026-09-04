import csv
import json
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path


INPUT_FILE = Path("data/raw/parcels.csv")
OUTPUT_FILE = Path("data/generated/irrigation.jsonl")

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 6, 29)

MIN_READINGS_PER_DAY = 1
MAX_READINGS_PER_DAY = 3

MIN_HOUR = 5
MAX_HOUR = 20


def load_parcels() -> list[dict]:
    """Charge les parcelles validées."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def generate_timestamp(current_date: date) -> str:
    """Génère un timestamp entre 05h00 et 20h00."""
    hour = random.randint(MIN_HOUR, MAX_HOUR)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    timestamp = datetime.combine(
        current_date,
        time(hour, minute, second),
    )

    return timestamp.isoformat()


def generate_reading(
    parcel_id: str,
    current_date: date,
) -> dict:
    """Génère un relevé d'irrigation normal."""
    return {
        "parcel_id": parcel_id,
        "timestamp": generate_timestamp(current_date),
        "water_volume_m3": round(
            random.uniform(0.5, 8.0),
            2,
        ),
        "soil_humidity_pct": round(
            random.uniform(15.0, 60.0),
            2,
        ),
    }


def generate_irrigation(
    parcels: list[dict],
) -> list[dict]:
    """Génère les relevés pour toutes les parcelles."""
    readings = []

    for parcel in parcels:
        parcel_id = parcel["parcel_id"]

        planting_date = date.fromisoformat(
            parcel["planting_date"]
        )

        current_date = max(
            planting_date + timedelta(days=1),
            START_DATE,
         )
        while current_date <= END_DATE:
            number_of_readings = random.randint(
                MIN_READINGS_PER_DAY,
                MAX_READINGS_PER_DAY,
            )

            for _ in range(number_of_readings):
                readings.append(
                    generate_reading(
                        parcel_id,
                        current_date,
                    )
                )

            current_date += timedelta(days=1)

    return readings


def inject_anomalies(
    readings: list[dict],
) -> None:
    """Injecte volontairement des anomalies capteur."""
    number_of_anomalies = random.randint(3, 5)

    selected_readings = random.sample(
        readings,
        number_of_anomalies,
    )

    for reading in selected_readings:
        reading["soil_humidity_pct"] = round(
            random.uniform(101.0, 130.0),
            2,
        )


def save_to_jsonl(
    readings: list[dict],
) -> None:
    """Sauvegarde les données au format JSONL."""
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        for reading in readings:
            file.write(
                json.dumps(
                    reading,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    """Point d'entrée du générateur."""
    parcels = load_parcels()

    if not parcels:
        raise ValueError(
            "Aucune parcelle validée trouvée."
        )

    readings = generate_irrigation(parcels)

    inject_anomalies(readings)

    save_to_jsonl(readings)

    print(
        f"Parcelles utilisées : {len(parcels)}"
    )
    print(
        f"Relevés générés : {len(readings)}"
    )
    print(
        f"Fichier créé : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()