import csv
from pathlib import Path

from pydantic import ValidationError

from src.validation.weather import WeatherReading


INPUT_FILE = Path("data/generated/weather.csv") 
VALIDATED_FILE = Path("data/raw/weather.csv")
QUARANTINE_FILE = Path("data/quarantine/weather_rejected.csv")  # inchangé

FIELDNAMES = [
    "zone",
    "date",
    "temperature_c",
    "precipitation_mm",
    "humidity_pct",
]

QUARANTINE_FIELDNAMES = FIELDNAMES + ["validation_error"]


def lire_donnees() -> list[dict]:
    """Lit les mesures météo depuis le fichier CSV."""
    with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def valider_donnees(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Sépare les données conformes des données rejetées."""
    donnees_valides = []
    donnees_rejetees = []

    for row in rows:
        try:
            mesure = WeatherReading(**row)

            donnees_valides.append(
                {
                    "zone": mesure.zone,
                    "date": mesure.date.isoformat(),
                    "temperature_c": mesure.temperature_c,
                    "precipitation_mm": mesure.precipitation_mm,
                    "humidity_pct": mesure.humidity_pct,
                }
            )

        except ValidationError as error:
            row_rejete = dict(row)
            row_rejete["validation_error"] = str(error)
            donnees_rejetees.append(row_rejete)

    return donnees_valides, donnees_rejetees


def sauvegarder_donnees_valides(rows: list[dict]) -> None:
    """Écrit les données conformes dans le fichier de sortie."""
    VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)

    with VALIDATED_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def sauvegarder_donnees_rejetees(rows: list[dict]) -> None:
    """Écrit les données rejetées dans la quarantine."""
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with QUARANTINE_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=QUARANTINE_FIELDNAMES,
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Point d'entrée de la validation météo."""
    rows = lire_donnees()

    donnees_valides, donnees_rejetees = valider_donnees(rows)

    sauvegarder_donnees_valides(donnees_valides)
    sauvegarder_donnees_rejetees(donnees_rejetees)

    print("Validation météo terminée.")
    print(f"Nombre total : {len(rows)}")
    print(f"Données conformes : {len(donnees_valides)}")
    print(f"Données rejetées : {len(donnees_rejetees)}")
    print(f"Fichier conforme : {VALIDATED_FILE}")
    print(f"Fichier quarantine : {QUARANTINE_FILE}")


if __name__ == "__main__":
    main()