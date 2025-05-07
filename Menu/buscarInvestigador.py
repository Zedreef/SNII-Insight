import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import re
from Menu.utilidades import RUTA_PUBLICACIONES, RUTA_SNII, RUTA_MAESTRO, RUTA_PATENTES
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# ----------------------- Ruta App ---------------------------------------------
data = pd.read_csv(RUTA_PUBLICACIONES, encoding='utf-8')
snii = pd.read_csv(RUTA_SNII)
maestro = pd.read_csv(RUTA_MAESTRO, encoding='utf-8')
patentes = pd.read_csv(RUTA_PATENTES, encoding='utf-8')
# ----------------------- Funciones --------------------------------------------
# Función para obtener los datos de un autor
def obtener_datos_autor(nombre_autor, data, preprocessor):
    # Filtrar los datos del autor seleccionado
    autor_info = data[data['Investigador'] == nombre_autor]
    
    if autor_info.empty:
        return None

    # Seleccionar las columnas necesarias para el modelo
    columnas_requeridas = ['Total de Citas', 'Promedio por año',
                 '2000','2001','2002','2003','2004',
                 '2005','2006','2007','2008','2009','2010','2011','2012','2013',
                 '2014','2015','2016','2017','2018','2019','2020','2021','2022',
                 '2023','Title','Investigador', 'Corporate Authors', 'Book Editors',
                 'Source Title']
    
    # Extraer los datos del autor en el formato correcto
    input_data = autor_info[columnas_requeridas]

    # Aplicar el preprocesamiento (estandarización y codificación OneHot)
    input_data_encoded = preprocessor.transform(input_data)
    
    # Convertir csr_matrix a un array denso para el modelo
    input_data_encoded = input_data_encoded.toarray()
    
    return input_data_encoded

# Función para procesar los datos del autor seleccionado
def procesar_autor(df, autor_seleccionado):
    """Procesa datos de un autor específico desde el año 2000 en adelante."""
    # Filtrar y copiar datos del autor
    df_filtrado = (
        df.dropna(subset=['Investigador'])
          .query("Investigador == @autor_seleccionado")
          .copy()
    )

    # Filtrar desde el año 2000 usando Publication Year
    df_filtrado = df_filtrado[(df_filtrado['Publication Year'] >= 2000) & (df_filtrado['Publication Year'] <= 2024)]

    # Columnas fijas y dinámicas (años >=2000 con datos)
    columnas_especificas = ['Title', 'Publication Date', 'Total de Citas', 'Promedio por año']

    # Seleccionar y devolver
    return df_filtrado[columnas_especificas].reset_index(drop=True)

# Función para calcular el resumen de citas
def calcular_resumen(df, autor_seleccionado):
    # Filtrar y copiar datos del autor
    df = (
        df.dropna(subset=['Investigador'])
          .query("Investigador == @autor_seleccionado")
          .copy()
    )
    df = df[(df['Publication Year'] >= 2000) & (df['Publication Year'] <= 2024)]

    resumen = []

    # Obtener los autores únicos
    autores = df['Investigador'].unique()

    for autor in autores:
        # Filtrar los datos para el autor actual
        df_autor = df[df['Investigador'] == autor]

        # Calcular la suma de 'Total de Citas', el promedio de 'Promedio por año', y el índice h
        total_publicaciones = df_autor['Title'].count()
        total_citations = df_autor['Total de Citas'].sum()
        average_per_year = df_autor['Promedio por año'].mean()
        # Calcular el índice h
        citas = df_autor['Total de Citas'].sort_values(ascending=False).values
        h_index = sum(c >= i + 1 for i, c in enumerate(citas))

        # Agregar los datos al resumen
        resumen.append({
            'Publicaciones': total_publicaciones,
            'Total Citas': total_citations,
            'Promedio Año': average_per_year,
            'Índice h': h_index
        })

    # Convertir el resumen en un DataFrame
    return pd.DataFrame(resumen)

# # Función para gráfica las citas y publicaciones por año
# def graficar_citas_publicaciones(df_autor, autor_seleccionado):
#     # Filtrar autor
#     df_autor = (
#         df_autor.dropna(subset=['Investigador'])
#           .query("Investigador == @autor_seleccionado")
#           .copy()
#     )
#     df_autor = df_autor[(df_autor['Publication Year'] >= 2000) & (df_autor['Publication Year'] <= 2024)]
#     df_autor['Year'] = df_autor['Publication Year'].astype(int)

#     # Agrupar por el año y contar el número de publicaciones
#     publicaciones_por_año = df_autor.groupby(
#         'Year').size()  # Número de publicaciones por año

#     # Obtener los años únicos para la gráfica
#     años = sorted(publicaciones_por_año.index)

#     # Agrupar por el año y sumar el total de citas
#     citas_por_año = df_autor.groupby(
#         'Year')['Total de Citas'].sum()  # Total de citas por año

