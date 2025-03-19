import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QMainWindow,
    QStackedWidget,
    QComboBox,
    QLineEdit,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QMainWindow
import os
import sys
import os
from PyQt5 import uic
from PyQt5 import QtWidgets, uic
from modules.criteria_manager import CriteriaManager
from modules.project_manager import ProjectManager  # Import ProjectManager
from PyQt5.QtGui import QIntValidator, QMouseEvent

from ui.coach_page_logic import CoachPageManager
from ui.custom_exterior_cabin_logic import CustomExteriorConditionsCabinScreen
from ui.custom_exterior_saloon_logic import CustomExteriorConditionsSaloonScreen
from ui.custom_interior_conditions_logic import CustomInteriorConditionsScreen
import re  # For regex-based extraction
from modules.saving_project_manager import SavingProjectManager  # Add this line


GLOBAL_STATE = False
class MasterScreen(QtWidgets.QMainWindow):
    def __init__(self,user_data=None):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/main.ui", self)  # Load UI file dynamically
            from modules.ui_functions import UIFunctions
            self.ui=self
            self.set_buttons_cursor()
            # Store user details
            # Default user details if no user is provided
            # Ensure user_data is a dictionary, otherwise set default user
            if not isinstance(user_data, dict):
                user_data = {"id": 0, "username": "guest", "name": "Guest User"}

            # Store user details safely
            self.user_id = user_data.get("id", 0)
            self.username = user_data.get("username", "guest")
            self.name = user_data.get("name", "Guest User")

            # Display user details in the UI
            self.lblNameUser.setText(f"Welcome, {self.name} ({self.username})!")
                

            self.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
            UIFunctions.uiDefinitions(self)

            self.btnProjects.setStyleSheet(UIFunctions.selectMenu(self.btnProjects.styleSheet()))
            self.locked_custom_fields = set()


            self.saving_manager = SavingProjectManager()
            self.ProjectName="Test"

            self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
        #     # Initialize individual pages
            self.init_pages()
            self.original_default_interior_values={}
            self.original_default_exterior_values={}

            self.menu_buttons = [
            self.btnProjects,  # Replace with your actual button objects
            self.btnCriteria,
            self.btnTestList,
            self.btnCoach,
            self.btnReport,
            self.btnProjects,
            self.btnSensorList,
            self.btnPlanning,
            self.btnReportCampaign
        ]

            # Assign menu button clicks
            self.btnProjects.clicked.connect(self.show_project_page)
            self.btnCriteria.clicked.connect(self.show_criteria_page)
            self.btnCoach.clicked.connect(self.show_coach_page)
            self.btnReport.clicked.connect(self.show_multi_tool_menu)
            self.btnSensorList.clicked.connect(self.show_pairip_pass_menu)
            self.btnPlanning.clicked.connect(self.show_offset_leech_menu)

            self.btnSave.clicked.connect(self.on_save_button_clicked)

            self.coach_page_manager = CoachPageManager(self)


            # Define combo box - JSON file mapping
            self.cmbxOperationCountryProject = self.findChild(QComboBox, "cmbxOperationCountryProject")
            self.cmbxTypeOfTrainProject = self.findChild(QComboBox, "cmbxTypeOfTrainProject")

            combo_mapping = {
                self.cmbxOperationCountryProject: "data/Countries_zones.json",
                self.cmbxTypeOfTrainProject: "data/TrainType_standars.json",
            }

            # Load JSON data into combo boxes
            ProjectManager.load_multiple_json(combo_mapping)

             # **📌 Add Input Validations**
            self.txtMaximumSpeedProject = self.findChild(QLineEdit, "txtMaximumSpeedProject")
            self.txtMaximumSpeedProject.setValidator(QIntValidator(0, 400, self))
            self.txtMaximumSpeedProject.setMaxLength(3)  # Max 3 digits (e.g., 0-400)
            self.txtMaximumSpeedProject.textChanged.connect(lambda: self.restrict_range(self.txtMaximumSpeedProject, 0, 400))
            self.txtNCoachesPerTrainProject = self.findChild(QLineEdit, "txtNCoachesPerTrainProject")

            # Set validators (Only integers within range)
            self.txtNCoachesPerTrainProject.setValidator(QIntValidator(0, 12, self))
            # **Strictly Limit Input Length**
            self.txtNCoachesPerTrainProject.setMaxLength(2)  # Max 2 digits (e.g., 0-12)

            # **Real-Time Filtering**
            self.txtNCoachesPerTrainProject.textChanged.connect(lambda: self.restrict_range(self.txtNCoachesPerTrainProject, 0, 12))

            # Find UI Elements
            self.frameCoaches = self.findChild(QFrame, "frameCoaches")

            if not self.frameCoaches:
                raise Exception("frameCoaches not found in UI!")  # Debugging issue

            # Set layout for the frame if not already set
            if not self.frameCoaches.layout():
                self.layoutCoaches = QVBoxLayout(self.frameCoaches)
                self.layoutCoaches.setContentsMargins(0, 0, 0, 0)  # Remove all margins

                self.layoutCoaches.setAlignment(Qt.AlignmentFlag.AlignTop)
            else:
                self.layoutCoaches = self.frameCoaches.layout()

            # Store dynamically created widgets
            self.coach_widgets = []

            # **Set Input Validators**
            self.txtNCoachesPerTrainProject.setValidator(QIntValidator(0, 12, self))
            self.txtNCoachesPerTrainProject.setMaxLength(2)  # Max 2 digits (0-12)

            # **Connect Event**
            self.txtNCoachesPerTrainProject.textChanged.connect(self.update_coach_inputs)


            self.cmbxTypeOfTrainProject = self.findChild(QComboBox, "cmbxTypeOfTrainProject")
            self.lblStandardSaloon = self.findChild(QLabel, "lblStandardSaloon")
            self.cmbxStandardSaloon = self.findChild(QComboBox, "cmbxStandardSaloon")
            self.lblStandardCabin = self.findChild(QLabel, "lblStandardCabin")
            self.cmbxStandardCabin = self.findChild(QComboBox, "cmbxStandardCabin")
            self.btnCriteria.clicked.connect(self.update_criteria_standard_fields)
            # Initially hide them
            self.lblStandardSaloon.hide()
            self.cmbxStandardSaloon.hide()
            self.lblStandardCabin.hide()
            self.cmbxStandardCabin.hide()

            # Connect combo box change event
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_standard_fields)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_max_mean_interior_temp)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_max_mean_interior_temp)

            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_standby_operator_temp)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_standby_operator_temp)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_standby_operator_temp)

            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_temperature_conditions)


            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxSigleDeckDoubleDeck.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_k_coefficient)

            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxCompartmentProject.currentTextChanged.connect(self.update_tic_coefficients)

            
            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_max_mean_interior_temp)
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_max_mean_interior_temp)

            self.btnCustomInteriorConditions.clicked.connect(self.open_custom_interior_conditions)
            self.btnCustomExteriorSaloon.clicked.connect(self.open_custom_exterior_conditions_saloon)
            self.btnCustomExteriorCabin.clicked.connect(self.open_custom_exterior_conditions_cabin)





        except Exception as e:
            self.show_message_box("Error", f"Error loading UI: {str(e)}")
    
    def on_save_button_clicked(self):
        """Triggered when btnSave is clicked. Collects all project details and passes them for saving."""
        try:
            # Check if Project Name is provided
            project_name = self.txtNameProject.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Missing Information", "Please enter the Project Name before saving.")
                return

            # Create the base structure for project information
            self.ProjectName=project_name
            project_data = {
                "Project_info": {
                    "Project Name": project_name,
                    "Coach Builder": self.txtCoachBuilderProject.text(),
                    "Customer/Operator": self.txtCustomerOperatorProject.text(),
                    "Operation Country": self.cmbxOperationCountryProject.currentText(),
                    "Type of Train": self.cmbxTypeOfTrainProject.currentText(),
                    "Number of Coaches per Train": self.txtNCoachesPerTrainProject.text(),
                    "Type of Compartment": self.cmbxCompartmentProject.currentText(),
                    "Type of HVAC": self.cmbxTypesOfHVACProject.currentText(),
                    "Maximum Speed": self.txtMaximumSpeedProject.text(),
                    "Single/Double Deck": self.cmbxSigleDeckDoubleDeck.currentText(),
                    "Standard Saloon": self.lblStandardSaloon.text() if self.lblStandardSaloon.isVisible() else self.cmbxStandardSaloon.currentText(),
                    "Category Saloon": self.lblCategorySaloon.text(),
                    "Standard Cabin": self.lblStandardCabin.text() if self.lblStandardCabin.isVisible() else self.cmbxStandardCabin.currentText(),
                    "Category Cabin": self.lblCategoryCabin.text(),
                    "Heat Transfer Saloon": self.lblHeatTransferSaloon.text(),
                    "Heat Transfer Cabin": self.lblHeatTransferCabin.text(),
                    "Cabin 1 Name": self.txtCabin1NameProject.text(),
                    "Cabin 2 Name": self.txtCabin2NameProject.text(),
                    "Coaches": {}
                }
            }

            # Collect dynamically generated coach names
            for index, widget in enumerate(self.coach_widgets):
                coach_name = widget["input"].text().strip()
                if coach_name:
                    project_data["Project_info"]["Coaches"][f"Coach {index + 1}"] = coach_name

            # Save using SavingProjectManager
            self.saving_manager.save_project(project_data)
            QMessageBox.information(self, "Success", f"Project '{project_name}' saved successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the project: {str(e)}")

    def open_custom_exterior_conditions_cabin(self):
        """Opens the Custom Exterior Conditions screen for the Cabin with properly formatted default values."""
        try:
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )

            # Validation: Ensure both Standard Saloon & Standard Cabin are selected
            if not standard_cabin:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Selection Required", 
                    "Please select both Standard Saloon and Standard Cabin before proceeding."
                )
                return  # Stop function execution

            if not hasattr(self, 'original_default_exterior_values'):
                self.original_default_exterior_values = {
                    "standard_saloon": standard_saloon,
                }
            else:
                # Update only the relevant parts
                self.original_default_exterior_values.update({
                    "standard_saloon": standard_saloon,

                })
            # Initialize custom values storage if not already defined
            if not hasattr(self, "cabin_custom_values"):
                self.cabin_custom_values = {}

            # Open the Custom Exterior Conditions screen with custom values
            transformed_values = self.transform_default_cabin_values(self.original_default_exterior_values)
 
            # Open Custom Exterior Conditions screen with formatted values
            self.custom_exterior_window = CustomExteriorConditionsCabinScreen(  
                default_values=transformed_values,
                custom_values=self.cabin_custom_values)
            if hasattr(self.custom_exterior_window, "custom_values_updated"):
                self.custom_exterior_window.custom_values_updated.connect(self.apply_custom_values_cabin)
            else:
                print("custom_values_updated signal not found!")
            self.custom_exterior_window.show()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error opening Custom Exterior Conditions screen: {str(e)}")


    def open_custom_exterior_conditions_saloon(self):
        """Opens the Custom Exterior Conditions screen with properly formatted custom values."""
        try:
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )

            # Validation: Ensure both Standard Saloon & Standard Cabin are selected
            if not standard_saloon or not standard_cabin:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Selection Required", 
                    "Please select both Standard Saloon and Standard Cabin before proceeding."
                )
                return  # Stop function execution
            if not hasattr(self, 'original_default_exterior_values'):
                self.original_default_exterior_values = {
                    "standard": standard_saloon,
                }
            else:
                # Update only the relevant parts
                self.original_default_exterior_values.update({
                    "standard_saloon": standard_saloon,

                })
            # Initialize custom values
            # Initialize custom values storage if not already defined
            if not hasattr(self, "saloon_custom_values"):
                self.saloon_custom_values = {}

            # Open the Custom Exterior Conditions screen with custom values
            transformed_values = self.transform_default_values(self.original_default_exterior_values)
            self.custom_exterior_window = CustomExteriorConditionsSaloonScreen(                
                default_values=transformed_values,
                custom_values=self.saloon_custom_values)

            if hasattr(self.custom_exterior_window, "custom_values_updated"):
                self.custom_exterior_window.custom_values_updated.connect(self.apply_custom_values_saloon)
            else:
                print("custom_values_updated signal not found!")

            self.custom_exterior_window.show()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error opening Custom Exterior Conditions screen: {str(e)}")

    def transform_default_cabin_values(self, original_values: dict) -> dict:
        """Transform original_default_exterior_values to the new key format for Cabin, ensuring all values are strings."""
        transformed_values = {}

        # Map Standard Labels
        transformed_values["standard"] = str(original_values.get("standard_cabin", "None"))

        # Map Zone Values
        transformed_values["WinterZone"] = str(original_values.get("WinterZoneCabin", "None"))
        transformed_values["SummerZone"] = str(original_values.get("SummerZoneCabin", "None"))

        # Map Normal Range
        transformed_values["WinterNormal"] = str(original_values.get("WinterNormalCabin", "None"))
        transformed_values["SummerNormal"] = str(original_values.get("SummerNormalCabin", "None"))

        # Map Extended Range (Split into Min and Max)
        winter_extended = original_values.get("WinterExtendedCabin", "None - None").split(" - ")
        transformed_values["WinterExtendedMin"] = str(winter_extended[0])
        transformed_values["WinterExtendedMax"] = str(winter_extended[1])

        summer_extended = original_values.get("SummerExtendedCabin", "None - None").split(" - ")
        transformed_values["SummerExtendedMin"] = str(summer_extended[0])
        transformed_values["SummerExtendedMax"] = str(summer_extended[1])

        # Helper function to extract temperature, humidity, and heat flux
        def extract_components(value):
            if value and value != "None°C, None%, None W/m2":
                try:
                    temp, humidity, heat_flux = value.split(", ")
                    return str(temp.replace("°C", "")), str(humidity.replace("%", "")), str(heat_flux.replace(" W/m2", ""))
                except ValueError:
                    return "None", "None", "None"
            return "None", "None", "None"

        # Map Design Values
        design_winter = extract_components(original_values.get("WinterDesignCabin", "None°C, None%, None W/m2"))
        transformed_values["WinterDesignTemp"], transformed_values["WinterDesignHumidity"], transformed_values["WinterDesignHeatFlux"] = design_winter

        design_summer = extract_components(original_values.get("SummerDesignCabin", "None°C, None%, None W/m2"))
        transformed_values["SummerDesignTemp"], transformed_values["SummerDesignHumidity"], transformed_values["SummerDesignHeatFlux"] = design_summer

        # Map Extreme Values
        extreme_winter = extract_components(original_values.get("WinterExtremeCabin", "None°C, None%, None W/m2"))
        transformed_values["WinterExtremeTemp"], transformed_values["WinterExtremeHumidity"], transformed_values["WinterExtremeHeatFlux"] = extreme_winter

        extreme_summer = extract_components(original_values.get("SummerExtremeCabin", "None°C, None%, None W/m2"))
        transformed_values["SummerExtremeTemp"], transformed_values["SummerExtremeHumidity"], transformed_values["SummerExtremeHeatFlux"] = extreme_summer

        # Map Operational Values
        operational_winter = extract_components(original_values.get("WinterOperationalCabin", "None°C, None%, None W/m2"))
        transformed_values["WinterOperationalTemp"], transformed_values["WinterOperationalHumidity"], transformed_values["WinterOperationalHeatFlux"] = operational_winter

        operational_summer = extract_components(original_values.get("SummerOperationalCabin", "None°C, None%, None W/m2"))
        transformed_values["SummerOperationalTemp"], transformed_values["SummerOperationalHumidity"], transformed_values["SummerOperationalHeatFlux"] = operational_summer

        return transformed_values

    def transform_default_values(self,original_values: dict) -> dict:
        """Transform original_default_exterior_values to the new key format, ensuring all values are strings."""
        transformed_values = {}

        # Map Standard Labels
        transformed_values["standard"] = str(original_values.get("standard_saloon", "None"))

        # Map Zone Values
        transformed_values["WinterZone"] = str(original_values.get("WinterZoneSaloon", "None"))
        transformed_values["SummerZone"] = str(original_values.get("SummerZoneSaloon", "None"))

        # Map Normal Range
        transformed_values["WinterNormal"] = str(original_values.get("WinterNormalSaloon", "None"))
        transformed_values["SummerNormal"] = str(original_values.get("SummerNormalSaloon", "None"))

        # Map Extended Range (Split into Min and Max)
        winter_extended = original_values.get("WinterExtendedSaloon", "None - None").split(" - ")
        transformed_values["WinterExtendedMin"] = str(winter_extended[0])
        transformed_values["WinterExtendedMax"] = str(winter_extended[1])

        summer_extended = original_values.get("SummerExtendedSaloon", "None - None").split(" - ")
        transformed_values["SummerExtendedMin"] = str(summer_extended[0])
        transformed_values["SummerExtendedMax"] = str(summer_extended[1])

        # Helper function to extract temperature, humidity, and heat flux
        def extract_components(value):
            if value and value != "None°C, None%, None W/m2":
                try:
                    temp, humidity, heat_flux = value.split(", ")
                    return str(temp.replace("°C", "")), str(humidity.replace("%", "")), str(heat_flux.replace(" W/m2", ""))
                except ValueError:
                    return "None", "None", "None"
            return "None", "None", "None"

        # Map Design Values
        design_winter = extract_components(original_values.get("WinterDesignSaloon", "None�C, None%, None W/m2"))
        transformed_values["WinterDesignTemp"], transformed_values["WinterDesignHumidity"], transformed_values["WinterDesignHeatFlux"] = design_winter

        design_summer = extract_components(original_values.get("SummerDesignSaloon", "None�C, None%, None W/m2"))
        transformed_values["SummerDesignTemp"], transformed_values["SummerDesignHumidity"], transformed_values["SummerDesignHeatFlux"] = design_summer

        # Map Extreme Values
        extreme_winter = extract_components(original_values.get("WinterExtremeSaloon", "None�C, None%, None W/m2"))
        transformed_values["WinterExtremeTemp"], transformed_values["WinterExtremeHumidity"], transformed_values["WinterExtremeHeatFlux"] = extreme_winter

        extreme_summer = extract_components(original_values.get("SummerExtremeSaloon", "None�C, None%, None W/m2"))
        transformed_values["SummerExtremeTemp"], transformed_values["SummerExtremeHumidity"], transformed_values["SummerExtremeHeatFlux"] = extreme_summer

        # Map Operational Values
        operational_winter = extract_components(original_values.get("WinterOperationalSaloon", "None�C, None%, None W/m2"))
        transformed_values["WinterOperationalTemp"], transformed_values["WinterOperationalHumidity"], transformed_values["WinterOperationalHeatFlux"] = operational_winter

        operational_summer = extract_components(original_values.get("SummerOperationalSaloon", "None�C, None%, None W/m2"))
        transformed_values["SummerOperationalTemp"], transformed_values["SummerOperationalHumidity"], transformed_values["SummerOperationalHeatFlux"] = operational_summer

        return transformed_values


    # Helper function to extract temperature from "Normal" climate conditions
    def extract_normal_temperature(self, text):
        """
        Extracts the numeric temperature value from a string in the format: 
        'Text ≥ 25°C' and ensures it captures negative values as well.
        """
        try:
            match = re.search(r"≥\s*(-?\d+\.?\d*)°C", text)  # Capture positive or negative temperature
            if match:
                return f"{match.group(1)}°C"
            return "None"
        except:
            return "None"

    # Helper function to extract extended min/max values
    def extract_extended_range(self, text):
        """Extracts min and max values from extended climate conditions."""
        try:
            match = re.search(r"(-?\d+\.?\d*)°C\s*≤.*≤\s*(-?\d+\.?\d*)°C", text)  # Handles negative values too
            if match:
                min_val, max_val = match.groups()
                return f"{min_val}°C", f"{max_val}°C"
            else:
                return "None", "None"
        except:
            return "None", "None"

    # Helper function to extract Design/Extreme/Operational values
    def extract_climate_parameters(self, text):
        """Extracts temperature (°C), humidity (%), and heat flux (W/m²) from a string."""
        try:
            values = re.findall(r"(-?\d+\.?\d*)\s*(°C|%|W/m²)", text)  # Capture negative values
            temp, humidity, heat_flux = "None", "None", "None"

            for val, unit in values:
                if unit == "°C":
                    temp = f"{val}°C"
                elif unit == "%":
                    humidity = f"{val}%"
                elif unit == "W/m²":
                    heat_flux = f"{val} W/m²"

            return temp, humidity, heat_flux
        except:
            return "None", "None", "None"



    def apply_custom_values(self, custom_values):
        """
        Updates labels with custom values and highlights them if changed.
        Locks fields with custom values to prevent further updates.
        Stores custom values in a separate dictionary for saving.
        :param custom_values: Dictionary containing custom values.
        """
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields"):
                self.locked_custom_fields = set()
            
            # Initialize storage for custom values if not already defined
            if not hasattr(self, "custom_values_interior"):
                self.custom_values_interior = {}
            
            # Initialize storage for curves if not already defined
            if not hasattr(self, "custom_saloon_curve"):
                self.custom_saloon_curve = {}
            
            if not hasattr(self, "custom_cabin_curve"):
                self.custom_cabin_curve = {}

            # Define label mappings
            label_mappings = {
                "TicMaxSaloon": self.lblMaxSaloonInterior,
                "TicMinSaloon": self.lblMinSaloonInterior,
                "TicMaxCabin": self.lblTicMaxCabinInterior,
                "TicMinCabin": self.lblTicMinSaloonInterior,
                "MaxMeanTempSaloon": self.lblMaxMeanInteriorTempSaloon,
                "MaxMeanTempCabin": self.lblMaxMeanInteriorTempCabin,
                "StandByOperatorSaloonMax": self.lblStandByOperatorSaloonMax,
                "StandByOperatorSaloonMin": self.lblStandByOperatorSaloonMin,
                "StandByOperatorCabinMax": self.lblStandByOperatorCabinMax,
                "StandByOperatorCabinMin": self.lblStandByOperatorCabinMin,
                "RegulationCurveSaloon": self.lblRegulationCurveSaloon,
                "RegulationCurveCabin": self.lblRegulationCurveCabin
            }

            # Loop through each label and update values
            for key, label in label_mappings.items():
                custom_value = custom_values.get(key, "").strip()

                if custom_value:  # If a custom value exists
                    # Skip adding "°C" for regulation curves
                    if key in ["RegulationCurveSaloon", "RegulationCurveCabin"]:
                        label.setText(custom_value)
                    else:
                        label.setText(f"{custom_value}°C")
                    
                    label.setStyleSheet("background-color: #F97D02; padding-left:5px;")  # Highlight in orange
                    self.locked_custom_fields.add(key)  # Lock this field
                    self.custom_values_interior[key] = custom_value  # Store custom value separately

            # Load Saloon & Cabin Curves
            self.custom_saloon_curve = custom_values.get("saloon_curve", {})
            self.custom_cabin_curve = custom_values.get("cabin_curve", {})

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error applying custom values: {str(e)}")

    def apply_custom_values_saloon(self, custom_values):
        """
        Updates saloon labels with custom values and highlights them if changed.
        Locks fields with custom values to prevent further updates.
        Stores custom values in a separate dictionary for saving.
        :param custom_values: Dictionary containing custom values.
        """
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields"):
                self.locked_custom_fields = set()
            
            # Initialize custom values storage if not already defined
            if not hasattr(self, "saloon_custom_values"):
                self.saloon_custom_values = {}

            # Define label mappings for Zone values (Direct Text)
            label_mappings = {
                "CustomWinterZone": self.lblWinterZoneSaloon,
                "CustomSummerZone": self.lblSummerZoneSaloon,
            }

            # Directly set Zone values
            for key, label in label_mappings.items():
                custom_value = custom_values.get(key, "").strip()

                if custom_value:
                    text = f"{custom_value}"
                    label.setText(text)
                    label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                    self.locked_custom_fields.add(key)
                    self.saloon_custom_values[key] = custom_value  # Store custom value

            # Process Normal Values (Winter & Summer)
            normal_mappings = {
                "CustomWinterNormalMin": self.lblWinterNormalSaloon,
                "CustomSummerNormalMax": self.lblSummerNormalSaloon,
            }

            for key, label in normal_mappings.items():
                custom_value = custom_values.get(key, "").strip()

                if custom_value:
                    if "Min" in key:
                        self.set_label_textNormalWinter(label, custom_value)
                    elif "Max" in key:
                        self.set_label_textNormalSummer(label, custom_value)
                    label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                    self.locked_custom_fields.add(key)
                    self.saloon_custom_values[key] = custom_value  # Store custom value

            # Process Extended Values (Winter & Summer)
            for season in ["Winter", "Summer"]:
                min_key = f"Custom{season}ExtendedMin"
                max_key = f"Custom{season}ExtendedMax"
                label_attr = f"lbl{season}ExtendedSaloon"

                if hasattr(self, label_attr):  # Check if label exists
                    label = getattr(self, label_attr)

                    min_val = custom_values.get(min_key, "").strip()
                    max_val = custom_values.get(max_key, "").strip()

                    if min_val or max_val:  # If either value is set, update both
                        self.set_label_text_range(label, min_val if min_val else None, max_val if max_val else None)
                        label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                        self.locked_custom_fields.update({min_key, max_key})
                        self.saloon_custom_values[min_key] = min_val  # Store custom value
                        self.saloon_custom_values[max_key] = max_val  # Store custom value

            # Process Design, Extreme, and Operational values
            for condition in ["Design", "Extreme", "Operational"]:
                for season in ["Winter", "Summer"]:
                    temp_key = f"Custom{season}{condition}Temp"
                    hum_key = f"Custom{season}{condition}Humi"
                    flux_key = f"Custom{season}{condition}Solar"
                    label_attr = f"lbl{season}{condition}Saloon"

                    if hasattr(self, label_attr):  # Check if label exists
                        label = getattr(self, label_attr)

                        temp = custom_values.get(temp_key, "").strip() or "None"
                        hum = custom_values.get(hum_key, "").strip() or "None"
                        flux = custom_values.get(flux_key, "").strip() or "None"

                        if temp != "None" or hum != "None" or flux != "None":  # If any value is set, mark all as custom
                            text = f"{temp}°C, {hum}%, {flux} W/m²"
                            label.setText(text)
                            label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                            self.locked_custom_fields.update({temp_key, hum_key, flux_key})
                            
                            # Store custom values in the separate dictionary
                            self.saloon_custom_values[temp_key] = temp
                            self.saloon_custom_values[hum_key] = hum
                            self.saloon_custom_values[flux_key] = flux

        except Exception as e:
            print(f"[ERROR] Exception in apply_custom_values_saloon: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Error applying custom values: {str(e)}")
    def apply_custom_values_cabin(self, custom_values):
        """
        Updates cabin labels with custom values and highlights them if changed.
        Locks fields with custom values to prevent further updates.
        Stores custom values in a separate dictionary for saving.
        :param custom_values: Dictionary containing custom values.
        """
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields_cabin"):
                self.locked_custom_fields_cabin = set()
            
            # Initialize custom values storage if not already defined
            if not hasattr(self, "cabin_custom_values"):
                self.cabin_custom_values = {}

            # Define label mappings for Zone values (Direct Text)
            label_mappings = {
                "CustomWinterZone": self.lblWinterZoneCabin,
                "CustomSummerZone": self.lblSummerZoneCabin,
            }

            # Directly set Zone values
            for key, label in label_mappings.items():
                custom_value = custom_values.get(key, "").strip()

                if custom_value:
                    text = f"{custom_value}"
                    label.setText(text)
                    label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                    self.locked_custom_fields_cabin.add(key)
                    self.cabin_custom_values[key] = custom_value  # Store custom value

            # Process Normal Values (Winter & Summer)
            normal_mappings = {
                "CustomWinterNormalMin": self.lblWinterNormalCabin,
                "CustomSummerNormalMax": self.lblSummerNormalCabin,
            }

            for key, label in normal_mappings.items():
                custom_value = custom_values.get(key, "").strip()

                if custom_value:
                    if "Min" in key:
                        self.set_label_textNormalWinter(label, custom_value)
                    elif "Max" in key:
                        self.set_label_textNormalSummer(label, custom_value)
                    label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                    self.locked_custom_fields_cabin.add(key)
                    self.cabin_custom_values[key] = custom_value  # Store custom value

            # Process Extended Values (Winter & Summer)
            for season in ["Winter", "Summer"]:
                min_key = f"Custom{season}ExtendedMin"
                max_key = f"Custom{season}ExtendedMax"
                label_attr = f"lbl{season}ExtendedCabin"

                if hasattr(self, label_attr):  # Check if label exists
                    label = getattr(self, label_attr)

                    min_val = custom_values.get(min_key, "").strip()
                    max_val = custom_values.get(max_key, "").strip()

                    if min_val or max_val:  # If either value is set, update both
                        self.set_label_text_range(label, min_val if min_val else None, max_val if max_val else None)
                        label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                        self.locked_custom_fields_cabin.update({min_key, max_key})
                        
                        self.cabin_custom_values[min_key] = min_val  # Store custom value
                        self.cabin_custom_values[max_key] = max_val  # Store custom value

            # Process Design, Extreme, and Operational values
            for condition in ["Design", "Extreme", "Operational"]:
                for season in ["Winter", "Summer"]:
                    temp_key = f"Custom{season}{condition}Temp"
                    hum_key = f"Custom{season}{condition}Humi"
                    flux_key = f"Custom{season}{condition}Solar"
                    label_attr = f"lbl{season}{condition}Cabin"

                    if hasattr(self, label_attr):  # Check if label exists
                        label = getattr(self, label_attr)

                        temp = custom_values.get(temp_key, "").strip() or "None"
                        hum = custom_values.get(hum_key, "").strip() or "None"
                        flux = custom_values.get(flux_key, "").strip() or "None"

                        if temp != "None" or hum != "None" or flux != "None":  # If any value is set, mark all as custom
                            text = f"{temp}°C, {hum}%, {flux} W/m²"
                            label.setText(text)
                            label.setStyleSheet("background-color: #F97D02; padding-left:5px;")
                            self.locked_custom_fields_cabin.update({temp_key, hum_key, flux_key})
                            
                            # Store custom values in the separate dictionary
                            self.cabin_custom_values[temp_key] = temp
                            self.cabin_custom_values[hum_key] = hum
                            self.cabin_custom_values[flux_key] = flux

        except Exception as e:
            print(f"[ERROR] Exception in apply_custom_values_cabin: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Error applying custom values: {str(e)}")

    def open_custom_interior_conditions(self):
        """Opens the Custom Interior Conditions screen."""
        try:
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )
            
            if not standard_saloon or not standard_cabin:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Selection Required", 
                    "Please select both Standard Saloon and Standard Cabin before proceeding."
                )
                return  # Stop function execution

            # Fetch all values for saloon and cabin
            category_saloon = self.lblCategorySaloon.text().strip()
            category_cabin = self.lblCategoryCabin.text().strip()
            saloon_curve_values = ProjectManager.get_curve_values(standard_saloon, category_saloon)
            cabin_curve_values = ProjectManager.get_curve_values(standard_cabin, category_cabin)

            # Store the original default values only once at the start of the application
            if not hasattr(self, 'original_default_interior_values'):
                self.original_default_interior_values = {
                    "standard_saloon": standard_saloon,
                    "standard_cabin": standard_cabin,
                    "saloon_curve": saloon_curve_values,
                    "cabin_curve": cabin_curve_values
                }
            else:
                # Update only the relevant parts
                self.original_default_interior_values.update({
                    "standard_saloon": standard_saloon,
                    "standard_cabin": standard_cabin,
                    "saloon_curve": saloon_curve_values,
                    "cabin_curve": cabin_curve_values
                })
            if not hasattr(self, "custom_saloon_curve"):
                self.custom_saloon_curve = {}
            if not hasattr(self, "custom_cabin_curve"):
                self.custom_cabin_curve = {}
            

            
            # Initialize storage for custom values if not already defined
            if not hasattr(self, "custom_values_interior"):
                self.custom_values_interior = {}
            # Update only the relevant parts
            self.custom_values_interior.update({
                "saloon_curve": self.custom_saloon_curve,
                "cabin_curve": self.custom_cabin_curve,
            })
            # Open Custom Interior Conditions screen with both default and custom values
            self.custom_interior_window = CustomInteriorConditionsScreen(
                default_values=self.original_default_interior_values,
                custom_values=self.custom_values_interior
            )
            
            if hasattr(self.custom_interior_window, "custom_values_updated"):
                self.custom_interior_window.custom_values_updated.connect(self.apply_custom_values)
            else:
                print("custom_values_updated signal not found!")

            self.custom_interior_window.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error opening Custom Interior Conditions screen: {str(e)}")

    def update_standard_fields(self):
        """Updates Standard Saloon and Standard Cabin based on selected train type."""
        selected_train_type = self.cmbxTypeOfTrainProject.currentText()

        if not selected_train_type or selected_train_type == "--- Select Train Type ---":
            self.lblStandardSaloon.hide()
            self.cmbxStandardSaloon.hide()
            self.lblStandardCabin.hide()
            self.cmbxStandardCabin.hide()
            return

        try:
            standard_saloon, standard_cabin = ProjectManager.get_train_standards(selected_train_type)

            # **Update Standard Saloon**
            self.update_field(standard_saloon, self.lblStandardSaloon, self.cmbxStandardSaloon, self.lblCategorySaloon)

            # **Update Standard Cabin**
            self.update_field(standard_cabin, self.lblStandardCabin, self.cmbxStandardCabin, self.lblCategoryCabin)
            # Connect additional field updates
            
            

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load train data: {str(e)}")

    def update_standby_operator_temp(self):
        """Fetch and update Standby Operator Temperature for Saloon and Cabin with validation."""
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields"):
                self.locked_custom_fields = set()
            
            # Initialize original_default_interior_values if not already defined
            if not hasattr(self, "original_default_interior_values"):
                self.original_default_interior_values = {}
            
            # Define invalid values
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Country ---", "--- Select deck ---"}

            # Step 1: Get Standard Saloon & Standard Cabin
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )

            # Step 2: Validation: Ensure valid selections
            if standard_saloon in invalid_values or standard_cabin in invalid_values:
                if "StandByOperatorSaloonMax" not in self.locked_custom_fields:
                    self.lblStandByOperatorSaloonMax.setText("NA")
                if "StandByOperatorSaloonMin" not in self.locked_custom_fields:
                    self.lblStandByOperatorSaloonMin.setText("NA")
                if "StandByOperatorCabinMax" not in self.locked_custom_fields:
                    self.lblStandByOperatorCabinMax.setText("NA")
                if "StandByOperatorCabinMin" not in self.locked_custom_fields:
                    self.lblStandByOperatorCabinMin.setText("NA")
                return  # Exit function if validation fails

            # Step 3: Fetch Standby Operator Temperature from ProjectManager
            summer_saloon, winter_saloon = ProjectManager.get_standby_operator_temp(standard_saloon)
            summer_cabin, winter_cabin = ProjectManager.get_standby_operator_temp(standard_cabin)

            # Step 4: Store default values even if labels are locked
            self.original_default_interior_values.update({
                "StandByOperatorSaloonMax": str(summer_saloon) if summer_saloon is not None else "None°C",
                "StandByOperatorSaloonMin": str(winter_saloon) if winter_saloon is not None else "None°C",
                "StandByOperatorCabinMax": str(summer_cabin) if summer_cabin is not None else "None°C",
                "StandByOperatorCabinMin": str(winter_cabin) if winter_cabin is not None else "None°C"
            })


            # Step 5: Update UI Labels
            if "StandByOperatorSaloonMax" not in self.locked_custom_fields:
                self.lblStandByOperatorSaloonMax.setText(str(summer_saloon) if summer_saloon is not None else "None°C")
            if "StandByOperatorSaloonMin" not in self.locked_custom_fields:
                self.lblStandByOperatorSaloonMin.setText(str(winter_saloon) if winter_saloon is not None else "None°C")
            if "StandByOperatorCabinMax" not in self.locked_custom_fields:
                self.lblStandByOperatorCabinMax.setText(str(summer_cabin) if summer_cabin is not None else "None°C")
            if "StandByOperatorCabinMin" not in self.locked_custom_fields:
                self.lblStandByOperatorCabinMin.setText(str(winter_cabin) if winter_cabin is not None else "None°C")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update Standby Operator Temperature: {str(e)}")

    def update_criteria_standard_fields(self):
        """Fetch and update temperature conditions for Saloon and Cabin."""
        try:
            # Define invalid values
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Country ---", "--- Select deck ---"}

            # Get Train Type and Standards
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )
            standard_saloon=self.cmbxStandardSaloon.currentText()
            if standard_saloon == "":
                standard_saloon = self.lblStandardSaloon.text()
            if not standard_saloon or not standard_cabin:
                # QtWidgets.QMessageBox.warning(
                #     self, 
                #     "Selection Required", 
                #     "Please select both Standard Saloon and Standard Cabin before proceeding."
                # )
                return  # Stop function execution

            category_saloon = self.lblCategorySaloon.text().strip()
            category_cabin = self.lblCategoryCabin.text().strip()
            # Pass data to CriteriaManager and fetch the results
            saloon_criteria_normal = CriteriaManager.get_criteria_values(standard_saloon, category_saloon, "Normal range")
            saloon_criteria_extended= CriteriaManager.get_criteria_values(standard_saloon, category_saloon, "Extended range")

            cabin_criteria_normal = CriteriaManager.get_criteria_values(standard_cabin, category_cabin, "Normal range")
            cabin_criteria_extended = CriteriaManager.get_criteria_values(standard_cabin, category_cabin, "Extended range")

            # Process and update UI labels
            self.update_saloon_labels_normal(saloon_criteria_normal)
            self.update_saloon_labels_extended(saloon_criteria_extended)
            self.update_cabin_labels_normal(cabin_criteria_normal)
            self.update_cabin_labels_extended(cabin_criteria_extended)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update temperature conditions: {str(e)}")

    def update_saloon_labels_extended(self, saloon_criteria):
        """Update the UI labels with saloon criteria values."""
        if not saloon_criteria:
            print("No Saloon Criteria data available.")
            return
        if not hasattr(self, 'default_saloon_extended_criteria_values'):
            self.default_saloon_extended_criteria_values = {}  # Initialize if not already present
        saloon_label_map = {
            
                # Add additional mappings here as needed

                "Tim q1": "lblTim1ExtendedSaloon",
                "Tim q2": "lblTim2ExtendedSaloon",
                "Horizontal gradient q1": "lblHGradient1ExtendedSaloon",
                "Horizontal gradient q2": "lblHGradient2ExtendedSaloon",
                "Vertical gradient seated q1": "lblVGradientSeated1ExtendedSaloon",
                "Vertical gradient seated q2": "lblVGradientSeated2ExtendedSaloon",
                "Vertical gradient seated (Foot warmest) q1": "lblVGradientSeatedFoot1ExtendedSaloon",
                "Vertical gradient seated (Foot warmest) q2": "lblVGradientSeatedFoot2ExtendedSaloon",
                "Vertical gradient stand q1": "lblVGradientStand1ExtendedSaloon",
                "Vertical gradient stand q2": "lblVGradientStand2ExtendedSaloon",
                "Vertical gradient stand (Foot warmest) q1": "lblVGradientStandFoot1ExtendedSaloon",
                "Vertical gradient stand (Foot warmest) q2": "lblVGradientStandFoot2ExtendedSaloon",
                "Vertical minimun temperature": "lblVMinimumTempExtendedSaloon",
                "Surfaces (Walls) DMax q1": "lblSurfaceWallsMaxQ1ExtendedSaloon",
                "Surfaces (Walls) DMax q2": "lblSurfaceWallsMaxQ2ExtendedSaloon",
                "Surfaces (Walls) DMin q1": "lblSurfaceWallsMinQ1ExtendedSaloon",
                "Surfaces (Walls) DMin q2": "lblSurfaceWallsMinQ2ExtendedSaloon",
                "Surfaces (ceilings) DMax q1": "lblSurfaceCeilingsMaxQ1ExtendedSaloon",
                "Surfaces (ceilings) DMax q2": "lblSurfaceCeilingsMaxQ2ExtendedSaloon",
                "Surfaces (ceilings) DMin q1": "lblSurfaceCeilingsMinQ1ExtendedSaloon",
                "Surfaces (ceilings) DMin q2": "lblSurfaceCeilingsMinQ2ExtendedSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMax q1": "lblSurfacesExposedMaxQ1ExtendedSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMax q2": "lblSurfacesExposedMaxQ2ExtendedSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMin q1": "lblSurfacesExposedMinQ1ExtendedSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMin q2": "lblSurfacesExposedMinQ2ExtendedSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMax q1": "lblSurfacesNotExposedMaxQ1ExtendedSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMax q2": "lblSurfacesNotExposedMaxQ2ExtendedSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMin q1": "lblSurfacesNotExposedMinQ1ExtendedSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMin q2": "lblSurfacesNotExposedMinQ2ExtendedSaloon",
                "Surfaces (Window frame) q1": "lblSurfacesFrameQ1ExtendedSaloon",
                "Surfaces (Window frame) q2": "lblSurfacesFrameQ2ExtendedSaloon",
            }

        for key, value in saloon_criteria.items():
            formatted_value = str(value) if value is not None else "N/A"

            # Get the corresponding label name from the dictionary
            label_name = saloon_label_map.get(key)
            if label_name and hasattr(self, label_name):
                self.default_saloon_extended_criteria_values[key] = formatted_value
                getattr(self, label_name).setText(formatted_value)

    def update_saloon_labels_normal(self, saloon_criteria):
        """Update the UI labels with saloon criteria values."""
        if not saloon_criteria:
            print("No Saloon Criteria data available.")
            return
        if not hasattr(self, 'default_saloon_normal_criteria_values'):
            self.default_saloon_normal_criteria_values = {}  # Initialize if not already present
        saloon_label_map = {
                "Tim q1": "lblTim1NormalSaloon",
                "Tim q2": "lblTim2NormalSaloon",
                "Horizontal gradient q1": "lblHGradient1NormalSaloon",
                "Horizontal gradient q2": "lblHGradient2NormalSaloon",
                "Vertical gradient seated q1": "lblVGradientSeated1NormalSaloon",
                "Vertical gradient seated q2": "lblVGradientSeated2NormalSaloon",
                "Vertical gradient seated (Foot warmest) q1": "lblVGradientSeatedFoot1NormalSaloon",
                "Vertical gradient seated (Foot warmest) q2": "lblVGradientSeatedFoot2NormalSaloon",
                "Vertical gradient stand q1": "lblVGradientStand1NormalSaloon",
                "Vertical gradient stand q2": "lblVGradientStand2NormalSaloon",
                "Vertical gradient stand (Foot warmest) q1": "lblVGradientStandFoot1NormalSaloon",
                "Vertical gradient stand (Foot warmest) q2": "lblVGradientStandFoot2NormalSaloon",
                "Vertical minimun temperature": "lblVMinimumTempNormalSaloon",
                "Surfaces (Walls) DMax q1": "lblSurfaceWallsMaxQ1NormalSaloon",
                "Surfaces (Walls) DMax q2": "lblSurfaceWallsMaxQ2NormalSaloon",
                "Surfaces (Walls) DMin q1": "lblSurfaceWallsMinQ1NormalSaloon",
                "Surfaces (Walls) DMin q2": "lblSurfaceWallsMinQ2NormalSaloon",
                "Surfaces (ceilings) DMax q1": "lblSurfaceCeilingsMaxQ1NormalSaloon",
                "Surfaces (ceilings) DMax q2": "lblSurfaceCeilingsMaxQ2NormalSaloon",
                "Surfaces (ceilings) DMin q1": "lblSurfaceCeilingsMinQ1NormalSaloon",
                "Surfaces (ceilings) DMin q2": "lblSurfaceCeilingsMinQ2NormalSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMax q1": "lblSurfacesExposedMaxQ1NormalSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMax q2": "lblSurfacesExposedMaxQ2NormalSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMin q1": "lblSurfacesExposedMinQ1NormalSaloon",
                "Surfaces (Window panes exposed to sun radiation) DMin q2": "lblSurfacesExposedMinQ2NormalSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMax q1": "lblSurfacesNotExposedMaxQ1NormalSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMax q2": "lblSurfacesNotExposedMaxQ2NormalSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMin q1": "lblSurfacesNotExposedMinQ1NormalSaloon",
                "Surfaces (Window panes not exposed to sun radiation) DMin q2": "lblSurfacesNotExposedMinQ2NormalSaloon",
                "Surfaces (Window frame) q1": "lblSurfacesFrameQ1NormalSaloon",
                "Surfaces (Window frame) q2": "lblSurfacesFrameQ2NormalSaloon",
                
            }

        for key, value in saloon_criteria.items():
            formatted_value = str(value) if value is not None else "N/A"

            # Get the corresponding label name from the dictionary
            label_name = saloon_label_map.get(key)
            if label_name and hasattr(self, label_name):
                # Store the default value in the dictionary
                self.default_saloon_normal_criteria_values[key] = formatted_value
                getattr(self, label_name).setText(formatted_value)
    


        # Example: Assuming you have labels for each criteria value
        
    def update_cabin_labels_extended(self, cabin_criteria):
        """Update the UI labels with cabin criteria values."""
        if not cabin_criteria:
            print("No Cabin Criteria data available.")
            return
        if not hasattr(self, 'default_cabin_extended_criteria_values'):
            self.default_cabin_extended_criteria_values = {}  # Initialize if not already present
        cabin_label_map = {
          
            # Extended values
            "Tim q1": "lblTim1ExtendedCabin",
            "Tim q2": "lblTim2ExtendedCabin",
            "Horizontal gradient q1": "lblHGradient1ExtendedCabin",
            "Horizontal gradient q2": "lblHGradient2ExtendedCabin",
            "Vertical gradient seated q1": "lblVGradientSeated1ExtendedCabin",
            "Vertical gradient seated q2": "lblVGradientSeated2ExtendedCabin",
            "Vertical gradient seated (Foot warmest) q1": "lblVGradientSeatedFoot1ExtendedCabin",
            "Vertical gradient seated (Foot warmest) q2": "lblVGradientSeatedFoot2ExtendedCabin",
            "Vertical gradient stand q1": "lblVGradientStand1ExtendedCabin",
            "Vertical gradient stand q2": "lblVGradientStand2ExtendedCabin",
            "Vertical gradient stand (Foot warmest) q1": "lblVGradientStandFoot1ExtendedCabin",
            "Vertical gradient stand (Foot warmest) q2": "lblVGradientStandFoot2ExtendedCabin",
            "Vertical minimun temperature": "lblVMinimumTempExtendedCabin",
            "Surfaces (Walls) DMax q1": "lblSurfaceWallsMaxQ1ExtendedCabin",
            "Surfaces (Walls) DMax q2": "lblSurfaceWallsMaxQ2ExtendedCabin",
            "Surfaces (Walls) DMin q1": "lblSurfaceWallsMinQ1ExtendedCabin",
            "Surfaces (Walls) DMin q2": "lblSurfaceWallsMinQ2ExtendedCabin",
            "Surfaces (ceilings) DMax q1": "lblSurfaceCeilingsMaxQ1ExtendedCabin",
            "Surfaces (ceilings) DMax q2": "lblSurfaceCeilingsMaxQ2ExtendedCabin",
            "Surfaces (ceilings) DMin q1": "lblSurfaceCeilingsMinQ1ExtendedCabin",
            "Surfaces (ceilings) DMin q2": "lblSurfaceCeilingsMinQ2ExtendedCabin",
            "Surfaces (Window panes exposed to sun radiation) DMax q1": "lblSurfacesExposedMaxQ1ExtendedCabin",
            "Surfaces (Window panes exposed to sun radiation) DMax q2": "lblSurfacesExposedMaxQ2ExtendedCabin",
            "Surfaces (Window panes exposed to sun radiation) DMin q1": "lblSurfacesExposedMinQ1ExtendedCabin",
            "Surfaces (Window panes exposed to sun radiation) DMin q2": "lblSurfacesExposedMinQ2ExtendedCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMax q1": "lblSurfacesNotExposedMaxQ1ExtendedCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMax q2": "lblSurfacesNotExposedMaxQ2ExtendedCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMin q1": "lblSurfacesNotExposedMinQ1ExtendedCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMin q2": "lblSurfacesNotExposedMinQ2ExtendedCabin",
            "Surfaces (Window frame) q1": "lblSurfacesFrameQ1ExtendedCabin",
            "Surfaces (Window frame) q2": "lblSurfacesFrameQ2ExtendedCabin",
        }

        for key, value in cabin_criteria.items():
            formatted_value = str(value) if value is not None else "N/A"

            # Get the corresponding label name from the dictionary
            label_name = cabin_label_map.get(key)

            if label_name and hasattr(self, label_name):
                self.default_cabin_extended_criteria_values[key] = formatted_value

                getattr(self, label_name).setText(formatted_value)
    def update_cabin_labels_normal(self, cabin_criteria):
        """Update the UI labels with cabin criteria values."""
        if not cabin_criteria:
            print("No Cabin Criteria data available.")
            return
        if not hasattr(self, 'default_cabin_normal_criteria_values'):
            self.default_cabin_normal_criteria_values = {}  # Initialize if not already present 
        cabin_label_map = {
            "Tim q1": "lblTim1NormalCabin",
            "Tim q2": "lblTim2NormalCabin",
            "Horizontal gradient q1": "lblHGradient1NormalCabin",
            "Horizontal gradient q2": "lblHGradient2NormalCabin",
            "Vertical gradient seated q1": "lblVGradientSeated1NormalCabin",
            "Vertical gradient seated q2": "lblVGradientSeated2NormalCabin",
            "Vertical gradient seated (Foot warmest) q1": "lblVGradientSeatedFoot1NormalCabin",
            "Vertical gradient seated (Foot warmest) q2": "lblVGradientSeatedFoot2NormalCabin",
            "Vertical gradient stand q1": "lblVGradientStand1NormalCabin",
            "Vertical gradient stand q2": "lblVGradientStand2NormalCabin",
            "Vertical gradient stand (Foot warmest) q1": "lblVGradientStandFoot1NormalCabin",
            "Vertical gradient stand (Foot warmest) q2": "lblVGradientStandFoot2NormalCabin",
            "Vertical minimun temperature": "lblVMinimumTempNormalCabin",
            "Surfaces (Walls) DMax q1": "lblSurfaceWallsMaxQ1NormalCabin",
            "Surfaces (Walls) DMax q2": "lblSurfaceWallsMaxQ2NormalCabin",
            "Surfaces (Walls) DMin q1": "lblSurfaceWallsMinQ1NormalCabin",
            "Surfaces (Walls) DMin q2": "lblSurfaceWallsMinQ2NormalCabin",
            "Surfaces (ceilings) DMax q1": "lblSurfaceCeilingsMaxQ1NormalCabin",
            "Surfaces (ceilings) DMax q2": "lblSurfaceCeilingsMaxQ2NormalCabin",
            "Surfaces (ceilings) DMin q1": "lblSurfaceCeilingsMinQ1NormalCabin",
            "Surfaces (ceilings) DMin q2": "lblSurfaceCeilingsMinQ2NormalCabin",
            "Surfaces (Window panes exposed to sun radiation) DMax q1": "lblSurfacesExposedMaxQ1NormalCabin",
            "Surfaces (Window panes exposed to sun radiation) DMax q2": "lblSurfacesExposedMaxQ2NormalCabin",
            "Surfaces (Window panes exposed to sun radiation) DMin q1": "lblSurfacesExposedMinQ1NormalCabin",
            "Surfaces (Window panes exposed to sun radiation) DMin q2": "lblSurfacesExposedMinQ2NormalCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMax q1": "lblSurfacesNotExposedMaxQ1NormalCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMax q2": "lblSurfacesNotExposedMaxQ2NormalCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMin q1": "lblSurfacesNotExposedMinQ1NormalCabin",
            "Surfaces (Window panes not exposed to sun radiation) DMin q2": "lblSurfacesNotExposedMinQ2NormalCabin",
            "Surfaces (Window frame) q1": "lblSurfacesFrameQ1NormalCabin",
            "Surfaces (Window frame) q2": "lblSurfacesFrameQ2NormalCabin",
          
        }

        for key, value in cabin_criteria.items():
            formatted_value = str(value) if value is not None else "N/A"

            # Get the corresponding label name from the dictionary
            label_name = cabin_label_map.get(key)

            if label_name and hasattr(self, label_name):
                self.default_cabin_normal_criteria_values[key] = formatted_value
                getattr(self, label_name).setText(formatted_value)


       
    def update_temperature_conditions(self):
        """Fetch and update temperature conditions for Saloon and Cabin."""
        try:
            # Define invalid values
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Country ---", "--- Select deck ---"}

            # Get Train Type and Standards
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )

            # Get Winter & Summer Zones
            selected_country = self.cmbxOperationCountryProject.currentText().strip()
            winter_zone_saloon = ProjectManager.get_winter_zone(selected_country, standard_saloon)
            winter_zone_cabin = ProjectManager.get_winter_zone(selected_country, standard_cabin)
            summer_zone_saloon = ProjectManager.get_summer_zone(selected_country, standard_saloon)
            summer_zone_cabin = ProjectManager.get_summer_zone(selected_country, standard_cabin)

            # Validation Check
            if any(value in invalid_values for value in [standard_saloon, standard_cabin, selected_country]):
                labels = [
                    self.lblWinterZoneSaloon, self.lblWinterOperationalSaloon, self.lblWinterNormalSaloon,
                    self.lblWinterExtremeSaloon, self.lblWinterExtendedSaloon, self.lblWinterDesignSaloon,
                    self.lblSummerZoneSaloon, self.lblSummerOperationalSaloon, self.lblSummerNormalSaloon,
                    self.lblSummerExtremeSaloon, self.lblSummerExtendedSaloon, self.lblSummerDesignSaloon,
                    self.lblWinterZoneCabin, self.lblWinterOperationalCabin, self.lblWinterNormalCabin,
                    self.lblWinterExtremeCabin, self.lblWinterExtendedCabin, self.lblWinterDesignCabin,
                    self.lblSummerZoneCabin, self.lblSummerOperationalCabin, self.lblSummerNormalCabin,
                    self.lblSummerExtremeCabin, self.lblSummerExtendedCabin, self.lblSummerDesignCabin
                ]
                for label in labels:
                    label.setText("NA")
                return  # Exit function if validation fails

            # Fetch Winter & Summer Temperature Conditions
            winter_saloon = ProjectManager.get_temperature_conditions(standard_saloon, "Winter", winter_zone_saloon)
            winter_cabin = ProjectManager.get_temperature_conditions(standard_cabin, "Winter", winter_zone_cabin)
            summer_saloon = ProjectManager.get_temperature_conditions(standard_saloon, "Summer", summer_zone_saloon)
            summer_cabin = ProjectManager.get_temperature_conditions(standard_cabin, "Summer", summer_zone_cabin)

            # Define label mappings for easy access
            label_mappings = {
                "WinterZoneSaloon": (self.lblWinterZoneSaloon, winter_zone_saloon),
                "WinterOperationalSaloon": (self.lblWinterOperationalSaloon, self.format_label_text(winter_saloon["Operational"])),
                "WinterDesignSaloon": (self.lblWinterDesignSaloon, self.format_label_text(winter_saloon["Design"])),
                "WinterExtremeSaloon": (self.lblWinterExtremeSaloon, self.format_label_text(winter_saloon["Extreme"])),
                "SummerZoneSaloon": (self.lblSummerZoneSaloon, summer_zone_saloon),
                "SummerOperationalSaloon": (self.lblSummerOperationalSaloon, self.format_label_text(summer_saloon["Operational"])),
                "SummerDesignSaloon": (self.lblSummerDesignSaloon, self.format_label_text(summer_saloon["Design"])),
                "SummerExtremeSaloon": (self.lblSummerExtremeSaloon, self.format_label_text(summer_saloon["Extreme"])),
                "WinterZoneCabin": (self.lblWinterZoneCabin, winter_zone_cabin),
                "WinterOperationalCabin": (self.lblWinterOperationalCabin, self.format_label_text(winter_cabin["Operational"])),
                "WinterDesignCabin": (self.lblWinterDesignCabin, self.format_label_text(winter_cabin["Design"])),
                "WinterExtremeCabin": (self.lblWinterExtremeCabin, self.format_label_text(winter_cabin["Extreme"])),
                "SummerZoneCabin": (self.lblSummerZoneCabin, summer_zone_cabin),
                "SummerOperationalCabin": (self.lblSummerOperationalCabin, self.format_label_text(summer_cabin["Operational"])),
                "SummerDesignCabin": (self.lblSummerDesignCabin, self.format_label_text(summer_cabin["Design"])),
                "SummerExtremeCabin": (self.lblSummerExtremeCabin, self.format_label_text(summer_cabin["Extreme"]))
            }

            # Update labels and store values in original_default_exterior_values
            for key, (label, value) in label_mappings.items():
                self.original_default_exterior_values[key] = value
                if key not in self.locked_custom_fields:  # Update UI only if not locked
                    label.setText(value)

            # Fetch Normal and Extended Range Temperatures
            for season, labels in [("Winter", ["WinterNormalSaloon", "WinterNormalCabin"]), 
                                ("Summer", ["SummerNormalSaloon", "SummerNormalCabin"])]:
                for label_name in labels:
                    temperature_data = ProjectManager.get_zone_temperature(
                        standard_saloon if "Saloon" in label_name else standard_cabin,
                        season,
                        "Normal_Range",
                        winter_zone_saloon if season == "Winter" else summer_zone_saloon
                    )
                    temperature_value = temperature_data["Min"] if season == "Winter" else temperature_data["Max"]
                    
                    # Store in original default values
                    self.original_default_exterior_values[label_name] = temperature_value
                    
                    # Update label if not locked
                    if label_name not in self.locked_custom_fields:
                        label_widget = getattr(self, f"lbl{label_name}")
                        
                        if season == "Winter":
                            self.set_label_textNormalWinter(label_widget, temperature_value)
                        elif season == "Summer":
                            self.set_label_textNormalSummer(label_widget, temperature_value)

            # Handle Extended Range
            for season in ["Winter", "Summer"]:
                for location in ["Saloon", "Cabin"]:
                    extended_data = ProjectManager.get_zone_temperature(
                        standard_saloon if location == "Saloon" else standard_cabin,
                        season,
                        "Extended_Range",
                        winter_zone_saloon if season == "Winter" else summer_zone_saloon
                    )
                    
                    min_val = extended_data["Min"]
                    max_val = extended_data["Max"]
                    key = f"{season}Extended{location}"
                    
                    # Store in original default values
                    self.original_default_exterior_values[key] = f"{min_val} - {max_val}"
                    
                    # Update label if not locked
                    if key not in self.locked_custom_fields:
                        label_widget = getattr(self, f"lbl{key}")
                        self.set_label_text_range(label_widget, min_val, max_val)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update temperature conditions: {str(e)}")


    def format_label_text(self,condition):
        """Formats the condition dictionary into a readable text for labels."""
        return f'{condition["Temperature"]}, {condition["Humidity"]}, {condition["Solar Load"]}'

    def set_label_text_range(self, label, min_temp, max_temp):
        """
        Sets the label text in the format: Max°C ≤ Text ≥ Min°C
        Handles None values gracefully.
        """
        min_str = f"{min_temp}°C" if min_temp is not None else "None°C"
        max_str = f"{max_temp}°C" if max_temp is not None else "None°C"
        
        label.setText(f"{max_str} ≤ Text ≥ {min_str}")

    
    
    def set_label_textNormalWinter(self,label, val):
        """
        Set the label text based on available Min/Max values.
        """
        min_str = f"Text ≥ {val}°C" if val is not None else "Text ≥ None°C"
        label.setText(f"{min_str}")
    
    def set_label_textNormalSummer(self,label, val):
        """
        Set the label text based on available Min/Max values.
        """
        max_str = f"{val}°C ≤ Text" if val is not None else "None°C ≤ Text"
        label.setText(f"{max_str}")
        
    def set_label_text(self,label, min_val, max_val):
        """
        Set the label text based on available Min/Max values.
        """
        if min_val is not None and max_val is not None:
            label.setText(f"{min_val} to {max_val}")
        elif min_val is not None:
            label.setText(f"{min_val}")
        elif max_val is not None:
            label.setText(f"{max_val}")
        else:
            label.setText("None")
    def get_standard_saloon_and_cabin(self, selected_train_type, cmbx_saloon, lbl_saloon, cmbx_cabin, lbl_cabin):
        """
        Determines the standard saloon and cabin based on UI visibility.
        If the combo box is visible, get the selected item; otherwise, use the label text.
        """
        # Get train standards (not needed for selecting saloon/cabin anymore)
        


        # Check visibility of combo box; if visible, get text from combo box, else from label
        standard_saloon = cmbx_saloon.currentText().strip() if cmbx_saloon.isVisible() else lbl_saloon.text().strip()
        standard_cabin = cmbx_cabin.currentText().strip() if cmbx_cabin.isVisible() else lbl_cabin.text().strip()

        return standard_saloon, standard_cabin

    def update_tic_coefficients(self):
        """Fetch and update Tic coefficient based on selected values, but keep locked custom values unchanged."""
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields"):
                self.locked_custom_fields = set()
            
            # Initialize original_default_interior_values if not already defined
            if not hasattr(self, "original_default_interior_values"):
                self.original_default_interior_values = {}

            # Step 1: Get Standard Saloon & Category
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )
            compartment = self.cmbxCompartmentProject.currentText().strip()

            # List of invalid selections
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Category ---", "--- Select Compartment ---"}

            # Validation: Ensure inputs are selected
            if standard_saloon in invalid_values or standard_cabin in invalid_values or compartment in invalid_values:
                # Reset only if fields are not locked
                if "TicMaxSaloon" not in self.locked_custom_fields:
                    self.lblMaxSaloonInterior.setText("°C")
                if "TicMinSaloon" not in self.locked_custom_fields:
                    self.lblMinSaloonInterior.setText("°C")
                if "TicMaxCabin" not in self.locked_custom_fields:
                    self.lblTicMaxCabinInterior.setText("°C")
                if "TicMinCabin" not in self.locked_custom_fields:
                    self.lblTicMinSaloonInterior.setText("°C")
                return  # Exit function

            # Step 2: Get Tic coefficients using ProjectManager
            tic_max_saloon, tic_min_saloon = ProjectManager.get_tic_coefficients(standard_saloon, compartment)
            tic_max_cabin, tic_min_cabin = ProjectManager.get_tic_coefficients(standard_cabin, compartment)

            # Step 3: Store default values even if labels are locked
            self.original_default_interior_values.update({
            "TicMaxSaloon": f"{tic_max_saloon}°C",
            "TicMinSaloon": f"{tic_min_saloon}°C",
            "TicMaxCabin": f"{tic_max_cabin}°C",
            "TicMinCabin": f"{tic_min_cabin}°C",
        })


            # Step 4: Update Labels, but only if they are NOT locked
            if "TicMaxSaloon" not in self.locked_custom_fields:
                self.lblMaxSaloonInterior.setText(f"{tic_max_saloon}°C")
            if "TicMinSaloon" not in self.locked_custom_fields:
                self.lblMinSaloonInterior.setText(f"{tic_min_saloon}°C")
            if "TicMaxCabin" not in self.locked_custom_fields:
                self.lblTicMaxCabinInterior.setText(f"{tic_max_cabin}°C")
            if "TicMinCabin" not in self.locked_custom_fields:
                self.lblTicMinSaloonInterior.setText(f"{tic_min_cabin}°C")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update Tic Coefficients: {str(e)}")

        
    def update_k_coefficient(self):
        """Fetch and update heat transfer coefficient based on selected values."""
        try:
            # Step 1: Get Standard Saloon & Standard Cabin
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )


            # Step 2: Get Category
            category_saloon = self.lblCategorySaloon.text().strip()
            category_cabin = self.lblCategoryCabin.text().strip()
            # Step 3:    Get Deck Type
            deck_type = self.cmbxSigleDeckDoubleDeck.currentText().strip()
            # Step 4: Get Operation Country & Winter Zone
            selected_country = self.cmbxOperationCountryProject.currentText().strip()
            # List of default/invalid options to check
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---","--- Select Country ---","--- Select deck ---"}
            # Validation: Ensure all required inputs are selected
            if (
                standard_saloon in invalid_values or
                standard_cabin in invalid_values or
                category_saloon in invalid_values or
                category_cabin in invalid_values or
                deck_type in invalid_values or
                selected_country in invalid_values
            ):
                # Reset labels if validation fails
                self.lblHeatTransferSaloon.setText("NA")
                self.lblHeatTransferCabin.setText("NA")
                return  # Exit the function without proceeding further

            # Step 5: Get Winter Zone
            winter_zone = ProjectManager.get_winter_zone(selected_country, standard_saloon)
            winter_zone_2 = ProjectManager.get_winter_zone(selected_country, standard_cabin)

            if not winter_zone:
                self.lblHeatTransferSaloon.setText("")
                self.lblHeatTransferCabin.setText("")
                return
            # Step 6: Fetch k coefficient from K_coefficient.json
            k_saloon = ProjectManager.get_k_coefficient(standard_saloon, category_saloon, deck_type, winter_zone)
            k_cabin = ProjectManager.get_k_coefficient(standard_cabin, category_cabin, deck_type, winter_zone_2)

            # Step 7: Update Labels
            self.lblHeatTransferSaloon.setText(f"{k_saloon}" if k_saloon else "NA")
            self.lblHeatTransferCabin.setText(f"{k_cabin}" if k_cabin else "NA")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update Heat Transfer Coefficients: {str(e)}")

    def update_max_mean_interior_temp(self):
        """Fetch and update Max Mean Interior Temperature for Saloon and Cabin."""
        try:
            # Initialize locked fields if not already defined
            if not hasattr(self, "locked_custom_fields"):
                self.locked_custom_fields = set()
            
            # Initialize original_default_interior_values if not already defined
            if not hasattr(self, "original_default_interior_values"):
                self.original_default_interior_values = {}

            # Step 1: Get Standard Saloon & Standard Cabin
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )

            # Step 2: Get Summer Zone
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Country ---", "--- Select deck ---"}

            selected_country = self.cmbxOperationCountryProject.currentText().strip()
            if (
                selected_country in invalid_values or standard_saloon in invalid_values or standard_cabin in invalid_values
            ):
                # Reset labels if validation fails
                if "MaxMeanTempSaloon" not in self.locked_custom_fields:
                    self.lblMaxMeanInteriorTempSaloon.setText("°C")
                if "MaxMeanTempCabin" not in self.locked_custom_fields:
                    self.lblMaxMeanInteriorTempCabin.setText("°C")
                return  # Exit the function without proceeding further
            
            summer_zone_saloon = ProjectManager.get_summer_zone(selected_country, standard_saloon)
            summer_zone_cabin = ProjectManager.get_summer_zone(selected_country, standard_cabin)
            
            # Step 3: Get Category
            category_saloon = self.lblCategorySaloon.text().strip()
            category_cabin = self.lblCategoryCabin.text().strip()

            # Step 4: Fetch Max Mean Interior Temperature from JSON
            temp_saloon = ProjectManager.get_max_mean_interior_temp(
                standard_saloon, "Summer zone", category_saloon, summer_zone_saloon
            )
            temp_cabin = ProjectManager.get_max_mean_interior_temp(
                standard_cabin, "Summer zone", category_cabin, summer_zone_cabin
            )

            # Step 5: Store default values even if labels are locked
            self.original_default_interior_values.update({
            "MaxMeanTempSaloon": f"{temp_saloon}°C" if temp_saloon else "°C",
            "MaxMeanTempCabin": f"{temp_cabin}°C" if temp_cabin else "°C"
        })

            # Step 6: Update Labels only if they are NOT locked
            if temp_saloon:
                if "MaxMeanTempSaloon" not in self.locked_custom_fields:
                    self.lblMaxMeanInteriorTempSaloon.setText(f'{temp_saloon}°C')
            else:
                self.lblMaxMeanInteriorTempSaloon.setText("°C")

            if temp_cabin:
                if "MaxMeanTempCabin" not in self.locked_custom_fields:
                    self.lblMaxMeanInteriorTempCabin.setText(f'{temp_cabin}°C')
            else:
                self.lblMaxMeanInteriorTempCabin.setText("°C")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update Max Mean Interior Temperature: {str(e)}")

    def update_field(self, data_dict, label, combo_box, category_label):
        """Updates label & combo box visibility based on dictionary keys.
        - Shows keys (e.g., EN14750:2006) in combo box if multiple options exist.
        - Displays category directly if only one option exists.
        """
        keys = list(data_dict.keys())  # Get only the keys (e.g., EN14750:2006)

        if len(keys) > 1:
            combo_box.clear()
            combo_box.addItems(keys)
            combo_box.show()
            label.hide()
            category_label.setText(data_dict[keys[0]])  # Show the category directly
            category_label.show()

            # Connect event to update category label when an item is selected
            combo_box.currentTextChanged.connect(lambda: self.update_category_label(data_dict, combo_box, category_label))

        elif len(keys) == 1:
            label.setText(keys[0])  # Show key directly in label
            label.show()
            combo_box.clear()
            combo_box.hide()
            category_label.setText(data_dict[keys[0]])  # Show the category directly
            category_label.show()

        else:
            label.hide()
            combo_box.hide()
            category_label.hide()


    def update_category_label(self, data_dict, combo_box, category_label):
        """Updates the category label when an item is selected in the combo box."""
        selected_key = combo_box.currentText()
        category_label.setText(data_dict.get(selected_key, ""))
        category_label.show()

    def update_coach_inputs(self):
        """Dynamically updates the number of input boxes in frameCoaches based on txtNCoachesPerTrainProject."""
        try:
            num_coaches = int(self.txtNCoachesPerTrainProject.text()) if self.txtNCoachesPerTrainProject.text() else 0
            num_coaches = min(max(num_coaches, 0), 12)  # Ensure range 0-12

            # **Remove old inputs safely**
            while self.coach_widgets:
                widget = self.coach_widgets.pop()
                widget["label"].setParent(None)
                widget["input"].setParent(None)

            # **Check if layoutCoaches exists, otherwise create it**
            if not hasattr(self, 'layoutCoaches'):
                self.layoutCoaches = QVBoxLayout(self.frameCoaches)
                self.layoutCoaches.setContentsMargins(0, 0, 0, 0)  # Remove all margins
                self.layoutCoaches.setSpacing(2)  # Minimal spacing
                self.layoutCoaches.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align top

            # **Ensure frameCoaches has no internal margins**
            self.frameCoaches.setContentsMargins(0, 0, 0, 0)

            # **Add new inputs**
            for i in range(num_coaches):
                layout = QHBoxLayout()  # Horizontal layout for label + input
                layout.setContentsMargins(0, 0, 0, 0)  # Remove left/right margins
                layout.setSpacing(5)  # Small spacing between label and input

                label = QLabel(f"Coach {i+1} Name:", self.frameCoaches)
                input_box = QLineEdit(self.frameCoaches)
                input_box.setPlaceholderText(f"Enter Coach {i+1} Name")

                layout.addWidget(label)
                layout.addWidget(input_box)

                self.layoutCoaches.addLayout(layout)  # Add row to main layout

                self.coach_widgets.append({"label": label, "input": input_box})  # Store for cleanup

        except ValueError:
            pass  # Ignore invalid input

    def restrict_range(self, line_edit, min_val, max_val):
        """Prevents entering values out of range while typing."""
        try:
            text = line_edit.text()
            if text:
                value = int(text)
                if value < min_val or value > max_val:
                    line_edit.setText(str(max_val))  # Auto-fix to max if exceeded
        except ValueError:
            line_edit.setText(str(min_val))  # Auto-fix if n
    def show_message_box(self, title, message):
        """Displays a QMessageBox for general errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    def init_pages(self):
        """Initialize backend logic for each page."""
        # Initialize ConfigSystem logic
        self.stackedWidget.setCurrentIndex(0)


    def show_project_page(self):
        self.handleMenuClick(self.btnProjects, 0)

    def show_criteria_page(self):
        self.handleMenuClick(self.btnCriteria,1)
    def show_coach_page(self):
        self.handleMenuClick(self.btnCoach,2)

        
        # Load the project data
        project_data = self.saving_manager.load_project(self.ProjectName)
        # Pass the loaded data to the CoachPageManager
        if project_data:
            self.coach_page_manager.load_coach_data(project_data)

    def show_pairip_pass_menu(self):
        """Show the Pair IP Pass page."""
        self.handleMenuClick(self.btnSensorList, 4)

    def show_offset_leech_menu(self):
        """Show the Offset Leech page."""
        # self.current_page = self.offset_leech
        self.handleMenuClick(self.btnPlanning, 5)
    def show_multi_tool_menu(self):
        """Show the Multi-Tool page."""
        self.handleMenuClick(self.btnReport, 6)    
    def handleMenuClick(self, button, page_index):
        """
        Handles menu button clicks to update styles and switch pages.
        """
        from modules.ui_functions import UIFunctions

        # Deselect all buttons
        for btn in self.menu_buttons:
            btn.setStyleSheet(UIFunctions.deselectMenu(btn.styleSheet()))

        # Select the clicked button
        button.setStyleSheet(UIFunctions.selectMenu(button.styleSheet()))

        # Switch to the selected page
        self.stackedWidget.setCurrentIndex(page_index)


    def set_buttons_cursor(self):
        """Set the pointer cursor for all buttons in the UI."""
        buttons = self.findChildren(QPushButton)  # Find all QPushButton objects
        for button in buttons:
            button.setCursor(Qt.PointingHandCursor)

    def resizeEvent(self, event):
        # Update Size Grips
        from modules.ui_functions import UIFunctions
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MasterScreen()
    main_window.show()
    sys.exit(app.exec_())
