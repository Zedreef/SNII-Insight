import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from statsmodels.tsa.stattools import grangercausalitytests
from Menu.utilidades import procesar_archivos, RUTA_GUARDADO

# ----------------------------------------- Definiciones ---------------------------------
def mostrar_causalidad(dfEntrenamiento):
    st.title("📈 Análisis de Causalidad de Granger")

    # Preparar datos para análisis de causalidad
    df_causalidad = dfEntrenamiento[['total_publicaciones', 'patents']].dropna()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Publicaciones → Patentes")
        resultados_pub_pat = grangercausalitytests(df_causalidad[['total_publicaciones', 'patents']], maxlag=2, verbose=False)
        mostrar_resultados_causalidad(resultados_pub_pat)

    with col2:
        st.subheader("Patentes → Publicaciones")
        resultados_pat_pub = grangercausalitytests(df_causalidad[['patents', 'total_publicaciones']], maxlag=2, verbose=False)
        mostrar_resultados_causalidad(resultados_pat_pub)

    st.info("🔍 **Nota:** Un valor p bajo (por ejemplo, < 0.05) indica una relación causal significativa.")

def mostrar_resultados_causalidad(resultados):
    for lag, resultado in resultados.items():
        st.markdown(f"### Lag {lag}")
        data = {
            "Prueba": ["SSR F-test", "Chi2 test", "Likelihood ratio test"],
            "Estadístico": [
                resultado[0]['ssr_ftest'][0],
                resultado[0]['ssr_chi2test'][0],
                resultado[0]['lrtest'][0]
            ],
            "p-valor": [
                resultado[0]['ssr_ftest'][1],
                resultado[0]['ssr_chi2test'][1],
                resultado[0]['lrtest'][1]
            ]
        }
        df_resultados = pd.DataFrame(data)

        # Resaltar valores p significativos
        def resaltar_p_valor(val):
            color = 'background-color: #ffcccc;' if val < 0.05 else ''
            return color

        st.dataframe(
            df_resultados.style.applymap(resaltar_p_valor, subset=["p-valor"]),
            use_container_width=True
        )

def realizar_clustering_y_clasificacion(dfEntrenamiento):
    st.title("🔍 Análisis de Clustering y Clasificación")

    # Clustering con KMeans
    X = dfEntrenamiento[['total_publicaciones', 'patents']].dropna()
    kmeans = KMeans(n_clusters=3, random_state=42).fit(X)
    # Solo asignar etiquetas a las filas sin NaN en X
    dfEntrenamiento['cluster'] = None
    dfEntrenamiento.loc[X.index, 'cluster'] = kmeans.labels_

    # Etiquetas mejoradas para los clusters
    cluster_labels = {i: f'Grupo {i+1}' for i in range(kmeans.n_clusters)}
    dfEntrenamiento['cluster_label'] = dfEntrenamiento['cluster'].map(cluster_labels)

    # Crear gráfico de dispersión interactivo
    fig_clusters = px.scatter(
        dfEntrenamiento.loc[X.index],
        x='total_publicaciones',
        y='patents',
        color='cluster_label',
        title="Visualización de Grupos (KMeans)",
        labels={
            'total_publicaciones': 'Total de Publicaciones',
            'patents': 'Total de Patentes',
            'cluster_label': 'Grupo'
        },
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    # Añadir centroides al gráfico
    centroids = kmeans.cluster_centers_
    for i, (x, y) in enumerate(centroids):
        fig_clusters.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=14, color='black', symbol='x', line=dict(width=2, color='white')),
            name=f'Centroide Grupo {i+1}',
            text=[f'Centroide {i+1}'],
            textposition='top center',
            showlegend=True
        ))

    # Clasificación con Random Forest
    y = kmeans.labels_
    rf = RandomForestClassifier(random_state=42)
    rf.fit(X, y)

    # Importancia de características
    importances = rf.feature_importances_
    features = ['Total de Publicaciones', 'Total de Patentes']

    # Crear gráfico de barras para la importancia de características
    fig_importances = px.bar(
        x=features,
        y=importances,
        labels={'x': 'Características', 'y': 'Importancia'},
        title="Importancia de Características en Random Forest",
        color=importances,
        color_continuous_scale='Blues'
    )

    # Mostrar ambas gráficas en una sola línea
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Clustering con KMeans")
        st.plotly_chart(fig_clusters, use_container_width=True)
    with col2:
        st.subheader("🌲 Clasificación con Random Forest")
        st.plotly_chart(fig_importances, use_container_width=True)

