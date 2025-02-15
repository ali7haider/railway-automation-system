from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from database.db_handler import Database  # Import database handler

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/login.ui", self)  # Load UI file dynamically

            self.db = Database()  # Singleton database instance

            self.lblMessage.setText("")  # Clear any previous messages
            self.btnLogin.clicked.connect(self.handle_login)  # Connect login button
        except Exception as e:
            self.show_message_box("Error", f"Error loading UI: {str(e)}")

    def handle_login(self):
        """Handles login process by validating user credentials."""
        try:
            username = self.txtUsername.text().strip()
            password = self.txtPassword.text().strip()

            if not username or not password:
                self.show_message_box("Login Error", "Username and password cannot be empty.")
                return

            if self.db.authenticate_user(username, password):
                self.clear_message()  # Remove error message on success
                self.lblMessage.setText("Login Successful! Redirecting...")

                # Switch to the main application page (Assuming stackedWidget exists)
                self.stackedWidget.setCurrentIndex(1)  # Change to page index 1
            else:
                self.show_label_error("*Invalid username or password.")

        except Exception as e:
            self.show_message_box("Unexpected Error", str(e))

    def show_label_error(self, message):
        """Displays an error message in lblMessage (only for incorrect login)."""
        self.lblMessage.setStyleSheet("color: red;")  # Set text color to red
        self.lblMessage.setText(message)

    def clear_message(self):
        """Clears the lblMessage text."""
        self.lblMessage.setText("")

    def show_message_box(self, title, message):
        """Displays a QMessageBox for general errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