#     # Obtener el valor máximo para escalar ejes
#     max_publicaciones = publicaciones_por_año.max()
#     max_citas = citas_por_año.max()

#     # Crear la gráfica con Plotly
#     fig = go.Figure()

#     # Agregar las barras para las publicaciones (Eje izquierdo)
#     fig.add_trace(go.Bar(
#         x=años,
#         y=publicaciones_por_año,
#         name='Publicaciones',
#         yaxis='y1',
#         width=0.6 
#     ))

#     # Agregar la línea para las citas (Eje derecho)
#     fig.add_trace(go.Scatter(
#         x=años,
#         y=citas_por_año,
#         mode='lines+markers',
#         name='Citas',
#         line=dict(color='crimson'),
#         yaxis='y2'
#     ))

#     # Configurar los ejes
#     fig.update_layout(
#         template='plotly_white',
#         title=f"Total de Citas y publicaciones para {autor_seleccionado} del periodo 2000–2024",
#         bargap=0.2,
#         xaxis_title='Año',
#         yaxis=dict(
#             title='Número Publicaciones',
#             side='left',
#             range=[0, max_publicaciones + 1]
#         ),
#         yaxis2=dict(
#             title='Total Citas',
#             overlaying='y',
#             side='right',
#             range=[0, max_citas + 1]
#         ),
#         legend=dict(orientation='h', x=0.95, xanchor='center', y=1.25),
#         xaxis=dict(
#             title='Año',
#             tickmode='linear',
#             dtick=1
#         )
#     )

#     # Mostrar la gráfica en Streamlit
#     st.plotly_chart(fig)


# Función para gráfica las citas y publicaciones por año
def graficar_citas_publicaciones(df_autor, autor_seleccionado, df_patentes, df_snii):
    # Filtrar autor
    df_autor = (
        df_autor.dropna(subset=['Investigador'])
          .query("Investigador == @autor_seleccionado")
          .copy()
    )
    df_autor = df_autor[(df_autor['Publication Year'] >= 2000) & 
                        (df_autor['Publication Year'] <= 2024)]
    df_autor['Year'] = df_autor['Publication Year'].astype(int)
    # Agrupar por el año y contar el número de publicaciones
    publicaciones_por_año = df_autor.groupby('Year').size()
    # Agrupar por el año y sumar el total de citas
    citas_por_año = df_autor.groupby('Year')['Total de Citas'].sum()
    # Obtener los años únicos para la gráfica
    años = sorted(publicaciones_por_año.index)
    # Obtener el valor máximo para escalar ejes
    max_publicaciones = publicaciones_por_año.max()
    max_citas = citas_por_año.max()
    # Crear la gráfica con Plotly
    fig = go.Figure()
    # Agregar las barras para las publicaciones (Eje izquierdo)
    fig.add_trace(go.Bar(
        x=años,
        y=publicaciones_por_año,
        name='Publicaciones',
        yaxis='y1',
        width=0.6 
    ))

    # Agregar la línea para las citas (Eje derecho)
    fig.add_trace(go.Scatter(
        x=años,
        y=citas_por_año,
        mode='lines+markers',
        name='Citas',
        line=dict(color='crimson'),
        yaxis='y2'
    ))

    # --- SNII: sombrear período activo ---
    if not df_snii.empty:
        rango_s = df_snii.at[0, 'Años Activos']  # p.e. "2017 - 2024"
        if rango_s:
            partes = re.split(r'\s*[-–]\s*', rango_s)
            if len(partes) == 2:
                inicio_s, fin_s = map(int, partes)
                inicio_s = max(inicio_s, 2000)
                fin_s    = min(fin_s, 2023)
                if inicio_s <= fin_s:
                    # Sombreado de fondo
                    fig.add_shape(
                        type='rect',
                        x0=inicio_s, x1=fin_s,
                        y0=0, y1=max_publicaciones + 1,
                        fillcolor='#00CED1',
                        opacity=0.25,
                        layer='below'
                    )
                    # Trazar línea para la leyenda
                    etiqueta_s = f"SNII activo: {inicio_s}–{fin_s}"
                    fig.add_trace(go.Scatter(
                        x=[inicio_s, fin_s],
                        y=[max_publicaciones + 1] * 2,
                        mode='lines',
                        line=dict(color='#00CED1', width=4),
                        name=etiqueta_s,
                        showlegend=True
                    ))

    # --- Patentes: sombrear período activo (igual al SNII) ---
    if not df_patentes.empty:
        rango_p   = df_patentes['Años activos'].iloc[0]
        total_pat = int(df_patentes['Total Patentes'].sum())
        if rango_p:
            partes = re.split(r'\s*[-–]\s*', rango_p)
            if len(partes) == 2:
                inicio_p, fin_p = map(int, partes)
                inicio_p = max(inicio_p, 2000)
                fin_p    = min(fin_p, 2023)
                if inicio_p <= fin_p:
                    # Sombreado de fondo
                    fig.add_shape(
                        type='rect',
                        x0=inicio_p, x1=fin_p,
                        y0=0, y1=max_publicaciones + 1,
                        fillcolor='#FFA500', opacity=0.25, layer='below'
                    )
                    # Trazar línea invisible sólo para la leyenda
                    etiqueta = f"Patentes activas: {rango_p} (Total: {total_pat})"
                    fig.add_trace(go.Scatter(
                        x=[inicio_p, fin_p],
                        y=[max_publicaciones + 1]*2,
                        mode='lines',
                        line=dict(color='#FFA500', width=4),
                        name=etiqueta,
                        showlegend=True
                    ))


    # Configurar los ejes
    fig.update_layout(
        template='plotly_white',
        title=f"Total de Citas y publicaciones para {autor_seleccionado} del periodo (2000–2024)",
        bargap=0.2,
        xaxis_title='Año',
        yaxis=dict(
            title='Número Publicaciones',
            side='left',
            range=[0, max_publicaciones + 1]
        ),
        yaxis2=dict(
            title='Total Citas',
            overlaying='y',
            side='right',
            range=[0, max_citas + 1]
        ),
        legend=dict(orientation='h', x=0.95, xanchor='center', y=1.25),
        xaxis=dict(
            title='Año',
            tickmode='linear',
            dtick=1
        )
    )

    # Mostrar la gráfica en Streamlit
    st.plotly_chart(fig)




