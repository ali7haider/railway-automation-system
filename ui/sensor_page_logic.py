from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QTableWidget, QHeaderView
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math
from PyQt5 import QtWidgets

class SensorPageManager:
    def __init__(self, parent):
        self.parent = parent
        self.coach_widgets = []
        self.current_coach_index = 0  # Initialize current_coach_index
        self.project_data = {}  # Initialize project_data  
        self.coach_table_data = {}  # Initialize coach_table_data  
    
     # Initialize an array to store all tables
        self.sensor_tables = {
            "tableAT": None,   # Air temperature sensor
            "tableRH": None,   # Relative humidity sensor
            "tableAS": None,   # Air speed sensor
            "tableST": None,   # Surface temperature sensor
            "tableCO2": None,  # CO2 sensor
            "tableDP": None,   # Differential pressure sensor
            "tableP": None,    # Power sensor
            "tableOTH": None,  # Other sensor
            "tableVAR": None   # Variables
        }
        self.load_tables()
        # Connect buttons to add rows
        self.connect_buttons()
    
    def connect_buttons(self):
        """Connect buttons to add rows to their respective tables."""
        button_names = [
            "btnAT", "btnRH", "btnAS", "btnST", 
            "btnCO2", "btnDP", "btnP", "btnOTH", "btnVAR"
        ]
        table_names = list(self.sensor_tables.keys())

        for btn_name, table_name in zip(button_names, table_names):
            button = self.parent.findChild(QtWidgets.QPushButton, btn_name)
            if button:
                button.clicked.connect(lambda _, t=table_name: self.add_sensor_row(t))
    
    def add_sensor_row(self, table_name):
        """Add a new sensor row to the specified table."""
        try:
            table_widget = self.sensor_tables[table_name]
            if not table_widget:
                print(f"Table {table_name} not found.")
                return
            
            # Calculate the new sensor ID
            row_count = table_widget.rowCount()
            sensor_id = f"{table_name[5:]}_{row_count + 1}"  # Extract short form (e.g., AT from tableAT)

            # Add a new row
            row_count=row_count
            table_widget.insertRow(row_count)

            # Sensor Name (ID)
            sensor_id_item = QtWidgets.QTableWidgetItem(sensor_id)
            table_widget.setItem(row_count, 0, sensor_id_item)

            # Zone (ComboBox)
            zone_combo = QtWidgets.QComboBox()
            zone_combo.addItems(["Zone 1", "Zone 2", "Zone 3", "Zone 4"])  # Example zones
            table_widget.setCellWidget(row_count, 1, zone_combo)

            # Sensor Type (constant based on table)
            sensor_type = self.get_sensor_type(table_name)
            type_item = QtWidgets.QTableWidgetItem(sensor_type)
            type_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            table_widget.setItem(row_count, 2, type_item)

            # Valuation 1 (ComboBox)
            valuation_combo = QtWidgets.QComboBox()
            valuation_combo.addItems(["Value 1", "Value 2", "Value 3"])  # Example values
            table_widget.setCellWidget(row_count, 3, valuation_combo)

            # Position (ComboBox)
            position_combo = QtWidgets.QComboBox()
            position_combo.addItems(["Front", "Middle", "Back"])  # Example positions
            table_widget.setCellWidget(row_count, 4, position_combo)

            # Seat (LineEdit)
            seat_input = QtWidgets.QLineEdit()
            table_widget.setCellWidget(row_count, 5, seat_input)

            # Height (LineEdit)
            height_input = QtWidgets.QLineEdit()
            table_widget.setCellWidget(row_count, 6, height_input)

            # Description (LineEdit)
            description_input = QtWidgets.QLineEdit()
            table_widget.setCellWidget(row_count, 7, description_input)

            # Save to dictionary
            self.save_sensor_data(table_name, sensor_id, sensor_type, zone_combo.currentText(), 
                                  valuation_combo.currentText(), position_combo.currentText(), 
                                  seat_input.text(), height_input.text(), description_input.text())
            
            print(f"Added row {sensor_id} to {table_name}.")

        except Exception as e:
            print(f"Error adding row to {table_name}: {str(e)}")
    def get_sensor_type(self, table_name):
        """Return the sensor type based on the table name."""
        sensor_types = {
            "tableAT": "Air Temperature Sensor",
            "tableRH": "Relative Humidity Sensor",
            "tableAS": "Air Speed Sensor",
            "tableST": "Surface Temperature Sensor",
            "tableCO2": "CO2 Sensor",
            "tableDP": "Differential Pressure Sensor",
            "tableP": "Power Sensor",
            "tableOTH": "Other Sensor",
            "tableVAR": "Variable Sensor"
        }
        return sensor_types.get(table_name, "Unknown Sensor")
    def save_sensor_data(self, table_name, sensor_id, sensor_type, zone, valuation, position, seat, height, description):
        """Save sensor data to the project data dictionary for the current coach."""
        if self.current_coach_index not in self.project_data:
            self.project_data[self.current_coach_index] = {}

        if table_name not in self.project_data[self.current_coach_index]:
            self.project_data[self.current_coach_index][table_name] = []

        # Prepare the sensor data dictionary
        sensor_data = {
            "Sensor Name": sensor_id,
            "Type": sensor_type,
            "Zone": zone,
            "Valuation 1": valuation,
            "Position": position,
            "Seat": seat,
            "Height": height,
            "Description": description
        }

        # Append the sensor data to the table's list
        self.project_data[self.current_coach_index][table_name].append(sensor_data)
        print(f"Saved data for {sensor_id} in {table_name}: {sensor_data}")
    def load_tables(self):
        # Define the same headers for all tables
        headers = ["Sensor Name", "Zone", "Type", "Valuation 1", 
                "Position", "Seat", "Height", "Description"]
        
        # Set uniform row height and maximum header height
        row_height = 30
        header_max_height = 35

        for table_name in self.sensor_tables.keys():
            table_widget = self.parent.findChild(QtWidgets.QTableWidget, table_name)
            
            if table_widget:
                self.sensor_tables[table_name] = table_widget  # Store the table widget

                # Set the table to have 8 columns
                table_widget.setColumnCount(8)
                table_widget.setRowCount(0)
                table_widget.setHorizontalHeaderLabels(headers)

                # Make the headers stretch to fill the width
                header = table_widget.horizontalHeader()
                header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                header.setMaximumHeight(header_max_height)

                # Set the uniform row height for all rows
                table_widget.verticalHeader().setDefaultSectionSize(row_height)

    
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
    def save_current_coach_tables(self):
        """Save the current coach's table data to the dictionary."""
        coach_data = {}
        
        for table_name, table_widget in self.sensor_tables.items():
            if table_widget:
                table_data = []
                row_count = table_widget.rowCount()  # Exclude last 5 rows

                for row in range(row_count):
                    row_data = []
                    for col in range(table_widget.columnCount()):
                        item = table_widget.cellWidget(row, col)
                        
                        if isinstance(item, QtWidgets.QComboBox):  # If the item is a ComboBox
                            row_data.append(item.currentText())
                        elif isinstance(item, QtWidgets.QLineEdit):  # If the item is a LineEdit (for text entries)
                            row_data.append(item.text())
                        else:
                            table_item = table_widget.item(row, col)
                            row_data.append(table_item.text() if table_item else "")
                            
                    table_data.append(row_data)
                
                coach_data[table_name] = table_data
        
        # Save the data for the current coach index
        self.coach_table_data[self.current_coach_index] = coach_data
        print(self.coach_table_data)


    def load_coach_tables(self):
        """Load table data for the current coach index, if available."""
        for table_name, table_widget in self.sensor_tables.items():
                table_widget.setRowCount(0)
        if self.current_coach_index in self.coach_table_data:
            coach_data = self.coach_table_data[self.current_coach_index]
            
            for table_name, table_widget in self.sensor_tables.items():
                if table_widget and table_name in coach_data:
                    table_data = coach_data[table_name]

                    # Clear all rows before loading
                    table_widget.setRowCount(0)
                    
                    for row_data in table_data:
                        row_index = table_widget.rowCount()
                        table_widget.insertRow(row_index)
                        
                        for col_index, cell_text in enumerate(row_data):
                            if col_index in [1, 3, 4]:  # ComboBoxes for Zone, Valuation 1, Position
                                combo_box = QtWidgets.QComboBox()
                                if col_index == 1:  # Zone ComboBox
                                    combo_box.addItems(["Zone A", "Zone B", "Zone C"])
                                elif col_index == 3:  # Valuation 1 ComboBox
                                    combo_box.addItems(["Value 1", "Value 2", "Value 3"])
                                elif col_index == 4:  # Position ComboBox
                                    combo_box.addItems(["Front", "Middle", "Back"])
                                combo_box.setCurrentText(cell_text)
                                table_widget.setCellWidget(row_index, col_index, combo_box)
                            
                            elif col_index in [5, 6, 7]:  # Text Entries for Seat, Height, Description
                                line_edit = QtWidgets.QLineEdit()
                                line_edit.setText(cell_text)
                                table_widget.setCellWidget(row_index, col_index, line_edit)
                            
                            else:
                                item = QtWidgets.QTableWidgetItem(cell_text)
                                if col_index == 0:  # Make Sensor Name yellow
                                    item.setForeground(QtGui.QColor("yellow"))
                                table_widget.setItem(row_index, col_index, item)


    def on_coach_button_click(self, index):
        """Handles clicking on a coach button and updates the UI."""
        try:  
            # Save the current coach's table data before switching
            self.save_current_coach_tables()

            # Update the current coach index
            self.current_coach_index = index

            # Load the data for the newly selected coach
            self.load_coach_tables()

            # Update the coach name label
            coaches = self.project_data.get("Coaches", {})
            coach_name = coaches.get(f"Coach {index + 1}", f"Coach {index + 1}")
            self.parent.lblCoachName_3.setText(f"Coach {index + 1} - {coach_name}")
            
            print(f"Switched to Coach {index + 1} and loaded its data.")
        except Exception as e:
            print(f"An error occurred while handling the coach button click: {e}")