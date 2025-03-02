from PyQt5 import QtWidgets, uic

class CustomExteriorConditionsSaloonScreen(QtWidgets.QMainWindow):
    def __init__(self, default_values=None):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/custom_exterior_saloon.ui", self)  # Load custom UI
            self.setWindowTitle("Custom Exterior Conditions - Saloon")  # Set window title
            if default_values:
                self.default_values=default_values
                self.lblStandard.setText(default_values.get("standard", ""))
                self.lblStandard_2.setText(default_values.get("standard", ""))
                self.lblStandard_3.setText(default_values.get("standard", ""))


                self.txtNormWinterZone.setText(default_values.get("WinterZone", "None"))
                self.txtNormSummerZone.setText(default_values.get("SummerZone", "None"))
                self.txtNormWinterNormalMin.setText(default_values.get("WinterNormal", "None"))

                self.txtNormSummerNormalMax.setText(default_values.get("SummerNormal", "None"))
                 # Extended values (Min/Max)
                self.txtNormWinterExtendedMin.setText(self.default_values.get("WinterExtendedMin", "None"))
                self.txtNormWinterExtendedMax.setText(self.default_values.get("WinterExtendedMax", "None"))
                self.txtNormSummerExtendedMin.setText(self.default_values.get("SummerExtendedMin", "None"))
                self.txtNormSummerExtendedMax.setText(self.default_values.get("SummerExtendedMax", "None"))

                # Design values (Temp, Humidity, Heat Flux)
                self.txtNormWinterDesignTemp.setText(self.default_values.get("WinterDesignTemp", "None"))
                self.txtNormWinterDesignHumi.setText(self.default_values.get("WinterDesignHumidity", "None"))
                self.txtNormWinterDesignSolar.setText(self.default_values.get("WinterDesignHeatFlux", "None"))

                self.txtNormSummerDesignTemp.setText(self.default_values.get("SummerDesignTemp", "None"))
                self.txtNormSummerDesignHumi.setText(self.default_values.get("SummerDesignHumidity", "None"))
                self.txtNormSummerDesignSolar.setText(self.default_values.get("SummerDesignHeatFlux", "None"))

                # Extreme values
                self.txtNormWinterExtremeTemp.setText(self.default_values.get("WinterExtremeTemp", "None"))
                self.txtNormWinterExtremeHumi.setText(self.default_values.get("WinterExtremeHumidity", "None"))
                self.txtNormWinterExtremeSolar.setText(self.default_values.get("WinterExtremeHeatFlux", "None"))

                self.txtNormSummerExtremeTemp.setText(self.default_values.get("SummerExtremeTemp", "None"))
                self.txtNormSummerExtremeHumi.setText(self.default_values.get("SummerExtremeHumidity", "None"))
                self.txtNormSummerExtremeSolar.setText(self.default_values.get("SummerExtremeHeatFlux", "None"))

                # Operational values
                self.txtNormWinterOperationalTemp.setText(self.default_values.get("WinterOperationalTemp", "None"))
                self.txtNormWinterOperationalHumi.setText(self.default_values.get("WinterOperationalHumidity", "None"))
                self.txtNormWinterOperationalSolar.setText(self.default_values.get("WinterOperationalHeatFlux", "None"))

                self.txtNormSummerOperationalTemp.setText(self.default_values.get("SummerOperationalTemp", "None"))
                self.txtNormSummerOperationalHumi.setText(self.default_values.get("SummerOperationalHumidity", "None"))
                self.txtNormSummerOperationalSolar.setText(self.default_values.get("SummerOperationalHeatFlux", "None"))


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")