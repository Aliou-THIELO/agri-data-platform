# Agri Data Platform

**Plateforme Data Engineering de bout en bout pour l'aide à la décision agricole**

*Projet Force-N — Certificat Data Engineering*

---

## 1. Vue d'ensemble

Agri Data Platform est une plateforme de données locale conçue pour intégrer des données agricoles hétérogènes et les transformer en jeux de données analytiques et en indicateurs d'aide à la décision.

Le projet simule l'environnement de données d'une exploitation maraîchère où les données de production, d'irrigation, de météo, de capteurs et de ventes sont réparties sur plusieurs sources.

L'objectif est d'implémenter un pipeline de données reproductible couvrant :

`génération des données → validation → ingestion → stockage → transformation → analyse → visualisation`

La plateforme est conçue pour fonctionner en local via Docker Compose.

## 2. Problématique métier

Les données opérationnelles agricoles sont souvent cloisonnées dans des fichiers CSV, des relevés manuels et des données de capteurs.

Ce cloisonnement rend difficile :

- le suivi de l'efficience de l'irrigation ;
- la comparaison de la productivité des parcelles ;
- l'analyse de la performance des cultures ;
- l'identification des pertes post-récolte ;
- la corrélation entre production et conditions environnementales.

La plateforme fournit un flux de données centralisé pour appuyer ces analyses.

**Utilisateurs cibles**
- Responsables d'exploitation
- Techniciens agricoles
- Conseillers de coopérative

**Domaines de décision**
- Gestion de l'irrigation
- Analyse de production et de rendement
- Performance des parcelles
- Suivi des pertes post-récolte

## 3. Architecture

L'architecture cible est la suivante :

```
                   SOURCES DE DONNÉES
                          │
          ┌───────────────┼────────────────┐
          │               │                │
       CSV/JSON          Météo           Capteurs
          │            (simulée)            │
          └───────────────┼────────────────┘
                          ▼
                 Validation des données
                       Python
                    /           \
              valide              invalide
                │                   │
                ▼                   ▼
             data/raw         data/quarantine
                │
                ▼
           Apache NiFi
                │
        ┌───────┼────────┐
        │       │        │
        ▼       ▼        ▼
      MinIO PostgreSQL MongoDB
      Data     Data       Logs /
      Lake     Warehouse  données temporelles
                 │
                 ▼
               Grafana
                 │
                 ▼
     Indicateurs d'aide à la décision
```

Cette architecture sépare clairement les responsabilités de la plateforme :

| Couche | Technologie | Responsabilité |
|---|---|---|
| Génération des données | Python | Générer des jeux de données de test réalistes et entièrement synthétiques |
| Validation des données | Pydantic | Valider les structures entrantes |
| Intégration | Apache NiFi | Ingérer, router et transformer les données |
| Data Lake | MinIO | Stocker les jeux de données bruts |
| Data Warehouse | PostgreSQL | Stocker les données analytiques structurées |
| Données opérationnelles / temporelles | MongoDB | Stocker les logs et données temporelles |
| Visualisation | Grafana | Exposer les indicateurs d'aide à la décision |
| Environnement d'exécution | Docker Compose | Environnement local reproductible |
| Gestion de versions | Git | Suivre les modifications et l'historique technique |

## 4. Flux de données

La plateforme traite plusieurs catégories de données.

**Données agricoles**
- Parcelles
- Cultures
- Production
- Récoltes
- Ventes
- Pertes post-récolte

**Données environnementales**
- Température
- Pluviométrie
- Humidité
- Rayonnement solaire
- Vitesse du vent

**Données d'irrigation**
- Horodatage de l'irrigation
- Parcelle
- Volume d'eau
- Humidité du sol

**Données capteurs**

Mesures IoT et logs opérationnels simulés.

Toutes les données utilisées par la plateforme sont générées localement et sont entièrement synthétiques — aucune source de données externe ou tierce n'est utilisée, conformément à l'exigence de confidentialité de la fiche projet.

## 5. Stratégie de qualité des données

La qualité des données est vérifiée avant intégration dans le pipeline principal.

Les enregistrements valides sont dirigés vers le flux d'ingestion :

```
data/raw/
```

Les enregistrements ne respectant pas les règles de structure ou de validation sont isolés dans :

```
data/quarantine/
```

Cela empêche les enregistrements invalides d'entrer silencieusement dans le pipeline analytique et rend les échecs de qualité des données observables et récupérables.

La couche de validation utilise des schémas Pydantic.

## 6. Data Warehouse

PostgreSQL implémente un modèle dimensionnel basé sur un schéma en étoile.

**Dimensions**
- `dim_date`
- `dim_parcelle`
- `dim_culture`

**Tables de faits**
- `fact_irrigation`
- `fact_meteo`
- `fact_harvest`

Le modèle est conçu pour supporter des requêtes analytiques par :

- date ;
- parcelle ;
- culture ;
- irrigation ;
- production ;
- ventes.

Le modèle physique final est documenté dans `sql/migrations/`.

