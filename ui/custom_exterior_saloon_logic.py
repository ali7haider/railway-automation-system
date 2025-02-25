from PyQt5 import QtWidgets, uic

class CustomExteriorConditionsSaloonScreen(QtWidgets.QMainWindow):
    def __init__(self, default_values=None):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/custom_exterior_saloon.ui", self)  # Load custom UI
            self.setWindowTitle("Custom Exterior Conditions - Saloon")  # Set window title
            if default_values:
                self.lblStandard.setText(default_values.get("standard", ""))
                self.lblStandard_2.setText(default_values.get("standard", ""))
                self.lblStandard_3.setText(default_values.get("standard", ""))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")