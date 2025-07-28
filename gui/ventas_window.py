from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QCompleter
)
from PySide6.QtCore import Qt, QStringListModel
from database.db_handler import get_all_products, add_venta
import subprocess


class VentasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Venta Actual")
        self.setMinimumSize(900, 600)

        self.carrito = []  # lista de (id, nombre, [precios], cantidad, idx_precio)
        self.productos_disponibles = get_all_products()

        layout = QVBoxLayout(self)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto por nombre...")
        self.search_input.textChanged.connect(self.actualizar_completador)

        self.lista_autocompletado = [p[2] for p in self.productos_disponibles]  # nombre = p[2]
        self.modelo_completado = QStringListModel(self.lista_autocompletado)
        self.completer = QCompleter(self.modelo_completado)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.autocompletar_producto)
        self.search_input.setCompleter(self.completer)

        self.btn_buscar = QPushButton("Agregar")
        self.btn_buscar.clicked.connect(self.buscar_y_agregar)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_buscar)
        layout.addLayout(search_layout)

        # Tabla de carrito
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", "Precio Usado", "Acciones"])
        self.table.cellChanged.connect(self.editar_cantidad_manual)
        layout.addWidget(self.table)

        # Total y botón pagar
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
        texto = self.search_input.text().strip().lower()
        coincidencias = []
        for prod in self.productos_disponibles:
            nombre = str(prod[2]).lower()  # nombre = p[2]
            if texto in nombre:
                coincidencias.append(prod[2])
        self.modelo_completado.setStringList(coincidencias)

    def autocompletar_producto(self, texto):
        for prod in self.productos_disponibles:
            if prod[2].lower() == texto.lower():  # nombre = p[2]
                self.agregar_al_carrito(prod)
                self.search_input.clear()
                return

    def buscar_y_agregar(self):
        texto = self.search_input.text().strip().lower()
        if not texto:
            return
        for prod in self.productos_disponibles:
            if texto == prod[2].lower():  # nombre = p[2]
                self.agregar_al_carrito(prod)
                self.search_input.clear()
                return
        QMessageBox.information(self, "No encontrado", "Producto no encontrado.")

    def agregar_al_carrito(self, producto):
        prod_id, sku, nombre, precio1, precio2, precio3, stock, categoria, departamento = producto
        precios = [precio1, precio2, precio3]

        # Buscar si ya está en el carrito
        for i, item in enumerate(self.carrito):
            if item[0] == prod_id:
                if item[3] < stock:
                    self.carrito[i] = (prod_id, nombre, precios, item[3] + 1, item[4])
                else:
                    QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock} unidades de {nombre}.")
                self.actualizar_tabla()
                return

        if stock > 0:
            self.carrito.append((prod_id, nombre, precios, 1, 0))
        else:
            QMessageBox.warning(self, "Sin stock", f"El producto {nombre} está agotado.")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        total = 0
        for i, item in enumerate(self.carrito):
            prod_id, nombre, precios, cantidad, precio_idx = item
            precio = precios[precio_idx] if precios[precio_idx] else precios[0]
            subtotal = precio * cantidad
            total += subtotal
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(nombre))
            self.table.setItem(i, 1, QTableWidgetItem(f"${precio:.2f}"))
            cantidad_item = QTableWidgetItem(str(cantidad))
            cantidad_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, cantidad_item)
            self.table.setItem(i, 3, QTableWidgetItem(f"${subtotal:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"Precio {precio_idx+1}"))

            acciones_layout = QHBoxLayout()
            acciones_layout.setContentsMargins(0, 0, 0, 0)
            acciones_widget = QWidget()

            btn_menos = QPushButton("–")
            btn_menos.clicked.connect(lambda _, idx=i: self.cambiar_cantidad(idx, -1))
            btn_mas = QPushButton("+")
            btn_mas.clicked.connect(lambda _, idx=i: self.cambiar_cantidad(idx, 1))
            btn_precio = QPushButton("💲")
            btn_precio.clicked.connect(lambda _, idx=i: self.cambiar_precio(idx))
            btn_eliminar = QPushButton("❌")
            btn_eliminar.clicked.connect(lambda _, idx=i: self.eliminar_producto(idx))

            for btn in [btn_menos, btn_mas, btn_precio, btn_eliminar]:
                acciones_layout.addWidget(btn)
            acciones_widget.setLayout(acciones_layout)
            self.table.setCellWidget(i, 5, acciones_widget)

        self.label_total.setText(f"Total: ${total:.2f}")
        self.table.blockSignals(False)

    def cambiar_precio(self, row):
        prod_id, nombre, precios, cantidad, precio_idx = self.carrito[row]
        nuevo_idx = (precio_idx + 1) % 3
        while precios[nuevo_idx] is None and nuevo_idx != precio_idx:
            nuevo_idx = (nuevo_idx + 1) % 3
        self.carrito[row] = (prod_id, nombre, precios, cantidad, nuevo_idx)
        self.actualizar_tabla()

    def eliminar_producto(self, row):
        self.carrito.pop(row)
        self.actualizar_tabla()

    def cambiar_cantidad(self, row, delta):
        prod_id, nombre, precios, cantidad, precio_idx = self.carrito[row]
        stock = [p[6] for p in self.productos_disponibles if p[0] == prod_id][0]
        nueva_cantidad = cantidad + delta
        if nueva_cantidad < 1:
            self.carrito.pop(row)
        elif nueva_cantidad <= stock:
            self.carrito[row] = (prod_id, nombre, precios, nueva_cantidad, precio_idx)
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
                    prod_id, nombre, precios, _, precio_idx = self.carrito[row]
                    stock = [p[6] for p in self.productos_disponibles if p[0] == prod_id][0]
                    if nueva <= stock:
                        self.carrito[row] = (prod_id, nombre, precios, nueva, precio_idx)
                    else:
                        QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock} unidades disponibles.")
                self.actualizar_tabla()
            except ValueError:
                QMessageBox.warning(self, "Error", "Cantidad no válida")

    def pagar(self):
        if not self.carrito:
            QMessageBox.information(self, "Carrito vacío", "Agrega productos antes de pagar.")
            return

        resumen = [(pid, nom, precios[precio_idx], cant) for pid, nom, precios, cant, precio_idx in self.carrito]
        add_venta(resumen)

        ticket = "\n".join([
            "     TICKET DE VENTA     ",
            "--------------------------",
            *[f"{nombre} x{cantidad}  ${precio * cantidad:.2f}" for _, nombre, precio, cantidad in resumen],
            "--------------------------",
            f"TOTAL: ${sum(p * c for _, _, p, c in resumen):.2f}",
            "\nGracias por su compra\n\n\n"
        ])

        try:
            subprocess.run(["lp", "-d", "SeafonPOS58"], input=ticket.encode(), check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error de impresión", f"No se pudo imprimir el ticket:\n{e}")

        QMessageBox.information(self, "Venta realizada", "¡Venta registrada con éxito!")
        self.carrito.clear()
        self.actualizar_tabla()
