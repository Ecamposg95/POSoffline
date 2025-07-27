# gui/login_window.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QCheckBox, QMessageBox
)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Data x POS - Iniciar Sesión")
        self.setFixedSize(800, 500)

        self.setup_ui()

    def setup_ui(self):
        # Panel izquierdo con logo y fondo
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_palette = left_panel.palette()
        left_palette.setColor(QPalette.Window, QColor(106, 48, 147))  # Morado degradado
        left_panel.setAutoFillBackground(True)
        left_panel.setPalette(left_palette)

        logo = QLabel("data ✱ POS", left_panel)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        logo.setGeometry(50, 200, 300, 50)

        # Panel derecho con el formulario
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Iniciar Sesión")
        title.setFont(QFont("Arial", 18))
        layout.addWidget(title)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ejemplo@datax.com")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.remember_check = QCheckBox("Recuérdame")
        layout.addWidget(self.remember_check)

        login_button = QPushButton("Iniciar Sesión")
        login_button.setStyleSheet("background-color: #00b8c5; color: white; padding: 10px;")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        layout.addSpacing(10)
        layout.addWidget(QLabel("<a href='#'>¿Olvidaste tu contraseña?</a>"))
        layout.addWidget(QLabel("¿Aún no estás registrado? <a href='#'>Crea una cuenta</a>"))

        # Distribución final
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Credenciales de prueba
        if email == "admin" and password == "1234":
            self.on_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")
