# gui/ventas_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QCompleter
)
from PySide6.QtCore import Qt
from database.db_handler import get_all_products, add_venta


class VentasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Venta Actual")
        self.setMinimumSize(900, 600)

        self.carrito = []  # lista de (id, nombre, precio, cantidad)
        self.productos_disponibles = get_all_products()

        layout = QVBoxLayout(self)

        # Campo de búsqueda con autocompletado
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.actualizar_completador)

        self.completer = QCompleter([p[1] for p in self.productos_disponibles])
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(self.completer)

        self.btn_buscar = QPushButton("Agregar")
        self.btn_buscar.clicked.connect(self.buscar_y_agregar)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_buscar)
        layout.addLayout(search_layout)

        # Tabla de carrito
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", "Acciones"])
        self.table.cellChanged.connect(self.editar_cantidad_manual)
        layout.addWidget(self.table)

        # Total y botón de pagar
        bottom_layout = QHBoxLayout()
        self.label_total = QLabel("Total: $0.00")
        self.label_total.setStyleSheet("font-weight: bold; font-size: 18px;")
        self.btn_pagar = QPushButton("Pagar")
        self.btn_pagar.setStyleSheet("background-color: #00b8c5; color: white; padding: 10px;")
        self.btn_pagar.clicked.connect(self.pagar)

        bottom_layout.addWidget(self.label_total)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_pagar)
        layout.addLayout(bottom_layout)

    def actualizar_completador(self):
        texto = self.search_input.text().lower()
        coincidencias = [p[1] for p in self.productos_disponibles if texto in p[1].lower()]
        self.completer.model().setStringList(coincidencias)

    def buscar_y_agregar(self):
        texto = self.search_input.text().strip().lower()
        if not texto:
            return
        for prod in self.productos_disponibles:
            if texto == prod[1].lower():
                self.agregar_al_carrito(prod)
                self.search_input.clear()
                return
        QMessageBox.information(self, "No encontrado", "Producto no encontrado.")

    def agregar_al_carrito(self, producto):
        prod_id, nombre, precio, stock = producto
        for i, item in enumerate(self.carrito):
            if item[0] == prod_id:
                if item[3] < stock:
                    self.carrito[i] = (prod_id, nombre, precio, item[3] + 1)
                else:
                    QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock} unidades de {nombre}.")
                self.actualizar_tabla()
                return
        if stock > 0:
            self.carrito.append((prod_id, nombre, precio, 1))
        else:
            QMessageBox.warning(self, "Sin stock", f"El producto {nombre} está agotado.")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        self.table.blockSignals(True)  # evitar loops con cellChanged
        self.table.setRowCount(0)
        total = 0

        for i, item in enumerate(self.carrito):
            prod_id, nombre, precio, cantidad = item
            subtotal = precio * cantidad
            total += subtotal

            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(nombre))
            self.table.setItem(i, 1, QTableWidgetItem(f"${precio:.2f}"))

            cantidad_item = QTableWidgetItem(str(cantidad))
            cantidad_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, cantidad_item)

            self.table.setItem(i, 3, QTableWidgetItem(f"${subtotal:.2f}"))

            # Botones + y -
            btn_mas = QPushButton("+")
            btn_menos = QPushButton("–")
            btn_mas.clicked.connect(lambda _, idx=i: self.cambiar_cantidad(idx, 1))
            btn_menos.clicked.connect(lambda _, idx=i: self.cambiar_cantidad(idx, -1))

            acciones = QWidget()
            h = QHBoxLayout(acciones)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(btn_menos)
            h.addWidget(btn_mas)
            self.table.setCellWidget(i, 4, acciones)

        self.label_total.setText(f"Total: ${total:.2f}")
        self.table.blockSignals(False)

    def cambiar_cantidad(self, row, delta):
        prod_id, nombre, precio, cantidad = self.carrito[row]
        stock = [p[3] for p in self.productos_disponibles if p[0] == prod_id][0]
        nueva_cantidad = cantidad + delta

        if nueva_cantidad < 1:
            self.carrito.pop(row)
        elif nueva_cantidad <= stock:
            self.carrito[row] = (prod_id, nombre, precio, nueva_cantidad)
        else:
            QMessageBox.warning(self, "Límite", f"No hay suficiente stock para {nombre}.")

        self.actualizar_tabla()

    def editar_cantidad_manual(self, row, column):
        if column == 2:
            try:
                nueva = int(self.table.item(row, column).text())
                if nueva < 1:
                    self.carrito.pop(row)
                else:
                    prod_id, nombre, precio, _ = self.carrito[row]
                    stock = [p[3] for p in self.productos_disponibles if p[0] == prod_id][0]
                    if nueva <= stock:
                        self.carrito[row] = (prod_id, nombre, precio, nueva)
                    else:
                        QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock} unidades disponibles.")
                self.actualizar_tabla()
            except ValueError:
                QMessageBox.warning(self, "Error", "Cantidad no válida")

    def pagar(self):
        if not self.carrito:
            QMessageBox.information(self, "Carrito vacío", "Agrega productos antes de pagar.")
            return

        add_venta(self.carrito)
        QMessageBox.information(self, "Venta realizada", "¡Venta registrada con éxito!")
        self.carrito.clear()
        self.actualizar_tabla()
