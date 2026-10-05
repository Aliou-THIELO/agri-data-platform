# Agri Data Platform

**Plateforme Data Engineering de bout en bout pour l'aide à la décision agricole**

*Projet Force-N — Certificat Data Engineering — Projet 5 : Agriculture maraîchère*

---

## 1. Vue d'ensemble

Agri Data Platform est une plateforme de données locale conçue pour intégrer des données agricoles hétérogènes et les transformer en jeux de données analytiques et en indicateurs d'aide à la décision.

Le projet simule l'environnement de données d'une exploitation maraîchère au Sénégal, où les données de parcelles, d'irrigation, de météo et de ventes/récoltes sont réparties sur plusieurs sources.

Le pipeline couvre l'ensemble de la chaîne :

`génération des données → validation qualité (Python) → ingestion brute (Bronze) → nettoyage et filtrage (Silver) → chargement analytique (Gold) → indexation temporelle → visualisation`

La plateforme fonctionne entièrement en local via Docker Compose.

## 2. Problématique métier

Les données opérationnelles agricoles sont souvent cloisonnées dans des fichiers CSV, des relevés manuels et des données de capteurs. Ce cloisonnement rend difficile :

- le suivi de l'efficience de l'irrigation ;
- la comparaison de la productivité des parcelles ;
- l'identification des pertes post-récolte ;
- la corrélation entre production et conditions environnementales.

La plateforme fournit un flux de données centralisé pour appuyer ces analyses.

**Utilisateurs cibles** : responsables d'exploitation, techniciens agricoles, conseillers de coopérative.

**Domaines de décision** : gestion de l'irrigation, analyse de production et de rendement, performance des parcelles, suivi des pertes post-récolte.

## 3. Architecture

Architecture medallion à trois zones (Bronze / Silver / Gold). Deux mécanismes de contrôle qualité, indépendants et complémentaires, coexistent :

- **Niveau génération (Python/Pydantic)** : valide la conformité structurelle des données générées, indépendamment du pipeline NiFi (`data/raw/` vs `data/quarantine/`). Démontre la qualité dès la source.
- **Niveau pipeline (NiFi, Flow 2)** : applique son propre filtrage des anomalies métier lors du passage Bronze → Silver, sur les données brutes non filtrées (`data/generated/`). Démontre la qualité orchestrée par l'outil d'intégration, conformément à l'exigence « NiFi comme outil principal d'intégration ».


```
                   SOURCES DE DONNÉES (générées, 100% synthétiques)
                          │
          ┌───────────────┼────────────────┬────────────────┐
          │               │                │                │
       Parcelles        Météo          Irrigation     Récoltes/Ventes
          │               │                │                │
          └───────────────┴────────────────┴────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼

  Validation Pydantic (Python)     Données brutes (data/generated/)
  data/raw/ ── data/quarantine/            │
  (contrôle qualité source,                ▼
  démonstratif, décorrélé          Apache NiFi (Flow 1 — Bronze)
  du pipeline NiFi)                        │
                                            ▼
                          MinIO — agriculture-raw/bronze/<entité>/
                                            │
                                            ▼
                       Apache NiFi (Flow 2 — typage, nettoyage, filtrage)
                                            │
                          ┌─────────────────┴─────────────────┐
                          ▼                                   ▼
                MinIO — silver/<entité>/          MinIO — silver_rejected/<entité>/
                                            │            (anomalies tracées)
                                            ▼
                          Apache NiFi (Flow 3 — chargement Gold)
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                                   ▼
                    PostgreSQL                            MongoDB
                  (schéma étoile)              (weather_readings, irrigation_readings)
                          │
                          ▼
                       Grafana
                          │
                          ▼
             Indicateurs d'aide à la décision (KPIs)
```


| Couche | Technologie | Responsabilité |
|---|---|---|
| Génération des données | Python | Jeux de données de test réalistes, entièrement synthétiques |
| Validation source (démonstrative) | Pydantic | Valider la conformité structurelle dès la génération, isoler les anomalies (`data/quarantine/`) |
| Intégration et qualité pipeline | Apache NiFi | Ingérer, typer, nettoyer, filtrer les anomalies métier, router, charger |
| Data Lake | MinIO | Stocker les jeux de données bruts (Bronze), nettoyés (Silver) et rejetés (Silver rejected) |
| Data Warehouse | PostgreSQL | Stocker les données analytiques structurées (Gold, schéma en étoile) |
| Données temporelles | MongoDB | Indexer les relevés météo et irrigation |
| Visualisation | Grafana | Exposer les indicateurs d'aide à la décision |
| Environnement d'exécution | Docker Compose | Environnement local reproductible |
| Gestion de versions | Git | Suivre les modifications et l'historique technique |

