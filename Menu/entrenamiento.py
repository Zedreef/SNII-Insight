import pandas as pd
from pycaret.regression import setup, compare_models, tune_model, finalize_model, predict_model

# Cargamos los datasets
dfpatentes = pd.read_csv('../Analisis/datasetPatentes.csv')
dfsnii = pd.read_csv('../Analisis/datasetSNII.csv')
dfwos = pd.read_csv('../Analisis/datasetWoS.csv')
dfkeys = pd.read_csv('../Analisis/Nombres_PxS.csv')

# Normalizamos nombres de columnas
for df in (dfpatentes, dfsnii, dfwos):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(' ', '_')
        .str.replace('-', '_')
    )

# Inner joins usando la tabla de keys
df = (
    dfkeys
    .merge(dfpatentes, on="inventor_id",how="inner")
    .merge(dfsnii, on="cvu",how="inner")
    .merge(dfwos, left_on="NOMBRE SNII", right_on="Investigador", how="inner")
)

# mostramos el dataframe resultante
print(df.head())