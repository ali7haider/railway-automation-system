import os
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QTableWidget, QHeaderView
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math
from PyQt5 import QtWidgets
from fpdf import FPDF
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction
from modules.project_manager import ProjectManager  # Import ProjectManager
import math

class PlanningPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.current_coach_index = 0  # Initialize current_coach_index
        self.project_info = {}  # Initialize project_data  
        self.coach_table_data = {}  # Initialize coach_table_data  
        self.project_data = {}
        self.load_table()
    def load_table(self):
        headers = [
            "File ID",                                 # Editable
            "Test norm ID",                            # From Test list module, non-editable
            "Client requirement",                      # From Test list module, non-editable
            "Description of the test",                 # From Test list module, non-editable
            "Estimated date",                          # Calculated
            "Duration of each test [h]",               # From Test list module, editable
            "Starting time",                           # Calculated
            "End time",                                # Calculated
            "Mean temperature in climatic chamber [ºC]", # From Test list module, non-editable
            "Relative humidity [%]",                   # From Test list module, non-editable
            "Air speed [km/h]",                        # From Test list module, non-editable
            "Solar radiation [W/m2]",                  # From Test list module, non-editable
            "Lights [ON/OFF]",                         # From Test list module, non-editable
            "Passenger loads [%]",                     # From Test list module, non-editable
            "Additional column 1",                     # Hidden / placeholder
            "Additional column 2",                     # Hidden / placeholder
            "Set point offset [K]",                    # From Test list module, non-editable
            "Tic [ºC]",                                 # From Test list module, non-editable
            "Range",                                   # From Test list module, non-editable
            "Evaluation criteria",                     # From Test list module, non-editable
            "Comments"                                 # Editable
        ]

        
        # Set uniform row height and maximum header height
        table_name = "planningTable"
        
        table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)
        
        if table_widget:

            # Set the table to have the correct number of columns
            table_widget.setColumnCount(len(headers))
            table_widget.setRowCount(0)
            table_widget.setHorizontalHeaderLabels(headers)

            # Make the headers stretch to fill the width
            header = table_widget.horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            table_widget.resizeRowsToContents()
            # Enable word wrap
            table_widget.setWordWrap(True)

            # Automatically resize row height based on content
            table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)


            # Optional: set minimum row height to avoid squishing short cells
            table_widget.verticalHeader().setDefaultSectionSize(30)
            # header.setMaximumHeight(header_max_height)


            # Set the uniform row height for all rows
            # table_widget.verticalHeader().setDefaultSectionSize(row_height)
            
            # Enable right-click menu for specific cells (e.g., "Test ID" and "Client requirement")
            
            table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            
            table_widget.customContextMenuRequested.connect(self.show_context_menu_user)
    def load_coach_data(self, project_data):
        """Loads coach data from project and updates UI."""
        try:
            if "Project_info" not in project_data:
                return
            
            self.project_info = project_data["Project_info"]
            self.project_data = project_data
            
            num_coaches = int(self.project_info.get("Number of Coaches per Train", 0))
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
                    self.parent.frameCoachesButtons_4.layout().addWidget(coach_button)
                except Exception as e:
                    print(f"An error occurred while creating button for Coach {i + 1}: {e}")
            coaches = self.project_info.get("Coaches", {})
            coach_name = coaches.get(f"Coach {0 + 1}", f"Coach {0 + 1}")
            self.parent.lblCoachName_5.setText(f"Coach {0 + 1} - {coach_name}")
        except Exception as e:
            print(f"An error occurred while updating coach inputs: {e}")
    def on_coach_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # # Save the current coach's table data before switching
            # self.save_current_coach_tables()

            # # Update the current coach index
            self.current_coach_index = index

            # # Load the data for the newly selected coach
            # self.load_coach_tables()

            # Update the coach name label
            coaches = self.project_info.get("Coaches", {})
            coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            self.parent.lblCoachName_5.setText(f"Coach {index + 1} - {coach_name}")
            
            print(f"Switched to Coach {index + 1} and loaded its data.")
        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")
    def show_context_menu_user(self, pos):
        """Handles showing the context menu when right-clicking on specific editable cells."""
        context_menu = QtWidgets.QMenu(self.parent)

        # Get the table widget where the right-click occurred
        table_widget = self.parent.sender()
        item = table_widget.itemAt(pos)

        if item:
            row = item.row()
            col = item.column()

            editable_labels = {
                0: "Edit Test ID",
                1: "Edit Test Norm ID",
                2: "Edit Description of the test",
                3: "Edit Mean temperature (°C)",
                4: "Edit Relative humidity (%)",
                5: "Edit Passenger load (%)",
                6: "Edit Sun radiation (W/m2)",
                13: "Edit Criteria To be taken into account for evaluation",
                14: "Edit Criteria To be checked",
                15: "Edit Remarks",
                21: "Edit Client requirement",
                22: "Edit Test duration",

            }

            if col in editable_labels:
                edit_action = QtWidgets.QAction(editable_labels[col], self.parent)
                edit_action.triggered.connect(lambda: self.edit_cell_user(table_widget, row, col))
                context_menu.addAction(edit_action)

        context_menu.exec_(table_widget.mapToGlobal(pos))


    def edit_cell_user(self, table_widget, row, col):
        """Edit a specific cell in the table with a text input dialog."""
        # Define limits for each column
        if col == 3:  # Mean temperature (°C)
            self.validate_and_edit(table_widget, row, col, -50, 60, "Mean temperature")
        elif col == 4:  # Relative humidity (%)
            self.validate_and_edit(table_widget, row, col, 0, 100, "Relative humidity")
        elif col == 5:  # Relative humidity (%)
            self.validate_and_edit(table_widget, row, col, 0, 100, "Passenger load")
        elif col == 6:  # Sun radiation (W/m2)
            self.validate_and_edit(table_widget, row, col, 0, 1500, "Sun radiation")
        elif col == 22:  # Test duration (hh:mm:ss)
            self.edit_test_duration(table_widget, row, col)
        else:
            # For other columns, simply allow editing as text
            table_widget.item(row, col).setText(
                QtWidgets.QInputDialog.getText(
                    self.parent, f"Edit Cell ({row}, {col})", "Enter new value:", text=table_widget.item(row, col).text()
                )[0]
            )


    def validate_and_edit(self, table_widget, row, col, min_value, max_value, column_name):
        """Common validation and editing function for columns with specific value ranges."""
        item = table_widget.item(row, col)
        
        if item:
            current_value = item.text() if item else ""

            # Handle empty values for specific columns
            if current_value == "":
                if column_name == "Relative humidity":
                    current_value = "-"  # Set to "-" for Relative humidity
                elif column_name == "Passenger load":
                    current_value = "0"  # Set to "0" for Passenger load [%]
                elif column_name == "Sun radiation":
                    current_value = "0"

            # Show input dialog
            new_value, ok = QtWidgets.QInputDialog.getText(
                self.parent, f"Edit {column_name}",
                f"Enter value for {column_name} ({min_value} to {max_value}):", text=current_value
            )

            if ok:
                try:
                    new_value = float(new_value)

                    # Check if the new value is within the allowed range
                    if min_value <= new_value <= max_value:
                        item.setText(str(new_value))
                    else:
                        QtWidgets.QMessageBox.warning(
                            self.parent, "Invalid Input",
                            f"{column_name} must be between {min_value} and {max_value}."
                        )
                except ValueError:
                    QtWidgets.QMessageBox.warning(
                        self.parent, "Invalid Input", f"Please enter a valid number for {column_name}."
                    )
    def edit_test_duration(self, table_widget, row, col):
        """Handle the editing of Test duration in hh:mm:ss format."""
        item = table_widget.item(row, col)
        if item:
            current_value = item.text() if item else ""

            # Show input dialog for time format
            new_value, ok = QtWidgets.QInputDialog.getText(
                self.parent, "Edit Test duration", "Enter time in format hh:mm:ss:", text=current_value
            )

            if ok:
                # Validate the time format
                if self.is_valid_time_format(new_value):
                    item.setText(new_value)
                else:
                    QtWidgets.QMessageBox.warning(
                        self.parent, "Invalid Input", "Please enter a valid time in hh:mm:ss format."
                    )


    def is_valid_time_format(self, time_str):
        """Check if the given time string is in hh:mm:ss format."""
        import re
        time_pattern = r"^\d{2}:\d{2}:\d{2}$"  # Regular expression for hh:mm:ss
        return bool(re.match(time_pattern, time_str))
