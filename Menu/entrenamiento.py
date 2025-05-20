from pycaret.regression import setup, compare_models, tune_model, finalize_model, predict_model, plot_model
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Cargamos los datasets
def safe_read_csv(path, **kwargs):
    try:
        df = pd.read_csv(path, **kwargs)
        print(f"Archivo leído correctamente: {path} (filas: {len(df)})")
        return df
    except Exception as e:
        print(f"Error al leer {path}: {e}")
        return pd.DataFrame()

dfpatentes = safe_read_csv('Analisis/datasetPatentes.csv')
dfsnii = safe_read_csv('Analisis/datasetSNII.csv')
dfwos = safe_read_csv('Analisis/datasetWoS.csv')
dfkeys = safe_read_csv('Analisis/Nombres_PxS.csv')

# Normalizamos nombres de columnas
for df in (dfpatentes, dfsnii, dfwos,dfkeys):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(' ', '_')
        .str.replace('-', '_')
    )

# Eliminamos las columnas del dfkeys 'nombre_inventor', 'nombre_del_investigador'
dfkeys = dfkeys.drop(columns=['nombre_inventor', 'nombre_del_investigador'])
# Eliminamos los NA de la columna 'inventor_id'
dfkeys = dfkeys.dropna(subset=['inventor_id'])
# Convertimos la columna 'inventor_id' a int
dfkeys['cvu'] = dfkeys['cvu'].astype(int)

# Contamos la cantidad nombres que hay en la columna 'authors' que estan separadas por ';'
dfwos['numCoautores'] = dfwos['authors'].str.split(';').str.len()

# Quitar espacios en los extremos
dfsnii['nivel'] = (
    dfsnii['nivel']
    .astype(str)              
    .str.strip()              
    .replace({
        r'.*Nivel I$': 1,
        r'.*Nivel II$': 2,
        r'.*Nivel III$': 3,
        r'.*Candidato.*': 'C',
        r'^Emérito$': 'E'
    }, regex=True)
    .astype(str)
)

