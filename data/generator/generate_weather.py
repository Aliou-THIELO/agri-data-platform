import csv
import random
from datetime import date, timedelta
from pathlib import Path


OUTPUT_FILE = Path("data/generated/weather.csv")   # était data/raw/weather.csv
NUMBER_OF_DAYS = 180

ZONES = [
    "Niayes",
    "Vallée du Fleuve",
    "Casamance",
    "Sine-Saloum",
]

FIELDNAMES = [
    "zone",
    "date",
    "temperature_c",
    "precipitation_mm",
    "humidity_pct",
]


def generate_dates() -> list[date]:
    """Génère les 180 dates de la période."""
    start_date = date(2026, 1, 1)

    return [
        start_date + timedelta(days=offset)
        for offset in range(NUMBER_OF_DAYS)
    ]


def generate_precipitation() -> float:
    """Génère une précipitation avec une majorité de valeurs faibles."""
    if random.random() < 0.80:
        return round(random.uniform(0, 2), 2)

    return round(random.uniform(2, 40), 2)


def generate_weather_reading(zone: str, reading_date: date) -> dict:
    """Génère une observation météo conforme au contrat."""
    return {
        "zone": zone,
        "date": reading_date.isoformat(),
        "temperature_c": round(random.uniform(22, 38), 2),
        "precipitation_mm": generate_precipitation(),
        "humidity_pct": round(random.uniform(30, 85), 2),
    }


def generate_weather() -> list[dict]:
    """Génère 180 jours de données pour chacune des 4 zones."""
    dates = generate_dates()

    readings = []

    for zone in ZONES:
        for reading_date in dates:
            readings.append(
                generate_weather_reading(zone, reading_date)
            )

    # Anomalies volontaires pour tester la validation.
    readings[0]["temperature_c"] = -5
    readings[1]["temperature_c"] = 55
    readings[2]["temperature_c"] = -8

    return readings


def save_to_csv(readings: list[dict]) -> None:
    """Écrit les données météo dans le fichier CSV."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()
        writer.writerows(readings)


def main() -> None:
    """Point d'entrée du générateur."""
    readings = generate_weather()
    save_to_csv(readings)

    print(f"{len(readings)} relevés météo générés.")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
