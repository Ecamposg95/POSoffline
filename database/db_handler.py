# database/db_handler.py
import sqlite3
import os
from datetime import datetime



def init_db():
    os.makedirs("data", exist_ok=True)  # Asegura que la carpeta exista

    conn = sqlite3.connect("data/pos.db")
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

# database/db_handler.py

def get_all_products():
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_product(sku, nombre, precio1, precio2, precio3, stock, categoria, departamento):
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento))
    conn.commit()
    conn.close()


def update_product(prod_id, sku, nombre, precio1, precio2, precio3, stock, categoria, departamento):
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET sku=?, nombre=?, precio1=?, precio2=?, precio3=?, stock=?, categoria=?, departamento=?
        WHERE id=?
    """, (sku, nombre, precio1, precio2, precio3, stock, categoria, departamento, prod_id))
    conn.commit()
    conn.close()


def delete_product(prod_id):
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()


def add_venta(carrito):
    conn = sqlite3.connect("data/pos.db")
    cursor = conn.cursor()

    total = sum(precio * cantidad for (_, _, precio, cantidad) in carrito)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
    venta_id = cursor.lastrowid

    for prod_id, _, precio, cantidad in carrito:
        subtotal = precio * cantidad
        cursor.execute("INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                       (venta_id, prod_id, cantidad, subtotal))
        cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_id))

    conn.commit()
    conn.close()