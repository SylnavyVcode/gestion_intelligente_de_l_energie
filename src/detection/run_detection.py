from pathlib import Path
import sys
import pandas as pd
# Remplace par des imports absolus depuis la racine :
from src.api.db import get_dict_connection
from src.detection.detection import calculer_facteurs_profil, detecter_anomalies

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def main():
    mesures = pd.read_csv(DATA_DIR / "mesures_synthetiques.csv", parse_dates=["timestamp"])
    sites_info = pd.read_csv(DATA_DIR / "sites.csv")
    facteur_horaire, facteur_hebdo = calculer_facteurs_profil(DATA_DIR / "conso_horaire_propre.csv")

    conn, cur = get_dict_connection()

    total_inserees = 0
    for _, site_row in sites_info.iterrows():
        site_id = site_row["id"]
        echelle = site_row["echelle"]

        mesures_site = mesures[mesures["site_id"] == site_id].set_index("timestamp")
        detections = detecter_anomalies(mesures_site, echelle, facteur_horaire, facteur_hebdo)

        for ts, ligne in detections.iterrows():
            cur.execute(
                "SELECT id FROM mesures WHERE site_id = %s AND timestamp = %s",
                (int(site_id), ts)
            )
            mesure_id = cur.fetchone()["id"]

            cur.execute(
                "INSERT INTO anomalies (mesure_id, methode, score) VALUES (%s, %s, %s)",
                (mesure_id, "residu_zscore_fenetre_glissante", float(ligne["score"]))
            )
            total_inserees += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"{total_inserees} anomalies insérées en base")

if __name__ == "__main__":
    main()