from PyQt5 import QtWidgets, uic

class CustomInteriorConditionsScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/custom_interior.ui", self)  # Load custom UI
            self.setWindowTitle("Custom Interior Conditions")  # Set window title
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")