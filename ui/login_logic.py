from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from database.db_handler import Database  # Import database handler
from ui.main_screen_logic import MasterScreen  # Import main screen logic

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/login.ui", self)  # Load UI file dynamically

            self.db = Database()  # Singleton database instance

            self.lblMessage.setText("")  # Clear any previous messages
            self.btnLogin.clicked.connect(self.handle_login)  # Connect login button
            self.btnNewProject.clicked.connect(self.open_main_screen)  # Connect new project button

            # **Trigger login when pressing Enter in username/password fields**
            self.txtUsername.returnPressed.connect(self.move_to_password)
            self.txtPassword.returnPressed.connect(self.handle_login)

        except Exception as e:
            self.show_message_box("Error", f"Error loading UI: {str(e)}")

    def move_to_password(self):
        """Moves cursor focus to password field when Enter is pressed in username field."""
        self.txtPassword.setFocus()

    def handle_login(self):
        """Handles login process by validating user credentials."""
        try:
            username = self.txtUsername.text().strip()
            password = self.txtPassword.text().strip()

            if not username or not password:
                self.show_message_box("Login Error", "Username and password cannot be empty.")
                return

            user_data = self.db.authenticate_user(username, password)  # Get user details

            if user_data:  # If authentication is successful
                self.clear_message()
                self.lblMessage.setText("Login Successful! Redirecting...")

                # Pass the user data (ID, username, name) to the main screen
                self.open_main_screen(user_data)  
            else:
                self.show_label_error("*Invalid username or password.")

        except Exception as e:
            self.show_message_box("Unexpected Error", str(e))

    def open_main_screen(self, user_data):
        """Opens the main application screen and passes user details."""
        try:
            self.main_screen = MasterScreen(user_data)  # Pass user details to MasterScreen
            self.main_screen.show()
            self.close()  # Close login window
        except Exception as e:
            self.show_message_box("Error", f"Error opening main screen: {str(e)}")


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
