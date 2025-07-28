import sqlite3
import os
from datetime import datetime
import pandas as pd

DB_PATH = "data/pos.db"

def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        nombre TEXT NOT NULL,
        precio1 REAL NOT NULL,
        precio2 REAL,
        precio3 REAL,
        stock INTEGER NOT NULL,
        categoria TEXT,
        departamento TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        subtotal REAL,
        FOREIGN KEY(venta_id) REFERENCES ventas(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    )""")

    conn.commit()
    conn.close()

# ────────────────────────────────────────────────
# FUNCIONES DE PRODUCTOS
# ────────────────────────────────────────────────

def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_product(sku, nombre, precio1, precio2, precio3, stock, categoria, departamento):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO productos (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ SKU duplicado no insertado: {sku}")
    conn.close()

def update_product(prod_id, sku, nombre, precio1, precio2, precio3, stock, categoria, departamento):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET sku=?, nombre=?, precio1=?, precio2=?, precio3=?, stock=?, categoria=?, departamento=?
        WHERE id=?
    """, (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento, prod_id))
    conn.commit()
    conn.close()

def delete_product(prod_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()

# ────────────────────────────────────────────────
# FUNCIONES DE VENTAS
# ────────────────────────────────────────────────

def add_venta(carrito):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total = sum(precio * cantidad for (_, _, precio, cantidad) in carrito)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
    venta_id = cursor.lastrowid

    for prod_id, _, precio, cantidad in carrito:
        subtotal = precio * cantidad
        cursor.execute("""
            INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal)
            VALUES (?, ?, ?, ?)
        """, (venta_id, prod_id, cantidad, subtotal))

        cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_id))

    conn.commit()
    conn.close()


def get_total_ventas():
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM ventas")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0.0




# ────────────────────────────────────────────────
# IMPORTACIÓN MASIVA DESDE EXCEL
# ────────────────────────────────────────────────

def importar_productos_desde_excel(path):
    try:
        df = pd.read_excel(path)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return

    required_cols = {"SKU", "Nombre", "Precio 1", "Precio 2", "Precio 3", "Stock", "Categoría", "Departamento"}
    if not required_cols.issubset(set(df.columns)):
        print(f"❌ El archivo no tiene las columnas requeridas: {required_cols}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        sku = str(row["SKU"]).strip()
        cursor.execute("SELECT id FROM productos WHERE sku = ?", (sku,))
        existing = cursor.fetchone()

        if existing:
            # Actualiza si ya existe
            cursor.execute("""
                UPDATE productos SET
                    nombre = ?, precio1 = ?, precio2 = ?, precio3 = ?,
                    stock = ?, categoria = ?, departamento = ?
                WHERE sku = ?
            """, (
                row["Nombre"], row["Precio 1"], row["Precio 2"], row["Precio 3"],
                row["Stock"], row["Categoría"], row["Departamento"], sku
            ))
            print(f"🔄 Producto actualizado: {sku}")
        else:
            # Inserta si no existe
            cursor.execute("""
                INSERT INTO productos (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sku, row["Nombre"], row["Precio 1"], row["Precio 2"],
                row["Precio 3"], row["Stock"], row["Categoría"], row["Departamento"]
            ))
            print(f"✅ Producto insertado: {sku}")

    conn.commit()
    conn.close()
    print("✔️ Importación completada con éxito.")
