import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Gestion Intelligente de l'Énergie", layout="wide")
st.title("Gestion Intelligente de l'Énergie")

sites = requests.get(f"{API_URL}/sites").json()
noms_sites = {s["nom"]: s["id"] for s in sites}

onglet_ensemble, onglet_detail = st.tabs(["Vue d'ensemble", "Vue détaillée par site"])

# --- Onglet 1 : vue d'ensemble ---
with onglet_ensemble:
    st.subheader("Consommation récente par site (30 derniers jours)")

    fig_ensemble = go.Figure()
    resume_anomalies = []

    for site in sites:
        mesures_site = requests.get(
            f"{API_URL}/mesures", params={"site_id": site["id"], "limit": 24 * 30}
        ).json()
        df_site = pd.DataFrame(mesures_site)
        df_site["timestamp"] = pd.to_datetime(df_site["timestamp"])

        fig_ensemble.add_trace(go.Scatter(
            x=df_site["timestamp"], y=df_site["valeur_kwh"],
            mode="lines", name=site["nom"]
        ))

        anomalies_site = requests.get(
            f"{API_URL}/anomalies", params={"site_id": site["id"]}
        ).json()
        resume_anomalies.append({"Site": site["nom"], "Anomalies détectées (total)": len(anomalies_site)})

    fig_ensemble.update_layout(xaxis_title="Date", yaxis_title="kWh")
    st.plotly_chart(fig_ensemble, use_container_width=True)

    st.subheader("Résumé des anomalies par site")
    st.dataframe(pd.DataFrame(resume_anomalies), use_container_width=True)

# --- Onglet 2 : vue détaillée (code de l'étape 26, inchangé) ---
with onglet_detail:
    site_choisi = st.selectbox("Choisir un site", list(noms_sites.keys()))
    site_id = noms_sites[site_choisi]

    mesures = requests.get(f"{API_URL}/mesures", params={"site_id": site_id, "limit": 24 * 30}).json()
    df_mesures = pd.DataFrame(mesures)
    df_mesures["timestamp"] = pd.to_datetime(df_mesures["timestamp"])

    anomalies = requests.get(f"{API_URL}/anomalies", params={"site_id": site_id}).json()
    df_anomalies = pd.DataFrame(anomalies)

    previsions = requests.get(f"{API_URL}/previsions", params={"site_id": site_id}).json()
    df_previsions = pd.DataFrame(previsions)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_mesures["timestamp"], y=df_mesures["valeur_kwh"],
        mode="lines", name="Consommation"
    ))

    if not df_anomalies.empty:
        df_anomalies["timestamp"] = pd.to_datetime(df_anomalies["timestamp"])
        df_anomalies_visibles = df_anomalies[df_anomalies["timestamp"] >= df_mesures["timestamp"].min()]
        fig.add_trace(go.Scatter(
            x=df_anomalies_visibles["timestamp"], y=df_anomalies_visibles["valeur_kwh"],
            mode="markers", name="Anomalies", marker=dict(color="red", size=8)
        ))

    if not df_previsions.empty:
        df_previsions["horizon_timestamp"] = pd.to_datetime(df_previsions["horizon_timestamp"])
        fig.add_trace(go.Scatter(
            x=df_previsions["horizon_timestamp"], y=df_previsions["valeur_prevue"],
            mode="lines", name="Prévision (7 jours)", line=dict(dash="dash")
        ))

    fig.update_layout(title=f"Consommation — {site_choisi}", xaxis_title="Date", yaxis_title="kWh")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Anomalies détectées")
    if df_anomalies.empty:
        st.info("Aucune anomalie détectée pour ce site.")
    else:
        st.dataframe(
            df_anomalies[["timestamp", "valeur_kwh", "score"]].sort_values("timestamp", ascending=False),
            use_container_width=True
        )