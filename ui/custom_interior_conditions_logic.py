from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

class CustomInteriorConditionsScreen(QtWidgets.QMainWindow):
    custom_values_updated = pyqtSignal(dict)  # Signal to send custom values

    def __init__(self, default_values=None,custom_values=None):
        super().__init__()
        try:
            self.default_values = default_values
            self.custom_values=custom_values
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

                
                # Format and display saloon values
                # Fetch values
                saloon_curve = default_values.get("saloon_curve", {})
                cabin_curve = default_values.get("cabin_curve", {})

                # Display values in labels
                self.display_curve_values(saloon_curve, "saloon",default_values.get("standard_saloon", ""),self.lblSaloonGraphNorm)
                self.display_curve_values(cabin_curve, "cabin",default_values.get("standard_cabin", ""),self.lblCabinGraphNorm)
            if self.custom_values:
                self.txtCustomTicMaxSaloon.setText(self.custom_values.get("TicMaxSaloon", ""))
                self.txtCustomTicMinSaloon.setText(self.custom_values.get("TicMinSaloon", ""))
                self.txtCustomTicMaxCabin.setText(self.custom_values.get("TicMaxCabin", ""))
                self.txtCustomTicMinCabin.setText(self.custom_values.get("TicMinCabin", ""))
                self.txtCustomMaxMeanInteriorSaloon.setText(self.custom_values.get("MaxMeanTempSaloon", ""))
                self.txtCustomMaxMeanInteriorCabin.setText(self.custom_values.get("MaxMeanTempCabin", ""))
                self.txtCustomMaxSaloon.setText(self.custom_values.get("StandByOperatorSaloonMax", ""))
                self.txtCustomMinSaloon.setText(self.custom_values.get("StandByOperatorSaloonMin", ""))
                self.txtCustomMaxCabin.setText(self.custom_values.get("StandByOperatorCabinMax", ""))
                self.txtCustomMinCabin.setText(self.custom_values.get("StandByOperatorCabinMin", ""))
                
                # Set comboboxes
                self.cmbxSaloonCustomNorm.setCurrentText(self.custom_values.get("RegulationCurveSaloon", ""))
                self.cmbxCabinCustomNorm.setCurrentText(self.custom_values.get("RegulationCurveCabin", ""))

            self.setup_custom_value_listeners()  # Connect custom input fields to update graph
            self.btnSave.clicked.connect(self.save_custom_values)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")
    def display_curve_values(self, curve_values, label_prefix,standard,graphLabel):
        """
        Maps curve values to UI labels for Saloon and Cabin.
        :param curve_values: Dictionary containing curve values.
        :param label_prefix: 'saloon' or 'cabin' to determine which labels to update.
        """
        try:
            limit_keys = [
                "Text Upper Limit", "Tin Upper Limit",
                "Text Lower Limit", "Tin Lower Limit",
                "Text Curve Limit", "Tin Curve Limit"
            ]

            for key in limit_keys:
                values = curve_values.get(key, {})
                first_five_values = list(values.values())[:5]  # Get first 5 values
                formatted_values = [str(val) if val is not None else "-" for val in first_five_values]

                # Map keys to correct label names
                if key == "Text Upper Limit":
                    label_names = [f"txtNormUpperLimit{i+1}" for i in range(5)]
                elif key == "Tin Upper Limit":
                    label_names = [f"txtNormUpperLimit{i+6}" for i in range(5)]  # Same as text
                elif key == "Text Lower Limit":
                    label_names = [f"txtNormLowerLimit{i+1}" for i in range(5)]
                elif key == "Tin Lower Limit":
                    label_names = [f"txtNormLowerLimit{i+6}" for i in range(5)]
                elif key == "Text Curve Limit":
                    label_names = [f"txtNormCurve{i+1}" for i in range(5)]
                elif key == "Tin Curve Limit":
                    label_names = [f"txtNormCurve{i+6}" for i in range(5)]

                # Adjust label names for Cabin
                if label_prefix == "cabin":
                    label_names = [name.replace("txtNorm", "txtNormCabin") for name in label_names]

                # Set values in the labels
                for label, value in zip(label_names, formatted_values):
                    label_widget = getattr(self, label, None)
                    if label_widget:
                        label_widget.setText(value)

        # After setting UI labels, generate the curve graph
            self.plot_curve_graph(curve_values, standard,graphLabel)

        except Exception as e:
            print(f"Error displaying {label_prefix} curve values: {e}")



    def plot_curve_graph(self, curve_values, standard, label_widget):
        """
        Plots the curve graph, saves it as an image, displays it in a QLabel, and deletes the image.
        :param curve_values: Dictionary containing curve values.
        :param standard: The standard being used (e.g., "EN13129:2016").
        :param label_widget: The QLabel where the image will be displayed.
        """
        try:
            # Extract the first 5 values from the respective limits
            def get_values(limit_name):
                values = curve_values.get(limit_name, {})
                return [val if isinstance(val, (int, float)) else None for val in list(values.values())[:5]]

            # Fetch data
            Text_upper = get_values("Text Upper Limit")
            Tin_upper = get_values("Tin Upper Limit")
            
            Text = get_values("Text Curve Limit")
            Tin = get_values("Tin Curve Limit")

            Text_low = get_values("Text Lower Limit")
            Tin_low = get_values("Tin Lower Limit")

            # Ensure all values are valid before plotting
            if all(val is not None for val in Text_upper + Tin_upper + Text + Tin + Text_low + Tin_low):
                # Create the plot
                plt.figure(figsize=(5, 4))  # Set figure size
                plt.plot(Text_upper, Tin_upper, marker='o', linestyle='-', color='r', label="Upper Limit")
                plt.plot(Text, Tin, marker='o', linestyle='-', color='b', label="Curve")
                plt.plot(Text_low, Tin_low, marker='o', linestyle='-', color='g', label="Lower Limit")

                # Labels and title
                plt.xlabel("Text [ºC]")
                plt.ylabel("Tin [ºC]")
                plt.title(standard)
                plt.legend()
                plt.grid(True)
                temp_filename = "curve_plot.png"
                plt.savefig(temp_filename)

                # Convert the saved image to a QPixmap and display it
                qpixmap = QPixmap(temp_filename)
                if not qpixmap.isNull():
                    label_widget.setPixmap(qpixmap)

                # Delete the temporary file
                os.remove(temp_filename) 

            else:
                print("Invalid values found in curve data. Ensure all values are numeric.")

        except Exception as e:
            print(f"Error generating graph: {e}")
    def setup_custom_value_listeners(self):
        """
        Connects textChanged signals of custom input fields to update the graph dynamically.
        """
        try:
            # List of text input fields to monitor
            custom_inputs = []
            
            for i in range(1, 11):
                custom_inputs.append(f"txtCustomUpperLimit{i}")
                custom_inputs.append(f"txtCustomLowerLimit{i}")
                custom_inputs.append(f"txtCustomCurve{i}")

            for i in range(1, 11):  # Cabin custom fields
                custom_inputs.append(f"txtCustomCabinUpperLimit{i}")
                custom_inputs.append(f"txtCustomCabinLowerLimit{i}")
                custom_inputs.append(f"txtCustomCabinCurve{i}")

            # Connect each field to the update function
            for field in custom_inputs:
                input_widget = getattr(self, field, None)
                if input_widget:
                    input_widget.textChanged.connect(self.update_custom_graphs)

        except Exception as e:
            print(f"Error setting up custom input listeners: {e}")
    def get_custom_curve_values(self, is_cabin=False):
        """
        Reads the custom curve values from the UI input fields.
        :param is_cabin: If True, fetch values for Cabin; otherwise, fetch values for Saloon.
        Returns a dictionary formatted like curve_values.
        """
        try:
            prefix = "txtCustomCabin" if is_cabin else "txtCustom"

            def fetch_values(label, start, end, default=0):
                """
                Fetch values from UI input fields based on label and range.
                :param label: "UpperLimit", "LowerLimit", "Curve"
                :param start: Start index (e.g., 1 for Text, 6 for Tin)
                :param end: End index (e.g., 5 for Text, 10 for Tin)
                :param default: Default value for missing/non-numeric entries.
                :return: List of fetched values.
                """
                values = []
                for i in range(start, end + 1):  # Range from start to end
                    field_name = f"{prefix}{label}{i}"
                    widget = getattr(self, field_name, None)
                    if widget:
                        text_value = widget.text().strip()  # Remove spaces
                        try:
                            value = float(text_value) if text_value else default  # Use default if empty
                        except ValueError:
                            value = default  # Handle non-numeric values
                        values.append(value)
                    else:
                        values.append(default)  # If the widget doesn't exist, use default
                return values

            return {
                "Text Upper Limit": dict(zip("ABCDE", fetch_values("UpperLimit", 1, 5))),  # Text: 1-5
                "Tin Upper Limit": dict(zip("ABCDE", fetch_values("UpperLimit", 6, 10))),  # Tin: 6-10

                "Text Lower Limit": dict(zip("ABCDE", fetch_values("LowerLimit", 1, 5))),  # Text: 1-5
                "Tin Lower Limit": dict(zip("ABCDE", fetch_values("LowerLimit", 6, 10))),  # Tin: 6-10

                "Text Curve Limit": dict(zip("ABCDE", fetch_values("Curve", 1, 5))),  # Text: 1-5
                "Tin Curve Limit": dict(zip("ABCDE", fetch_values("Curve", 6, 10))),  # Tin: 6-10
            }

        except Exception as e:
            print(f"Error fetching custom curve values: {e}")
            return {}




    def update_custom_graphs(self):
        """
        Fetches updated values from custom input fields and re-plots the graph in QLabel.
        """
        try:
            # Fetch values for both Saloon and Cabin
            custom_saloon_values = self.get_custom_curve_values(is_cabin=False)
            custom_cabin_values = self.get_custom_curve_values(is_cabin=True)

            # Update Saloon Custom Graph
            self.plot_custom_curve_graph(custom_saloon_values, "Custom Saloon Graph", self.lblSaloonGraphCustom)

            # Update Cabin Custom Graph
            self.plot_custom_curve_graph(custom_cabin_values, "Custom Cabin Graph", self.lblCabinGraphCustom)

        except Exception as e:
            print(f"Error updating custom graphs: {e}")

    def plot_custom_curve_graph(self, curve_values, standard, label_widget):
        """
        Plots the custom curve graph, saves it as an image, displays it in a QLabel, and deletes the image.
        :param curve_values: Dictionary containing curve values.
        :param standard: The standard being used (e.g., "Custom Standard").
        :param label_widget: The QLabel where the image will be displayed.
        """
        try:
            # Extract first 5 values from the respective limits
            def get_values(limit_name):
                values = curve_values.get(limit_name, {})
                return [val if isinstance(val, (int, float)) else None for val in list(values.values())[:5]]

            # Fetch data
            Text_upper = get_values("Text Upper Limit")
            Tin_upper = get_values("Tin Upper Limit")
            
            Text = get_values("Text Curve Limit")
            Tin = get_values("Tin Curve Limit")

            Text_low = get_values("Text Lower Limit")
            Tin_low = get_values("Tin Lower Limit")

            # Ensure all values are valid before plotting
            if all(val is not None for val in Text_upper + Tin_upper + Text + Tin + Text_low + Tin_low):
                # Create the plot
                plt.figure(figsize=(5, 4))  # Set figure size
                plt.plot(Text_upper, Tin_upper, marker='o', linestyle='-', color='r', label="Upper Limit")
                plt.plot(Text, Tin, marker='o', linestyle='-', color='b', label="Curve")
                plt.plot(Text_low, Tin_low, marker='o', linestyle='-', color='g', label="Lower Limit")

                # Labels and title
                plt.xlabel("Text [ºC]")
                plt.ylabel("Tin [ºC]")
                plt.title(standard)
                plt.legend()
                plt.grid(True)

                # Save and display the plot
                temp_filename = "custom_curve_plot.png"
                plt.savefig(temp_filename)

                # Convert the saved image to a QPixmap and display it
                qpixmap = QPixmap(temp_filename)
                if not qpixmap.isNull():
                    label_widget.setPixmap(qpixmap)
                    label_widget.setScaledContents(True)  # Scale to fit label

                # Delete the temporary file
                os.remove(temp_filename)

            else:
                print("Invalid values found in custom curve data. Ensure all values are numeric.")

        except Exception as e:
            print(f"Error generating custom graph: {e}")
    def save_custom_values(self):
        try:
            custom_values = {
                "TicMaxSaloon": self.txtCustomTicMaxSaloon.text().strip(),
                "TicMinSaloon": self.txtCustomTicMinSaloon.text().strip(),
                "TicMaxCabin": self.txtCustomTicMaxCabin.text().strip(),
                "TicMinCabin": self.txtCustomTicMinCabin.text().strip(),
                "MaxMeanTempSaloon": self.txtCustomMaxMeanInteriorSaloon.text().strip(),
                "MaxMeanTempCabin": self.txtCustomMaxMeanInteriorCabin.text().strip(),
                "StandByOperatorSaloonMax": self.txtCustomMaxSaloon.text().strip(),
                "StandByOperatorSaloonMin": self.txtCustomMinSaloon.text().strip(),
                "StandByOperatorCabinMax": self.txtCustomMaxCabin.text().strip(),
                "StandByOperatorCabinMin": self.txtCustomMinCabin.text().strip(),
            }

            # Only include if combo box text is "Custom"
            if self.cmbxSaloonCustomNorm.currentText().strip() == "Custom":
                custom_values["RegulationCurveSaloon"] = self.cmbxSaloonCustomNorm.currentText().strip()

            if self.cmbxCabinCustomNorm.currentText().strip() == "Custom":
                custom_values["RegulationCurveCabin"] = self.cmbxCabinCustomNorm.currentText().strip()

            if self.custom_values_updated:
                self.custom_values_updated.emit(custom_values)
            else:
                print("Signal not found!")

            self.close()  # Ensure window closes after saving

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error saving custom values: {str(e)}")
