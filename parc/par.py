import sqlite3
from datetime import datetime

# ==============================
# Conexión y creación de tablas
# ==============================
def conectar():
    conn = sqlite3.connect("tienda.db")
    return conn

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        cantidad_disponible INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER NOT NULL,
        cantidad_vendida INTEGER NOT NULL,
        fecha_venta TEXT NOT NULL,
        FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
    )
    """)

    conn.commit()
    conn.close()

# ==============================
# Funciones CRUD
# ==============================
def registrar_producto(nombre, precio, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Productos (nombre, precio, cantidad_disponible) VALUES (?, ?, ?)",
                   (nombre, precio, cantidad))
    conn.commit()
    conn.close()
    print(" Producto registrado.")

def consultar_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Productos")
    productos = cursor.fetchall()
    conn.close()
    for p in productos:
        print(f"ID:{p[0]} | {p[1]} | Precio:${p[2]:.2f} | Stock:{p[3]}")

def actualizar_producto(id_producto, nuevo_precio=None, nueva_cantidad=None):
    conn = conectar()
    cursor = conn.cursor()
    if nuevo_precio is not None:
        cursor.execute("UPDATE Productos SET precio=? WHERE id_producto=?", (nuevo_precio, id_producto))
    if nueva_cantidad is not None:
        cursor.execute("UPDATE Productos SET cantidad_disponible=? WHERE id_producto=?", (nueva_cantidad, id_producto))
    conn.commit()
    conn.close()
    print(" Producto actualizado.")

def eliminar_producto(id_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Productos WHERE id_producto=?", (id_producto,))
    conn.commit()
    conn.close()
    print("Producto eliminado.")

def registrar_venta(id_producto, cantidad_vendida):
    conn = conectar()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN")  # Inicia transacción

        # Verificar existencia
        cursor.execute("SELECT cantidad_disponible FROM Productos WHERE id_producto=?", (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            raise Exception(" Producto no existe.")

        stock = producto[0]
        if stock < cantidad_vendida:
            raise Exception(" Stock insuficiente.")

        # Registrar venta
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Ventas (id_producto, cantidad_vendida, fecha_venta) VALUES (?, ?, ?)",
                       (id_producto, cantidad_vendida, fecha))

        # Provocar error controlado (ejemplo)
        # raise Exception("Error simulado después de registrar venta.")

        # Actualizar inventario
        nuevo_stock = stock - cantidad_vendida
        cursor.execute("UPDATE Productos SET cantidad_disponible=? WHERE id_producto=?",
                       (nuevo_stock, id_producto))

        conn.commit()
        print(" Venta registrada y stock actualizado.")

    except Exception as e:
        conn.rollback()
        print(f" Error: {e}. Operación cancelada.")

    finally:
        conn.close()

def historial_ventas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT V.id_venta, P.nombre, V.cantidad_vendida, V.fecha_venta
    FROM Ventas V
    JOIN Productos P ON V.id_producto = P.id_producto
    """)
    ventas = cursor.fetchall()
    conn.close()
    for v in ventas:
        print(f"Venta {v[0]} | Producto:{v[1]} | Cantidad:{v[2]} | Fecha:{v[3]}")

def menu():
    crear_tablas()
    while True:
        print("==========================")
        print("\n--- MENÚ ---")
        print("1. Registrar producto")
        print("2. Consultar productos")
        print("3. Actualizar producto")
        print("4. Eliminar producto")
        print("5. Registrar venta")
        print("6. Historial de ventas")
        print("7. Salir")
        print("==========================")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            precio = float(input("Precio: "))
            cantidad = int(input("Cantidad: "))
            registrar_producto(nombre, precio, cantidad)

        elif opcion == "2":
            consultar_productos()

        elif opcion == "3":
            idp = int(input("ID producto: "))
            precio = input("Nuevo precio (Enter para omitir): ")
            cantidad = input("Nueva cantidad (Enter para omitir): ")
            actualizar_producto(idp,
                                float(precio) if precio else None,
                                int(cantidad) if cantidad else None)

        elif opcion == "4":
            idp = int(input("ID producto: "))
            eliminar_producto(idp)

        elif opcion == "5":
            idp = int(input("ID producto: "))
            cant = int(input("Cantidad vendida: "))
            registrar_venta(idp, cant)

        elif opcion == "6":
            historial_ventas()

        elif opcion == "7":
            print(" Saliendo del programa.")
            break

        else:
            print(" Opción inválida.")

if __name__ == "__main__":
    menu()