#Funcion para mostrar los datos de Patentes
def buscar_datos_patentes(maestro, patentes, autor_seleccionado):
    """
    Busca en el maestro el inventor_id del autor seleccionado
    y retorna un DataFrame con sus patentes.
    """
    # Eliminamos los NAN de la columna 'inventor_id'
    maestro = maestro.dropna(subset=['inventor_id'])
    # Normalizar tipo y formato de inventor_id
    maestro['inventor_id']  = maestro['inventor_id'].astype(str).str.strip()
    patentes['inventor_id'] = patentes['inventor_id'].astype(str).str.strip()

    # Obtener inventor_id(s) del maestro
    raw_ids = maestro.loc[
        maestro['NOMBRE SNII'].str.strip() == autor_seleccionado.strip(),
        'inventor_id'
    ]
    ids = [i for i in raw_ids.unique() if i and i.lower() != 'nan']
    if len(ids) == 0:
        return pd.DataFrame()  # sin coincidencias
    
    # debug: ver ids encontrados
    # st.write("IDs encontrados:", ids)
    # Renombramos las columnas years active y Cites
    patentes.rename(columns={'years active': 'Años activos', 'Cites': 'Citas', 'Patents':'Total Patentes'}, inplace=True)

    # Columnas a extraer
    cols = [
        'Total Patentes',
        'Citas',
        'Años activos',
        'INSTITUCIÓN Pública= 1; Privada= 0',
        'Posgrado SI= 1 NO= 0',
        'Puesto',
        'Nacionalidad'
    ]

    # Filtrar por inventor_id y devolver
    return (
        patentes
        .loc[patentes['inventor_id'].isin(ids), cols]
        .reset_index(drop=True)
    )

