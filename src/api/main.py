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