from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

class CabinScreen(QtWidgets.QMainWindow):
    custom_values_updated = pyqtSignal(dict)  # Signal to send custom values
    def __init__(self, parent,cabin_index,project_data,old_values=None):
        super().__init__()
        self.parent = parent
        self.cabin_index=cabin_index
        self.project_data=project_data
        self.coach_inputs = old_values if old_values else {}  # Load old values if provided
        self.imagePath=None
        # Load existing values to UI if they exist
        try:
            uic.loadUi("ui/ui_files/cabin_setting.ui", self)  # Load custom UI
            self.set_cabin_info()
            # Define all input field names in one place
            self.input_fields = [
                "txtNPassenger", "txtHeatTransferRead", "txtHeatTransfer", "txtCabinLengthRoof", 
                "txtCabinLengthFloor", "txtWindowAngle", "txtWindowArea", "txtCabinWidth", 
                "txtCabinHeight", "txtAreaPerSide", "txtTotalArea", "txtGWindow", "txtBWindow", 
                "txtKWalls", "txtEW", "txtTheta", "txtHWalls", "txtKD", "txtED", "txtHRoof",
                "txtCabinName", "txtExterior", "txtHVAC","txtCabinName","txtHVAC","txtExterior"
            ]
            self.load_existing_values()
            self.btnUploadLayout.clicked.connect(lambda: self.upload_layout_image(self.cabin_index))
            self.btnSave.clicked.connect(self.save_custom_values)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Cabin UI: {str(e)}")
    
    def save_custom_values(self):
        try:
            # Collect all current inputs into the dictionary
            current_data = {}
            
            for field_name in self.input_fields:
                widget = self.findChild(QtWidgets.QLineEdit, field_name)
                if widget:
                    current_data[field_name] = widget.text()
            
            current_data["Layout Image"] = self.imagePath
            # Save data to self.coach_inputs under the current cabin index
            self.coach_inputs[self.cabin_index] = current_data

            
            if self.custom_values_updated:
                self.custom_values_updated.emit(self.coach_inputs)
            else:
                print("Signal not found!")            
            self.close()
            
        except Exception as e:  
            print(f"An error occurred while saving custom values: {e}")
    def load_existing_values(self):
        """Load existing values from self.coach_inputs if they exist for the current cabin index."""
        try:
            if self.cabin_index in self.coach_inputs:
                cabin_data = self.coach_inputs[self.cabin_index]

                for field_name in self.input_fields:
                    widget = self.findChild(QtWidgets.QLineEdit, field_name)
                    if widget:
                        widget.setText(cabin_data[field_name])  # Load saved value into the widget

                # Check if a saved image exists for this cabin and display it
                if "Layout Image" in cabin_data:
                    image_path = cabin_data["Layout Image"]
                    self.display_image(image_path)
                    
                print(f"Loaded existing values for cabin index {self.cabin_index}: {cabin_data}")

        except Exception as e:
            print(f"An error occurred while loading existing values: {e}")

    


    def display_image(self, image_path):
        """Displays the image in lblCabinLayout."""
        try:
            pixmap = QtGui.QPixmap(image_path)
            self.lblCabinLayout.setPixmap(pixmap)
            self.lblCabinLayout.setScaledContents(True)  # Scale the image to fit the label size
        except Exception as e:
            print(f"An error occurred while displaying the image: {e}")

    def upload_layout_image(self, cabin_index):
        """Handles uploading and saving the layout image for a specific cabin."""
        try:
            # Open a file dialog to select an image file
            image_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image File",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
            )

            if image_path:
                # Save the selected image path to self.coach_inputs for the given cabin index
                if cabin_index not in self.coach_inputs:
                    self.coach_inputs[cabin_index] = {}
                self.imagePath = image_path

                # Display the image in lblCabinLayout
                self.display_image(image_path)

        except Exception as e:
            print(f"An error occurred while uploading the layout image: {e}")

    def set_cabin_info(self):
        """Retrieves the cabin name, standard cabin, and heat transfer cabin based on index."""
        try:
            project_info = self.project_data.get('Project_info', {})
            
            # Retrieve Heat Transfer Cabin
            heat_transfer_cabin = project_info.get('Heat Transfer Cabin', '')

            # Retrieve Cabin Name based on index
            cabin_name_key = f"Cabin {self.cabin_index+1} Name"
            cabin_name = project_info.get(cabin_name_key, '')

            # Retrieve Standard Cabin
            standard_cabin = project_info.get('Standard Cabin', '')
            
            # Display the values
            self.lblCabinName.setText(cabin_name)
            self.lblStandardCabin.setText(standard_cabin)
            self.txtHeatTransferRead.setText(str(heat_transfer_cabin))
            
            
            return cabin_name, standard_cabin, heat_transfer_cabin
        except Exception as e:
            print(f"An error occurred while retrieving cabin info: {e}")
            return '', '', ''

    