# Funcion para mostrar los datos del SNII
def buscar_datos_snii(maestro, snii, autor_seleccionado):
    """
    Busca el CVU del autor en el maestro y filtra el DataFrame snii.
    Calcula el rango de años activos y extrae el último estado y áreas temáticas.
    """
    # 1. Preparar maestro: quedarnos solo with NOMBRE SNII y CVU válidos
    df_m = (
        maestro
        .dropna(subset=['NOMBRE SNII','CVU'])
        .assign(
            **{
                'NOMBRE SNII': lambda d: d['NOMBRE SNII'].astype(str).str.strip(),
                'CVU':          lambda d: d['CVU'].astype(str).str.strip()
            }
        )
    )
    # 2. Obtener CVU(s) del autor
    cvus = df_m.loc[
        df_m['NOMBRE SNII'] == autor_seleccionado.strip(),
        'CVU'
    ].unique().tolist()
    cvus = [c for c in cvus if c and c.lower() != 'nan']
    if not cvus:
        return pd.DataFrame()

    # 3. Filtrar snii por esos CVU
    df_s = (
        snii
        .assign(CVU=lambda d: d['CVU'].astype(str).str.strip())
        .loc[lambda d: d['CVU'].isin(cvus)]
    )
    if df_s.empty:
        return pd.DataFrame()

    # 4. Calcular rango de años activos
    años = (
        pd.to_numeric(df_s['AÑO'], errors='coerce')
          .dropna()
          .astype(int)
          .sort_values()
    )
    inicio, fin = (años.min(), años.max()) if not años.empty else (None, None)
    rango_activo = f"{inicio} - {fin}" if inicio is not None and fin is not None else ""

    # 5. Extraer último registro (por año máximo)
    idx_ult = años.idxmax()
    ultimo = df_s.loc[idx_ult]

    # 6. Construir resultado
    resultado = {
        'Años Activos':              [rango_activo],
        'NOBILIS':                   [ultimo.get('NOBILIS')],
        'NIVEL':                     [ultimo.get('NIVEL')],
        'FECHA DE FIN DE VIGENCIA':  [ultimo.get('FECHA DE FIN DE VIGENCIA')],
        'INSTITUCIÓN DE ADSCRIPCIÓN':[ultimo.get('INSTITUCIÓN DE ADSCRIPCIÓN')],
        'PAÍS':                      [ultimo.get('PAÍS')],
        'ÁREA DEL CONOCIMIENTO':     [df_s['ÁREA DEL CONOCIMIENTO'].dropna().unique().tolist()],
        'DISCIPLINA':                [df_s['DISCIPLINA'].dropna().unique().tolist()],
        'SUBDISCIPLINA':             [df_s['SUBDISCIPLINA'].dropna().unique().tolist()],
        'ESPECIALIDAD':              [df_s['ESPECIALIDAD'].dropna().unique().tolist()]
    }

    return pd.DataFrame(resultado)

# ----------------------- Preprocessor -----------------------------------------
# Creación del preprocessor una vez
numeric_features = ['Total de Citas', 'Promedio por año'] + \
    [col for col in data.columns if col.isdigit() and 2000 <= int(col) <= 2024]
categorical_features = ['Title', 'Investigador', 'Corporate Authors', 'Book Editors', 'Source Title']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Ajustar el preprocesador a los datos completos
preprocessor.fit(data)
# ----------------------- Streamlit --------------------------------------------
def mostrar_buscar_investigador(rutaWoS):
    # Cargar el archivo CSV y eliminar duplicados de autores
    dfWoS = pd.read_csv(rutaWoS)
    autores_unicos = dfWoS['Investigador'].drop_duplicates().sort_values()

    # Configuración de la app en Streamlit
    st.title("📊 Análisis de Investigadores")

    # Selector de autor
    # Lista original de autores
    autores = list(autores_unicos)

    # Si ya hay selección previa, rotamos la lista para que empiece por ella
    if 'autor_seleccionado' in st.session_state:
        sel = st.session_state.autor_seleccionado
        if sel in autores:
            i = autores.index(sel)
            opciones = autores[i:] + autores[:i]
        else:
            opciones = autores
    else:
        opciones = autores

    # Desplegable con la lista rotada
    autor_seleccionado = st.selectbox(
        "Selecciona un investigador",
        opciones,
        index=0,
        key="autor_seleccionado"
    )

    # Mostrar automáticamente los datos del autor seleccionado
    if autor_seleccionado:
        try:
            # Procesar la información del autor seleccionado
            df_publicaciones = procesar_autor(dfWoS, autor_seleccionado)
            # Calcular el resumen
            df_resumen = calcular_resumen(dfWoS, autor_seleccionado)
            # Busca los datos de la patentes
            df_patentes = buscar_datos_patentes(maestro, patentes, autor_seleccionado)
            # Busca los datos del SNII
            df_snii = buscar_datos_snii(maestro, snii, autor_seleccionado)

            st.write(f"## Información para {autor_seleccionado}")
            # Gráfica con los datos
            graficar_citas_publicaciones(dfWoS, autor_seleccionado, df_patentes, df_snii)
            # Dividir en dos columnas con proporciones ajustadas
            col1, col4 = st.columns([1, 2])
            col2 = st.columns([2])[0]

            # Mostrar el resumen en la primera columna centrado
            with col1:
                st.write("#### Métrica de citas")
                if df_resumen.empty:
                    st.write("No se encontraron datos de citas para este autor.")
                else:
                    # Mostrar el resumen de citas
                    st.dataframe(df_resumen)

                st.write("#### Patentes")
                if df_patentes.empty:
                    st.write("No se encontraron patentes para este autor.")
                else:
                    st.dataframe(df_patentes.T, use_container_width=True)

            # Mostrar los datos de publicaciones en la segunda columna
            with col2:
                st.write("#### Datos de Publicaciones ")
                st.dataframe(df_publicaciones)

            with col4:
                st.write("#### Datos del SNII")
                if df_snii.empty:
                    st.write("No se encontraron datos del SNII para este autor.")
                else:
                    # Mostrar el rango de años activos y los datos del SNII
                    st.dataframe(df_snii.T)

        except Exception as e:
            st.error(f"Error procesando los datos: {e}")