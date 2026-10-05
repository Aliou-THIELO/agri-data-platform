# Module NoSQL (MongoDB)

Ce dossier contient l'initialisation de la couche MongoDB de la plateforme `agri-data-platform`.

## 1. Rôle et collections

MongoDB indexe les données temporelles de la plateforme. Elles sont chargées depuis la couche Silver par Apache NiFi (`PutMongoRecord`), en parallèle du chargement PostgreSQL (Gold). La base utilisée est `agri_logs`.

| Collection | Contenu | Documents |
|---|---|---|
| `weather_readings` | Relevés météo par zone et par date | 717 |
| `irrigation_readings` | Relevés d'irrigation par parcelle et par horodatage | 6910 |

Ces comptes sont identiques à ceux de `fact_weather` et `fact_irrigation` dans PostgreSQL.

## 2. Pourquoi MongoDB plutôt qu'ELK

Le projet exige l'indexation de données temporelles à relevés fréquents. MongoDB a été retenu plutôt que la stack ELK : un seul service léger à ajouter au `docker-compose.yml` (contre trois pour ELK), des documents JSON qui correspondent directement aux enregistrements NiFi, et des index composites suffisants pour les requêtes du projet.

## 3. Indexation

Le script `init_indexes.js` crée deux index composites, avec la période la plus récente en premier :

- `idx_zone_date` sur `{ zone: 1, date: -1 }` (`weather_readings`)
- `idx_parcel_timestamp` sur `{ parcel_id: 1, timestamp: -1 }` (`irrigation_readings`)

Le script est idempotent : `createIndex` ne fait rien si l'index existe déjà avec la même définition. Il affiche ensuite les comptes de documents et la liste des index pour vérification.

## 4. Exécution

Les identifiants sont ceux du fichier `.env` (utilisateur `agri_user`, mot de passe dans `<MONGO_PASSWORD>`).

```bash
cat mongo/init_indexes.js | docker exec -i agri_mongo mongosh "mongodb://agri_user:<MONGO_PASSWORD>@localhost:27017/agri_logs"
```

Sous PowerShell, remplacer `cat` par `Get-Content`.
