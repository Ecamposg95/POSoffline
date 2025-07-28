from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QInputDialog, QFileDialog
)
from database.db_handler import (
    get_all_products, add_product, delete_product,
    update_product, importar_productos_desde_excel
)


class ProductosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.setMinimumSize(900, 500)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "SKU", "Nombre", "Precio 1", "Precio 2", "Precio 3",
            "Stock", "Categoría", "Departamento"
        ])
        self.layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Agregar Producto")
        self.btn_edit = QPushButton("Editar Seleccionado")
        self.btn_delete = QPushButton("Eliminar Seleccionado")
        self.btn_importar = QPushButton("Importar desde Excel")

        self.btn_add.clicked.connect(self.agregar_producto)
        self.btn_edit.clicked.connect(self.editar_producto)
        self.btn_delete.clicked.connect(self.eliminar_producto)
        self.btn_importar.clicked.connect(self.importar_excel)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_importar)
        self.layout.addLayout(btn_layout)

        self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        productos = get_all_products()
        for row_idx, producto in enumerate(productos):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(producto):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def agregar_producto(self):
        sku, ok1 = QInputDialog.getText(self, "SKU", "Código de barras:")
        if not ok1 or not sku: return
        nombre, ok2 = QInputDialog.getText(self, "Nombre", "Nombre del producto:")
        if not ok2 or not nombre: return
        precio1, ok3 = QInputDialog.getDouble(self, "Precio 1", "Precio general:")
        if not ok3: return
        precio2, ok4 = QInputDialog.getDouble(self, "Precio 2", "Precio mayoreo:", decimals=2)
        if not ok4: return
        precio3, ok5 = QInputDialog.getDouble(self, "Precio 3", "Precio oferta:", decimals=2)
        if not ok5: return
        stock, ok6 = QInputDialog.getInt(self, "Stock", "Stock inicial:")
        if not ok6: return
        categoria, ok7 = QInputDialog.getText(self, "Categoría", "Categoría del producto:")
        if not ok7: return
        departamento, ok8 = QInputDialog.getText(self, "Departamento", "Departamento del producto:")
        if not ok8: return

        add_product(sku, nombre, precio1, precio2, precio3, stock, categoria, departamento)
        self.load_products()

    def editar_producto(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un producto.")
            return

        prod_id = int(self.table.item(selected, 0).text())
        sku = self.table.item(selected, 1).text()
        nombre = self.table.item(selected, 2).text()
        precio1 = float(self.table.item(selected, 3).text())
        precio2 = float(self.table.item(selected, 4).text())
        precio3 = float(self.table.item(selected, 5).text())
        stock = int(self.table.item(selected, 6).text())
        categoria = self.table.item(selected, 7).text()
        departamento = self.table.item(selected, 8).text()

        nuevo_sku, _ = QInputDialog.getText(self, "SKU", "Editar código de barras:", text=sku)
        nuevo_nombre, _ = QInputDialog.getText(self, "Nombre", "Editar nombre:", text=nombre)
        nuevo_precio1, _ = QInputDialog.getDouble(self, "Precio 1", "Editar precio general:", value=precio1)
        nuevo_precio2, _ = QInputDialog.getDouble(self, "Precio 2", "Editar precio mayoreo:", value=precio2)
        nuevo_precio3, _ = QInputDialog.getDouble(self, "Precio 3", "Editar precio oferta:", value=precio3)
        nuevo_stock, _ = QInputDialog.getInt(self, "Stock", "Editar stock:", value=stock)
        nueva_categoria, _ = QInputDialog.getText(self, "Categoría", "Editar categoría:", text=categoria)
        nuevo_departamento, _ = QInputDialog.getText(self, "Departamento", "Editar departamento:", text=departamento)

        update_product(prod_id, nuevo_sku, nuevo_nombre, nuevo_precio1, nuevo_precio2, nuevo_precio3,
                       nuevo_stock, nueva_categoria, nuevo_departamento)
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

    def importar_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo Excel", "", "Archivos Excel (*.xlsx)")
        if file_path:
            importar_productos_desde_excel(file_path)
            self.load_products()
