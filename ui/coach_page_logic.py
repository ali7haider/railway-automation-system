from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math

class CoachPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.project_data = {}
        self.coach_inputs = {}
        self.current_coach_index = 0  # Initialize current_coach_index
        self.first_time_click = True  # Track if it's the first click
        self.parent.btnUploadLayout.clicked.connect(lambda: self.upload_layout_image(self.current_coach_index))


        self.area_labels = ["Saloon 1", "Saloon 2", "Saloon 3","Catering/Buffet","Vestibule 1","Vestibule 2","WC 1","WC 2"
                            ,"Crew","Corridor 1","Corridor 2","Compartment 1","Compartment 2","Compartment 3","Compartment 4","Compartment 5","Compartment 6",
                            "Annex Area 1","Annex Area 2","Nursery","HVAC 1","HVAC 2","Exterior"]
        self.area_labels_2 = ["Nº Passengers", "Heat transfer coefficient standstill (k)", "Coach Length",
                              "Saloon 1 Length","Saloon 2 Length","Saloon 3 Length","Coach Width","Coach Length"
                              ,"Windows Area per side","Total Exterior Area","Total Exterior Area (no ends)"
                              ,"g (Windows)","B (Windows)","kW (Walls)","EW","Theta (Walls)","h (Walls)","kD (Roof)","ED","h (Roof)"]


    def upload_layout_image(self, cabin_index):
        """Handles uploading and saving the layout image for a specific cabin."""
        try:
            # Open a file dialog to select an image file
            image_path, _ = QFileDialog.getOpenFileName(
                self.parent,
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

    def load_coach_data(self, project_data):
        """Loads coach data from project and updates UI."""
        try:
            if "Project_info" not in project_data:
                return
            
            self.project_data = project_data["Project_info"]
            self.parent.lblStandardSaloonCoach.setText(self.project_data.get("Standard Saloon", ""))
            
            num_coaches = int(self.project_data.get("Number of Coaches per Train", 0))
            self.update_coach_buttons(num_coaches)

        except ValueError:
            print("Error: Invalid number of coaches found in project data.")
        except KeyError as e:
            print(f"Error: Missing key in project data - {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading coach data: {e}")
    def update_coach_buttons(self, num_coaches):
        """Updates dynamically generated QPushButton widgets based on the number of coaches."""
        try:
            if not isinstance(num_coaches, int) or num_coaches <= 0:
                return
            
            while self.coach_widgets:
                widget = self.coach_widgets.pop()
                widget.deleteLater()

            for i in range(num_coaches):
                try:
                    coach_button = QPushButton(f"Coach {i + 1}", self.parent)
                    coach_button.setMinimumHeight(32)
                    coach_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                    coach_button.clicked.connect(lambda _, index=i: self.on_coach_button_click(index))
                    self.coach_widgets.append(coach_button)
                    self.parent.frameCoachesButtons.layout().addWidget(coach_button)
                except Exception as e:
                    print(f"An error occurred while creating button for Coach {i + 1}: {e}")

            self.initialize_coach_ui(num_coaches)
            self.load_heat_transfer_from_json()  # Load the JSON data
            self.load_json_values_to_ui()  # Apply the loaded value to the UI

        except Exception as e:
            print(f"An error occurred while updating coach inputs: {e}")

    def initialize_coach_ui(self, total_coaches):
        """Creates the UI layout for the coaches once and only updates values on switching."""
        try:
            label_minimum_width = 120  # Set the minimum width for labels
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
                for label_name in self.area_labels:
                    row_layout = QHBoxLayout()  
                    row_layout.setAlignment(Qt.AlignLeft)
                    row_layout.setContentsMargins(0, 0, 0, 0)  
                    row_layout.setSpacing(15)  

                    label = QLabel(label_name)
                    label.setMinimumWidth(label_minimum_width)

                    line_edit = QLineEdit()
                    line_edit.setObjectName(label_name)
                    
                    if label_name in readonly_fields:
                        line_edit.setReadOnly(True)

                    row_layout.addWidget(label)
                    row_layout.addWidget(line_edit)
                    
                    # Adding an empty label at the end for alignment
                    row_layout.addWidget(QLabel("")) 

                    self.parent.frameAreaLabels.layout().addLayout(row_layout)

                    for coach_index in range(total_coaches):
                        self.coach_inputs[coach_index][label_name] = (line_edit.objectName(), line_edit.text())

                # Adding labels and QLineEdits for frameAreaLabels_2
                for label_name in self.area_labels_2:
                    row_layout = QHBoxLayout()  
                    row_layout.setAlignment(Qt.AlignLeft)
                    row_layout.setContentsMargins(0, 0, 0, 0)  
                    row_layout.setSpacing(15)  

                    label = QLabel(label_name)
                    label.setMinimumWidth(260)

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
                    
                    self.parent.frameAreaLabels_2.layout().addLayout(row_layout)

                print("UI for coaches created successfully.")
                
        except Exception as e:
            print(f"An error occurred while initializing the coach UI: {e}")


    def load_heat_transfer_from_json(self):
        """Loads Heat transfer coefficient standstill (k) from the project data."""
        try:            
            # Check if 'Heat Transfer Saloon' key exists in project data
            if "Heat Transfer Saloon" in self.project_data:
                heat_transfer_value = self.project_data["Heat Transfer Saloon"]
                self.readonly_heat_transfer_values["Heat transfer coefficient standstill (k)"] = heat_transfer_value
            else:
                print("Key 'Heat Transfer Saloon' not found in project data.")
                
        except Exception as e:
            print(f"An error occurred while loading the JSON file: {e}")


    def load_json_values_to_ui(self):
        """Loads read-only values from the JSON file to the UI."""
        try:
            if hasattr(self, 'readonly_heat_transfer_values'):
                for label_name, value in self.readonly_heat_transfer_values.items():
                    # Handle double input fields
                    readonly_input = self.parent.findChild(QLineEdit, f"readonly_{label_name}")
                    if readonly_input:
                        readonly_input.setText(str(value))
                        print(f"Loaded JSON value for {label_name}: {value}")
            else:
                print("JSON data not found. Make sure 'self.readonly_heat_transfer_values' exists.")
        except Exception as e:
            print(f"An error occurred while loading JSON values to UI: {e}")
    def on_coach_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # Only save inputs if a previous coach was selected
            
            self.save_current_coach_inputs(self.current_coach_index)

            # Update the current coach index
            self.current_coach_index = index

            # Display stored inputs for the selected coach
            self.load_coach_inputs(index)
            
            # Update the coach name label
            coaches = self.project_data.get("Coaches", {})
            coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            self.parent.lblCoachName.setText(f"Coach {index + 1} - {coach_name}")

            
            print(f"Coach {index + 1} button clicked. Displaying stored values if available.")

        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")


    def save_current_coach_inputs(self, index):
        """Saves the current inputs for the given coach index."""
        try:
            if index in self.coach_inputs:
                for label_name, line_edit in self.coach_inputs[index].items():
                    widget = self.parent.findChild(QLineEdit, label_name)
                    if widget:  # If QLineEdit exists, save as tuple (object name, text)
                        self.coach_inputs[index][label_name] = (widget.objectName(), widget.text())
        except Exception as e:
            self.print_utf8(f"An error occurred while saving inputs for Coach {index + 1}: {e}")

    def load_coach_inputs(self, index):
        """Loads the saved inputs for the given coach index into the UI."""
        try:
            if index in self.coach_inputs:
                for label_name, (object_name, saved_text) in self.coach_inputs[index].items():
                    widget = self.parent.findChild(QLineEdit, object_name)
                    if widget:  # If QLineEdit exists, set its text
                        widget.setText(saved_text)
        except Exception as e:
            self.print_utf8(f"An error occurred while loading inputs for Coach {index + 1}: {e}")
    def print_utf8(self,text):
        try:
            print(text.encode('utf-8').decode('utf-8'))  # Ensure the text is properly encoded/decoded
        except UnicodeEncodeError:
            print("Error printing text due to unsupported characters.")


    def natural_convection_heat_transfer_coefficient_vertical(self, delta_t, l):
        """
        Calculates the natural convection heat transfer coefficient for a vertical surface.
        
        Parameters:
        delta_t (float): Temperature difference (°C)
        l (float): Characteristic length (m)
        
        Returns:
        float: Natural convection heat transfer coefficient (h) in W/m²K
        """
        # Constants (these may be updated later)
        C = 1.42
        n = 0.25

        # Apply the formula: h = C * (ΔT / L)^n
        h = C * ((delta_t / l) ** n)
        return h
    
    def natural_convection_heat_transfer_coefficient_horizontal(self, delta_t, l):
        """
        Calculates the natural convection heat transfer coefficient for a horizontal surface.
        
        Parameters:
        delta_t (float): Temperature difference (°C)
        l (float): Characteristic length (m)
        
        Returns:
        float: Natural convection heat transfer coefficient (h) in W/m²K
        """
        # Constants (these may be updated later)
        C = 1.31
        n = 0.33

        # Apply the formula: h = C * (ΔT / L)^n
        h = C * ((delta_t / l) ** n)
        return h




    



