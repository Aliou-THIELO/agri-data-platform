ALTER TABLE agri_dw.fact_irrigation
  ADD CONSTRAINT chk_soil_humidity CHECK (soil_humidity_pct BETWEEN 0 AND 100);