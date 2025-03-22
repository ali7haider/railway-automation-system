from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

class CoachPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.project_data = {}
        self.coach_inputs = {}
        self.current_coach_index = 0  # Initialize current_coach_index
        self.first_time_click = True  # Track if it's the first click

        self.area_labels = ["Saloon 1", "Saloon 2", "Saloon 3","Catering/Buffet","Vestibule 1","Vestibule 2","WC 1","WC 2"
                            ,"Crew","Corridor 1","Corridor 2","Compartment 1","Compartment 2","Compartment 3","Compartment 4","Compartment 5","Compartment 6",
                            "Annex Area 1","Annex Area 2","Nursery","HVAC 1","HVAC 2","Exterior"]
        self.area_labels_2 = ["Nº Passengers", "Heat transfer coefficient standstill (k)", "Coach Length",
                              "Saloon 1 Length","Saloon 2 Length","Saloon 3 Length","Coach Width","Coach Length"
                              ,"Windows Area per side","Total Exterior Area","Total Exterior Area (no ends)"
                              ,"g (Windows)","ϐ (Windows)","kW (Walls)","εW","φ (Walls)","h (Walls)","kD (Roof)","εD","h (Roof)"]

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
            
            # Define units for specific labels in area_labels_2
            units = {
                "Total Exterior Area": "m²",
                "Total Exterior Area (no ends)": "m²",
                "h (Walls)": "W/k*m²",
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
                    label.setMinimumWidth(label_minimum_width)  # Set minimum width for label

                    line_edit = QLineEdit()
                    line_edit.setObjectName(label_name)
                    
                    if label_name in readonly_fields:
                        line_edit.setReadOnly(True)

                    row_layout.addWidget(label)
                    row_layout.addWidget(line_edit)
                    
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
                    label.setMinimumWidth(260)  # Set minimum width for label

                    line_edit = QLineEdit()
                    line_edit.setObjectName(label_name)
                    
                    if label_name in readonly_fields:
                        line_edit.setReadOnly(True)

                    row_layout.addWidget(label)
                    row_layout.addWidget(line_edit)

                    # Add unit label if it exists, otherwise add a placeholder QLabel for alignment
                    if label_name in units:
                        unit_label = QLabel(units[label_name])
                    else:
                        unit_label = QLabel("")  # Placeholder QLabel
                    
                    unit_label.setMinimumWidth(50)  # Ensuring a consistent space even if no unit exists
                    row_layout.addWidget(unit_label)

                    self.parent.frameAreaLabels_2.layout().addLayout(row_layout)

                    for coach_index in range(total_coaches):
                        self.coach_inputs[coach_index][label_name] = (line_edit.objectName(), line_edit.text())

                print("UI for coaches created successfully.")

        except Exception as e:
            print(f"An error occurred while initializing the coach UI: {e}")

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
            print(f"An error occurred while saving inputs for Coach {index + 1}: {e}")


    def load_coach_inputs(self, index):
        """Loads the saved inputs for the given coach index into the UI."""
        try:
            if index in self.coach_inputs:
                for label_name, (object_name, saved_text) in self.coach_inputs[index].items():
                    widget = self.parent.findChild(QLineEdit, object_name)
                    if widget:  # If QLineEdit exists, set its text
                        widget.setText(saved_text)
                        print(f"Loaded: {label_name} -> {saved_text}")
        except Exception as e:
            print(f"An error occurred while loading inputs for Coach {index + 1}: {e}")






    



