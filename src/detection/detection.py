import pandas as pd

FENETRE = 24 * 7
SEUIL = 5

def calculer_facteurs_profil(chemin_csv_horaire: str):
    df = pd.read_csv(chemin_csv_horaire, index_col="timestamp", parse_dates=True)
    conso = df[["Global_active_power"]].rename(columns={"Global_active_power": "conso_kw"})
    conso["heure"] = conso.index.hour
    conso["jour_semaine"] = conso.index.dayofweek

    profil_horaire = conso.groupby("heure")["conso_kw"].mean()
    profil_hebdo = conso.groupby("jour_semaine")["conso_kw"].mean()
    moyenne_globale = conso["conso_kw"].mean()

    return profil_horaire / moyenne_globale, profil_hebdo / moyenne_globale


def detecter_anomalies(mesures_site: pd.DataFrame, echelle: float, facteur_horaire, facteur_hebdo) -> pd.DataFrame:
    df = mesures_site.copy()
    df["heure"] = df.index.hour
    df["jour_semaine"] = df.index.dayofweek
    df["valeur_attendue"] = (
        facteur_horaire[df["heure"]].values
        * facteur_hebdo[df["jour_semaine"]].values
        * echelle
    )
    df["residu"] = df["valeur_kwh"] - df["valeur_attendue"]
    df["residu_moyenne"] = df["residu"].rolling(FENETRE, min_periods=24).mean()
    df["residu_ecart_type"] = df["residu"].rolling(FENETRE, min_periods=24).std()

    borne_haute = df["residu_moyenne"] + SEUIL * df["residu_ecart_type"]
    borne_basse = df["residu_moyenne"] - SEUIL * df["residu_ecart_type"]

    df["anomalie"] = (df["residu"] > borne_haute) | (df["residu"] < borne_basse)
    ecart_normalise = (df["residu"] - df["residu_moyenne"]) / df["residu_ecart_type"]
    df["score"] = ecart_normalise.abs()

    return df[df["anomalie"]]