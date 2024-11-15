from rapidfuzz import fuzz, process
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time
import os

file_path = 'dataset\Investigadores_vigentes_2023.xlsx'
df = pd.read_excel(file_path)

print(df.head())

numerodatos = len(df) 
print("Número de datos:", numerodatos)
investigadores = df['NOMBRE DEL INVESTIGADOR']
new_df = pd.DataFrame({'Investigador': investigadores})
new_df['Investigador'] = new_df['Investigador'].str.replace(r'\s*,\s*', ',', regex=True)
new_df['Investigador'] = new_df['Investigador'].str.strip()
new_df = new_df.drop_duplicates(subset=['Investigador'])
numerodatosN = len(new_df) 
print("Número de datos eliminando duplicados:", numerodatosN)

# Umbral mínimo de coincidencia
threshold = 70

# Crear una lista de nombres en el DataFrame original
nombres_originales = df['NOMBRE DEL INVESTIGADOR'].tolist()
investigadores_lista = new_df['Investigador'].values.tolist()

def bmc(investigador):
    # Busca la mejor coincidencia en los nombres originales
    mejor_coincidencia = process.extractOne(investigadores_lista, nombres_originales, scorer=fuzz.ratio, score_cutoff=threshold)
    return mejor_coincidencia

# Buscar coincidencias para cada nombre en new_df['Investigador']
def obtener_coincidencias_parallel(investigadores, max_workers=None):
    coincidencias = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resultados = executor.map(bmc, investigadores)
    
    for investigador, mejor_coincidencia in zip(investigadores, resultados):
        if mejor_coincidencia and mejor_coincidencia[1] >= threshold:
            coincidencias.append({
                'Nombre Buscado': investigador,
                'Mejor Coincidencia': mejor_coincidencia[0],
                'Similitud': mejor_coincidencia[1]
            })
    
    return coincidencias

start_time = time.time()

# Ajustar el número máximo de workers según la configuración del sistema
max_workers = min(len(investigadores), os.cpu_count())
# Obtener las coincidencias en paralelo
coincidencias = obtener_coincidencias_parallel(new_df['Investigador'].tolist(), max_workers)

end_time = time.time()
execution_time = end_time - start_time

# Convertir los resultados en un DataFrame
coincidencias_df = pd.DataFrame(coincidencias)
print(coincidencias_df)
print(f"Tiempo de ejecución: {execution_time} segundos")
