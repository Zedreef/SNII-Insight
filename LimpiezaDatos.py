import os
import re
import unicodedata
import pandas as pd

# Configuración
CONFIG = {
    "directorio_datasets": "datasetMD",
    "archivo_salida": "datasetMD.csv",
    "archivo_nombres": "nombres_investigadores.csv",
    "archivo_nombres_limpios": "Nombres_Limpios.csv",
    "archivo_nombres_descartados": "Nombres_Descartados.csv",
}

# Diccionario de equivalencias
equivalencias = {
    "Ð": "Ñ",
    ";": "Ñ",
    "▄": "Ü",
    "_": "Ü",
    "Þ": "Ü",
    "0": "O",
    "¬": ".",
    "╚": "È",
    "+": "È",
    "¦": "É",
    "Ì": "Í",
    "Ò": "Ó"
}

# === Funciones de utilidad ===
def limpiar_nombre(nombre):
    """Limpia y normaliza un nombre."""
    if pd.notna(nombre) and isinstance(nombre, str):
        nombre = normalizar_nombre(nombre) # Normalizar caracteres
        nombre = re.sub(r'\s*,\s*', ',', nombre.strip())
        nombre = re.sub(r'^-', '', nombre)  # Quitar guiones iniciales
        return nombre
    return None

def normalizar_nombre(nombre):
    """Normaliza caracteres en un nombre."""
    if pd.notna(nombre) and isinstance(nombre, str):
        nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
        nombre = nombre.replace("Ñ", "N")
        # Aplicar equivalencias del diccionario
        for caracter, reemplazo in equivalencias.items():
            nombre = nombre.replace(caracter, reemplazo)
        return nombre
    return None

def verificar_separacion(nombre):
    """Verifica si un nombre tiene separación por coma."""
    return isinstance(nombre, str) and ',' in nombre

def verifica_caracteres(nombre):
    """Identifica caracteres no permitidos."""
    if isinstance(nombre, str):
        return bool(re.search(r"[^a-zA-Z.,\s\"'-]", nombre))
    return False


def procesar_dataframe(df):
    """Limpia nombres en el DataFrame."""
    if "NOMBRE DEL INVESTIGADOR" in df.columns:
        df["NOMBRE DEL INVESTIGADOR"] = df["NOMBRE DEL INVESTIGADOR"].apply(limpiar_nombre)
    return df


def guardar_archivo(df, ruta, mensaje):
    """Guarda un DataFrame en un archivo CSV."""
    df.to_csv(ruta, index=False)
    print(mensaje)


# Proceso principal
def combinar_archivos():
    """Combina todos los archivos CSV del directorio."""
    ruta_directorio = CONFIG["directorio_datasets"]
    archivos = [os.path.join(ruta_directorio, f) for f in os.listdir(ruta_directorio) if f.endswith(".csv")]

    # Combinar archivos sin procesar más allá de limpieza básica
    dataframes = [procesar_dataframe(pd.read_csv(archivo)) for archivo in archivos]
    df_combinado = pd.concat(dataframes, ignore_index=True)

    # Guardar archivo combinado
    guardar_archivo(df_combinado, CONFIG["archivo_salida"], "Archivo combinado guardado como datasetMD.csv.")

    return df_combinado


def limpiar_nombres(df):
    """Procesa la lista de nombres para dejar solo los válidos."""
    # Extraer nombres únicos
    nombres_unicos = df["NOMBRE DEL INVESTIGADOR"].dropna().unique()
    nombres_unicos = [normalizar_nombre(nombre) for nombre in nombres_unicos]
    df_nombres = pd.DataFrame({"NOMBRE DEL INVESTIGADOR": sorted(nombres_unicos)})

    # Guardar nombres únicos
    guardar_archivo(df_nombres, CONFIG["archivo_nombres"], "Archivo de nombres únicos guardado como nombres_investigadores.csv.")

    # Filtrar nombres válidos (que tienen una coma)
    df_nombres["RAZON_DESCARTE"] = None  # Columna para motivos de descarte
    df_nombres["RAZON_DESCARTE"] = df_nombres["NOMBRE DEL INVESTIGADOR"].apply(
        lambda x: "Sin coma" if not verificar_separacion(x) else None
    )
    df_validos = df_nombres[df_nombres["RAZON_DESCARTE"].isna()]  # Nombres con coma
    descartados_sin_coma = df_nombres[~df_nombres["RAZON_DESCARTE"].isna()]  # Sin coma

    # Verificar y eliminar nombres con caracteres raros
    df_validos.loc[:, "RAZON_DESCARTE"] = df_validos["NOMBRE DEL INVESTIGADOR"].apply(
        lambda x: "Caracteres raros" if verifica_caracteres(x) else None
    )
    nombres_limpios = df_validos[df_validos["RAZON_DESCARTE"].isna()]  # Sin caracteres raros
    descartados_caracteres = df_validos[~df_validos["RAZON_DESCARTE"].isna()]  # Con caracteres raros

    # Guardar descartados para análisis
    descartados = pd.concat([descartados_sin_coma, descartados_caracteres])
    guardar_archivo(descartados, CONFIG["archivo_nombres_descartados"], "Archivo de nombres descartados guardado como Nombres_Descartados.csv.")

    # Quitar duplicados
    nombres_limpios = nombres_limpios.drop(columns=["RAZON_DESCARTE"]).drop_duplicates(subset="NOMBRE DEL INVESTIGADOR").sort_values("NOMBRE DEL INVESTIGADOR")

    # Guardar lista final de nombres limpios
    guardar_archivo(nombres_limpios, CONFIG["archivo_nombres_limpios"], "Archivo limpio guardado como Nombres_Limpios.csv.")

    return nombres_limpios

# === Ejecutar el script ===
if __name__ == "__main__":
    print("=== Combinando archivos ===")
    df_combinado = combinar_archivos()
    print("=== Procesando nombres ===")
    limpiar_nombres(df_combinado)
    print("=== Proceso completado. ===")
