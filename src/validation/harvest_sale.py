"""Modèle de validation d'un événement de récolte/vente (HarvestSale)."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class HarvestSale(BaseModel):
    """Modèle de validation d'un enregistrement récolte/vente."""

    parcel_id: str = Field(min_length=8, max_length=8)
    harvest_date: date
    harvest_kg: float = Field(gt=0, le=2000)
    sold_kg: float = Field(ge=0)
    unit_price_fcfa: int = Field(gt=0, le=1000)

    @field_validator("sold_kg")
    @classmethod
    def sold_ne_depasse_pas_harvest(cls, value: float, info) -> float:
        """Vérifie que la quantité vendue ne dépasse pas la quantité récoltée."""
        harvest_kg = info.data.get("harvest_kg")
        if harvest_kg is not None and value > harvest_kg:
            raise ValueError(
                f"sold_kg ({value}) ne peut pas dépasser harvest_kg ({harvest_kg})"
            )
        return value