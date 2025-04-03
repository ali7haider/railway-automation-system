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

class TestPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.current_coach_index = 0  # Initialize current_coach_index
        self.project_info = {}  # Initialize project_data  
        self.coach_table_data = {}  # Initialize coach_table_data  
        self.project_data = {}

        self.test_tables = {
            "tableTestList1": None, 
            "tableTestList2": None
        }
        self.load_tables()
        # Load the test data based on the standard saloon
    def load_test_data(self):
        """
        Load and filter the test data by dynamically generating the filename from the project standard saloon.
        The method fetches the test data and passes it to another function for filtering based on project-specific parameters (like Winter/Summer conditions).

        :return: The filtered test data, or None if an error occurs or data is not found.
        """
        try:
            # Retrieve the standard saloon from the project data
            standard_saloon = self.project_data.get('Project_info', {}).get('Standard Saloon', 'None')
            
            if standard_saloon != 'None':
                standard_name = standard_saloon.split(":")[0]
                test_data_filename = f"TestList{standard_name}.json"
                
                # Call the function to fetch the test data based on the filename
                data = ProjectManager.get_test_data(test_data_filename)
                
                # Check if data is successfully loaded
                if data:
                    # Pass the data to the filter function
                    filtered_data = self.filter_test_data(data)
                    
                    print(f"Filtered data for {test_data_filename}: {filtered_data[:3]}")  # Adjust the number here as needed
                else:
                    print(f"Error: No test data found for {test_data_filename}")
                    return None
            else:
                print("Standard saloon not found in project data.")
                return None
        except Exception as e:
            print(f"Error loading and processing test data: {e}")
            return None


    def filter_test_data(self, data):
        """
        Filter the test data based on project-specific parameters like WinterZone and SummerZone.

        :param data: The test data to be filtered
        :return: The filtered test data
        """
        try:
            # Retrieve WinterZone and SummerZone from project data
           # Retrieve WinterZone

            # Retrieve WinterZone
            winter_zone = self.project_data.get('Exterior_Condition_Saloon', {}).get('WinterZone', {}).get('custom', None)
            if winter_zone == 'None' or winter_zone is None:
                winter_zone = self.project_data.get('Exterior_Condition_Saloon', {}).get('WinterZone', {}).get('default', 'II')

            # Retrieve SummerZone
            summer_zone = self.project_data.get('Exterior_Condition_Saloon', {}).get('SummerZone', {}).get('custom', None)
            if summer_zone == 'None' or summer_zone is None:
                summer_zone = self.project_data.get('Exterior_Condition_Saloon', {}).get('SummerZone', {}).get('default', 'II')
            # Process each test entry in the data
            for test_entry in data:
                # Handle the "Mean temperature in climatic chamber" based on Winter/Summer
                if isinstance(test_entry['Mean temperature in climatic chamber [ºC]'], dict):
                    if f'Winter {winter_zone}' in test_entry['Mean temperature in climatic chamber [ºC]']:
                        test_entry['Mean temperature in climatic chamber [ºC]'] = test_entry['Mean temperature in climatic chamber [ºC]'].get(f'Winter {winter_zone}', 'N/A')
                    elif f'Summer {summer_zone}' in test_entry['Mean temperature in climatic chamber [ºC]']:
                        test_entry['Mean temperature in climatic chamber [ºC]'] = test_entry['Mean temperature in climatic chamber [ºC]'].get(f'Summer {summer_zone}', 'N/A')
                else:
                    # If it's not a dictionary, simply leave the value as it is
                    test_entry['Mean temperature in climatic chamber [ºC]'] = test_entry['Mean temperature in climatic chamber [ºC]']

                # Similarly handle the other fields that depend on project data (like humidity, wind speed, etc.)
                if isinstance(test_entry['Relative humidity in climatic chamber [%]'], dict):
                    test_entry['Relative humidity in climatic chamber [%]'] = test_entry['Relative humidity in climatic chamber [%]'].get(f'Winter {winter_zone}', 'N/A')
                else:
                    # If it's not a dictionary, simply leave the value as it is
                    test_entry['Relative humidity in climatic chamber [%]'] = test_entry['Relative humidity in climatic chamber [%]']

                if isinstance(test_entry['Sun radiation [W/m2]'], dict):
                    test_entry['Sun radiation [W/m2]'] = test_entry['Sun radiation [W/m2]'].get(f'Summer {summer_zone}', 'N/A')
                else:
                    # If it's not a dictionary, simply leave the value as it is
                    test_entry['Sun radiation [W/m2]'] = test_entry['Sun radiation [W/m2]']
                # Handle Wind speed logic
                if 'Wind speed' in test_entry:
                    if 'max' in test_entry['Wind speed'].lower():  # If Wind speed is max
                        # Assign the maximum speed from the project data
                        test_entry['Wind speed [km/h]'] = self.project_data.get('Project_info', {}).get('Maximum Speed', 0)
                    elif 'min' in test_entry['Wind speed'].lower():  # If Wind speed is min
                        test_entry['Wind speed [km/h]'] = '0-15'
            return data  # Return the filtered data

        except Exception as e:
            print(f"Error filtering test data: {e}")
            return None



    def process_test_data(self, test_data):
        """Process and load the test data into the relevant tables or fields."""
        # Example: Populate the test tables with test data
        for table_name, table_widget in self.test_tables.items():
            if table_widget:
                # Example: Populate table with test data
                for row_index, test_case in enumerate(test_data):
                    table_widget.insertRow(row_index)
                    for col_index, key in enumerate(test_case.keys()):
                        item = QTableWidgetItem(str(test_case[key]))
                        table_widget.setItem(row_index, col_index, item)
    
    
    
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
                    self.parent.frameCoachesButtons_3.layout().addWidget(coach_button)
                except Exception as e:
                    print(f"An error occurred while creating button for Coach {i + 1}: {e}")
            coaches = self.project_info.get("Coaches", {})
            coach_name = coaches.get(f"Coach {0 + 1}", f"Coach {0 + 1}")
            self.parent.lblCoachName_4.setText(f"Coach {0 + 1} - {coach_name}")
        except Exception as e:
            print(f"An error occurred while updating coach inputs: {e}")
    def on_coach_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # # Save the current coach's table data before switching
            # self.save_current_coach_tables()

            # # Update the current coach index
            # self.current_coach_index = index

            # # Load the data for the newly selected coach
            # self.load_coach_tables()

            # # Update the coach name label
            # coaches = self.project_info.get("Coaches", {})
            # coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            # self.parent.lblCoachName_3.setText(f"Coach {index + 1} - {coach_name}")
            
            print(f"Switched to Coach {index + 1} and loaded its data.")
        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")

    def load_tables(self):
        headers = [
            "Test ID", "Test Norm ID", "Description of the test", "Mean temperature in climatic chamber (Winter/Summer)",
            "Relative humidity in climatic chamber (Winter/Summer)", "Passenger load [%]", "Sun radiation [W/m2] (Winter/Summer)",
            "Wind speed", "Wind speed [km/h]", "Setpoint [ºC]", "Setpoint curve [ºC]", "Setpoint delta", "Setpoint delta value",
            "Criteria To be taken into account for evaluation", "Criteria To be checked", "Remarks", "Compartment test",
            "Range", "Sensible heat passengers", "Latent heat passengers", "Solar Power", "Client requirement", "Test duration"
        ]
        
        # Set uniform row height and maximum header height
        row_height = 30
        header_max_height = 35

        for table_name in self.test_tables.keys():
            table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)
            
            if table_widget:
                self.test_tables[table_name] = table_widget  # Store the table widget

                # Set the table to have the correct number of columns
                table_widget.setColumnCount(len(headers))
                table_widget.setRowCount(0)
                table_widget.setHorizontalHeaderLabels(headers)

                # Make the headers stretch to fill the width
                header = table_widget.horizontalHeader()
                header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                header.setMaximumHeight(header_max_height)

                # Set the uniform row height for all rows
                table_widget.verticalHeader().setDefaultSectionSize(row_height)
                
                # Enable right-click menu for specific cells (e.g., "Test ID" and "Client requirement")
                table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
                table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        """Handles showing the context menu when right-clicking on certain cells."""
        context_menu = QMenu(self.parent)

        # Get the table widget where the right-click occurred
        table_widget = self.sender()
        item = table_widget.itemAt(pos)

        if item:
            row = item.row()
            col = item.column()

            # Check if the clicked cell is Test ID or Client requirement (columns 0 and 21)
            if col == 0:  # Test ID column
                edit_action = QAction("Edit Test ID", self.parent)
                edit_action.triggered.connect(lambda: self.edit_cell(row, col))
                context_menu.addAction(edit_action)
            elif col == 21:  # Client requirement column
                edit_action = QAction("Edit Client Requirement", self.parent)
                edit_action.triggered.connect(lambda: self.edit_cell(row, col))
                context_menu.addAction(edit_action)

        context_menu.exec_(table_widget.mapToGlobal(pos))

    def edit_cell(self, row, col):
        """Handles editing the content of a cell via a right-click menu."""
        table_widget = self.parent.findChild(QtWidgets.QTableWidget, "tableTestList1")
        item = table_widget.item(row, col)
        
        if item:
            # Allow the user to modify the content of the cell
            new_text, ok = QtWidgets.QInputDialog.getText(self.parent, f"Edit Cell ({row}, {col})", "Enter new value:", text=item.text())
            
            if ok:
                item.setText(new_text)
