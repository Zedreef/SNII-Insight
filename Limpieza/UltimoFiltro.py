import pandas as pd
import logging
from tqdm import tqdm
from rapidfuzz import process, fuzz

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Lista para nombres no emparejados
nombres_no_emparejados = []

def separar(dataset_sin):
    """Separar apellidos y nombres para ambos datasets."""
    logger.info("Separando apellidos y nombres...")
    dataset_sin[["APELLIDOS", "NOMBRES"]] = dataset_sin["NOMBRE DEL INVESTIGADOR"].str.split(",", expand=True)
    nombres_limpios[["APELLIDOS", "NOMBRES"]] = nombres_limpios["NOMBRE DEL INVESTIGADOR"].str.split(",", expand=True)


def procesar_nombres_faltantes():
    """Creamos el archivo datasetSIN que contiene los nombres que les hace falta un nombre de búsqueda en el dataset Final."""
    # Filtra las filas donde la columna INVESTIGADOR este vacia
    filtro = dataset['INVESTIGADOR'].isna() | (dataset['INVESTIGADOR'] == "")
    datos_filtrados = dataset[filtro]

    # Filtra filas cuyos nombres en la columna "NOMBRE DEL INVESTIGADOR" no contienen una coma
    filtro_coma = datos_filtrados["NOMBRE DEL INVESTIGADOR"].str.contains(",", na=False)
    datos_con_coma = datos_filtrados[filtro_coma]

    # Elimina filas con nombres repetidas en la columna "NOMBRE DEL INVESTIGADOR"
    nombres_unicos = datos_con_coma["NOMBRE DEL INVESTIGADOR"].drop_duplicates().sort_values()

    # Guarda los resultados en un CSV
    nombres_unicos.to_csv("Limpieza/datasetSIN.csv", index=False, header=True, encoding='utf-8-sig')
    print("Los nombres únicos se han guardado en 'datasetSIN.csv'.")

def analizar_similitudes(fila, nombres_limpios):
    """Función para analizar similitudes."""
    try:
        # Buscar coincidencias exactas o parciales en apellidos
        coincidencias = nombres_limpios.loc[
            nombres_limpios["APELLIDOS"] == fila["APELLIDOS"]
        ]

        if coincidencias.empty:
            # No hay coincidencia en apellidos, añadir directamente
            logging.debug(f"No se encontró coincidencia para: {fila['NOMBRE DEL INVESTIGADOR']}")
            nombres_no_emparejados.append(fila["NOMBRE DEL INVESTIGADOR"])
        else:
            # Analizar coincidencia de nombres
            mejor_coincidencia = process.extractOne(
                fila["NOMBRES"],
                coincidencias["NOMBRES"],
                scorer=fuzz.ratio
            )

            if mejor_coincidencia and mejor_coincidencia[1] < 85:
                # Si la similitud en nombres es baja, añadir a no emparejados
                logging.debug(f"Similitud baja en nombres para: {fila['NOMBRE DEL INVESTIGADOR']}.")
                nombres_no_emparejados.append(fila["NOMBRE DEL INVESTIGADOR"])
    except Exception as e:
        logger.error(f"Error al procesar la fila: {fila['NOMBRE DEL INVESTIGADOR']} - {e}")

def procesar_archivo():
    """Función principal."""
    dataset_sin = pd.read_csv("Limpieza/datasetSIN.csv", header=None, names=["NOMBRE DEL INVESTIGADOR"])
    # Separamos los nombres
    separar(dataset_sin)

    # Iterar por cada fila en datasetSIN con barra de progreso
    logging.info("Iniciando el proceso de comparación.")
    for _, fila in tqdm(dataset_sin.iterrows(), total=dataset_sin.shape[0], desc="Procesando filas"):
        analizar_similitudes(fila, nombres_limpios)

    # Combinar nombres no emparejados con la lista limpia existente
    logging.info("Combinando los nombres no emparejados con la lista existente.")
    nombres_actualizados = pd.concat([
        nombres_limpios[["NOMBRE DEL INVESTIGADOR"]],
        pd.DataFrame(nombres_no_emparejados, columns=["NOMBRE DEL INVESTIGADOR"])
    ]).drop_duplicates().sort_values(by="NOMBRE DEL INVESTIGADOR")

    # Guardar el resultado final
    logging.info("Guardando el archivo final.")
    nombres_actualizados.to_csv("Nombres_Limpios_Final.csv", index=False, header=True, encoding='utf-8-sig')

    logging.info("El proceso ha terminado. Los nombres actualizados se han guardado en 'Nombres_Limpios_Final.csv'.")

def main():
    procesar_nombres_faltantes()
    procesar_archivo()

if __name__ == "__main__":
   # Cargar los archivos
   logger.info("Cargando los archivos...")
   dataset = pd.read_csv("datasetF.csv")
   nombres_limpios = pd.read_csv("Nombres_Limpios_Final.csv")

   main()