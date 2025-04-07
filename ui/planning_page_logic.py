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
        self.parent.btnAddPlanning.clicked.connect(self.open_planning_dialog)

        self.load_table()
    def open_planning_dialog(self):

        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("Add Planning Entry")
        layout = QtWidgets.QVBoxLayout()

        # Label and input
        label = QtWidgets.QLabel("Enter Test ID:")
        test_id_input = QtWidgets.QLineEdit()
        layout.addWidget(label)
        layout.addWidget(test_id_input)

        # Buttons for actions
        btn_stab = QtWidgets.QPushButton("Stabilization")
        btn_off = QtWidgets.QPushButton("OFF")
        btn_prep = QtWidgets.QPushButton("Vehicle Preparation")

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(btn_stab)
        button_layout.addWidget(btn_off)
        button_layout.addWidget(btn_prep)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # ENTER key press triggers normal entry
        test_id_input.returnPressed.connect(lambda: self.handle_test_id_entry(test_id_input.text(), dialog))

        # Buttons trigger other special rows
        btn_stab.clicked.connect(lambda: self.add_planning_row("", "stab", dialog))
        btn_off.clicked.connect(lambda: self.add_planning_row("", "off", dialog))
        btn_prep.clicked.connect(lambda: self.add_planning_row("", "prep", dialog))

        dialog.exec_()


    def handle_test_id_entry(self, test_id, dialog):
        coach_index = self.current_coach_index
        coach_data = self.parent.test_page_manager.coach_table_data.get(coach_index, {})

        # Aggregate all rows from all tables under current coach
        all_rows = []
        for table_name, table_rows in coach_data.items():
            all_rows.extend(table_rows)

        # Search for matching Test Norm ID (index 1 in each row)
        for row in all_rows:
            if row[1] == test_id:
                self.add_planning_row(test_id, "enter", dialog, row)  # Allow dialog to close inside this
                return

        # If no match found, show warning and DO NOT close the dialog
        QtWidgets.QMessageBox.warning(self.parent, "Not Found", f"Test Norm ID '{test_id}' not found.")
        # Do not close the dialog here; keep it open


    def add_planning_row(self, test_id, mode, dialog, row_data=None):
        if mode == "enter":
            if row_data is None:
                return  # This shouldn't happen because we check before calling
            # Insert row with provided data
            self.insert_test_row_into_table(row_data)
        elif mode in ("stab", "off", "prep"):
            # Logic for special rows: Stabilization, OFF, and Vehicle Preparation
            if mode == "stab":
                description = "Stabilization test"
                duration = "0:00:00"
            elif mode == "off":
                description = "OFF test"
                duration = "0:00:00"
            elif mode == "prep":
                description = "Vehicle Preparation"
                duration = "0:00:00"
            
            # Create row with special values
            row_data = [
                "",                          # File ID (empty)
                "",                          # Test Norm ID
                description,                 # Description of the test
                "",                          # Mean temperature in climatic chamber [ºC]
                "",                          # Relative humidity [%]
                "",                          # Passenger load [%]
                "",                          # Sun radiation [W/m2]
                "",                          # Wind speed
                "",                          # Wind speed [km/h]
                "",                          # Setpoint [ºC]
                "",                          # Setpoint curve [ºC]
                "",                          # Setpoint delta
                "",                          # Setpoint delta value
                "",                          # Criteria To be taken into account for evaluation
                "",                          # Criteria To be checked
                "",                          # Remarks
                "",                          # Compartment test
                "",                          # Range
                "",                          # Sensible heat passengers
                "",                          # Latent heat passengers
                "",                          # Solar Power
                "",                          # Client requirement
                duration                     # Test duration (0h)
            ]
            
            # Insert the new row into the table with the special row flag
            self.insert_test_row_into_table(row_data, mode)  # Pass the mode to color the row correctly

        dialog.accept()  # Close the dialog only after the row is added



    def insert_test_row_into_table(self, row_data, mode="normal"):
        table = self.parent.planningTable  # Your planning QTableWidget
        row_position = table.rowCount()
        table.insertRow(row_position)

        # Base values
        today = QtCore.QDate.currentDate()
        estimated_date_str = today.toString("yyyy-MM-dd")

        # Get start time for special rows
        if row_position == 0:
            start_time = QtCore.QTime(8, 0, 0)  # 08:00:00 for the first test
        else:
            prev_end_time_item = table.item(row_position - 1, 7)  # Column 7 = End Time
            if prev_end_time_item:
                prev_end_datetime = QtCore.QDateTime.fromString(prev_end_time_item.text(), "yyyy-MM-dd HH:mm:ss")
                start_time = prev_end_datetime.time()
            else:
                start_time = QtCore.QTime(8, 0, 0)

        # Duration (will be 0:00:00 for special rows)
        if mode == "stab":
            duration_str = "0:00:00"
        elif mode == "off":
            duration_str = "0:00:00"
        elif mode == "prep":
            duration_str = "0:00:00"
        else:
            duration_str = row_data[22]  # e.g., '2:00:00' for normal rows
        duration = QtCore.QTime.fromString(duration_str, "H:mm:ss")
        duration_secs = duration.hour() * 3600 + duration.minute() * 60 + duration.second()

        # Combine date and time into QDateTime
        start_datetime = QtCore.QDateTime(today, start_time)
        end_datetime = start_datetime.addSecs(duration_secs)

        # Column mapping with updated fields
        column_mapping = {
            0: "",  # File ID (editable)
            1: row_data[1],  # Test Norm ID
            2: row_data[21],  # Client requirement
            3: row_data[2],  # Description of the test
            4: estimated_date_str,  # Estimated date
            5: duration_str,  # Duration (editable)
            6: start_datetime.toString("yyyy-MM-dd HH:mm:ss"),  # Start time
            7: end_datetime.toString("yyyy-MM-dd HH:mm:ss"), # End time
            8: row_data[3],  # Mean temperature in climatic chamber [ºC]
            9: row_data[4],  # Relative humidity [%]
            10: row_data[5],  # Air speed [km/h]
            11: row_data[6],  # Solar radiation [W/m2]
            12: row_data[16],  # Lights [ON/OFF]
            13: row_data[5],  # Passenger loads [%]
            16: row_data[12],  # Set Points value k
            17: row_data[14],  # Criteria to be checked
            18: row_data[17],  # Range
            19: row_data[13],  # Evaluation criteria
            20: row_data[15],  # Comments (editable)
        }

        # Set items into table
        for col_index in range(21):  # Adjusted for the number of columns in your mapping
            value = column_mapping.get(col_index, "")
            item = QtWidgets.QTableWidgetItem(value)
            if col_index in [0, 5, 20]:  # Editable: File ID, Duration, Comments
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            else:  # Non-editable
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            # Set the background color based on the mode
            if mode == "stab":
                item.setBackground(QtGui.QColor(211, 211, 211))  # Light grey for Stabilization
            elif mode == "off":
                item.setBackground(QtGui.QColor(169, 169, 169))  # Dark grey for OFF
            elif mode == "prep":
                item.setBackground(QtGui.QColor(255, 255, 224))  # Light yellow for Vehicle Preparation
            
            table.setItem(row_position, col_index, item)


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
