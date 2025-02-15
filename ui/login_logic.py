from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
import sys

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/login.ui", self)  # Load UI file dynamically
            self.btnLogin.clicked.connect(self.handle_login)  # Connect button
        except Exception as e:
            self.show_error("Error loading UI", str(e))

    def handle_login(self):
        try:
            username = self.txtUsername.text()
            password = self.txtPassword.text()

            if not username or not password:
                raise ValueError("Username and password cannot be empty.")

            # Here, you can add actual login validation logic
            print(f"Logging in with {username}:{password}")

        except ValueError as ve:
            self.show_error("Login Error", str(ve))
        except Exception as e:
            self.show_error("Unexpected Error", str(e))

    def show_error(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