## 4. Flux de données

Quatre entités, générées localement, 100 % synthétiques (aucune source externe, conformément à la fiche projet) :

| Entité | Format Bronze | Colonnes principales |
|---|---|---|
| **Parcelles** | CSV | `parcel_id`, `zone`, `crop`, `surface_m2`, `planting_date`, `latitude`, `longitude`, `manager` |
| **Météo** | CSV | `zone`, `date`, `temperature_c`, `precipitation_mm`, `humidity_pct` |
| **Irrigation** | JSONL | `parcel_id`, `timestamp`, `water_volume_m3`, `soil_humidity_pct` |
| **Récoltes/Ventes** | CSV | `parcel_id`, `harvest_date`, `harvest_kg`, `sold_kg`, `unit_price_fcfa` |

## 5. Stratégie de qualité des données

**Niveau génération (Python/Pydantic)** : démonstratif, en parallèle du pipeline principal. Les enregistrements valides vont dans `data/raw/`, les invalides dans `data/quarantine/` (ex. `surface_m2 <= 0`, `sold_kg > harvest_kg`, `soil_humidity_pct > 100`).

**Niveau pipeline (NiFi, Flow 2)** : c'est ce flux, et non la validation Python, qui alimente réellement le data lake. Chaque entité passe par un typage strict de schéma (Avro), un nettoyage des valeurs manquantes (ex. `manager` vide → `Non renseigné`), puis un filtrage des anomalies métier via `QueryRecord`. Les enregistrements filtrés sont tracés dans `silver_rejected/` plutôt qu'écartés silencieusement.

## 6. Data Warehouse

PostgreSQL implémente un modèle dimensionnel en schéma en étoile, base `agri_db`, schéma `agri_dw`.

**Dimensions**
- `dim_zone` : référentiel fixe des 4 zones (Niayes, Vallée du Fleuve, Casamance, Sine-Saloum)
- `dim_date` : référentiel calendaire (2024–2030)
- `dim_parcel` : les parcelles, avec clé de substitution technique `parcel_dim_id` (SERIAL) séparée de la clé métier source `parcel_id` (VARCHAR unique)

**Tables de faits** (référencent les dimensions via `parcel_dim_id`, `zone_id`, `date_id`)
- `fact_irrigation`
- `fact_weather`
- `fact_harvest`

Ordre de chargement (Flow 3) : `dim_zone` → `dim_date` → `dim_parcel` → tables de faits, avec lookup de `parcel_dim_id` / `zone_id` / `date_id` avant chaque insertion.

Volumes chargés : `dim_zone` 4, `dim_date` 2557, `dim_parcel` 23, `fact_weather` 717, `fact_harvest` 21, `fact_irrigation` 6910.

Le modèle physique est documenté dans `sql/migrations/`.

## 7. Indicateurs d'aide à la décision (KPIs)

Les KPIs sont exposés sous forme de vues PostgreSQL et visualisés dans Grafana.

| KPI | Formule | Colonnes sources |
|---|---|---|
| Efficience de l'irrigation | `rendement_kg / volume_eau_m3` | `harvest_kg`, `water_volume_m3` |
| Taux de perte post-récolte | `(recolte_kg - vendu_kg) / recolte_kg` | `harvest_kg`, `sold_kg` |
| Productivité de la parcelle | `rendement_kg / surface_m2` | `harvest_kg`, `surface_m2` |

## 8. Choix technologiques

**Apache NiFi** : couche centrale d'intégration et d'orchestration (ingestion, typage, nettoyage, filtrage des anomalies, chargement), uniquement via des processeurs standards, sans ETL Python custom.

**MinIO** : stockage objet local S3-compatible pour les zones Bronze, Silver et Silver rejected.

**PostgreSQL** : entrepôt analytique relationnel, modélisation dimensionnelle en étoile.

**MongoDB** : retenu à la place de la stack ELK pour indexer les données temporelles (météo, irrigation) : stockage document flexible, complémentaire de PostgreSQL plutôt que substitutif. Détail dans `mongo/README.md`. Le détail des compromis ELK vs MongoDB est développé dans le rapport technique.

**Grafana** : visualisation des KPIs.

**Docker Compose** : reproductibilité de l'environnement local (5 services : PostgreSQL, MinIO, MongoDB, NiFi, Grafana).

## 9. Structure du dépôt

