from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLineEdit, QPushButton
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

class CoachPageManager:
    def __init__(self, parent):
        self.parent = parent  # Reference to MasterScreen
        self.coach_widgets = []

    def update_coach_inputs(self, num_coaches):
        """Updates dynamically generated QPushButton widgets based on the number of coaches."""
        try:
            if not isinstance(num_coaches, int) or num_coaches <= 0:
                return  # Ignore invalid inputs
            
            # Remove all existing QPushButtons in frameCoachesButtons
            while self.coach_widgets:
                widget = self.coach_widgets.pop()
                widget.deleteLater()
            
            # Create new QPushButtons for each coach
            for i in range(num_coaches):
                coach_button = QPushButton(f"Coach {i + 1}", self.parent)
                coach_button.setMinimumHeight(32)  # Set minimum height to 35
                # Set cursor to pointer (hand icon)
                coach_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                coach_button.clicked.connect(lambda _, index=i: self.on_coach_button_click(index))
                
                self.coach_widgets.append(coach_button)
                self.parent.frameCoachesButtons.layout().addWidget(coach_button)
        
        except Exception as e:
            print(f"An error occurred while updating coach inputs: {e}")

    def on_coach_button_click(self, index):
        """Handles clicking on a coach button."""
        print(f"Coach {index + 1} button clicked. Updating the GUI...")
        # TODO: Add the code to update the GUI with inputs for the clicked coach.

    def load_coach_data(self, project_data):
        """Loads coach data from project and updates UI."""
        try:
            if "Project_info" not in project_data:
                return  # No project data to load
            project_info = project_data["Project_info"]
            # Get the number of coaches
            num_coaches = project_info.get("Number of Coaches per Train", 0)

            num_coaches=int(num_coaches)
            # Update the coach inputs based on the loaded number of coaches
            self.update_coach_inputs(num_coaches)

            
                        
        except ValueError:
            print("Error: Invalid number of coaches found in project data.")
        except KeyError as e:
            print(f"Error: Missing key in project data - {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading coach data: {e}")
