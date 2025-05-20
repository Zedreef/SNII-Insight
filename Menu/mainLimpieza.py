import logging
import Limpieza.LimpiezaColumnas as LimpiezaColumnas
import Limpieza.LimpiezaDatos as LimpiezaDatos
import Limpieza.LimpiezaNombres as LimpiezaNombres
import Limpieza.LimpiezaNombresFinal as LimpiezaNombresFinal
import Limpieza.UnionNombres as UnionNombres
import Limpieza.UltimoFiltro as UltimoFiltro

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    LimpiezaColumnas.main()
    LimpiezaDatos.main()
    LimpiezaNombres.main()
    LimpiezaNombresFinal.main()
    UnionNombres.main()
    UltimoFiltro.main()
    UnionNombres.main()

if __name__ == "__main__":

    logging.info("Empezando Limpieza de datos")
    main()
    logging.info("Fin de la Limpieza de datos.")