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
            row_count=row_count-5
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
                table_widget.setRowCount(5)
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
