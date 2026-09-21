from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from api.db import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def charger_sites(conn):
    df = pd.read_csv(DATA_DIR / "sites.csv")
    with conn.cursor() as cur:
        # on force les id d'origine pour que site_id corresponde dans mesures
        execute_values(
            cur,
            "INSERT INTO sites (id, nom, echelle) VALUES %s ON CONFLICT (id) DO NOTHING",
            df[["id", "nom", "echelle"]].values.tolist()
        )
    conn.commit()
    print(f"{len(df)} sites insérés (ou déjà présents)")

def charger_mesures(conn):
    df = pd.read_csv(DATA_DIR / "mesures_synthetiques.csv")
    valeurs = list(df[["site_id", "timestamp", "valeur_kwh"]].itertuples(index=False, name=None))

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO mesures (site_id, timestamp, valeur_kwh) VALUES %s "
            "ON CONFLICT (site_id, timestamp) DO NOTHING",
            valeurs
        )
    conn.commit()
    print(f"{len(df)} mesures insérées (ou déjà présentes)")

if __name__ == "__main__":
    conn = get_connection()
    charger_sites(conn)
    charger_mesures(conn)
    conn.close()