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
from modules.project_manager import ProjectManager  # Import ProjectManager
from PyQt5.QtGui import QIntValidator, QMouseEvent


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

            self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
        #     # Initialize individual pages
            self.init_pages()

            self.menu_buttons = [
            self.btnProjects,  # Replace with your actual button objects
            self.btnCriteria,
            self.btnTestList,
            self.btnReport,
            self.btnProjects,
            self.btnSensorList,
            self.btnPlanning,
            self.btnReportCampaign
        ]

            # Assign menu button clicks
            self.btnProjects.clicked.connect(self.show_config_system)
            self.btnCriteria.clicked.connect(self.show_menu_compiler)
            self.btnTestList.clicked.connect(self.show_game_update_menu)
            self.btnReport.clicked.connect(self.show_multi_tool_menu)
            self.btnSensorList.clicked.connect(self.show_pairip_pass_menu)
            self.btnPlanning.clicked.connect(self.show_offset_leech_menu)


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

            # Initially hide them
            self.lblStandardSaloon.hide()
            self.cmbxStandardSaloon.hide()
            self.lblStandardCabin.hide()
            self.cmbxStandardCabin.hide()

            # Connect combo box change event
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_standard_fields)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_max_mean_interior_temp)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_max_mean_interior_temp)
            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_max_mean_interior_temp)
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_standby_operator_temp)

            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxTypeOfTrainProject.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_temperature_conditions)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_temperature_conditions)


        except Exception as e:
            self.show_message_box("Error", f"Error loading UI: {str(e)}")

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
            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxSigleDeckDoubleDeck.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_k_coefficient)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_k_coefficient)

            self.cmbxStandardSaloon.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxStandardCabin.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxOperationCountryProject.currentTextChanged.connect(self.update_tic_coefficients)
            self.cmbxCompartmentProject.currentTextChanged.connect(self.update_tic_coefficients)
            
            

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load train data: {str(e)}")

    def update_standby_operator_temp(self):
        """Fetch and update Standby Operator Temperature for Saloon and Cabin with validation."""
        try:
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
                self.lblStandByOperatorSaloonMax.setText("NA")
                self.lblStandByOperatorSaloonMin.setText("NA")
                self.lblStandByOperatorCabinMax.setText("NA")
                self.lblStandByOperatorCabinMin.setText("NA")
                return  # Exit function if validation fails

            # Step 3: Fetch Standby Operator Temperature from ProjectManager
            summer_saloon, winter_saloon = ProjectManager.get_standby_operator_temp(standard_saloon)
            summer_cabin, winter_cabin = ProjectManager.get_standby_operator_temp(standard_cabin)
            # Step 4: Update UI Labels
            self.lblStandByOperatorSaloonMax.setText(str(summer_saloon) if summer_saloon is not None else "None°C")
            self.lblStandByOperatorSaloonMin.setText(str(winter_saloon) if winter_saloon is not None else "None°C")
            self.lblStandByOperatorCabinMax.setText(str(summer_cabin) if summer_cabin is not None else "None°C")
            self.lblStandByOperatorCabinMin.setText(str(winter_cabin) if winter_cabin is not None else "None°C")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to update Standby Operator Temperature: {str(e)}")

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

            # Update Winter Labels (Saloon & Cabin)
            self.lblWinterZoneSaloon.setText(winter_zone_saloon)
            self.lblWinterOperationalSaloon.setText(self.format_label_text(winter_saloon["Operational"]))
            self.lblWinterDesignSaloon.setText(self.format_label_text(winter_saloon["Design"]))
            self.lblWinterExtremeSaloon.setText(self.format_label_text(winter_saloon["Extreme"]))


            self.lblWinterZoneCabin.setText(winter_zone_cabin)
            self.lblWinterOperationalCabin.setText(self.format_label_text(winter_cabin["Operational"]))
            self.lblWinterDesignCabin.setText(self.format_label_text(winter_cabin["Design"]))
            self.lblWinterExtremeCabin.setText(self.format_label_text(winter_cabin["Extreme"]))

            # Update Summer Labels (Saloon & Cabin)
            self.lblSummerZoneSaloon.setText(summer_zone_saloon)
            self.lblSummerOperationalSaloon.setText(self.format_label_text(summer_saloon["Operational"]))
            self.lblSummerDesignSaloon.setText(self.format_label_text(summer_saloon["Design"]))
            self.lblSummerExtremeSaloon.setText(self.format_label_text(summer_saloon["Extreme"]))

            self.lblSummerZoneCabin.setText(summer_zone_cabin)
            self.lblSummerOperationalCabin.setText(self.format_label_text(summer_cabin["Operational"]))
            self.lblSummerDesignCabin.setText(self.format_label_text(summer_cabin["Design"]))
            self.lblSummerExtremeCabin.setText(self.format_label_text(summer_cabin["Extreme"]))


                        # Fetch Winter & Summer Temperature Conditions for Saloon and Cabin
            winter_saloon = ProjectManager.get_zone_temperature(standard_saloon, "Winter", "Normal_Range", winter_zone_saloon)
            winter_cabin = ProjectManager.get_zone_temperature(standard_cabin, "Winter", "Normal_Range", winter_zone_cabin)
            summer_saloon = ProjectManager.get_zone_temperature(standard_saloon, "Summer", "Normal_Range", summer_zone_saloon)
            summer_cabin = ProjectManager.get_zone_temperature(standard_cabin, "Summer", "Normal_Range", summer_zone_cabin)

            # Fetch Extended Range Temperatures
            winter_extended_saloon = ProjectManager.get_zone_temperature(standard_saloon, "Winter", "Extended_Range", winter_zone_saloon)
            winter_extended_cabin = ProjectManager.get_zone_temperature(standard_cabin, "Winter", "Extended_Range", winter_zone_cabin)
            summer_extended_saloon = ProjectManager.get_zone_temperature(standard_saloon, "Summer", "Extended_Range", summer_zone_saloon)
            summer_extended_cabin = ProjectManager.get_zone_temperature(standard_cabin, "Summer", "Extended_Range", summer_zone_cabin)
            # Update Labels - Winter Normal
            self.set_label_textNormalWinter(self.lblWinterNormalSaloon, winter_saloon["Min"])
            self.set_label_textNormalWinter(self.lblWinterNormalCabin, winter_cabin["Min"])

            # Update Labels - Winter Extended
            # Update Labels - Winter Extended
            self.set_label_text_range(self.lblWinterExtendedSaloon, winter_extended_saloon["Min"], winter_extended_saloon["Max"])
            self.set_label_text_range(self.lblWinterExtendedCabin, winter_extended_cabin["Min"], winter_extended_cabin["Max"])
            
            self.set_label_text_range(self.lblSummerExtendedSaloon, summer_extended_saloon["Min"], summer_extended_saloon["Max"])
            self.set_label_text_range(self.lblSummerExtendedCabin, summer_extended_cabin["Min"], summer_extended_cabin["Max"])

            # Update Labels - Summer Normal
            self.set_label_textNormalSummer(self.lblSummerNormalSaloon,summer_saloon["Max"])
            self.set_label_textNormalSummer(self.lblSummerNormalCabin,summer_cabin["Max"])
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
        """Fetch and update Tic coefficient based on selected values."""
        try:
            # Step 1: Get Standard Saloon & Category
            selected_train_type = self.cmbxTypeOfTrainProject.currentText().strip()
            standard_saloon, standard_cabin = self.get_standard_saloon_and_cabin(
                selected_train_type, self.cmbxStandardSaloon, self.lblStandardSaloon,
                self.cmbxStandardCabin, self.lblStandardCabin
            )
            compartment = self.cmbxCompartmentProject.currentText().strip()


            # List of invalid selections
            invalid_values = {"", "--- Select ---", "--- Select Train Type ---", "--- Select Category ---","--- Select Compartment ---"}

            # Validation: Ensure inputs are selected
            if standard_saloon in invalid_values or standard_cabin in invalid_values or compartment in invalid_values:
                self.lblMaxSaloonInterior.setText("")
                self.lblMinSaloonInterior.setText("")
                self.lblTicMaxCabinInterior.setText("")
                self.lblTicMinSaloonInterior.setText("")
                return  # Exit function

            # Step 2: Get Tic coefficients using ProjectManager
            tic_max_saloon, tic_min_saloon = ProjectManager.get_tic_coefficients(standard_saloon, compartment)
            tic_max_cabin, tic_max_cabin = ProjectManager.get_tic_coefficients(standard_cabin, compartment)

            # Step 3: Update Labels
            self.lblMaxSaloonInterior.setText(f"{tic_max_saloon}")
            self.lblMinSaloonInterior.setText(f"{tic_min_saloon}")
            self.lblTicMaxCabinInterior.setText(f"{tic_max_cabin}")
            self.lblTicMinSaloonInterior.setText(f"{tic_max_cabin}")

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
            print(winter_zone, winter_zone_2,standard_cabin, category_cabin, deck_type)
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
                self.lblMaxMeanInteriorTempSaloon.setText("")
                self.lblMaxMeanInteriorTempCabin.setText("")
                return  # Exit the function without proceeding further
            summer_zone_saloon = ProjectManager.get_summer_zone(selected_country, standard_saloon)
            summer_zone_cabin = ProjectManager.get_summer_zone(selected_country, standard_cabin)

            # Step 3: Get Category
            category_saloon = self.lblCategorySaloon.text().strip()
            category_cabin = self.lblCategoryCabin.text().strip()

            # Step 4: Fetch Max Mean Interior Temperature from JSON
            temp_saloon = ProjectManager.get_max_mean_interior_temp(standard_saloon, "Summer zone", category_saloon,summer_zone_saloon)
            temp_cabin = ProjectManager.get_max_mean_interior_temp(standard_cabin, "Summer zone", category_cabin,summer_zone_cabin)

            # Step 5: Update Labels
            if temp_saloon:
                self.lblMaxMeanInteriorTempSaloon.setText(str(temp_saloon))
            else:
                self.lblMaxMeanInteriorTempSaloon.setText("NA")

            if temp_cabin:
                self.lblMaxMeanInteriorTempCabin.setText(str(temp_cabin))
            else:
                self.lblMaxMeanInteriorTempCabin.setText("NA")

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


    def show_config_system(self):
        self.handleMenuClick(self.btnProjects, 0)

    def show_menu_compiler(self):
        self.handleMenuClick(self.btnCriteria,2)
    def show_game_update_menu(self):
        self.handleMenuClick(self.btnTestList,3)
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