def graficar_correlaciones(dfEntrenamiento):
    """
    Genera un gráfico de barras horizontal para mostrar la correlación entre
    publicaciones y patentes por área de conocimiento.
    """
    # Calcular correlación por área de conocimiento
    correlaciones = {}
    for col in [c for c in dfEntrenamiento.columns if c.startswith('área_del_conocimiento_')]:
        subset = dfEntrenamiento[dfEntrenamiento[col] == True]
        
        # Validar que el subconjunto tenga suficientes datos y variación
        if len(subset) > 1 and subset['total_publicaciones'].std() > 0 and subset['patents'].std() > 0:
            correlaciones[col] = subset['total_publicaciones'].corr(subset['patents'])
        else:
            correlaciones[col] = None  # No calcular si no hay suficientes datos o variación

    # Ordenar las áreas por correlación
    correlaciones_ordenadas = sorted(correlaciones.items(), key=lambda x: x[1] if x[1] is not None else -float('inf'), reverse=True)

    # Filtrar áreas con valores calculables
    areas = [area.replace('área_del_conocimiento_', '').replace('_', ' ') for area, corr in correlaciones_ordenadas if corr is not None]
    valores = [corr for area, corr in correlaciones_ordenadas if corr is not None]

    # Crear el gráfico de barras horizontal con Plotly
    colores = ['green' if c > 0 else 'red' for c in valores]
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=valores,
        y=areas,
        orientation='h',
        marker=dict(color=colores),
        text=[f"{v:.2f}" for v in valores],
        textposition='auto',
        hoverinfo='x+y'
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        title="Correlación entre Publicaciones y Patentes por Área de Conocimiento",
        xaxis_title="Correlación",
        yaxis_title="Áreas de Conocimiento",
        xaxis=dict(showgrid=True, zeroline=True, zerolinecolor='black', zerolinewidth=1),
        yaxis=dict(showgrid=False),
        template='plotly_white',
        bargap=0.2
    )

    return fig

# ----------------------------------------- Codigo ---------------------------------
def mostrar_inicio(rutaAnalisis):
    correctos, incorrectos, archivos_incorrectos = procesar_archivos(RUTA_GUARDADO)
    dfEntrenamiento = pd.read_csv(rutaAnalisis)

    st.title("📊 Informe de Archivos Procesados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos correctos", correctos)
    col2.metric("Archivos con error", incorrectos)
    col3.metric("Archivos en total", correctos + incorrectos)

    if incorrectos > 0:
        st.subheader("Archivos con error:")
        for archivo in archivos_incorrectos:
            st.write(f"- {archivo}")

    # Gráfico de barras
    data = {
        'Categoría': ['Correctos', 'Incorrectos'],
        'Cantidad': [correctos, incorrectos]
    }
    df = pd.DataFrame(data)

    fig = px.bar(df, x='Categoría', y='Cantidad', color='Categoría',
                 title="Archivos Procesados Correctamente vs Incorrectamente",
                 labels={'Cantidad': 'Número de Archivos'},
                 height=400)

    st.plotly_chart(fig)

    # Crear una lista para almacenar los resultados
    resultados = []

    # Iterar sobre las columnas que comienzan con 'área_del_conocimiento_'
    for col in [c for c in dfEntrenamiento.columns if c.startswith('área_del_conocimiento_')]:
        subset = dfEntrenamiento[dfEntrenamiento[col] == True]
        resultados.append({
            "Área": col.replace('área_del_conocimiento_', '').replace('_', ' ').capitalize(),
            "Tamaño del subconjunto": len(subset),
            "Desviación estándar (Publicaciones)": subset['total_publicaciones'].std(),
            "Desviación estándar (Patentes)": subset['patents'].std()
        })

    # Convertir los resultados en un DataFrame
    df_resultados = pd.DataFrame(resultados)

    # Mostrar los resultados en Streamlit
    st.title("📋 Correlación entre Publicaciones y Patentes")

    col_fig1, col_fig2 = st.columns(2)
    with col_fig1:
        fig = px.bar(
            df_resultados,
            x="Área",
            y=["Desviación estándar (Publicaciones)", "Desviación estándar (Patentes)"],
            title="Desviación Estándar de Publicaciones y Patentes por Área del Conocimiento",
            barmode="group",
            labels={"value": "Desviación estándar", "variable": "Tipo"},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_fig2:
        fig_correlaciones = graficar_correlaciones(dfEntrenamiento)
        st.plotly_chart(fig_correlaciones, use_container_width=True)

    mostrar_causalidad(dfEntrenamiento)
    realizar_clustering_y_clasificacion(dfEntrenamiento)