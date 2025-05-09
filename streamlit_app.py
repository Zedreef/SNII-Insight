# Importaciones Menu
from Menu.utilidades import RUTA_PUBLICACIONES
from Menu.inicio import mostrar_inicio
from Menu.buscarInvestigador import mostrar_buscar_investigador
# from Menu.comparar_investigadores import mostrar_comparar_investigadores
# from Menu.todos_investigadores import mostrar_todos_investigadores
# from Menu.analisis_coautoria import mostrar_analisis_coautoria
# from Menu.analisis_patentes import mostrar_analisis_patentes
# from Menu.kmeans_investigadores import mostrar_analisis_kmeans
# from Menu.Entrenamiento_Publicaciones import mostrar_keras

# Librerías de visualización
import streamlit as st

# Otras librerías
from streamlit_option_menu import option_menu

# ---------------- Integrantes Inteligencia Artificial --------------------------
# Ruiz Mora Diego                     2202000335
# Morales Mogollon Bryan              2202004306
# Fernandez Pineda Carlos Adrian      2162000644
# -------------------------------------------------------------------------------

# ---------------- Configuración de la página -----------------------------------
st.set_page_config(page_title="Investigadores", layout="wide")
st.sidebar.image("img/CBI.png")
# ----------------------------- Menú lateral ------------------------------------
# Los iconos que usa son de Bootstrap Icons
with st.sidebar:
    st.title("Análisis de Investigadores")

    selected = option_menu(
        "Menú",
        ["Inicio", "Información por Investigador", "Comparar investigadores", "Todos los investigadores",
         "Análisis de Coautoría", "Análisis de patentes","Análisis Kmeans","Análisis Keras",
         ],
        icons=['house', 'search', 'person-arms-up', 'people-fill', 'graph-up',
               'file-earmark-bar-graph-fill','bar-chart-fill','server'],
        menu_icon="clipboard-data-fill",
        default_index=0
    )
# -------------------------------------------------------------------------------
# Dashboard principal
if selected == "Inicio":
    mostrar_inicio()
elif selected == "Información por Investigador":
    mostrar_buscar_investigador(RUTA_PUBLICACIONES)
# elif selected == "Comparar investigadores":
#     mostrar_comparar_investigadores()
# elif selected == "Todos los investigadores":
#     mostrar_todos_investigadores()
# elif selected == "Análisis de Coautoría":
#     mostrar_analisis_coautoria()
# elif selected == "Análisis de patentes":
#     mostrar_analisis_patentes()
# elif selected == "Análisis Kmeans":
#     mostrar_analisis_kmeans()
# elif selected == "Análisis Keras":
#     mostrar_keras()