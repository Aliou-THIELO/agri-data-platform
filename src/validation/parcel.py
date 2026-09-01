from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ZONES = {
    "Niayes",
    "Vallée du Fleuve",
    "Casamance",
    "Sine-Saloum",
}

CROPS = {
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
}

MANAGERS = {
    "Coopérative A",
    "Coopérative B",
    "Exploitant indépendant",
}


class Parcel(BaseModel):
    """Modèle de validation d'une parcelle agricole."""

    model_config = ConfigDict(str_strip_whitespace=True)

    parcel_id: str = Field(min_length=1, max_length=8)
    zone: str
    crop: str
    surface_m2: float = Field(gt=0, le=5000)
    planting_date: date
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    manager: Optional[str] = None

    @field_validator("zone")
    @classmethod
    def validate_zone(cls, value: str) -> str:
        if value not in ZONES:
            raise ValueError(f"Zone invalide : {value}")
        return value

    @field_validator("crop")
    @classmethod
    def validate_crop(cls, value: str) -> str:
        if value not in CROPS:
            raise ValueError(f"Culture invalide : {value}")
        return value

    @field_validator("planting_date")
    @classmethod
    def validate_planting_date(cls, value: date) -> date:
        start = date(2026, 1, 1)
        end = date(2026, 3, 1)

        if not start <= value <= end:
            raise ValueError(
                "La date de plantation doit être comprise "
                "entre le 2026-01-01 et le 2026-03-01."
            )

        return value

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not 14.6 <= value <= 16.5:
            raise ValueError("Latitude hors de la plage autorisée.")

        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not -17.5 <= value <= -13.0:
            raise ValueError("Longitude hors de la plage autorisée.")

        return value

    @field_validator("manager")
    @classmethod
    def validate_manager(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in MANAGERS:
            raise ValueError(f"Manager invalide : {value}")

        return value