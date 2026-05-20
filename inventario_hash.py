TAMAÑO = 7  
def crear_producto(id_producto, nombre, precio, cantidad):
    return [id_producto, nombre, precio, cantidad]

#  INICIALIZAR LA TABLA HASH

def crear_tabla():
    tabla = []
    for i in range(TAMAÑO):
        tabla.append(None)      
    return tabla

#  FUNCIÓN HASH
#  Fórmula:  indice = id % TAMAÑO
# ─────────────────────────────────────────────────────────────
def funcion_hash(id_producto):
    return id_producto % TAMAÑO

def insertar(tabla, id_producto, nombre, precio, cantidad):
    "Inserta un producto en la tabla hash con sondeo lineal."
    indice_inicial = funcion_hash(id_producto)
    print(f"\n{'─'*55}")
    print(f"  Insertando: ID={id_producto}  |  {nombre}")
    print(f"  Índice calculado:  {id_producto} % {TAMAÑO} = {indice_inicial}")

    # sondeo lineal para encontrar celda disponible
    indice_actual = indice_inicial
    hubo_colision = False
    pasos = 0

    while pasos < TAMAÑO:
        celda = tabla[indice_actual]

        if celda is None:
            # Celda libre
            tabla[indice_actual] = crear_producto(id_producto, nombre, precio, cantidad)

            if hubo_colision:
                print(f"Insertado en índice {indice_actual} (tras resolver colisión)")
            else:
                print(f"Insertado en índice {indice_actual} (sin colisión)")
            return True

        else:
            # Celda ocupada
            if not hubo_colision:
                print(f" COLISIÓN en índice {indice_actual} "
                      f"(ocupado por ID={celda[0]} '{celda[1]}')")
                hubo_colision = True
            else:
                print(f" índice {indice_actual} ocupado por ID={celda[0]}, avanzando...")

            # Avanza al siguiente índice en forma circular
            indice_actual = (indice_actual + 1) % TAMAÑO
            pasos += 1

    # Si completó el ciclo sin espacio, tabla llena
    print(" La tabla está llena. No se pudo insertar.")
    return False

#  BUSCAR PRODUCTO POR ID

def buscar(tabla, id_producto):
    "Busca un producto por su ID. Retorna el producto o None."

    indice_inicial = funcion_hash(id_producto)

    print(f"\n{'─'*55}")
    print(f"  Buscando ID: {id_producto}")
    print(f"  Índice calculado:  {id_producto} % {TAMAÑO} = {indice_inicial}")

    indice_actual = indice_inicial
    pasos = 0

    while pasos < TAMAÑO:
        celda = tabla[indice_actual]

        if celda is None:
            print(f" Celda {indice_actual} vacía. Producto no encontrado.")
            return None

        if celda[0] == id_producto:
            if pasos == 0:
                print(f" Encontrado en índice {indice_actual} (acceso directo)")
            else:
                print(f" Encontrado en índice {indice_actual} (tras {pasos} sondeo(s))")
            return celda

        # El ID no coincide 
        print(f" índice {indice_actual} tiene ID={celda[0]}, buscando...")
        indice_actual = (indice_actual + 1) % TAMAÑO
        pasos += 1

    print(" Producto no encontrado.")
    return None

#  ELIMINAR PRODUCTO POR ID

ELIMINADO = ["__DEL__", "", 0, 0]   # marcador especial de celda eliminada

def eliminar(tabla, id_producto):
    "Elimina un producto marcando su celda como eliminada."

    indice_inicial = funcion_hash(id_producto)

    print(f"\n{'─'*55}")
    print(f"  Eliminando ID: {id_producto}")
    print(f"  Índice calculado:  {id_producto} % {TAMAÑO} = {indice_inicial}")

    indice_actual = indice_inicial
    pasos = 0

    while pasos < TAMAÑO:
        celda = tabla[indice_actual]

        if celda is None:
            print(f"Producto ID={id_producto} no encontrado.")
            return False

        if celda[0] == id_producto:
            tabla[indice_actual] = ELIMINADO   # marcar como eliminado
            print(f" Producto ID={id_producto} eliminado del índice {indice_actual}")
            return True

        indice_actual = (indice_actual + 1) % TAMAÑO
        pasos += 1

    print(f"Producto ID={id_producto} no encontrado.")
    return False

#  MOSTRAR LA TABLA HASH COMPLETA

