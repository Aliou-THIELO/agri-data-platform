import pytest
from pydantic import ValidationError

from src.validation.harvest_sale import HarvestSale
from src.validation.weather import WeatherReading

VALID_WEATHER = {
    "zone": "Niayes",
    "date": "2026-01-05",
    "temperature_c": 30.0,
    "precipitation_mm": 0.5,
    "humidity_pct": 55.0,
}

VALID_HARVEST = {
    "parcel_id": "a1b2c3d4",
    "harvest_date": "2026-04-03",
    "harvest_kg": 1000.0,
    "sold_kg": 900.0,
    "unit_price_fcfa": 500,
}


def test_valid_weather_is_accepted():
    assert WeatherReading(**VALID_WEATHER).temperature_c == 30.0


@pytest.mark.parametrize("temperature", [-5.0, -8.0, 55.0])
def test_out_of_range_temperature_is_rejected(temperature):
    with pytest.raises(ValidationError):
        WeatherReading(**{**VALID_WEATHER, "temperature_c": temperature})


def test_valid_harvest_is_accepted():
    assert HarvestSale(**VALID_HARVEST).sold_kg == 900.0


def test_sold_more_than_harvested_is_rejected():
    with pytest.raises(ValidationError):
        HarvestSale(**{**VALID_HARVEST, "sold_kg": 1100.0})
