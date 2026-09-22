from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.api.db import get_dict_connection
from src.forecast.forecast import nettoyer_serie, entrainer_et_prevoir

HORIZON = 24 * 7  # prévision à 7 jours, conforme au cas d'usage défini en Phase 0

def main():
    conn, cur = get_dict_connection()

    cur.execute("SELECT id FROM sites ORDER BY id;")
    site_ids = [row["id"] for row in cur.fetchall()]

    total_previsions = 0
    for site_id in site_ids:
        cur.execute(
            "SELECT timestamp, valeur_kwh FROM mesures WHERE site_id = %s ORDER BY timestamp",
            (site_id,)
        )
        lignes = cur.fetchall()
        serie = pd.Series(
            [float(l["valeur_kwh"]) for l in lignes],
            index=pd.to_datetime([l["timestamp"] for l in lignes])
        ).asfreq("h")

        cur.execute(
            "SELECT m.timestamp FROM anomalies a JOIN mesures m ON m.id = a.mesure_id WHERE m.site_id = %s",
            (site_id,)
        )
        timestamps_anomalies = [r["timestamp"] for r in cur.fetchall()]

        serie_propre = nettoyer_serie(serie, timestamps_anomalies)
        previsions = entrainer_et_prevoir(serie_propre, horizon=HORIZON)

        for ts, valeur in previsions.items():
            cur.execute(
                "INSERT INTO previsions (site_id, horizon_timestamp, valeur_prevue) VALUES (%s, %s, %s)",
                (site_id, ts, float(valeur))
            )
            total_previsions += 1

        print(f"Site {site_id} : {len(previsions)} prévisions générées")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nTotal : {total_previsions} prévisions insérées")

if __name__ == "__main__":
    main()