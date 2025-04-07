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
        self.parent.btnCabin1_4.clicked.connect(lambda: self.on_cabin_button_click(0))
        self.parent.btnCabin2_4.clicked.connect(lambda: self.on_cabin_button_click(1))
        self.setup_table_context_menu(self.parent.planningTable)
        self.planning_tables = {
            "planningTable": None, 
        }

        self.load_table()
    def on_cabin_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # Save the current coach's table data before switching
            self.save_current_coach_tables()
            num_coaches_t = int(self.project_data.get("Number of Coaches per Train", 0))
            # Update the current coach index
            if index==0:
                num_coaches_t = num_coaches_t+1
            else:
                num_coaches_t = num_coaches_t+2
            self.current_coach_index = num_coaches_t

            # Load the data for the newly selected coach
            self.load_coach_tables()

            # Update the coach name label
            # Retrieve Cabin Name based on index
            cabin_name_key = f"Cabin {index+1} Name"
            cabin_name = self.project_data.get(cabin_name_key, '')
            self.parent.lblCoachName_5.setText(f"Cabin {index + 1} - {cabin_name}")
            
            print(f"Switched to Cabin {index + 1} and loaded its data.")
        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")
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
            # Set the item in the table
            table.setItem(row_position, col_index, item)

        # Debug: Check mode and row color
        if mode == "stab":
            row_color = "#d3d3d3"  # Light grey for Stabilization
        elif mode == "off":
            row_color = "#a9a9a9"  # Dark grey for OFF
        elif mode == "prep":
            row_color = "#fffacd"  # Light yellow for Vehicle Preparation
        else:
            row_color = "#ffffff"  # Default color for normal rows
        
        # print(f"Row color for mode '{mode}': {row_color}")  # Debug: Check the color

        # Apply background color for each item in the row
        for col_index in range(table.columnCount()):
            item = table.item(row_position, col_index)
            if item is not None:
                item.setBackground(QtGui.QColor(row_color))  # Set the background color for each item

        # print(f"Background color applied for each item in row {row_position}.")  # Debug: Confirm color applied
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
            # Enable right-click menu for specific cells (e.g., "Test ID" and "Client requirement")
            
            table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            
            # Hide the additional columns (column index 14 and 15)
            table_widget.setColumnHidden(14, True)  # Hide column 14
            table_widget.setColumnHidden(15, True)  # Hide column 15

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
            self.save_current_coach_tables()

            # # Update the current coach index
            self.current_coach_index = index

            # # Load the data for the newly selected coach
            self.load_coach_tables()

            # Update the coach name label
            coaches = self.project_info.get("Coaches", {})
            coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            self.parent.lblCoachName_5.setText(f"Coach {index + 1} - {coach_name}")
            
            print(f"Switched to Coach {index + 1} and loaded its data.")
        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")

    def save_current_coach_tables(self):
        """Save the current coach's table data to the dictionary."""
        try:
            coach_data = {}

            for table_name in self.planning_tables.keys():
                table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)

                if table_widget:
                    table_data = []
                    row_count = table_widget.rowCount()

                    for row in range(row_count):
                        row_data = []
                        for col in range(table_widget.columnCount()):
                            item = table_widget.cellWidget(row, col)
                            table_item = table_widget.item(row, col)
                            row_data.append(table_item.text() if table_item else "")
                                
                        table_data.append(row_data)
                    
                    coach_data[table_name] = table_data
            
            # Save the data for the current coach index
            self.coach_table_data[self.current_coach_index] = coach_data
        except Exception as e:
            print(f"An error occurred while saving table data: {e}")
    def load_coach_tables(self):
        """Load table data for the current coach index, if available."""
        try:
            # Clear all rows for all tables before loading data
            for table_name in self.planning_tables.keys():
                table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)

                table_widget.setRowCount(0)
            
            if self.current_coach_index in self.coach_table_data:
                coach_data = self.coach_table_data[self.current_coach_index]
                for table_name in self.planning_tables.keys():
                    table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)
                    if table_name in coach_data:
                        table_data = coach_data[table_name]
                        # Clear all rows before loading
                        # Set row count
                        table_widget.setRowCount(len(table_data))

                        for row_index, row_data in enumerate(table_data):
                            for col_index, cell_value in enumerate(row_data):
                                item = QtWidgets.QTableWidgetItem(str(cell_value))
                                table_widget.setItem(row_index, col_index, item)

                        # Optional: Resize rows and columns to content
                        table_widget.resizeColumnsToContents()
                        table_widget.resizeRowsToContents()
                        #populate the table with the data
            
            print(f"Successfully loaded data for index {self.current_coach_index}.")
            
        except Exception as e:
            print(f"An error occurred while loading table data: {e}")
    def setup_table_context_menu(self, table_widget):
        try:
            # Enable custom context menu
            table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            table_widget.customContextMenuRequested.connect(lambda pos: self.show_table_context_menu(pos, table_widget))
        except Exception as e:
            print(f"Error setting up context menu: {e}")

    def show_table_context_menu(self, pos, table_widget):
        try:
            # Get the position of the clicked row
            index = table_widget.indexAt(pos)

            if index.isValid():
                menu = QMenu(table_widget)
                
                # Create 'Edit Row' action
                edit_action = QAction("Edit Row", table_widget)
                edit_action.triggered.connect(lambda: self.edit_row_in_table(index.row(), table_widget))
                
                # Create 'Delete Row' action
                delete_action = QAction("Delete Row", table_widget)
                delete_action.triggered.connect(lambda: self.delete_row_from_table(index.row(), table_widget))
                
                # Create 'Move Up Row' action
                move_up_action = QAction("Move Up", table_widget)
                move_up_action.triggered.connect(lambda: self.move_row_up(index.row(), table_widget))
                
                # Create 'Move Down Row' action
                move_down_action = QAction("Move Down", table_widget)
                move_down_action.triggered.connect(lambda: self.move_row_down(index.row(), table_widget))
                
                # Add actions to menu
                menu.addAction(edit_action)
                menu.addAction(delete_action)
                menu.addAction(move_up_action)
                menu.addAction(move_down_action)
                
                # Show the menu at the cursor position
                menu.exec_(table_widget.viewport().mapToGlobal(pos))
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def edit_row_in_table(self, row, table_widget):
        try:
            # Logic to edit the selected row, you can implement the edit functionality here
            print(f"Editing row {row}")
            # You can open a dialog to edit row or make the items editable, based on your requirements
        except Exception as e:
            print(f"Error editing row: {e}")

    def delete_row_from_table(self, row, table_widget):
        try:
            # Remove the specified row from the table
            table_widget.removeRow(row)
        except Exception as e:
            print(f"Error deleting row: {e}")

    def move_row_up(self, row, table_widget):
        try:
            # Check if the row is not the first one
            if row > 0:
                # Get the items from the row to move
                items = [table_widget.takeItem(row, col) for col in range(table_widget.columnCount())]
                
                # Insert the items back one row up
                for col in range(table_widget.columnCount()):
                    table_widget.setItem(row - 1, col, items[col])
                
                # Remove the original row
                table_widget.removeRow(row)
        except Exception as e:
            print(f"Error moving row up: {e}")

    def move_row_down(self, row, table_widget):
        try:
            # Check if the row is not the last one
            if row < table_widget.rowCount() - 1:
                # Get the items from the row to move
                items = [table_widget.takeItem(row, col) for col in range(table_widget.columnCount())]
                
                # Insert the items back one row down
                for col in range(table_widget.columnCount()):
                    table_widget.setItem(row + 1, col, items[col])
                
                # Remove the original row
                table_widget.removeRow(row)
        except Exception as e:
            print(f"Error moving row down: {e}")
