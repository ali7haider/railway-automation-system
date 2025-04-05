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
    def prepare_curve_data(self,project_data, curve_type='saloon'):
        # Fetch the regulation curve value dynamically based on the curve type (saloon or cabin)
        regulation_curve = project_data.get('Interior_Condition_Data', {}).get(f'RegulationCurve{curve_type.capitalize()}', {}).get('custom') or \
                            project_data.get('Interior_Condition_Data', {}).get(f'RegulationCurve{curve_type.capitalize()}', {}).get('default', 'Norm')

        # Fetch the curve data dynamically based on the curve type (saloon or cabin)
        curve_data = project_data['Interior_Condition_Data'].get(f'{curve_type}_curve', {})

        # Define the sections and labels (assuming the same structure for both saloon and cabin)
        curve_sections = [
            'Text Upper Limit', 'Tin Upper Limit', 'Text Lower Limit', 
            'Tin Lower Limit', 'Text Curve Limit', 'Tin Curve Limit'
        ]
        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        result = {}

        # Check if the curve type is Custom or Default
        for section in curve_sections:
            for label in labels:
                raw_value = curve_data.get(section, {}).get(label, {})

                # Select the correct value based on curve_type (Custom or Default)
                if regulation_curve == 'Custom':
                    # Use the custom value if available, else use default
                    value = raw_value.get('custom') if raw_value.get('custom') not in (None, 'None') else raw_value.get('default')
                else:
                    # For 'Norm' (or other default curve types), use default values directly
                    value = raw_value.get('default')

                # Ensure we have a valid float value, otherwise default to 0.0
                result[f'{section}_{label}'] = float(value) if value not in (None, 'None') else 0.0

        return result

    def calculate_curve(self,text, curve_data):
        """
        Calculates the interpolated Tin value based on the Text Curve Limit and Tin Curve Limit up to E.
        :param text: Input value (e.g., temperature).
        :param curve_data: Dictionary with keys for Text and Tin values for 'Curve Limit' (A to E).
        :return: Interpolated Tin value.
        """
        # Extract the Text and Tin values from the curve data (for both saloon and cabin, up to E)
        text_vals = [curve_data.get(f'Text Curve Limit_{chr(65+i)}', 0.0) for i in range(5)]  # A to E
        tin_vals = [curve_data.get(f'Tin Curve Limit_{chr(65+i)}', 0.0) for i in range(5)]  # A to E

        # Debug: Print the Text and Tin values being used in the curve calculation
        print(f"Text values (A-E): {text_vals}")
        print(f"TIN values (A-E): {tin_vals}")

        # Perform interpolation based on the input text value
        for i in range(4):  # We have 5 points, so 4 intervals (A-E)
            if text_vals[i] <= text < text_vals[i+1]:
                # Perform the interpolation between the two points
                return tin_vals[i] + (text - text_vals[i]) * (
                    (tin_vals[i+1] - tin_vals[i]) / (text_vals[i+1] - text_vals[i])
                )

        # Handle the case for the last range (TextE to TinE)
        if text_vals[3] <= text <= text_vals[4]:
            return tin_vals[4] if text_vals[3] == text_vals[4] else tin_vals[3] + (
                text - text_vals[3]) * ((tin_vals[4] - tin_vals[3]) / (text_vals[4] - text_vals[3]))

        # If no match, return None (out of range)
        return None

    def filter_test_data(self, data):
        """
        Filter the test data based on project-specific parameters like WinterZone, SummerZone,
        wind speed logic, and setpoint delta + curve-based Setpoint [ºC] calculations.

        :param data: The test data to be filtered
        :return: The filtered test data
        """
        def get_custom_or_default(field_dict):
            if isinstance(field_dict, dict):
                custom = field_dict.get('custom', None)
                if custom is not None and custom != 'None':
                    return custom
                return field_dict.get('default', 'N/A')
            return field_dict

        try:
            # Zones
            exterior = self.project_data.get('Exterior_Condition_Saloon', {})
            winter_zone = get_custom_or_default(exterior.get('WinterZone', {}))
            summer_zone = get_custom_or_default(exterior.get('SummerZone', {}))

            # Interior data
            interior_data = self.project_data.get('Interior_Condition_Data', {})
            max_speed = self.project_data.get('Project_info', {}).get('Maximum Speed', 0)

            # Max mean temp saloon
            raw_max_mean_temp = get_custom_or_default(interior_data.get('MaxMeanTempSaloon'))
            try:
                max_mean_temp_saloon = float(str(raw_max_mean_temp).replace('°C', '').strip())
            except ValueError:
                max_mean_temp_saloon = None

            # Saloon curve preparation
            curve_data = self.prepare_curve_data(self.project_data,curve_type='saloon')

            # Loop through data
            for test_entry in data:
                # Mean temperature
                temp_data = test_entry.get('Mean temperature in climatic chamber [ºC]')
                exterior_temp = None
                if isinstance(temp_data, dict):
                    exterior_temp = temp_data.get(f'Winter {winter_zone}') or temp_data.get(f'Summer {summer_zone}')
                    test_entry['Mean temperature in climatic chamber [ºC]'] = exterior_temp
                else:
                    exterior_temp = temp_data

                # Relative humidity
                humidity_data = test_entry.get('Relative humidity in climatic chamber [%]')
                if isinstance(humidity_data, dict):
                    test_entry['Relative humidity in climatic chamber [%]'] = \
                        humidity_data.get(f'Winter {winter_zone}', 'N/A')

                # Sun radiation
                radiation_data = test_entry.get('Sun radiation [W/m2]')
                if isinstance(radiation_data, dict):
                    test_entry['Sun radiation [W/m2]'] = \
                        radiation_data.get(f'Summer {summer_zone}', 'N/A')

                # Wind speed logic
                wind_type = test_entry.get('Wind speed', '').lower()
                if 'max' in wind_type:
                    test_entry['Wind speed [km/h]'] = max_speed
                elif 'min' in wind_type:
                    test_entry['Wind speed [km/h]'] = '0-15'

                # Setpoint delta value
                delta_type = test_entry.get('Setpoint delta', '').lower() if test_entry.get('Setpoint delta') else ''
                if delta_type == 'normal':
                    delta_val = 0
                elif delta_type == 'max':
                    delta_val = get_custom_or_default(interior_data.get('TicMaxSaloon'))
                elif delta_type == 'min':
                    delta_val = get_custom_or_default(interior_data.get('TicMinSaloon'))
                else:
                    delta_val = 0
                test_entry['Setpoint delta value [K]'] = delta_val

                # Try to convert delta_val to float, ensuring it handles any invalid cases
                try:
                    delta_val = float(str(delta_val).replace('°C', '').strip())
                except:
                    delta_val = 0.0


                # Setpoint curve + final Setpoint [ºC]
                if max_mean_temp_saloon not in [None, 'N/A', '']:
                    try:
                        # Debug: Check the value of max_mean_temp_saloon before conversion

                        ext_temp_float = float(max_mean_temp_saloon)
                        # Debug: Show the converted float value

                        base_curve_val = self.calculate_curve(ext_temp_float, curve_data)
                        # Debug: Check the result of the saloon curve function
                        print(f"Base curve value from saloon_curve function: {base_curve_val}")

                        if base_curve_val is not None:
                            test_entry['Setpoint curve [ºC]'] = round(base_curve_val, 2)
                            test_entry['Setpoint [ºC]'] = round(base_curve_val + delta_val, 2)
                            # Debug: Output the calculated setpoint and setpoint curve
                            
                        else:
                            test_entry['Setpoint curve [ºC]'] = 'N/A'
                            test_entry['Setpoint [ºC]'] = 'N/A'
                            # Debug: Indicate that the base curve value was None
                            print("Base curve value is None, setting Setpoint values to 'N/A'")
                    except Exception as e:
                        test_entry['Setpoint curve [ºC]'] = 'N/A'
                        test_entry['Setpoint [ºC]'] = 'N/A'
                        # Debug: Output any exceptions
                        print(f"Error calculating setpoint curve and final setpoint: {e}")
                else:
                    test_entry['Setpoint curve [ºC]'] = 'N/A'
                    test_entry['Setpoint [ºC]'] = 'N/A'
                    # Debug: If max_mean_temp_saloon is invalid, output a message
                    print("Max mean temperature saloon is invalid or missing, setting Setpoint values to 'N/A'")

            return data

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
