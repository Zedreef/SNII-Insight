import csv
import time
from rapidfuzz import fuzz, process
from collections import defaultdict
from multiprocessing import Pool, cpu_count

def normalizar_nombre(nombre):
    """
    Normaliza un nombre para comparación (internamente), pero no modifica el formato original.
    """
    return nombre.replace(',', '').strip().upper()

def comparar_nombres(args):
    """
    Función para calcular similitud entre un nombre y el resto de nombres.
    """
    nombre_normalizado, lista_nombres_normalizados = args
    similares = process.extract(nombre_normalizado, lista_nombres_normalizados, scorer=fuzz.ratio, limit=10)
    return similares

def agrupar_nombres_similares(nombres_originales, nombres_normalizados, umbral_similitud):
    """
    Agrupa nombres similares utilizando su forma normalizada.
    """
    print("Agrupando nombres similares...")
    grupos = defaultdict(list)

    for nombre_original, nombre_normalizado in zip(nombres_originales, nombres_normalizados):
        grupo_asignado = False
        for clave_original, clave_normalizada in list(grupos.keys()):
            similitud = fuzz.ratio(nombre_normalizado, clave_normalizada)
            if similitud >= umbral_similitud:  # Si la similitud es mayor al umbral, los agrupo
                grupos[(clave_original, clave_normalizada)].append((nombre_original, nombre_normalizado))
                grupo_asignado = True
                break
        if not grupo_asignado:
            grupos[(nombre_original, nombre_normalizado)].append((nombre_original, nombre_normalizado))
    
    print(f"Total de grupos formados: {len(grupos)}")
    return grupos

def seleccionar_nombre_representativo(grupos):
    """
    Selecciona un nombre representativo de cada grupo basado en criterios definidos.
    """
    print("Seleccionando nombres representativos...")
    nombres_limpios = []
    for (nombre_original, _), nombres in grupos.items():
        # Regla para seleccionar el nombre representativo: el más largo en su formato original
        nombre_representativo = max(nombres, key=lambda x: len(x[0]))[0]
        nombres_limpios.append(nombre_representativo)
    
    print(f"Total de nombres representativos seleccionados: {len(nombres_limpios)}")
    return nombres_limpios

def procesar_nombres(ruta_archivo, umbral_similitud=85):
    """
    Procesa los nombres de un archivo CSV, agrupando nombres similares y seleccionando el representativo.
    """
    print(f"Procesando archivo: {ruta_archivo} con umbral: {umbral_similitud}")
    nombres_originales = []
    nombres_normalizados = []
    with open(ruta_archivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nombre_original = row['NOMBRE DEL INVESTIGADOR']
            nombres_originales.append(nombre_original)
            nombres_normalizados.append(normalizar_nombre(nombre_original))

    print(f"Total de nombres cargados: {len(nombres_originales)}")

    # Usar multiprocessing para comparar los nombres
    print("Iniciando comparación de nombres utilizando multiprocessing...")
    with Pool(cpu_count()) as pool:
        argumentos = [(nombre_normalizado, nombres_normalizados) for nombre_normalizado in nombres_normalizados]
        resultados = pool.map(comparar_nombres, argumentos)

    # Agrupar los nombres similares
    grupos = agrupar_nombres_similares(nombres_originales, nombres_normalizados, umbral_similitud)

    # Seleccionar un nombre representativo para cada grupo
    nombres_limpios = seleccionar_nombre_representativo(grupos)

    return nombres_limpios

def guardar_nombres_limpios(nombres_limpios, ruta_salida):
    """
    Guarda los nombres limpios en un nuevo archivo CSV.
    """
    print(f"Guardando los nombres limpios en el archivo: {ruta_salida}")
    with open(ruta_salida, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NOMBRE DEL INVESTIGADOR']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nombre in nombres_limpios:
            writer.writerow({'NOMBRE DEL INVESTIGADOR': nombre})

# === Ejecutar el script ===
if __name__ == "__main__":

    inicio = time.time()

    ruta_entrada  = 'Nombres_LimpiosCompleto.csv'
    ruta_intermedia = 'Nombres_Limpios_85.csv'
    ruta_salida = 'Nombres_Limpios_Final.csv'
    
    print("=== Primera limpieza con umbral de 85 ===")
    nombres_limpios_85 = procesar_nombres(ruta_entrada, umbral_similitud=85)
    guardar_nombres_limpios(nombres_limpios_85, ruta_intermedia)
    print("=== Primera limpieza completada ===")

    print("=== Segunda limpieza con umbral de 75 ===")
    nombres_limpios_75 = procesar_nombres(ruta_intermedia, umbral_similitud=75)
    guardar_nombres_limpios(nombres_limpios_75, ruta_salida)
    print("=== Segunda limpieza completada ===")

    print("=== Proceso completado. ===")

    fin = time.time()
    print(f"Tiempo total de ejecución: {fin - inicio:.2f} segundos")