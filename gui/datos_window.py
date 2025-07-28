from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from database.db_handler import get_total_ventas


class DatosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Datos del Sistema")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)

        title = QLabel("Resumen del Sistema")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        total_ventas = get_total_ventas()
        total_label = QLabel(f"Total acumulado de ventas: ${total_ventas:.2f}")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("font-size: 16px; color: green;")

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(total_label)
