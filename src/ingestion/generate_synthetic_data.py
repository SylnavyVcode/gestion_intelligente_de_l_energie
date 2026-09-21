from pathlib import Path
import numpy as np
import pandas as pd

np.random.seed(42)  # reproductibilité : mêmes résultats à chaque exécution

# Chemins robustes, indépendants du dossier depuis lequel tu lances le script
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# --- 1. Recalculer les profils réels (comme dans le notebook) ---
df_horaire = pd.read_csv(DATA_DIR / "conso_horaire_propre.csv", index_col="timestamp", parse_dates=True)
conso_df = df_horaire[["Global_active_power"]].rename(columns={"Global_active_power": "conso_kw"})
conso_df["heure"] = conso_df.index.hour
conso_df["jour_semaine"] = conso_df.index.dayofweek

profil_horaire = conso_df.groupby("heure")["conso_kw"].mean()
profil_hebdo = conso_df.groupby("jour_semaine")["conso_kw"].mean()
moyenne_globale = conso_df["conso_kw"].mean()

facteur_horaire = profil_horaire / moyenne_globale
facteur_hebdo = profil_hebdo / moyenne_globale

# --- 2. Définir les sites ---
sites = [
    {"id": 1, "nom": "Petit bureau",   "echelle": 2.0},
    {"id": 2, "nom": "Boutique",       "echelle": 3.5},
    {"id": 3, "nom": "Atelier",        "echelle": 6.0},
    {"id": 4, "nom": "Entrepôt",       "echelle": 10.0},
    {"id": 5, "nom": "Petit immeuble", "echelle": 15.0},
]

# --- 3. Générer les mesures sur 6 mois, pas horaire ---
dates = pd.date_range(start="2024-01-01", end="2024-06-30 23:00", freq="h")

mesures = []
for site in sites:
    for ts in dates:
        base = facteur_horaire[ts.hour] * facteur_hebdo[ts.dayofweek] * site["echelle"]
        bruit = np.random.normal(loc=0, scale=0.05 * base)  # bruit ~5% de la valeur de base
        valeur = max(base + bruit, 0)  # une consommation ne peut pas être négative
        mesures.append({"site_id": site["id"], "timestamp": ts, "valeur_kwh": round(valeur, 3)})

df_mesures = pd.DataFrame(mesures)

# --- 4. Injecter des anomalies connues ---
NB_ANOMALIES_PAR_SITE = 10
anomalies_verite = []

for site in sites:
    indices_site = df_mesures[df_mesures["site_id"] == site["id"]].index.to_numpy()
    indices_choisis = np.random.choice(indices_site, size=NB_ANOMALIES_PAR_SITE, replace=False)

    for idx in indices_choisis:
        type_anomalie = np.random.choice(["pic", "coupure"])
        valeur_originale = df_mesures.loc[idx, "valeur_kwh"]

        if type_anomalie == "pic":
            nouvelle_valeur = valeur_originale * np.random.uniform(3, 5)
        else:
            nouvelle_valeur = valeur_originale * np.random.uniform(0, 0.1)

        df_mesures.loc[idx, "valeur_kwh"] = round(nouvelle_valeur, 3)
        anomalies_verite.append({
            "site_id": site["id"],
            "timestamp": df_mesures.loc[idx, "timestamp"],
            "type": type_anomalie,
            "valeur_originale": valeur_originale,
            "valeur_injectee": round(nouvelle_valeur, 3),
        })

df_anomalies_verite = pd.DataFrame(anomalies_verite)

# --- 5. Sauvegarder ---
pd.DataFrame(sites).to_csv(DATA_DIR / "sites.csv", index=False)
df_mesures.to_csv(DATA_DIR / "mesures_synthetiques.csv", index=False)
df_anomalies_verite.to_csv(DATA_DIR / "anomalies_verite_terrain.csv", index=False)

print(f"{len(df_mesures)} mesures générées pour {len(sites)} sites")
print(f"{len(df_anomalies_verite)} anomalies injectées (ground truth)")
