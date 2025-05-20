# Importaciones Menu
from Menu.utilidades import RUTA_PUBLICACIONES, RUTA_ANALISIS
from Menu.inicio import mostrar_inicio
from Menu.buscarInvestigador import mostrar_buscar_investigador
import time
# Librerías de visualización
import streamlit as st
# Otras librerías
from streamlit_option_menu import option_menu
# ---------------- Configuración de la página -----------------------------------
st.set_page_config(page_title="Investigadores", layout="wide")
st.sidebar.image("img/CBI.png")
# ----------------------------- Menú lateral ------------------------------------
# Los iconos que usa son de Bootstrap Icons
with st.sidebar:
    st.title("Análisis de Investigadores")

    selected = option_menu(
        "Menú",
        options=["Inicio", "Información por Investigador"],
        icons=['house', 'search'],
        menu_icon="clipboard-data-fill",
        default_index=0
    )
# -------------------------------------------------------------------------------
# Dashboard principal
if selected == "Inicio":
    st.toast("Has seleccionado Inicio")
    mostrar_inicio(RUTA_ANALISIS)
elif selected == "Información por Investigador":
    # Mostrar el mensaje en el contenedor
    st.toast("Has seleccionado Información por Investigador")
    mostrar_buscar_investigador(RUTA_PUBLICACIONES)
# -------------------------------------------------------------------------------