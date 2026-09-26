-- Peuplement de la dimension calendaire (dim_date)
-- Idempotent : peut etre relance sans risque de duplication (ON CONFLICT DO NOTHING)
-- Plage large (2024-2030) pour accompagner l'ajout futur de donnees historiques
-- Resultat attendu : 2557 lignes

INSERT INTO agri_dw.dim_date (date_id, year, month, day, quarter, day_of_week)
SELECT
    d::date AS date_id,
    EXTRACT(YEAR FROM d)::smallint AS year,
    EXTRACT(MONTH FROM d)::smallint AS month,
    EXTRACT(DAY FROM d)::smallint AS day,
    EXTRACT(QUARTER FROM d)::smallint AS quarter,
    TO_CHAR(d, 'Day') AS day_of_week
FROM generate_series('2024-01-01'::date, '2030-12-31'::date, '1 day'::interval) AS d
ON CONFLICT (date_id) DO NOTHING;