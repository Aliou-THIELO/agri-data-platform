from datetime import date

from pydantic import BaseModel, Field, field_validator


ZONES = {
    "Niayes",
    "Vallée du Fleuve",
    "Casamance",
    "Sine-Saloum",
}


class WeatherReading(BaseModel):
    """Modèle de validation d'une mesure météo."""

    zone: str
    date: date
    temperature_c: float = Field(ge=22, le=38)
    precipitation_mm: float = Field(ge=0)
    humidity_pct: float = Field(ge=30, le=85)

    @field_validator("zone")
    @classmethod
    def valider_zone(cls, value: str) -> str:
        """Vérifie que la zone appartient au référentiel."""
        if value not in ZONES:
            raise ValueError(f"Zone invalide : {value}")
        return value

    @field_validator("date")
    @classmethod
    def valider_date(cls, value: date) -> date:
        """Vérifie que la date appartient à la période de la campagne."""
        date_debut = date(2026, 1, 1)
        date_fin = date(2026, 6, 29)

        if not date_debut <= value <= date_fin:
            raise ValueError(
                f"Date hors période : {value}. "
                f"La période autorisée est du {date_debut} au {date_fin}."
            )

        return value