import streamlit as st
import pandas as pd
import plotly.express as px
from Menu.utilidades import procesar_archivos, RUTA_GUARDADO

def mostrar_inicio():
    correctos, incorrectos, archivos_incorrectos = procesar_archivos(RUTA_GUARDADO)

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
