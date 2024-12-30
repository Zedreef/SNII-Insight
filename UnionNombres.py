import logging
import time
import pandas as pd
from rapidfuzz import process, fuzz

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def cargar_archivos(dataset_path, nombres_path):
    """Carga los archivos CSV y retorna los DataFrames."""
    logging.info(f"Cargando archivo {dataset_path}...")
    dataset_dm = pd.read_csv(dataset_path, low_memory=False)
    logging.info(f"Archivo {dataset_path} cargado con éxito.")

    logging.info(f"Cargando archivo {nombres_path}...")
    nombres_limpios = pd.read_csv(nombres_path)
    logging.info(f"Archivo {nombres_path} cargado con éxito.")
    
    return dataset_dm, nombres_limpios

def inspeccionar_tipos_mixtos(df):
    """Identifica columnas con tipos mixtos en un DataFrame."""
    logging.info("Inspeccionando columnas con tipos mixtos...")
    mixed_columns = []
    for column in df.columns:
        unique_types = df[column].apply(type).unique()
        if len(unique_types) > 1:
            mixed_columns.append((column, unique_types))
    if mixed_columns:
        logging.warning("Se encontraron columnas con tipos mixtos:")
        for col, types in mixed_columns:
            logging.warning(f"Columna: {col}, Tipos encontrados: {types}")
    else:
        logging.info("No se encontraron columnas con tipos mixtos.")

def limpiar_columna_cvu(df):
    """Limpia la columna 'CVU' del DataFrame, manejando valores nulos o inválidos y eliminando filas no numéricas."""
    if "CVU" in df.columns:
        logging.info("Procesando columna 'CVU'...")

        # Filtrar filas no numéricas en 'CVU' y crear una copia explícita
        df = df[df['CVU'].apply(lambda x: str(x).replace("-", "").strip().replace(".", "").isdigit())].copy()

        # Reemplazar valores inválidos y convertir a float
        df.loc[:, 'CVU'] = df['CVU'].replace({"-": None}).astype("float64")
        logging.info("Columna 'CVU' procesada con éxito, filas con valores no numéricos eliminadas.")
    return df

def preparar_columna_investigador(df):
    """Crea y posiciona la columna 'INVESTIGADOR' al lado de 'NOMBRE DEL INVESTIGADOR'."""
    logging.info("Creando la columna 'INVESTIGADOR'...")
    df['INVESTIGADOR'] = ""
    columns = df.columns.tolist()
    index_nombre = columns.index("NOMBRE DEL INVESTIGADOR")
    columns.insert(index_nombre + 1, columns.pop(columns.index("INVESTIGADOR")))
    df = df[columns]
    logging.info("Columna 'INVESTIGADOR' creada y posicionada correctamente.")
    return df

def encontrar_mejor_match(nombre, nombres_limpios, umbral=75):
    """Encuentra el mejor match para un nombre usando RapidFuzz."""
    mejor_match = process.extractOne(nombre, nombres_limpios, scorer=fuzz.ratio)
    if mejor_match and mejor_match[1] >= umbral:
        return mejor_match[0]
    return ""

def asignar_investigadores(dataset_dm, nombres_limpios):
    """Asigna nombres de investigadores usando coincidencias basadas en RapidFuzz."""
    logging.info("Iniciando asignación de investigadores...")
    nombres_limpios_list = nombres_limpios['NOMBRE DEL INVESTIGADOR'].tolist()
    for index, row in dataset_dm.iterrows():
        nombre_original = row['NOMBRE DEL INVESTIGADOR']
        mejor_match = encontrar_mejor_match(nombre_original, nombres_limpios_list)
        dataset_dm.at[index, 'INVESTIGADOR'] = mejor_match
        logging.debug(f"Procesado: {nombre_original} -> {mejor_match}")
    logging.info("Asignación de investigadores completada.")
    return dataset_dm

def main():

    # Archivos de entrada
    dataset_path = "datasetMD.csv"
    nombres_path = "Nombres_Limpios_Final.csv"
    output_path = "datasetF.csv"

    # Cargar los archivos
    dataset_dm, nombres_limpios = cargar_archivos(dataset_path, nombres_path)

    # Inspeccionar tipos mixtos
    inspeccionar_tipos_mixtos(dataset_dm)

    # Limpiar la columna 'CVU'
    dataset_dm = limpiar_columna_cvu(dataset_dm)

    # Preparar la columna 'INVESTIGADOR'
    dataset_dm = preparar_columna_investigador(dataset_dm)

    # Asignar investigadores
    dataset_dm = asignar_investigadores(dataset_dm, nombres_limpios)

    # Guardar el resultado
    logging.info(f"Guardando el archivo procesado en {output_path}...")
    dataset_dm.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"Archivo guardado con éxito en {output_path}.")

if __name__ == "__main__":
    inicio = time.time()
    main()
    fin = time.time()
    print("=== Fin de la Limpieza de datos ===")
    tiempo_total_segundos = fin - inicio
    tiempo_total_horas = tiempo_total_segundos / 60
    print(f"Tiempo total de ejecución FINAL: {tiempo_total_horas:.2f} minutos")