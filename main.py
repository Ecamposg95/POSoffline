# main.py
import sys
from PySide6.QtWidgets import QApplication
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from database.db_handler import init_db


def main():
    init_db()
    app = QApplication(sys.argv)

    # Cargaremos main_window desde aquí para mantener el control
    main_window = MainWindow()

    def show_main_window():
        main_window.show()

    login_win = LoginWindow(on_login_success=show_main_window)
    login_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