# Normalizar formatos de fecha a 'YYYY-MM-DD' sin eliminar vals no estándar
def normalize_date(val):
    try:
        return pd.to_datetime(val, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return val

for col in ['fecha_de_inicio_de_vigencia', 'fecha_de_fin_de_vigencia']:
    dfsnii[col] = dfsnii[col].apply(normalize_date)

# Definir función para extraer años de forma segura
def safe_year(val):
    try:
        return pd.to_datetime(val, dayfirst=True, errors='coerce').year
    except Exception:
        return None

# Extraer años de inicio y fin
dfsnii['anio_inicio'] = dfsnii['año']  # Se asume que 'año' ya está en formato correcto
dfsnii['anio_fin'] = dfsnii['fecha_de_fin_de_vigencia'].apply(safe_year)

# Ordenar por cvu y año de fin (descendente)
dfsnii = dfsnii.sort_values(['cvu', 'anio_fin'], ascending=[True, False])

# Agrupar por cvu y nivel, y calcular la actividad
def calcular_actividad(grupo):
    grupo = grupo.sort_values('anio_inicio')  # Ordenar por año de inicio
    actividad = f"{grupo['anio_inicio'].iloc[0]}-{grupo['anio_fin'].iloc[-1]}"
    return pd.Series({
        'Actividad': actividad,
        'anio_inicio': grupo['anio_inicio'].iloc[0],
        'anio_fin': grupo['anio_fin'].iloc[-1]
    })

dfsnii_actividad = (
    dfsnii.groupby(['cvu', 'nivel'])
    .apply(calcular_actividad)
    .reset_index()
)

# Quedarse con el año más reciente de cada nivel
dfsnii_recent = dfsnii_actividad.sort_values(['cvu', 'anio_fin'], ascending=[True, False])
dfsnii_recent = dfsnii_recent.drop_duplicates(subset=['cvu', 'nivel'], keep='first')

# Eliminamos la columna anio_inicio, anio_fin
dfsnii_recent = dfsnii_recent.drop(columns=['anio_inicio', 'anio_fin'])

# Limpiamos los datos
dfsnii = dfsnii.sort_values(['cvu', 'anio_inicio'], ascending=[True, False])
dfsnii = dfsnii.drop_duplicates(subset=['cvu', 'nivel'], keep='first')

# Eliminamos la columna anio_inicio, anio_fin y cruzamos con el dataset de actividad
dfsnii = dfsnii.drop(columns=['anio_inicio', 'anio_fin'])

# Convertimos int la columna cvu sin decimales del dfsnii_recent
dfsnii_recent['cvu'] = dfsnii_recent['cvu'].astype(int)
dfsnii['cvu'] = dfsnii['cvu'].astype(int)
# Quitamos el decimal a la columna 'Actividad' del dfsnii_recent
dfsnii_recent['Actividad'] = dfsnii_recent['Actividad'].str.replace('.0', '', regex=False)

# Cruzamos los dataserts para solo recuperar el Actividad dfsnii_recent
dfsnii = dfsnii.merge(dfsnii_recent, on=['cvu', 'nivel'], how='left', suffixes=('', '_y'))

# Reducir SNII a un registro por CVU (por ejemplo, el más reciente)
dfsnii = (
    dfsnii
    .sort_values("fecha_de_fin_de_vigencia")
    .drop_duplicates(subset="cvu", keep="last")
)

# Merge de las tablas
dfFinal = (
    dfkeys
      .merge(dfsnii, on="cvu", how="inner", suffixes=('', '_snii'))
      .merge(dfpatentes, on="inventor_id", how="inner", suffixes=('', '_patentes'))
      .merge(dfwos, left_on="nombre_snii", right_on="investigador", how="inner", suffixes=('', '_wos'))
)

dfEntrenamiento = dfFinal.copy()

# Llenamos los valores de la columna 'co_inventoras_mujeres' con 0
dfEntrenamiento['co_inventoras_mujeres'] = dfEntrenamiento['co_inventoras_mujeres'].fillna(0)
dfEntrenamiento['número_de_coinventores'] = dfEntrenamiento['número_de_coinventores'].fillna(0)

# Patentes
# Asegurarse de que las columnas sean numéricas
dfEntrenamiento['co_inventoras_mujeres'] = pd.to_numeric(dfEntrenamiento['co_inventoras_mujeres'], errors='coerce')
dfEntrenamiento['número_de_coinventores'] = pd.to_numeric(dfEntrenamiento['número_de_coinventores'], errors='coerce')

dfEntrenamiento['años_patente'] = dfEntrenamiento['última_patente'].astype(int) - dfEntrenamiento['año_de_inicio'].astype(int)

# Evitar divisiones por cero
dfEntrenamiento['prop_coinv_mujeres'] = dfEntrenamiento['co_inventoras_mujeres'] / (dfEntrenamiento['número_de_coinventores'] + 1e-9)

# Publicaciones WoS
cols_anuales = [str(y) for y in range(2000, 2025)]
dfEntrenamiento['total_publicaciones'] = dfEntrenamiento[cols_anuales].sum(axis=1)
dfEntrenamiento['h_index'] = dfEntrenamiento['h']
dfEntrenamiento['citas_pub'] = dfEntrenamiento['total_de_citas']

# SNII
dfEntrenamiento['vigencia_años'] = (
    pd.to_datetime(dfEntrenamiento['fecha_de_fin_de_vigencia']) -
    pd.to_datetime(dfEntrenamiento['fecha_de_inicio_de_vigencia'])
).dt.days / 365

# One-hot encoding de variables categóricas
dfEntrenamiento = pd.get_dummies(
dfEntrenamiento,
columns=['nivel', 'área_del_conocimiento', 'disciplina', 'entidad_federativa'],
drop_first=True
)

# Verificar y manejar valores faltantes en columnas numéricas y categóricas
numeric_cols = ['patents', 'años_patente', 'prop_coinv_mujeres', 'h_index', 'citas_pub', 'vigencia_años']
categorical_cols = [c for c in dfEntrenamiento.columns if c.startswith(('nivel_', 'área_', 'disciplina_', 'entidad_'))]

# Validar y limpiar columnas numéricas
for col in numeric_cols:
    dfEntrenamiento[col] = pd.to_numeric(dfEntrenamiento[col], errors='coerce')
    dfEntrenamiento[col] = dfEntrenamiento[col].fillna(0)

# Validar columnas categóricas
for col in categorical_cols:
    if not pd.api.types.is_categorical_dtype(dfEntrenamiento[col]):
        dfEntrenamiento[col] = dfEntrenamiento[col].astype('category')

# Verificar que no existan valores faltantes en las columnas categóricas
dfEntrenamiento = dfEntrenamiento.dropna(subset=categorical_cols)

# Filtrar solo columnas relevantes para el modelo
columnas_modelo = numeric_cols + categorical_cols + ['total_publicaciones']
dfEntrenamiento = dfEntrenamiento[columnas_modelo].copy()

# Definir experimento en PyCaret
exp = setup(
    data=dfEntrenamiento,
    target='total_publicaciones', # Variable objetivo: publicaciones
    numeric_features=numeric_cols,
    categorical_features=categorical_cols,
    normalize=True,
    imputation_type=None, # Desactivar imputación automática
    session_id=42
)

# Comparar y tunear modelos
best = compare_models() # Elegir el mejor modelo
tuned = tune_model(best) # Afinar el modelo
final = finalize_model(tuned) # Entrenar en todo el conjunto de datos

# Predicción sobre hold-out (por ejemplo, últimos 20%)
# Asegurarnos que el holdout tiene las mismas columnas que el dataset de entrenamiento
df_holdout = dfEntrenamiento.sample(frac=0.2, random_state=42)
preds = predict_model(final, data=df_holdout)

# Mostrar las columnas disponibles en preds
def print_pred_cols(df):
    print("Columnas disponibles en preds:", list(df.columns))
    cols = [c for c in ['total_publicaciones', 'Label', 'Score'] if c in df.columns]
    print(df[cols].head())

print_pred_cols(preds)

# Resultados (plots sobre el conjunto completo)
# Solo generamos el gráfico de importancia de variables que funciona correctamente
plot_model(final, plot='feature') # Importancia de variables

# Predecir sobre el conjunto completo de datos
preds_full = predict_model(final, data=dfEntrenamiento)

# Calcular residuales
# Verificar si la columna 'Label' existe, de lo contrario usar 'prediction_label'
predicted_column = 'Label' if 'Label' in preds_full.columns else 'prediction_label'
residuals = dfEntrenamiento['total_publicaciones'] - preds_full[predicted_column]

# Crear gráfico de residuales vs valores predichos
plt.figure(figsize=(10, 6))
plt.scatter(preds_full[predicted_column], residuals, alpha=0.5)
plt.axhline(y=0, color='r', linestyle='-')
plt.xlabel('Valores predichos')
plt.ylabel('Residuales')
plt.title('Gráfico de Residuales')
z = np.polyfit(preds_full[predicted_column], residuals, 1)
p = np.poly1d(z)
plt.plot(preds_full[predicted_column], p(preds_full[predicted_column]), 'r--', alpha=0.5)

# Mostrar RMSE
rmse = mean_squared_error(dfEntrenamiento['total_publicaciones'], preds_full[predicted_column], squared=False)
plt.annotate(f'RMSE: {rmse:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12)

plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Histograma de residuales
plt.figure(figsize=(10, 6))
plt.hist(residuals, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
plt.axvline(x=0, color='r', linestyle='-')
plt.xlabel('Residuales')
plt.ylabel('Frecuencia')
plt.title('Distribución de Residuales')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Guardamos el 'dfEntrenamiento'
dfEntrenamiento.to_csv('Analisis/analisisEntrenamiento.csv', index=False)