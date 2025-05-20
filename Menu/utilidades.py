import os
import re
import unicodedata
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------- Ruta App ---------------------------------------------
RUTA_BRUTOS  = '/mount/src/prueba/Autores WoS'
RUTA_GUARDADO  = '/mount/src/prueba/Autores WoS Limpios'
RUTA_PUBLICACIONES  = '/mount/src/prueba/Analisis/datasetWoS.csv'
RUTA_SNII  = '/mount/src/prueba/Analisis/datasetSNII.csv'
RUTA_PATENTES  = '/mount/src/prueba/Analisis/datasetPatentes.csv'
RUTA_MAESTRO  = '/mount/src/prueba/Analisis/Nombres_PxS.csv'
RUTA_PUBLICACIONES_KERAS = '/mount/src/prueba/Analisis/Entrena_Publicaciones.keras'
RUTA_ANALISIS = '/mount/src/prueba/Analisis/analisisEntrenamiento.csv'
# ----------------------- Ruta GitHub ------------------------------------------
# RUTA_BRUTOS  = 'Autores WoS'
# RUTA_GUARDADO  = 'Autores WoS Limpios'
# RUTA_PUBLICACIONES  = 'Analisis/datasetWoS.csv'
# RUTA_SNII  = 'Analisis/datasetSNII.csv'
# RUTA_PATENTES  = 'Analisis/datasetPatentes.csv'
# RUTA_MAESTRO  = 'Analisis/Nombres_PxS.csv'
# RUTA_PUBLICACIONES_KERAS = 'Analisis/Entrena_Publicaciones.keras'
# RUTA_ANALISIS = 'Analisis/analisisEntrenamiento.csv'
# -------------------------------------------------------------------------------

# ----------------------- Funciones --------------------------------------------
# Función para calcular el índice h
def calcular_indice_h(df):
    # Ordenar las publicaciones por número de citas en orden descendente
    citas = df['Total Citations'].sort_values(ascending=False).values
    h_index = 0

    # Calcular el índice h
    for i, c in enumerate(citas):
        if c >= i + 1:
            h_index = i + 1
        else:
            break
    return h_index

# Función para graficar citas y publicaciones por año
def graficar_citas_publicaciones_comparados(df):
    df['Year'] = df['Publication Date'].apply(lambda x: re.search(
        r'\d{4}', str(x)).group() if re.search(r'\d{4}', str(x)) else None)
    df = df[df['Year'].notna()].copy()
    df['Year'] = df['Year'].astype(int)
    publicaciones_por_año = df.groupby('Year').size()
    citas_por_año = df.groupby('Year')['Total de Citas'].sum()

    #anos = sorted(publicaciones_por_año.index)
    max_publicaciones = publicaciones_por_año.max()
    max_citas = citas_por_año.max()

    fig = go.Figure()
    for autor in df['Investigador'].unique():
        df_autor = df[df['Investigador'] == autor]

        publicaciones_por_año = df_autor.groupby('Year').size()
        citas_por_año = df_autor.groupby('Year')['Total de Citas'].sum()

        # Agregar las barras para las publicaciones por autor (Eje izquierdo)
        fig.add_trace(go.Bar(
            x=publicaciones_por_año.index,
            y=publicaciones_por_año,
            name=f'Publications ({autor})',
            yaxis='y1'
        ))

        # Agregar la línea para las citas por autor (Eje derecho)
        fig.add_trace(go.Scatter(
            x=citas_por_año.index,
            y=citas_por_año,
            mode='lines+markers',
            name=f'Times Cited ({autor})',
            yaxis='y2'
        ))

    fig.update_layout(
        title="Times Cited and Publications Over Time",
        xaxis_title='Year',
        yaxis=dict(title='Publications', side='left',
                    range=[0, max_publicaciones + 1]),
        yaxis2=dict(title='Times Cited', overlaying='y',
                    side='right', range=[0, max_citas + 1]),
        legend=dict(orientation="v", yanchor="middle",
                    y=0.5, xanchor="left", x=1.1)
    )

    st.plotly_chart(fig)

