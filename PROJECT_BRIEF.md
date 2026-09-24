# PROJECT_BRIEF — Gestion Intelligente de l'Énergie

## Cas d'usage

Un gestionnaire de bâtiment suit la consommation électrique de plusieurs sites, reçoit des alertes en cas d'anomalie, et dispose d'une prévision à 7 jours pour anticiper les pics.

## Résumé

Ce projet mobilise 6 compétences (SQL, API, analyse, dashboard, détection, prédiction) via un pipeline simple : données → base SQL → API FastAPI → détection d'anomalies → prévision → dashboard. L'architecture réutilise un stack déjà connu (FastAPI + Supabase) pour minimiser la friction technique et concentrer l'effort sur la vraie valeur ajoutée : la détection et la prévision.

## Source de données

Pas de vrais capteurs disponibles, donc combinaison de deux sources :
- **UCI "Individual Household Electric Power Consumption"** (mesures minute par minute sur ~4 ans, dataset réel) — utilisé pour extraire un profil de consommation réaliste (facteurs horaires et hebdomadaires).
- **Données synthétiques multi-sites** générées à partir de ce profil (5 sites, 6 mois, pas horaire, bruit + anomalies injectées avec vérité terrain connue) — pour disposer d'un dashboard multi-sites riche sans dépendre d'un compteur réel unique.

## Plan d'action (9 phases)

**Phase 0 — Cadrage**
- Définir le cas d'usage (ci-dessus) et la source de données.
- Livrable : `PROJECT_BRIEF.md`.

**Phase 1 — Stack et architecture**
- Backend : FastAPI
- BDD : PostgreSQL via Supabase
- Analyse : pandas/numpy
- Prévision : lissage exponentiel Holt-Winters (`statsmodels.tsa.holtwinters.ExponentialSmoothing`)
- Dashboard : Streamlit (MVP rapide, 100% Python) — migration React envisageable en itération 2 si le temps le permet ; un projet complet vaut mieux que deux à moitié.
- Livrable : repo GitHub initialisé, structure de dossiers, schéma d'architecture.

**Phase 2 — Modélisation SQL**
- Tables : `sites`, `mesures` (FK site, timestamp, valeur_kwh), `anomalies` (FK mesure, score), `previsions` (FK site, horizon, valeur)
- Livrable : schéma SQL de création (voir README).

**Phase 3 — Ingestion**
- Script d'insertion par lots, idempotent (contrainte d'unicité `site_id, timestamp`).
- Livrable : `src/ingestion/generate_synthetic_data.py`, `src/ingestion/load_to_db.py`.

**Phase 4 — API FastAPI**
- Endpoints : `GET /sites`, `GET /mesures` (pagination), `GET /anomalies`, `GET /previsions`
- Livrable : API testée via `/docs`.

**Phase 5 — Détection d'anomalies**
- Méthode retenue : résidu (valeur observée − valeur attendue selon profil horaire/hebdomadaire) comparé à une moyenne/écart-type glissants — plutôt qu'un seuil brut, pour ne pas confondre saisonnalité normale et anomalie.
- Validation contre la vérité terrain injectée, choix du seuil documenté dans `notebooks/02_detection_exploration.ipynb`.
- Livrable : `src/detection/detection.py`, `src/detection/run_detection.py`.

**Phase 6 — Prévision**
- Holt-Winters sur l'historique par site, saisonnalité horaire (24).
- Validation par backtesting (splits glissants), jamais sur les données d'entraînement.
- Livrable : `src/forecast/forecast.py`, `src/forecast/run_forecast.py`, `notebooks/03_forecast_exploration.ipynb`.

**Phase 7 — Dashboard**
- Vue d'ensemble (tendance globale), vue par site (courbe + anomalies + bande de prévision).
- Connecté à l'API, jamais directement à la base.
- Livrable : `src/dashboard/app.py`.

**Phase 8 — Alertes** *(repoussée)*
- Email (SMTP) ou webhook Slack/Discord si anomalie sévère.
- Config via variables d'environnement, jamais de secrets en dur.

**Phase 9 — Finalisation CV/GitHub**
- README pro (contexte, capture d'écran, stack, lancement, limites connues).
- Déploiement démo (à évaluer).

## Erreurs courantes évitées

- Pas de ML avant un pipeline de données propre (nettoyage/exploration UCI en Phase 0 avant tout modèle).
- Découpage par phase (commits/branches), pas un seul gros commit final.
- Dashboard branché sur l'API, jamais directement sur la base.
- Pas de seuil fixe brut pour la détection — le résidu retire la saisonnalité normale avant de chercher l'anomalie.

## Grille d'évaluation

| Compétence | Ce qui est vérifié |
|---|---|
| Base de données (SQL) | Schéma normalisé, contrainte d'unicité, requêtes paramétrées |
| API & Backend | Endpoints cohérents, pagination, filtres |
| Analyse de données | Nettoyage justifié (interpolation temporelle), choix de méthode documenté en notebook |
| Dashboard | Lisible, connecté à l'API, informatif |
| Détection & Alertes | Méthode adaptée à la saisonnalité (résidu, pas seuil naïf) ; alertes non implémentées (Phase 8 repoussée) |
| Logique métier & Prédictions | Modèle validé par backtesting, pas sur l'entraînement |
