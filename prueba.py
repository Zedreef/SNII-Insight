from rapidfuzz import fuzz, process
import pandas as pd
import time

file_path = 'dataset\Investigadores_vigentes_2023.xlsx'
df = pd.read_excel(file_path)

print(df.head())
df = df.dropna(subset=['NOMBRE DEL INVESTIGADOR'])
numerodatos = len(df) 
print("Número de datos:", numerodatos)

# Limpiar y preparar los datos
new_df = pd.DataFrame({'Investigador': df['NOMBRE DEL INVESTIGADOR']})
new_df['Investigador'] = new_df['Investigador'].str.replace(r'\s*,\s*', ',', regex=True)
new_df['Investigador'] = new_df['Investigador'].str.strip()
new_df = new_df.drop_duplicates(subset=['Investigador'])
new_df = new_df[new_df['Investigador'].notna()]

numerodatosN = len(new_df)
print("Número de datos eliminando duplicados:", numerodatosN)

# Parámetros de coincidencia
threshold = 60
nombres_originales = df['NOMBRE DEL INVESTIGADOR'].tolist()


# Función de búsqueda de coincidencia
def bmc(investigador):
    if investigador:  # Validar que no sea vacío o nulo
        mejor_coincidencia = process.extractOne(
            investigador, nombres_originales, scorer=fuzz.ratio, score_cutoff=threshold
        )
        return mejor_coincidencia
    return None

# Buscar coincidencias de forma secuencial
def obtener_coincidencias(investigadores):
    coincidencias = []
    for investigador in investigadores:
        mejor_coincidencia = bmc(investigador)
        if mejor_coincidencia:
            coincidencias.append({
                'Nombre Buscado': investigador,
                'Mejor Coincidencia': mejor_coincidencia[0],
                'Similitud': mejor_coincidencia[1]
            })
    return coincidencias

start_time = time.time()

# Obtener coincidencias
coincidencias = obtener_coincidencias(new_df['Investigador'].tolist())

end_time = time.time()
execution_time = end_time - start_time

# Convertir resultados a DataFrame
coincidencias_df = pd.DataFrame(coincidencias)
print(coincidencias_df)
print(f"Tiempo de ejecución: {execution_time / 60:.2f} minutos")

# Guardar el DataFrame en un archivo CSV
output_file = "coincidencias.csv" 
coincidencias_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"Los resultados se han guardado en el archivo: {output_file}")