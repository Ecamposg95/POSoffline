from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt
from gui.productos_window import ProductosWindow
from gui.ventas_window import VentasWindow
from gui.datos_window import DatosWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data x POS - Sistema de Punto de Venta")
        self.setMinimumSize(1000, 600)

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout general
        main_layout = QHBoxLayout(central_widget)

        # Menú lateral
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Contenido principal
        self.stack = QStackedWidget()
        self.venta_actual_view = self.create_main_panel()
        self.stack.addWidget(self.venta_actual_view)

        main_layout.addWidget(self.stack, 1)

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setAlignment(Qt.AlignTop)

        # Logo / título
        title = QLabel("data ✱ POS")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("smartsitecompany")
        subtitle.setStyleSheet("font-size: 12px; color: white;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Botones del menú
        btn_venta = QPushButton("Ventas")
        btn_productos = QPushButton("Productos")
        btn_inventario = QPushButton("Inventario")
        btn_corte = QPushButton("Corte")
        btn_config = QPushButton("Configuración")
        btn_datos = QPushButton("Datos")  # Botón nuevo para ver estadísticas

        for btn in [btn_venta, btn_productos, btn_inventario, btn_corte, btn_config, btn_datos]:
            btn.setStyleSheet("text-align: left; padding: 10px; background: none; color: white;")
            layout.addWidget(btn)

        # Conexión de botones
        btn_productos.clicked.connect(self.abrir_productos)
        btn_venta.clicked.connect(self.abrir_ventas)
        btn_datos.clicked.connect(self.abrir_datos)

        # Estilo del sidebar
        sidebar.setStyleSheet("background-color: #6A3093;")
        return sidebar

    def create_main_panel(self):
        content = QWidget()
        layout = QVBoxLayout(content)

        # Encabezado
        header = QLabel("Venta Actual")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #4A0072;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Panel informativo temporal
        panel = QLabel("Aquí irán los tickets pendientes, la venta activa y la búsqueda.")
        panel.setStyleSheet("background-color: white; padding: 40px; border-radius: 12px;")
        panel.setAlignment(Qt.AlignCenter)
        layout.addWidget(panel)

        content.setStyleSheet("background-color: #edf0f9; padding: 20px;")
        return content

    def abrir_productos(self):
        self.productos_win = ProductosWindow()
        self.productos_win.show()
    
    def abrir_ventas(self):
        self.ventas_win = VentasWindow()
        self.ventas_win.show()

    def abrir_datos(self):
        self.datos_win = DatosWindow()
        self.datos_win.show()
