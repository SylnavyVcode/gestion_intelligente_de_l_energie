import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def nettoyer_serie(serie: pd.Series, timestamps_anomalies: list) -> pd.Series:
    serie_propre = serie.copy()
    serie_propre.loc[serie_propre.index.isin(timestamps_anomalies)] = np.nan
    return serie_propre.interpolate(method="time")

def entrainer_et_prevoir(serie: pd.Series, horizon: int = 24 * 7) -> pd.Series:
    modele = ExponentialSmoothing(
        serie, trend="add", seasonal="add", seasonal_periods=24
    ).fit()
    return modele.forecast(horizon)