def procesar_autores(df, cantidad_autores, fecha_inicio, fecha_fin):
    # Filtrar por rango de fechas
    df_filtrado = df[(df['Publication Date'].notna()) &
                        (pd.to_datetime(df['Publication Date'], errors='coerce').dt.year >= fecha_inicio) &
                        (pd.to_datetime(df['Publication Date'], errors='coerce').dt.year <= fecha_fin)]

    # Filtrar solo las columnas de interés
    columnas_especificas = ['Title', 'Authors', 'Source Title',
                            'Publication Date', 'Total Citations', 'Average per Year']
    columnas_de_años = [
        col for col in df.columns if col.isdigit() and int(col) >= 2005]
    columnas_de_años_validas = [col for col in columnas_de_años if (
        df_filtrado[col].notna() & (df_filtrado[col] != 0)).any()]

    # Agrupar por autor y contar cuántas publicaciones tiene cada autor
    df_agrupado = df_filtrado.groupby(
        'Authors').size().reset_index(name='Publicaciones')

    # Seleccionar los autores con más publicaciones (según la cantidad seleccionada por el usuario)
    autores_seleccionados = df_agrupado.nlargest(
        cantidad_autores, 'Publicaciones')['Authors']

    # Filtrar el DataFrame original por los autores seleccionados
    df_final = df_filtrado[df_filtrado['Authors'].isin(
        autores_seleccionados)].copy()

    # Mantener solo las columnas relevantes
    df_final = pd.concat(
        [df_final[columnas_especificas], df_final[columnas_de_años_validas]], axis=1)

    return df_final

def procesar_archivos(carpeta):
    correctos = 0
    incorrectos = 0
    archivos_incorrectos = []

    for filename in os.listdir(carpeta):
        if filename.endswith(".txt"):
            ruta_archivo = os.path.join(carpeta, filename)

            try:
                pd.read_csv(ruta_archivo, sep=',', quotechar='"', engine='python')
                correctos += 1
            except Exception:
                incorrectos += 1
                archivos_incorrectos.append(filename)

    return correctos, incorrectos, archivos_incorrectos

def procesar_estadisticas_autores(ruta_final):
    data = pd.read_csv(ruta_final)
    year_columns = [col for col in data.columns if col.isdigit()]
    data['Sum Of Times Cited'] = data[year_columns].fillna(0).sum(axis=1)
    publications_per_author = data.groupby('Authors')['Title'].count().reset_index()
    publications_per_author.columns = ['Authors', 'Publications']
    citations_per_author = data.groupby('Authors')['Sum Of Times Cited'].sum().reset_index()
    author_stats = pd.merge(publications_per_author, citations_per_author, on='Authors')
    author_stats = author_stats[author_stats['Authors'].notna()]
    return author_stats

# Función para procesar los autores y reemplazar
def procesar_autores_brutos(df, nombre_archivo):
    if 'Corporate Authors' in df.columns:
        df = df.rename(columns={'Corporate Authors': 'co-author'})
    df['co-author'] = df['co-author'].fillna('') + \
        '; ' + df['Authors'].fillna('')
    df['Authors'] = os.path.splitext(nombre_archivo)[0]
    columnas_a_mantener = ['Title', 'Authors', 'co-author']
    columnas_existentes = [
        col for col in columnas_a_mantener if col in df.columns]
    if len(columnas_existentes) < len(columnas_a_mantener):
        columnas_faltantes = set(
            columnas_a_mantener) - set(columnas_existentes)
        print(f"Advertencia: Columnas faltantes {columnas_faltantes}")
    df = df[columnas_existentes]
    return df

# Función para limpiar texto
def limpiar_texto(texto):
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    texto = ''.join(c for c in texto if c.isprintable())
    texto = re.sub(r'\d+', '', texto)
    texto = ' '.join(word for word in re.sub(
        r'\s+', ' ', texto).strip().split() if len(word) > 1)
    return texto

# Crea un objeto Scatter de Plotly para los nodos del grafo.
def create_node_trace(G, pos, node_colors, node_size=10):
    x_nodes = []
    y_nodes = []
    node_texts = []
    for node in G.nodes():
        x, y = pos[node]
        x_nodes.append(x)
        y_nodes.append(y)
        node_texts.append(node)
    return go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers',
        marker=dict(size=node_size, color=node_colors,
                    line=dict(width=1, color='black')),
        hovertext=node_texts,
        hoverinfo='text'
    )

# Crea un objeto Scatter de Plotly para las aristas (conexiones) del grafo.
def create_edge_trace(G, pos, edge_color='gray'):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    return go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=0.5, color=edge_color),
        hoverinfo='none'
    )