from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

class CustomExteriorConditionsSaloonScreen(QtWidgets.QMainWindow):
    custom_values_updated = pyqtSignal(dict)  # Signal to send custom values
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
            self.btnSave.clicked.connect(self.save_custom_values)


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")
    def save_custom_values(self):
        try:
            custom_values = {
                "CustomWinterZone": self.txtCustomWinterZone.text().strip(),
                "CustomSummerZone": self.txtCustomSummerZone.text().strip(),
                "CustomWinterNormalMin": self.txtCustomWinterNormalMin.text().strip(),
                "CustomSummerNormalMax": self.txtCustomSummerNormalMax.text().strip(),

                # Extended values (Min/Max)
                "CustomWinterExtendedMin": self.txtCustomWinterExtendedMin.text().strip(),
                "CustomWinterExtendedMax": self.txtCustomWinterExtendedMax.text().strip(),
                "CustomSummerExtendedMin": self.txtCustomSummerExtendedMin.text().strip(),
                "CustomSummerExtendedMax": self.txtCustomSummerExtendedMax.text().strip(),

                # Design values (Temp, Humidity, Heat Flux)
                "CustomWinterDesignTemp": self.txtCustomWinterDesignTemp.text().strip(),
                "CustomWinterDesignHumi": self.txtCustomWinterDesignHumi.text().strip(),
                "CustomWinterDesignSolar": self.txtCustomWinterDesignSolar.text().strip(),

                "CustomSummerDesignTemp": self.txtCustomSummerDesignTemp.text().strip(),
                "CustomSummerDesignHumi": self.txtCustomSummerDesignHumi.text().strip(),
                "CustomSummerDesignSolar": self.txtCustomSummerDesignSolar.text().strip(),

                # Extreme values
                "CustomWinterExtremeTemp": self.txtCustomWinterExtremeTemp.text().strip(),
                "CustomWinterExtremeHumi": self.txtCustomWinterExtremeHumi.text().strip(),
                "CustomWinterExtremeSolar": self.txtCustomWinterExtremeSolar.text().strip(),

                "CustomSummerExtremeTemp": self.txtCustomSummerExtremeTemp.text().strip(),
                "CustomSummerExtremeHumi": self.txtCustomSummerExtremeHumi.text().strip(),
                "CustomSummerExtremeSolar": self.txtCustomSummerExtremeSolar.text().strip(),

                # Operational values
                "CustomWinterOperationalTemp": self.txtCustomWinterOperationalTemp.text().strip(),
                "CustomWinterOperationalHumi": self.txtCustomWinterOperationalHumi.text().strip(),
                "CustomWinterOperationalSolar": self.txtCustomWinterOperationalSolar.text().strip(),

                "CustomSummerOperationalTemp": self.txtCustomSummerOperationalTemp.text().strip(),
                "CustomSummerOperationalHumi": self.txtCustomSummerOperationalHumi.text().strip(),
                "CustomSummerOperationalSolar": self.txtCustomSummerOperationalSolar.text().strip(),
            }

            if self.custom_values_updated:
                self.custom_values_updated.emit(custom_values)
            else:
                print("Signal not found!")

            self.close()  # Ensure window closes after saving

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error saving custom values: {str(e)}")
