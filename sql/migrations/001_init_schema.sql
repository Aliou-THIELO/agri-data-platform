CREATE SCHEMA IF NOT EXISTS agri_dw;

CREATE TABLE IF NOT EXISTS agri_dw.dim_zone (
    zone_id     SERIAL PRIMARY KEY,
    zone_name   VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS agri_dw.dim_date (
    date_id      DATE PRIMARY KEY,
    year         SMALLINT NOT NULL,
    month        SMALLINT NOT NULL,
    day          SMALLINT NOT NULL,
    quarter      SMALLINT NOT NULL,
    day_of_week  VARCHAR(10) NOT NULL
);

-- Dimension parcelle : clé de substitution (parcel_dim_id) + clé source (parcel_id)
CREATE TABLE IF NOT EXISTS agri_dw.dim_parcel (
    parcel_dim_id   SERIAL PRIMARY KEY,           -- clé technique (surrogate key)
    parcel_id       VARCHAR(8) NOT NULL UNIQUE,   -- clé source, conservée pour traçabilité
    zone_id         INTEGER NOT NULL REFERENCES agri_dw.dim_zone(zone_id),
    crop            VARCHAR(50) NOT NULL,
    surface_m2      NUMERIC(10,1) NOT NULL,
    planting_date   DATE,
    latitude        NUMERIC(8,5),
    longitude       NUMERIC(8,5),
    manager         VARCHAR(100)
);

-- Les faits référencent désormais parcel_dim_id, pas parcel_id directement
CREATE TABLE IF NOT EXISTS agri_dw.fact_irrigation (
    id                 BIGSERIAL PRIMARY KEY,
    parcel_dim_id      INTEGER NOT NULL REFERENCES agri_dw.dim_parcel(parcel_dim_id),
    date_id            DATE NOT NULL REFERENCES agri_dw.dim_date(date_id),
    water_volume_m3    NUMERIC(6,2) NOT NULL,
    soil_humidity_pct  NUMERIC(5,1)
);

CREATE TABLE IF NOT EXISTS agri_dw.fact_weather (
    id                 BIGSERIAL PRIMARY KEY,
    zone_id            INTEGER NOT NULL REFERENCES agri_dw.dim_zone(zone_id),
    date_id            DATE NOT NULL REFERENCES agri_dw.dim_date(date_id),
    temperature_c      NUMERIC(4,1),
    precipitation_mm   NUMERIC(5,1),
    humidity_pct       NUMERIC(5,1)
);

CREATE TABLE IF NOT EXISTS agri_dw.fact_harvest (
    id                  BIGSERIAL PRIMARY KEY,
    parcel_dim_id       INTEGER NOT NULL REFERENCES agri_dw.dim_parcel(parcel_dim_id),
    date_id             DATE NOT NULL REFERENCES agri_dw.dim_date(date_id),
    harvest_kg          NUMERIC(8,1) NOT NULL,
    sold_kg             NUMERIC(8,1) NOT NULL,
    unit_price_fcfa     INTEGER
);

CREATE INDEX IF NOT EXISTS idx_fact_irrigation_parcel ON agri_dw.fact_irrigation(parcel_dim_id);
CREATE INDEX IF NOT EXISTS idx_fact_harvest_parcel ON agri_dw.fact_harvest(parcel_dim_id);
CREATE INDEX IF NOT EXISTS idx_dim_parcel_source_id ON agri_dw.dim_parcel(parcel_id);