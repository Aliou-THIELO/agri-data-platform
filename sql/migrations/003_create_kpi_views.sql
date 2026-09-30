-- Productivité parcelle
CREATE OR REPLACE VIEW agri_dw.kpi_parcel_productivity AS
SELECT
    p.parcel_dim_id,
    p.parcel_id,
    p.surface_m2,
    SUM(h.harvest_kg) AS total_rendement_kg,
    ROUND(SUM(h.harvest_kg) / NULLIF(p.surface_m2, 0), 4) AS productivite_kg_par_m2
FROM agri_dw.dim_parcel p
JOIN agri_dw.fact_harvest h ON h.parcel_dim_id = p.parcel_dim_id
GROUP BY p.parcel_dim_id, p.parcel_id, p.surface_m2;

-- Taux de perte post-récolte (par événement de récolte)
CREATE OR REPLACE VIEW agri_dw.kpi_post_harvest_loss AS
SELECT
    h.parcel_dim_id,
    p.parcel_id,
    h.date_id AS harvest_date,
    h.harvest_kg,
    h.sold_kg,
    ROUND((h.harvest_kg - h.sold_kg) / NULLIF(h.harvest_kg, 0), 4) AS taux_perte
FROM agri_dw.fact_harvest h
JOIN agri_dw.dim_parcel p ON p.parcel_dim_id = h.parcel_dim_id;

-- Efficience irrigation
CREATE OR REPLACE VIEW agri_dw.kpi_irrigation_efficiency AS
SELECT
    p.parcel_dim_id,
    p.parcel_id,
    SUM(h.harvest_kg) AS total_rendement_kg,
    SUM(i.water_volume_m3) AS total_volume_eau_m3,
    ROUND(SUM(h.harvest_kg) / NULLIF(SUM(i.water_volume_m3), 0), 4) AS efficience_irrigation
FROM agri_dw.dim_parcel p
JOIN agri_dw.fact_harvest h ON h.parcel_dim_id = p.parcel_dim_id
JOIN agri_dw.fact_irrigation i ON i.parcel_dim_id = p.parcel_dim_id
GROUP BY p.parcel_dim_id, p.parcel_id;