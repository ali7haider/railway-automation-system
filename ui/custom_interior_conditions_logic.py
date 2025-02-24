from PyQt5 import QtWidgets, uic

class CustomInteriorConditionsScreen(QtWidgets.QMainWindow):
    def __init__(self, default_values=None):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/custom_interior.ui", self)  # Load custom UI
            self.setWindowTitle("Custom Interior Conditions")  # Set window title

             # Set default values (if provided)
            if default_values:
                self.lblSaloonStandard.setText(default_values.get("standard_saloon", ""))
                self.lblSaloonStandard_3.setText(default_values.get("standard_saloon", ""))
                self.lblSaloonStandard_2.setText(default_values.get("standard_saloon", ""))
                self.lblSaloonStandard_4.setText(default_values.get("standard_saloon", ""))

                self.lblCabinStandard.setText(default_values.get("standard_cabin", ""))
                self.lblCabinStandard_2.setText(default_values.get("standard_cabin", ""))
                self.lblCabinStandard_3.setText(default_values.get("standard_cabin", ""))
                self.lblCabinStandard_4.setText(default_values.get("standard_cabin", ""))


                self.txtNormTicMaxSaloon.setText(default_values.get("TicMaxSaloon", ""))
                self.txtNormTicMinSaloon.setText(default_values.get("TicMinSaloon", ""))
                self.txtNormTicMaxCabin.setText(default_values.get("TicMaxCabin", ""))
                self.txtNormTicMinCabin.setText(default_values.get("TicMinCabin", ""))
                self.txtNormMaxMeanInteriorSaloon.setText(default_values.get("MaxMeanTempSaloon", ""))
                self.txtNormMaxMeanInteriorCabin.setText(default_values.get("MaxMeanTempCabin", ""))
                self.txtNormMaxSaloon.setText(default_values.get("StandByOperatorSaloonMax", ""))
                self.txtNormMinSaloon.setText(default_values.get("StandByOperatorSaloonMin", ""))
                self.txtNormMaxCabin.setText(default_values.get("StandByOperatorCabinMax", ""))
                self.txtNormMinCabin.setText(default_values.get("StandByOperatorCabinMin", ""))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")