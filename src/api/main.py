from fastapi import FastAPI
from db import get_dict_connection

from typing import Optional
from datetime import datetime

app = FastAPI(title="API Gestion Intelligente de l'Énergie")

@app.get("/sites")
def lister_sites():
    conn, cur = get_dict_connection()
    cur.execute("SELECT id, nom, echelle FROM sites ORDER BY id;")
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    return resultats


@app.get("/mesures")
def lister_mesures(
    site_id: int,
    debut: Optional[datetime] = None,
    fin: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
):
    conn, cur = get_dict_connection()

    requete = "SELECT id, site_id, timestamp, valeur_kwh FROM mesures WHERE site_id = %s"
    parametres = [site_id]

    if debut:
        requete += " AND timestamp >= %s"
        parametres.append(debut)
    if fin:
        requete += " AND timestamp <= %s"
        parametres.append(fin)

    requete += " ORDER BY timestamp LIMIT %s OFFSET %s"
    parametres.extend([limit, offset])

    cur.execute(requete, parametres)
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    return resultats

@app.get("/anomalies")
def lister_anomalies(site_id: Optional[int] = None):
    conn, cur = get_dict_connection()

    requete = """
        SELECT a.id, m.site_id, m.timestamp, m.valeur_kwh, a.methode, a.score, a.detectee_le
        FROM anomalies a
        JOIN mesures m ON m.id = a.mesure_id
    """
    parametres = []

    if site_id:
        requete += " WHERE m.site_id = %s"
        parametres.append(site_id)

    requete += " ORDER BY m.timestamp"

    cur.execute(requete, parametres)
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    return resultats


@app.get("/previsions")
def lister_previsions(site_id: int):
    conn, cur = get_dict_connection()
    cur.execute(
        "SELECT id, site_id, horizon_timestamp, valeur_prevue, date_calcul "
        "FROM previsions WHERE site_id = %s ORDER BY horizon_timestamp",
        [site_id]
    )
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    return resultats