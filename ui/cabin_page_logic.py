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
        # Load existing values to UI if they exist
        try:
            uic.loadUi("ui/ui_files/cabin_setting.ui", self)  # Load custom UI
            self.area_labels_2 = ["Nº Passengers", "Heat transfer coefficient standstill (k)", "Coach Length",
                              "Saloon 1 Length","Saloon 2 Length","Saloon 3 Length","Coach Width","Coach Length"
                              ,"Windows Area per side","Total Exterior Area","Total Exterior Area (no ends)"
                              ,"g (Windows)","B (Windows)","kW (Walls)","EW","Theta (Walls)","h (Walls)","kD (Roof)","ED","h (Roof)"]

            self.coach_widgets = []
            self.initialize_coach_ui(2)
            self.load_existing_values()

            self.set_cabin_info()
            self.btnUploadLayout.clicked.connect(lambda: self.upload_layout_image(self.cabin_index))


            self.btnSave.clicked.connect(self.save_custom_values)

            
            # self.btnSave.clicked.connect(self.save_custom_values)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Cabin UI: {str(e)}")
    
    def load_existing_values(self):
        """Loads existing values to the UI if available."""
        print(self.coach_inputs)
        # if self.coach_inputs:
        #     for key, value in self.coach_inputs.items():
        #         input_field = self.findChild(QLineEdit, f"txt{key.replace(' ', '')}")
        #         if input_field:
        #             input_field.setText(value)
        #             print(f"Loaded old value for {key}: {value}")
    def save_custom_values(self):
        try:
            # Save the custom values for the current coach
            self.save_current_coach_inputs(self.cabin_index)
            if self.custom_values_updated:
                self.custom_values_updated.emit(self.coach_inputs)
            else:
                print("Signal not found!")
            self.close()
        except Exception as e:  
            print(f"An error occurred while saving custom values: {e}")
    def save_current_coach_inputs(self, index):
        """Saves the current inputs for the given coach index."""
        try:
            if index in self.coach_inputs:
                for label_name, line_edit in self.coach_inputs[index].items():
                    widget = self.findChild(QLineEdit, label_name)
                    if widget:  # If QLineEdit exists, save as tuple (object name, text)
                        self.coach_inputs[index][label_name] = (widget.objectName(), widget.text())
        except Exception as e:
            print(f"An error occurred while saving inputs for Coach {index + 1}: {e}")

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
                self.coach_inputs[cabin_index]["Layout Image"] = image_path

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
            self.readonly_heat_transfer_values["Heat transfer coefficient standstill (k)"] = heat_transfer_cabin
            for label_name, value in self.readonly_heat_transfer_values.items():
                    # Handle double input fields
                    readonly_input = self.findChild(QLineEdit, f"readonly_{label_name}")
                    if readonly_input:
                        readonly_input.setText(str(value))
            
            return cabin_name, standard_cabin, heat_transfer_cabin
        except Exception as e:
            print(f"An error occurred while retrieving cabin info: {e}")
            return '', '', ''

    def initialize_coach_ui(self, total_coaches):
        """Creates the UI layout for the coaches once and only updates values on switching."""
        try:
            readonly_fields = {  # Fields to be set as read-only
                "Total Exterior Area",
                "Total Exterior Area (no ends)",
                "h (Walls)",
                "h (Roof)"
            }
            
            # Labels that require two inputs (read-only + custom)
            double_input_labels = {"Heat transfer coefficient standstill (k)"}
            # Dictionary to store the read-only value separately
            self.readonly_heat_transfer_values = {} 

            # Define units for specific labels in area_labels_2
            units = {
                "Heat transfer coefficient standstill (k)": "W/k*m²",
                "Coach Length": "m",
                "Saloon 1 Length": "m",
                "Saloon 2 Length": "m",
                "Saloon 3 Length": "m",
                "Coach Width": "m",
                "Coach Height": "m",
                "Windows Area per side": "m²",
                "Total Exterior Area": "m²",
                "Total Exterior Area (no ends)": "m²",
                "kW (Walls)": "W/k*m²",
                "h (Walls)": "W/k*m²",
                "kD (Roof)": "W/k*m²",
                "h (Roof)": "W/k*m²"
            }

            # Prepare the coach_inputs dictionary for all coaches
            for coach_index in range(total_coaches):
                if coach_index not in self.coach_inputs:
                    self.coach_inputs[coach_index] = {}

            # Create UI elements only once (for the first time)
            if not self.coach_inputs[0]:  # Check if the UI is not yet created
                # Adding labels and QLineEdits for frameAreaLabels
                # Adding labels and QLineEdits for frameAreaLabels_2
                for label_name in self.area_labels_2:
                    row_layout = QHBoxLayout()  
                    row_layout.setAlignment(Qt.AlignLeft)
                    row_layout.setContentsMargins(0, 0, 0, 0)  
                    row_layout.setSpacing(15)  

                    label = QLabel(label_name)
                    label.setMinimumWidth(300)

                    if label_name in double_input_labels:
                        # Creating two inputs: read-only and custom
                        readonly_input = QLineEdit()
                        readonly_input.setObjectName(f"readonly_{label_name}")
                        readonly_input.setReadOnly(True)
                        
                        custom_input = QLineEdit()
                        custom_input.setObjectName(f"{label_name}")

                        row_layout.addWidget(label)
                        row_layout.addWidget(readonly_input)
                        row_layout.addWidget(custom_input)

                        # Add unit label if it exists, otherwise placeholder for alignment
                        unit_label = QLabel(units.get(label_name, ""))
                        unit_label.setMinimumWidth(60)
                        row_layout.addWidget(unit_label)
                        # Save only the read-only widget separately
                        self.readonly_heat_transfer_values[f"readonly_{label_name}"] = readonly_input.text()

                        # Save the widgets for all coaches
                        for coach_index in range(total_coaches):
                            self.coach_inputs[coach_index][label_name] = (custom_input.objectName(), custom_input.text())

                    else:
                        # Regular QLineEdit for all other labels
                        line_edit = QLineEdit()
                        line_edit.setObjectName(label_name)
                        
                        if label_name in readonly_fields:
                            line_edit.setReadOnly(True)

                        row_layout.addWidget(label)
                        row_layout.addWidget(line_edit)

                        # Add unit label if it exists, otherwise placeholder for alignment
                        unit_label = QLabel(units.get(label_name, ""))
                        unit_label.setMinimumWidth(60)
                        row_layout.addWidget(unit_label)

                        for coach_index in range(total_coaches):
                            self.coach_inputs[coach_index][label_name] = (line_edit.objectName(), line_edit.text())
                    
                    self.frameAreaLabels_2.layout().addLayout(row_layout)

                print("UI for coaches created successfully.")
                
        except Exception as e:
            print(f"An error occurred while initializing the coach UI: {e}")
