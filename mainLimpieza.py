import time
import Limpieza.LimpiezaColumnas as LimpiezaColumnas
import Limpieza.LimpiezaDatos as LimpiezaDatos
import Limpieza.LimpiezaNombres as LimpiezaNombres
import Limpieza.LimpiezaNombresFinal as LimpiezaNombresFinal

def main():
    LimpiezaColumnas.main()
    LimpiezaDatos.main()
    LimpiezaNombres.main()
    LimpiezaNombresFinal.main()

if __name__ == "__main__":
    inicio = time.time()
    print("=== Empezando Limpieza de datos ===")
    main()
    fin = time.time()
    print("=== Fin de la Limpieza de datos ===")
    tiempo_total_segundos = fin - inicio
    tiempo_total_horas = tiempo_total_segundos / 3600
    print(f"Tiempo total de ejecución FINAL: {tiempo_total_horas:.2f} horas")