import pandas as pd
from rapidfuzz import process, fuzz

def limpiar_nombres(nombre):
    """Limpia y organiza los nombres eliminando caracteres no deseados y espacios extra."""
    return ' '.join(nombre.upper().replace(',', '').split())

def comparar_nombres(nombre1, nombre2):
    """Compara dos nombres por su similitud basada en tokens."""
    return fuzz.token_set_ratio(nombre1, nombre2)

def guardar_archivo(df, ruta, mensaje):
    """Guarda un DataFrame en un archivo CSV."""
    df.to_csv(ruta, index=False)
    print(mensaje)

# Cargar el archivo CSV
try:
    df = pd.read_csv("Nombres.csv")  # Asegúrate de usar el nombre correcto del archivo
except FileNotFoundError:
    print("Error: El archivo 'Nombres.csv' no se encontró.")
    exit()

# Validar si la columna 'NOMBRE DEL INVESTIGADOR' existe
if 'NOMBRE DEL INVESTIGADOR' not in df.columns:
    print("Error: La columna 'NOMBRE DEL INVESTIGADOR' no está presente en el archivo.")
    exit()

# Normaliza los nombres antes de analizarlos
df['nombre_limpio'] = df['NOMBRE DEL INVESTIGADOR'].apply(limpiar_nombres)

# Comparar nombres similares con un enfoque basado en tokens
nombre_dict = {}
nombres = df['nombre_limpio'].unique()
for nombre in nombres:
    similares = process.extract(nombre, nombres, scorer=fuzz.token_set_ratio, limit=5)
    for similar, score, _ in similares:
        if score > 95:  
            nombre_dict[similar] = nombre

# Crear la columna con nombres corregidos
df['nombre_corregido'] = df['nombre_limpio'].replace(nombre_dict)

# Eliminar duplicados basados en los nombres corregidos
df_sin_duplicados = df.drop_duplicates(subset=['nombre_corregido'])

# Guardar la salida
guardar_archivo(df_sin_duplicados, "nombresLimpios.csv", "Archivo limpio guardado como nombresLimpios.csv.")