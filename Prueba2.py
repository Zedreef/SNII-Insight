from rapidfuzz import fuzz, process
import pandas as pd
import time
import re

#file_path = 'dataset/Investigadores_vigentes_2023.xlsx'
file_path = 'dataset/Padron_de_Beneficiarios_2022_actualizado_julio_2.xlsx'

# Leer todas las hojas del Excel
sheets = pd.read_excel(file_path, sheet_name=None)


# Inicializar lista acumulada de nombres únicos
nombres_acumulados = []

# Parámetros de coincidencia
threshold = 60

# Función para limpiar nombres
def limpiar_nombre(nombre):
    if pd.notna(nombre) and isinstance(nombre, str):
        # Usar re.sub para reemplazo basado en expresiones regulares
        nombre = re.sub(r'\s*,\s*', ',', nombre)  # Reemplazar espacios alrededor de comas
        nombre = nombre.strip()  # Eliminar espacios al inicio y final
        return nombre
    return None

# Función para buscar la mejor coincidencia
def buscar_mejor_coincidencia(nombre, nombres_referencia):
    if nombre and nombres_referencia:
        mejor_coincidencia = process.extractOne(
            nombre, nombres_referencia, scorer=fuzz.ratio, score_cutoff=threshold
        )
        return mejor_coincidencia
    return None

start_time = time.time()

# Procesar cada hoja
for sheet_name, df in sheets.items():
    print(f"Procesando hoja: {sheet_name}")
    
    # Eliminar filas sin nombre de investigador
    df = df.dropna(subset=['NOMBRE DEL INVESTIGADOR'])
    #df = df.dropna(subset=['NOMBRE'])
    
    # Limpiar los nombres en la hoja actual
    df['NOMBRE DEL INVESTIGADOR'] = df['NOMBRE DEL INVESTIGADOR'].apply(limpiar_nombre)
    #df['NOMBRE'] = df['NOMBRE'].apply(limpiar_nombre)
    
    # Iterar sobre los nombres en la hoja actual
    for nombre in df['NOMBRE DEL INVESTIGADOR']:
    #for nombre in df['NOMBRE']:
        if nombre:
            mejor_coincidencia = buscar_mejor_coincidencia(nombre, nombres_acumulados)
            if not mejor_coincidencia:  # Si no hay coincidencia, agregar a la lista acumulada
                nombres_acumulados.append(nombre)

# Crear un DataFrame con los nombres únicos y limpios
nombres_df = pd.DataFrame({'NOMBRE LIMPIO': nombres_acumulados})

# Guardar los nombres únicos en un archivo CSV
output_file = "nombres_investigadores_limpios.csv"
nombres_df.to_csv(output_file, index=False, encoding='utf-8-sig')

end_time = time.time()
execution_time = end_time - start_time

print(f"Nombres únicos y limpios guardados en: {output_file}")
print(f"Tiempo de ejecución: {execution_time / 60:.2f} minutos")