def mostrar_tabla(tabla):
    "Muestra el estado actual de toda la tabla hash."

    print(f"\n{'═'*60}")
    print(f"   TABLA HASH — INVENTARIO DE PRODUCTOS")
    print(f"   Tamaño: {TAMAÑO} celdas  |  Función: id % {TAMAÑO}")
    print(f"{'═'*60}")
    print(f"  {'IDX':>4}  {'ID':>5}  {'NOMBRE':<18}  {'PRECIO':>8}  {'CANT':>5}")
    print(f"  {'─'*52}")

    ocupadas = 0
    for i in range(TAMAÑO):
        celda = tabla[i]

        if celda is None:
            print(f"  [ {i} ]  {'·  (vacía)'}")

        elif celda[0] == "__DEL__":
            print(f"  [ {i} ]  {'  (eliminada)'}")

        else:
            id_p   = celda[0]
            nombre = celda[1]
            precio = celda[2]
            cant   = celda[3]
            # Marcar si el producto está en su índice natural o fue desplazado
            idx_natural = funcion_hash(id_p)
            marca = "" if idx_natural == i else f"  hash natural: {idx_natural}"
            print(f"  [ {i} ]  {id_p:>5}  {nombre:<18}  ${precio:>7.2f}  {cant:>5}{marca}")
            ocupadas += 1

    print(f"  {'─'*52}")
    print(f"   Celdas ocupadas: {ocupadas}/{TAMAÑO}  |  "
          f"Factor de carga α = {ocupadas}/{TAMAÑO} = {ocupadas/TAMAÑO:.2f}")
    print(f"{'═'*60}")

#  MOSTRAR RESULTADO DE BÚSQUEDA

def mostrar_producto(producto):
    "Imprime los datos de un producto encontrado."
    if producto is None:
        return
    print(f"\n  ┌─ Resultado ───────────────────────────────")
    print(f"  │  ID       : {producto[0]}")
    print(f"  │  Nombre   : {producto[1]}")
    print(f"  │  Precio   : ${producto[2]:.2f}")
    print(f"  │  Cantidad : {producto[3]} unidades")
    print(f"  └───────────────────────────────────────────")

def menu():
    print("\n  ╔══════════════════════════════════╗")
    print("  ║   SISTEMA DE INVENTARIO HASH     ║")
    print("  ╠══════════════════════════════════╣")
    print("  ║  1. Insertar producto            ║")
    print("  ║  2. Buscar producto por ID       ║")
    print("  ║  3. Eliminar producto por ID     ║")
    print("  ║  4. Mostrar tabla completa       ║")
    print("  ║  5. Cargar datos de prueba       ║")
    print("  ║  0. Salir                        ║")
    print("  ╚══════════════════════════════════╝")
    opcion = input("  Opción: ").strip()
    return opcion


def pedir_int(mensaje):
    while True:
        valor = input(f"  {mensaje}: ").strip()
        if valor.lstrip("-").isdigit():
            return int(valor)
        print("Ingresa un número entero válido.")


def pedir_float(mensaje):
    while True:
        valor = input(f"  {mensaje}: ").strip()
        try:
            return float(valor)
        except ValueError:
            print("Ingresa un número válido.")


#  DATOS DE PRUEBA
#    IDs elegidos para forzar colisiones con TAMAÑO=7:
#    ID 10 → 10%7 = 3
#    ID 17 → 17%7 = 3  (colisión con 10)
#    ID 24 → 24%7 = 3  (colisión con 10 y 17)

def cargar_datos_prueba(tabla):
    print("\n  Cargando datos de prueba...")
    print("  (IDs 10, 17, 24 colisionan en el mismo índice)")

    productos = [
        (5,  "Laptop",       1299.99, 10),
        (10, "Mouse",          25.50, 50),
        (17, "Teclado",        45.00, 30),   # colisión con ID 10
        (24, "Monitor",       350.00, 15),   # colisión con ID 10 y 17
        (3,  "Auriculares",    89.99, 20),
        (6,  "Webcam",         75.00, 25),
    ]

    for prod in productos:
        insertar(tabla, prod[0], prod[1], prod[2], prod[3])

def main():
    print("\n" + "═"*60)
    print("   SISTEMA DE INVENTARIO CON TABLA HASH")
    print("   Estructura de Datos II — Ingeniería de Sistemas")
    print("   Técnica: Tabla Hash + Sondeo Lineal")
    print("═"*60)

    tabla = crear_tabla()  

    while True:
        opcion = menu()

        if opcion == "1":
            print("\n  ─── Nuevo Producto ───")
            id_p   = pedir_int("ID del producto (int)")
            nombre = input("  Nombre         : ").strip()
            precio = pedir_float("Precio (ej: 9.99)")
            cant   = pedir_int("Cantidad")
            insertar(tabla, id_p, nombre, precio, cant)

        elif opcion == "2":
            id_p = pedir_int("ID a buscar")
            resultado = buscar(tabla, id_p)
            mostrar_producto(resultado)

        elif opcion == "3":
            id_p = pedir_int("ID a eliminar")
            eliminar(tabla, id_p)

        elif opcion == "4":
            mostrar_tabla(tabla)

        elif opcion == "5":
            cargar_datos_prueba(tabla)
            mostrar_tabla(tabla)

        elif opcion == "0":
            break

        else:
            print(" Opción inválida. Elige entre 0 y 5.")
main()
