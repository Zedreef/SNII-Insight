import os
import pandas as pd
import logging

# Configuración básica del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ruta de las carpetas
ruta_carpeta = "dataset"
ruta_guardado = "datasetMD"

# Crear la carpeta de salida si no existe
os.makedirs(ruta_guardado, exist_ok=True)

# Diccionario para reemplazar los nombres de las columnas
columnas_cambio = {
    "NOMBRE DE LA INVESTIGADORA O INVESTIGADOR": "NOMBRE DEL INVESTIGADOR",
    "NOMBRE DE LA INVESTIGADORA O DEL INVESTIGADOR": "NOMBRE DEL INVESTIGADOR",
    "NOMBRE DEL INVESTIGADOR(A)": "NOMBRE DEL INVESTIGADOR",
    "CVU (a partir de 2003)": "CVU",
    "GRADO ACADEMICO": "NOBILIS",
    "GRADO ACADÉMICO": "NOBILIS",
    "DISCIPLINA (a partir de 1991)": "DISCIPLINA",
    "SUBDISCIPLINA (a partir de 1991)": "SUBDISCIPLINA",
    "ESPECIALIDAD (a partir de 1991)": "ESPECIALIDAD",
    "INSTITUCIÓN DE ADSCRIPCIÓN (a partir de 1990)": "INSTITUCIÓN DE ADSCRIPCIÓN",
    "INSTITUCION DE ADSCRIPCIÓN": "INSTITUCIÓN DE ADSCRIPCIÓN",
    "DEPENDENCIA (a partir de 1991)": "DEPENDENCIA",
    "DEPENDENCIA DE ADSCRIPCIÓN": "DEPENDENCIA",
    "ENTIDAD FEDERATIVA ADSCRIPCIÓN\n(a partir de 1990)": "ENTIDAD FEDERATIVA",
    "ENTIDAD FEDERATIVA ADSCRIPCIÓN": "ENTIDAD FEDERATIVA",
    "ENTIDAD FEDERATIVA DE ADSCRIPCIÓN": "ENTIDAD FEDERATIVA",
    "PAIS ADSCRIPCIÓN \n(a partir de 1990)": "PAÍS",
    "PAÍS DE ADSCRIPCIÓN": "PAÍS",
    "PAIS": "PAÍS",
    "CATEGORÍA": "NIVEL"
}

# Columnas faltantes para 2021 y 2022
columnas_faltantes_por_año = {
    "2021": ['FECHA DE INICIO DE VIGENCIA', 'FECHA DE FIN DE VIGENCIA', 'NOBILIS'],
    "2022": ['NOBILIS']
}

# Columnas a mover
columnas_a_mover = {
    "NOBILIS": "NOMBRE DEL INVESTIGADOR",
    "FECHA DE FIN DE VIGENCIA": "ÁREA DEL CONOCIMIENTO",
    "FECHA DE INICIO DE VIGENCIA": "FECHA DE FIN DE VIGENCIA"
}

# Función para cambiar nombres de columnas
def cambiar_nombres_columnas(df: pd.DataFrame, columnas_cambio: dict) -> pd.DataFrame:
    """Renombra columnas según un diccionario de cambios."""
    return df.rename(columns=columnas_cambio)

# Función para agregar columnas faltantes
def agregar_columnas_faltantes(df: pd.DataFrame, columnas_faltantes: list) -> pd.DataFrame:
    """Agrega columnas faltantes al DataFrame."""
    for columna in columnas_faltantes:
        if columna not in df.columns:
            df[columna] = pd.NA
            logger.info(f"Agregada la columna: {columna}")
    return df

# Función para mover una columna a una posición específica
def mover_columna(df: pd.DataFrame, columna: str, destino: str) -> pd.DataFrame:
    """Mueve una columna a una posición específica."""
    if columna in df.columns and destino in df.columns:
        columnas = list(df.columns)
        columnas.remove(columna)
        posicion = columnas.index(destino)
        columnas.insert(posicion, columna)
        return df[columnas]
    return df

# Función para procesar archivos según el rango de años
def procesar_archivo(df: pd.DataFrame, año: int) -> pd.DataFrame:
    """Procesa un archivo según el año correspondiente."""
    if año <= 2014:
        # Eliminar columna específica si existe
        if "EXPEDIENTE" in df.columns:
            df = df.drop(columns=["EXPEDIENTE"])
            logger.info("Columna 'EXPEDIENTE' eliminada.")

        # Mover columna NOBILIS antes de NOMBRE DEL INVESTIGADOR
        df = mover_columna(df, "NOBILIS", "NOMBRE DEL INVESTIGADOR")
    else:
        # Agregar columna AÑO al inicio
        df.insert(0, "AÑO", año)
        logger.info("Columna 'AÑO' agregada al inicio.")

        # Eliminar columnas específicas si existen
        columnas_eliminar = ["EMÉRITO", "VIVO", "VIVO?", "APOYO ECONÓMICO", "ESTÍMULO ECONÓMICO", "TECNOLOGO", "Estímulo Económico"]
        df = df.drop(columns=[col for col in columnas_eliminar if col in df.columns], errors="ignore")
    return df

# Funcion Principal
def main():

    # Procesar los archivos
    for archivo in os.listdir(ruta_carpeta):
        if archivo.startswith("Investigadores_vigentes_20") and archivo.endswith(".xlsx"):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)

            try:
                # Extraer el año del nombre del archivo
                año = int(archivo.split("_")[-1].split(".")[0])
                logger.info(f"Procesando archivo: {archivo}, Año: {año}")

                # Leer archivo en un DataFrame
                df = pd.read_excel(ruta_archivo)

                # Cambiar los nombres de las columnas
                df = cambiar_nombres_columnas(df, columnas_cambio)

                # Agregar columnas faltantes si es necesario
                if str(año) in columnas_faltantes_por_año:
                    columnas_faltantes = columnas_faltantes_por_año[str(año)]
                    df = agregar_columnas_faltantes(df, columnas_faltantes)

                # Mover columnas en 2021 y 2022
                if año in [2021, 2022]:
                    for columna, destino in columnas_a_mover.items():
                        df = mover_columna(df, columna, destino)

                # Procesar el archivo según el año
                df = procesar_archivo(df, año)

                # Guardar el archivo procesado
                nombre_salida = f"{archivo.replace('.xlsx', '.csv')}"
                ruta_guardar = os.path.join(ruta_guardado, nombre_salida)
                df.to_csv(ruta_guardar, index=False, encoding='utf-8-sig')
                logger.info(f"Archivo procesado y guardado: {nombre_salida}")
            except Exception as e:
                logger.error(f"Error procesando {archivo}: {e}")

    # Comparar columnas entre archivos
    columnas_archivos = {}
    for archivo in os.listdir(ruta_guardado):
        if archivo.endswith(".csv"):
            ruta_archivo = os.path.join(ruta_guardado, archivo)
            try:
                df = pd.read_csv(ruta_archivo)
                columnas_archivos[archivo] = list(df.columns)
            except Exception as e:
                logger.error(f"Error leyendo {archivo}: {e}")

    # Verificar esquemas únicos
    nombres_columnas_unicos = set(tuple(columnas) for columnas in columnas_archivos.values())
    if len(nombres_columnas_unicos) == 1:
        logger.info("✅ Todos los archivos tienen las mismas columnas.")
    else:
        logger.warning("❌ Los archivos tienen diferentes esquemas de columnas.")
        for archivo, columnas in columnas_archivos.items():
            logger.info(f"{archivo}: {columnas}")

if __name__ == "__main__":
    main()