## 7. Indicateurs d'aide à la décision (KPIs)

La plateforme expose au minimum trois indicateurs agricoles.

| KPI | Formule |
|---|---|
| Efficience de l'irrigation | `rendement_kg / volume_eau_m3` |
| Taux de perte post-récolte | `(recolte_kg - vendu_kg) / recolte_kg` |
| Productivité de la parcelle | `rendement_kg / surface_m2` |

Les calculs de KPI sont principalement implémentés sous forme de vues PostgreSQL pour la consommation analytique, avec Python utilisé le cas échéant pour la validation ou des calculs complémentaires.

## 8. Choix technologiques

**Apache NiFi**
Utilisé comme couche centrale d'intégration et d'orchestration car le projet se concentre sur l'ingestion, le routage et la transformation légère de sources de données hétérogènes.

**MinIO**
Utilisé comme couche de stockage objet locale pour les jeux de données bruts.

**PostgreSQL**
Utilisé comme entrepôt analytique car le projet nécessite une analyse relationnelle structurée et une modélisation dimensionnelle.

**MongoDB**
Sélectionné à la place de la stack ELK afin de garder la plateforme locale ciblée et de réduire la complexité de l'infrastructure, tout en fournissant un stockage dédié pour les enregistrements temporels et les logs opérationnels. La décision ELK vs MongoDB et ses compromis sont documentés dans le rapport technique.

**Grafana**
Utilisé comme couche de visualisation pour les tableaux de bord finaux d'aide à la décision.

**Docker Compose**
Utilisé pour rendre l'environnement complet reproductible localement.

## 9. Structure du dépôt

```
agri-data-platform/
├── .github/workflows/
├── data/
│   ├── generator/
│   ├── raw/
│   └── quarantine/
├── src/
│   ├── validation/
│   └── kpi/
├── nifi/
│   └── flows/
├── sql/
│   ├── migrations/
│   └── views/
├── grafana/
│   └── dashboards/
├── mongo/
├── tests/
├── docs/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

## 10. Reproductibilité

La plateforme complète est exécutable localement via Docker Compose.

Commande de démarrage :

```
docker compose up -d
```

Le README documente :

- les prérequis ;
- la configuration de l'environnement ;
- les ports des services ;
- la procédure de démarrage ;
- la génération des données ;
- l'exécution du pipeline ;
- l'initialisation de la base de données ;
- l'accès au tableau de bord ;
- le dépannage.

## 11. Sources de données

Le projet utilise uniquement des données générées, entièrement synthétiques. Aucune source de données externe ou tierce n'est utilisée — cela permet de garder la plateforme reproductible localement et d'éviter toute ambiguïté sur la confidentialité des données, conformément à la fiche projet.

## 12. Tests & qualité des données

Le projet introduit progressivement :

- des tests unitaires avec pytest ;
- de la validation de schéma ;
- des scénarios de données invalides ;
- des tests de calcul de KPI ;
- de la validation de pipeline ;
- du linting ;
- de l'intégration continue avec GitHub Actions.

Les tests sont traités comme faisant partie du workflow d'ingénierie, et non comme une étape finale.

## 13. Statut du projet

**Statut : en cours de développement**

Phase actuelle :

- [x] Initialisation du dépôt
- [x] Structure du projet
- [x] Configuration Git
- [ ] Génération des données
- [ ] Validation des données
- [ ] Infrastructure Docker
- [ ] Modèle dimensionnel PostgreSQL
- [ ] Pipelines Apache NiFi
- [ ] Intégration MinIO
- [ ] Intégration MongoDB
- [ ] Tableau de bord Grafana
- [ ] Tests automatisés
- [ ] Intégration continue (CI)
- [ ] Documentation technique

La checklist est mise à jour au fur et à mesure de l'implémentation et de la validation de chaque composant.

## 14. Principes d'ingénierie

- **Reproductibilité** — l'environnement doit être exécutable localement.
- **Séparation des responsabilités** — génération, validation, intégration, stockage et visualisation restent des responsabilités distinctes.
- **Qualité des données** — les enregistrements invalides doivent être observables plutôt que silencieusement écartés.
- **Gestion de versions** — les modifications sont développées de manière incrémentale et suivies via Git.
- **Testabilité** — les composants sont validés avant d'être intégrés.
- **Observabilité** — les échecs du pipeline et du traitement des données doivent être traçables.
- **Documentation** — les décisions techniques et les limites sont explicitement documentées.

## 15. Limites

Ce projet utilise des données agricoles simulées et ne reproduit donc pas toute la complexité d'un système d'information agricole en production.

Les KPIs sont des indicateurs d'aide à la décision et ne doivent pas être interprétés comme des recommandations agronomiques autonomes.

Les simplifications et hypothèses sont documentées dans le rapport technique.

## 16. Contexte du projet

Ce projet est développé dans le cadre du projet de certification Data Engineering Force-N.

Il vise à démontrer un workflow Data Engineering de bout en bout, de l'ingestion de données hétérogènes jusqu'au stockage analytique et à la visualisation orientée décision.