```
agri-data-platform/
├── .github/
│   └── workflows/
├── data/
│   ├── generator/
│   ├── generated/
│   ├── raw/
│   └── quarantine/
├── src/
│   └── validation/
├── nifi/
│   └── flows/          # export JSON des flows
├── sql/
│   └── migrations/
├── grafana/            
├── mongo/
│   ├── init_indexes.js
│   └── README.md
├── tests/
├── docs/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

## 10. Reproductibilité

```bash
cp .env.example .env      # renseigner les identifiants
docker compose up -d
```

Services exposés : PostgreSQL (5433), MinIO (9000/9001), MongoDB (27018), NiFi (8443), Grafana (3000).

Prérequis additionnels :
- le driver JDBC PostgreSQL (`postgresql-42.7.4.jar`) doit être présent dans `/opt/nifi/nifi-current/lib/` du conteneur NiFi. Il n'est pas persisté entre redémarrages (limite connue, voir section 14) ;
- les index MongoDB se créent avec `mongo/init_indexes.js` (voir `mongo/README.md`).

## 11. Sources de données

Données 100 % générées et synthétiques, aucune source externe, conformément à la fiche projet.

## 12. Statut du projet

**Statut : en cours de finalisation**

- [x] Initialisation du dépôt et structure du projet
- [x] Génération des données (4 entités, Python)
- [x] Validation des données (Pydantic, quarantaine fonctionnelle)
- [x] Infrastructure Docker (5 services)
- [x] Modèle dimensionnel PostgreSQL (schéma validé, 6 tables)
- [x] Flow NiFi 1 : Bronze (4 entités)
- [x] Flow NiFi 2 : nettoyage, typage, filtrage, quarantaine `silver_rejected` (4 entités)
- [x] Flow NiFi 3 : chargement Gold PostgreSQL (4 entités)
- [x] Intégration MongoDB (indexation weather/irrigation, index documentés)
- [ ] Tableau de bord Grafana (3 KPIs créés, export JSON et améliorations en cours)
- [ ] Rapport technique et présentation finale

## 13. Principes d'ingénierie

- **Reproductibilité** : environnement exécutable localement via Docker Compose.
- **Séparation des responsabilités** : génération, validation, intégration, stockage et visualisation restent distincts.
- **Qualité des données à deux niveaux** : contrôle source (Pydantic) et contrôle pipeline (NiFi), tous deux observables, jamais silencieux.
- **Gestion de versions** : développement incrémental, un commit = une phase testée.
- **Documentation** : décisions techniques et limites explicitement documentées.

## 14. Limites connues

- Données agricoles simulées : ne reproduit pas toute la complexité d'un système d'information agricole réel.
- Les KPIs sont des indicateurs d'aide à la décision, pas des recommandations agronomiques autonomes.
- Le driver JDBC PostgreSQL, installé manuellement dans le conteneur NiFi, n'est pas persisté entre redémarrages (pas de volume dédié). À réinstaller après un `docker compose down`.
- Les flows de chargement Gold ne sont pas idempotents : relancer un flow Flow 3 sans `TRUNCATE` préalable de la table de faits cible ajoute des doublons.
- Identifiants Grafana actuellement en dur dans `docker-compose.yml` plutôt que via `.env`.
- Filtrage des anomalies basé sur des règles de plage simples (`surface_m2`, `temperature_c`, `soil_humidity_pct`, `sold_kg`).
- La validation Pydantic (`data/quarantine/`) et le filtrage NiFi (`silver_rejected/`) appliquent des règles équivalentes de façon indépendante, sans lien opérationnel.
- Les identifiants de parcelles (`parcel_id`) sont générés avec `uuid4()`, non reproductibles d'une génération à l'autre : régénérer les données exige de recharger toute la chaîne Parcel avant les autres entités.

## 15. Perspectives d'amélioration

- Réutilisation des scripts SQL (conçus de façon idempotente) dans un futur orchestrateur (Airflow, Spark).
- Volume Docker persistant pour les dépendances JDBC de NiFi.
- Externalisation complète des identifiants (Grafana, PostgreSQL) via variables d'environnement.
- Unification des deux mécanismes de contrôle qualité (Pydantic et NiFi).
- Génération des `parcel_id` avec une graine fixe, pour des jeux de données reproductibles.
- Chargement Gold idempotent (UPSERT) pour permettre de relancer un flow sans doublons.

## 16. Contexte du projet

Ce projet est développé dans le cadre de la certification Data Engineering Force-N. Il vise à démontrer un workflow Data Engineering de bout en bout, de l'ingestion de données hétérogènes jusqu'au stockage analytique et à la visualisation orientée décision.

## 17. Auteur

Aliou THIELO — [github.com/Aliou-THIELO](https://github.com/Aliou-THIELO)


