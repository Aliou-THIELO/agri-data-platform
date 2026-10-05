// =============================================================
// agri-data-platform : index MongoDB (données temporelles)
// -------------------------------------------------------------
// Les collections sont alimentées par NiFi (PutMongoRecord) :
//   - weather_readings    (relevés météo par zone)
//   - irrigation_readings (relevés d'irrigation par parcelle)
// Ce script est idempotent : createIndex ne fait rien si l'index
// existe déjà avec la même définition. Relançable sans risque.
// =============================================================

const agri = db.getSiblingDB("agri_logs");

// Météo : requêtes par zone, période la plus récente d'abord
agri.weather_readings.createIndex({ zone: 1, date: -1 }, { name: "idx_zone_date" });

// Irrigation : requêtes par parcelle, période la plus récente d'abord
agri.irrigation_readings.createIndex({ parcel_id: 1, timestamp: -1 }, { name: "idx_parcel_timestamp" });

// Vérification : comptes et index présents
print("weather_readings    :", agri.weather_readings.countDocuments(), "documents");
print("irrigation_readings :", agri.irrigation_readings.countDocuments(), "documents");
printjson(agri.weather_readings.getIndexes().map(i => i.name));
printjson(agri.irrigation_readings.getIndexes().map(i => i.name));