def reformatear_nombre(nombre):
    """
    Cambia el formato de 'NOMBRE APELLIDO' a 'APELLIDO NOMBRE'
    """
    print(f"Procesando: {nombre}")  # Mensaje de depuración

    # Separar el nombre por espacios
    partes = nombre.split()

    # Verificar que el nombre tenga más de un componente (nombre y apellido)
    if len(partes) > 1:
        # Suponer que el último componente es el apellido y todo lo anterior es el nombre
        apellido = ' '.join(partes[-2:])  # Los últimos dos componentes son el apellido
        nombre = ' '.join(partes[:-2])  # Todos los componentes anteriores son el nombre
        reformatted_name = f"{apellido} {nombre}"
        print(f"Reformateado a: {reformatted_name}")  # Mensaje de depuración
        return reformatted_name

    print("Nombre sin cambios")  # Mensaje de depuración
    return nombre  # Si no tiene más de una parte, no hacer cambios

# Lista de ejemplo
lista = [
    "AARON TORRES HUERTA",
    "ALAN PAVLOVICH ABRIL",
    "ALEJANDRA ISABEL VARGAS SEGURA",
    "ALFREDO RAYA MONTANO",
    # ... (otros nombres)
]

# Aplicar la función a cada nombre en la lista
for nombre in lista:
    nuevo_nombre = reformatear_nombre(nombre)
    print(f"Nuevo nombre: {nuevo_nombre}\n")  # Mensaje de depuración final
