# gui/productos_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QInputDialog
)
from database.db_handler import get_all_products, add_product, delete_product, update_product


class ProductosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.setMinimumSize(600, 400)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock"])
        self.layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Agregar Producto")
        self.btn_edit = QPushButton("Editar Seleccionado")
        self.btn_delete = QPushButton("Eliminar Seleccionado")

        self.btn_add.clicked.connect(self.agregar_producto)
        self.btn_edit.clicked.connect(self.editar_producto)
        self.btn_delete.clicked.connect(self.eliminar_producto)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        self.layout.addLayout(btn_layout)

        self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        productos = get_all_products()
        for row_idx, producto in enumerate(productos):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(producto):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def agregar_producto(self):
        nombre, ok1 = QInputDialog.getText(self, "Nombre", "Nombre del producto:")
        if not ok1 or not nombre: return
        precio, ok2 = QInputDialog.getDouble(self, "Precio", "Precio del producto:")
        if not ok2: return
        stock, ok3 = QInputDialog.getInt(self, "Stock", "Stock inicial:")
        if not ok3: return
        add_product(nombre, precio, stock)
        self.load_products()

    def editar_producto(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un producto.")
            return
        prod_id = int(self.table.item(selected, 0).text())
        nombre, _ = QInputDialog.getText(self, "Nombre", "Nuevo nombre:", text=self.table.item(selected, 1).text())
        precio, _ = QInputDialog.getDouble(self, "Precio", "Nuevo precio:", value=float(self.table.item(selected, 2).text()))
        stock, _ = QInputDialog.getInt(self, "Stock", "Nuevo stock:", value=int(self.table.item(selected, 3).text()))
        update_product(prod_id, nombre, precio, stock)
        self.load_products()

    def eliminar_producto(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un producto.")
            return
        prod_id = int(self.table.item(selected, 0).text())
        confirm = QMessageBox.question(self, "Eliminar", "¿Eliminar este producto?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            delete_product(prod_id)
            self.load_products()
