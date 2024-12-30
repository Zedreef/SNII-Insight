import csv
import sys
from rapidfuzz import fuzz, process
from multiprocessing import Pool, cpu_count, Manager

def normalizar_nombre_limpio(nombre):
    """
    Elimina la coma en los nombres de la lista Nombres_Limpios.csv
    """
    if ',' in nombre:
        return nombre.replace(',', ' ').strip().upper()
    return nombre.strip().upper()


def leer_nombres_limpios(ruta):
    """
    Leer y normalizar los nombres de Nombres_Limpios.csv
    """
    nombres_limpios = []
    with open(ruta, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nombre_normalizado = normalizar_nombre_limpio(row['NOMBRE DEL INVESTIGADOR'])
            nombres_limpios.append(nombre_normalizado)
    return nombres_limpios

def comparar_nombre(args):
    """
    Función para calcular similitud entre un nombre descartado y la lista de nombres limpios
    """
    nombre_descartado, nombres_limpios, umbral_similitud = args
    # Usar process.extractOne para buscar la mejor coincidencia
    coincidencia, similitud,_ = process.extractOne(
        nombre_descartado, nombres_limpios, scorer=fuzz.ratio
    )

    # Convertir similitud a float por si no lo es
    similitud = float(similitud)

    print(f"Comparando: {nombre_descartado} -> {coincidencia} (Similitud: {similitud}%)")
    if similitud >= umbral_similitud:
        return None  # Coincidencia encontrada, no lo incluimos en no encontrados
    return nombre_descartado  # No encontrado

def procesar_descartados(ruta_descartados, nombres_limpios, ruta_no_encontrados, umbral_similitud=85):
    """
    Procesar nombres descartados con multiprocessing
    """
    nombres_descartados = []
    with open(ruta_descartados, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nombre_normalizado = normalizar_nombre_limpio(row['NOMBRE DEL INVESTIGADOR'])
            nombres_descartados.append((nombre_normalizado))
        
        # Preparar argumentos para multiprocessing
        argumentos = [
            (nombre_descartado, nombres_limpios, umbral_similitud)
            for nombre_descartado in nombres_descartados
        ]
        
        # Usar multiprocessing para calcular similitudes en paralelo
        with Pool(cpu_count()) as pool:
            resultados = pool.map(comparar_nombre, argumentos)
        
        # Filtrar los nombres no encontrados
        no_encontrados = [nombre for nombre in resultados if nombre is not None]

    # Guardar los nombres no encontrados en un nuevo archivo CSV
    with open(ruta_no_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NOMBRE DEL INVESTIGADOR']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for nombre in no_encontrados:
            writer.writerow({'NOMBRE DEL INVESTIGADOR': nombre})

def reformatear_nombre(nombre):
    """
    Cambia el formato de 'NOMBRE APELLIDO' a 'APELLIDO NOMBRE'
    """
    #print(f"Procesando: {nombre}")  # Mensaje de depuración

    # Separar el nombre por espacios
    partes = nombre.split()

    # Verificar que el nombre tenga más de un componente (nombre y apellido)
    if len(partes) > 1:
        # Suponer que el último componente es el apellido y todo lo anterior es el nombre
        apellido = ' '.join(partes[-2:])  # Los últimos dos componentes son el apellido
        nombre = ' '.join(partes[:-2])  # Tods los componentes anteriores son el nombre
        reformatted_name = f"{apellido} {nombre}"
        #print(f"Reformateado a: {reformatted_name}")  # Mensaje de depuración
        return reformatted_name

    return nombre

def procesar_nombres_no_encontrados(ruta_no_encontrados, nombres_limpios, ruta_no_encontrados_actualizada, umbral_similitud=85):
    """
    Procesa nuevamente los nombres no encontrados, aplicando el formato APELLIDO NOMBRE
    """
    # Leer los nombres no encontrados
    nombres_descartados = []
    with open(ruta_no_encontrados, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nombre = row['NOMBRE DEL INVESTIGADOR']
            nombre_reformateado = reformatear_nombre(nombre)
            nombres_descartados.append((nombre_reformateado))

    # Preparar argumentos para multiprocessing
    argumentos = [
        (nombre_descartado, nombres_limpios, umbral_similitud)
        for nombre_descartado in nombres_descartados
    ]

    # Usar multiprocessing para calcular similitudes en paralelo
    with Pool(cpu_count()) as pool:
        resultados = pool.map(comparar_nombre, argumentos)

    # Filtrar los nombres no encontrados
    no_encontrados_actualizados = [nombre for nombre in resultados if nombre is not None]

    # Guardar los nuevos nombres no encontrados en un archivo CSV
    with open(ruta_no_encontrados_actualizada, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NOMBRE DEL INVESTIGADOR']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nombre in no_encontrados_actualizados:
            writer.writerow({'NOMBRE DEL INVESTIGADOR': nombre})

# Rutas de los archivos
ruta_nombres_limpios = 'Limpieza/Nombres_Limpios.csv'
ruta_nombres_descartados = 'Limpieza/Nombres_Descartados.csv'
ruta_nombres_no_encontrados = 'Limpieza/Nombres_No_Encontrados.csv'
ruta_nombres_no_encontrados_2 = 'Limpieza/Nombres_No_Encontrados_Actualizados.csv'

def main():
    print("=== Procesando archivo ===")
    nombres_limpios = leer_nombres_limpios(ruta_nombres_limpios)
    print("=== Procesando nombres ===")
    procesar_descartados(ruta_nombres_descartados, nombres_limpios, ruta_nombres_no_encontrados)
    print("=== Procesando archivo de nombres no encontrados ===")
    procesar_nombres_no_encontrados(ruta_nombres_no_encontrados, nombres_limpios, ruta_nombres_no_encontrados_2)
    print("=== Proceso completado. ===")
    print("El archivo Nombres_No_Encontrados.csv ha sido generado.")

# === Ejecutar el script ===
if __name__ == "__main__":
    main()