from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math

class SensorPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.current_coach_index = 0  # Initialize current_coach_index
        self.project_data = {}  # Initialize project_data    
    
    def load_coach_data(self, project_data):
        """Loads coach data from project and updates UI."""
        try:
            if "Project_info" not in project_data:
                return
            
            self.project_data = project_data["Project_info"]
            
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
                    self.parent.frameCoachesButtons_2.layout().addWidget(coach_button)
                except Exception as e:
                    print(f"An error occurred while creating button for Coach {i + 1}: {e}")
            coaches = self.project_data.get("Coaches", {})
            coach_name = coaches.get(f"Coach {0 + 1}", f"Coach {0 + 1}")
            self.parent.lblCoachName_3.setText(f"Coach {0 + 1} - {coach_name}")
        except Exception as e:
            print(f"An error occurred while updating coach inputs: {e}")
    def on_coach_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # Only save inputs if a previous coach was selected
            
            # self.save_current_coach_inputs(self.current_coach_index)

            # Update the current coach index
            self.current_coach_index = index

            # Display stored inputs for the selected coach
            # self.load_coach_inputs(index)
            
            # Update the coach name label
            coaches = self.project_data.get("Coaches", {})
            coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            self.parent.lblCoachName_3.setText(f"Coach {index + 1} - {coach_name}")

            
            print(f"Coach {index + 1} button clicked. Displaying stored values if available.")

        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")
