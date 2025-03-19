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

        self.area_labels = ["Area 1", "Area 2", "Area 3"]
        self.area_labels_2 = ["Area A", "Area B", "Area C"]

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
                    line_edit = QLineEdit()
                    line_edit.setObjectName(label_name)  # Set object name for identification

                    row_layout.addWidget(label)
                    row_layout.addWidget(line_edit)
                    
                    self.parent.frameAreaLabels.layout().addLayout(row_layout)

                    # Store the same QLineEdit object for ALL coaches
                    for coach_index in range(total_coaches):
                        self.coach_inputs[coach_index][label_name] = line_edit  

                # Adding labels and QLineEdits for frameAreaLabels_2
                for label_name in self.area_labels_2:
                    row_layout = QHBoxLayout()  
                    row_layout.setAlignment(Qt.AlignLeft)
                    row_layout.setContentsMargins(0, 0, 0, 0)  
                    row_layout.setSpacing(15)  

                    label = QLabel(label_name)
                    line_edit = QLineEdit()
                    line_edit.setObjectName(label_name)  # Set object name for identification

                    row_layout.addWidget(label)
                    row_layout.addWidget(line_edit)
                    
                    self.parent.frameAreaLabels_2.layout().addLayout(row_layout)

                    # Store the same QLineEdit object for ALL coaches
                    for coach_index in range(total_coaches):
                        self.coach_inputs[coach_index][label_name] = line_edit  

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
            self.update_coach_inputs(index)
            
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
            print(f"Saving inputs for Coach {index + 1}...")
            print(self.coach_inputs)
            if index in self.coach_inputs:
                for label_name, line_edit in self.coach_inputs[index].items():
                    if isinstance(line_edit, QLineEdit):
                        self.coach_inputs[index][label_name] = line_edit.text()  # Store QLineEdit text
            print(f"Inputs for Coach {index + 1} saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving inputs for Coach {index + 1}: {e}")


    def update_coach_inputs(self, index):
        """Updates the UI with stored inputs for the given coach index."""
        try:
            if index in self.coach_inputs:
                inputs_dict = self.coach_inputs[index]
                for label_name, saved_value in inputs_dict.items():
                    if isinstance(saved_value, str):  # Restore only if it's a saved text value
                        line_edit = self.find_line_edit(label_name)
                        if line_edit:
                            line_edit.setText(saved_value)
            print(f"Inputs for Coach {index + 1} restored successfully.")
        except Exception as e:
            print(f"An error occurred while updating inputs for Coach {index + 1}: {e}")


    def find_line_edit(self, label_name):
        """Finds the QLineEdit by name in the current UI."""
        for frame in [self.parent.frameAreaLabels, self.parent.frameAreaLabels_2]:
            layout = frame.layout()
            if layout is not None:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if isinstance(item, QHBoxLayout):
                        line_edit = item.itemAt(1).widget()  # Assuming it's QLabel + QLineEdit
                        if isinstance(line_edit, QLineEdit) and line_edit.objectName() == label_name:
                            return line_edit
        return None




    



