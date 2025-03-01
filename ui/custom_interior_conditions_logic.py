from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

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

                # Format and display saloon values
                # Fetch values
                saloon_curve = default_values.get("saloon_curve", {})
                cabin_curve = default_values.get("cabin_curve", {})

                # Display values in labels
                self.display_curve_values(saloon_curve, "saloon",default_values.get("standard_saloon", ""),self.lblSaloonGraphNorm)
                self.display_curve_values(cabin_curve, "cabin",default_values.get("standard_cabin", ""),self.lblCabinGraphNorm)

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

                # Save the plot as an image
                # image_path = "curve_plot.png"
                # plt.savefig(image_path, dpi=100, bbox_inches="tight")  # Save with good resolution
                # plt.close()  # Close the plot to free memory

                # # Load the image into QLabel
                # pixmap = QPixmap(image_path)
                # if not pixmap.isNull():
                #     label_widget.setPixmap(pixmap.scaled(label_widget.width(), label_widget.height(), Qt.KeepAspectRatio))

                # # Delete the image after loading into QLabel
                # os.remove(image_path)

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
