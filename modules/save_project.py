from PyQt5.QtWidgets import QMessageBox
import json  # For better print formatting

class ProjectSaver:
    def __init__(self, saving_manager):
        """
        Initialize ProjectSaver with a saving manager instance.
        :param saving_manager: The instance responsible for saving project data.
        """
        self.saving_manager = saving_manager

    def save_project(self, main_window):
        """
        Handles saving the project details.
        :param main_window: The main application window instance (to access UI elements).
        """
        try:
            # Check if Project Name is provided
            project_name = main_window.txtNameProject.text().strip()
            if not project_name:
                QMessageBox.warning(main_window, "Missing Information", "Please enter the Project Name before saving.")
                return

            # Store project name
            main_window.ProjectName = project_name

            # Create project data structure
            project_data = {
                "Project_info": self.build_project_info(main_window),
                "Interior_Condition_Data": self.build_interior_condition_data(main_window),
                "Exterior_Condition_Saloon": self.build_exterior_condition_saloon(main_window),
                "Exterior_Condition_Cabin": self.build_exterior_condition_cabin(main_window)

            }
            # Print project data for verification
            print("\n=== Project Data Before Saving ===")
            print(json.dumps(project_data, indent=4))  # Pretty-print JSON structure
            # Save the project data
            self.saving_manager.save_project(project_data)
            QMessageBox.information(main_window, "Success", f"Project '{project_name}' saved successfully.")

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"An error occurred while saving the project: {str(e)}")
    def build_project_info(self, main_window):
        """Builds and returns project information dictionary."""
        project_info = {
            "Project Name": main_window.txtNameProject.text().strip(),
            "Coach Builder": main_window.txtCoachBuilderProject.text(),
            "Customer/Operator": main_window.txtCustomerOperatorProject.text(),
            "Operation Country": main_window.cmbxOperationCountryProject.currentText(),
            "Type of Train": main_window.cmbxTypeOfTrainProject.currentText(),
            "Number of Coaches per Train": main_window.txtNCoachesPerTrainProject.text(),
            "Type of Compartment": main_window.cmbxCompartmentProject.currentText(),
            "Type of HVAC": main_window.cmbxTypesOfHVACProject.currentText(),
            "Maximum Speed": main_window.txtMaximumSpeedProject.text(),
            "Single/Double Deck": main_window.cmbxSigleDeckDoubleDeck.currentText(),
            "Standard Saloon": main_window.lblStandardSaloon.text() if main_window.lblStandardSaloon.isVisible() else main_window.cmbxStandardSaloon.currentText(),
            "Category Saloon": main_window.lblCategorySaloon.text(),
            "Standard Cabin": main_window.lblStandardCabin.text() if main_window.lblStandardCabin.isVisible() else main_window.cmbxStandardCabin.currentText(),
            "Category Cabin": main_window.lblCategoryCabin.text(),
            "Heat Transfer Saloon": main_window.lblHeatTransferSaloon.text(),
            "Heat Transfer Cabin": main_window.lblHeatTransferCabin.text(),
            "Cabin 1 Name": main_window.txtCabin1NameProject.text(),
            "Cabin 2 Name": main_window.txtCabin2NameProject.text(),
            "Coaches": {}
        }

        # Collect dynamically generated coach names
        for index, widget in enumerate(main_window.coach_widgets):
            coach_name = widget["input"].text().strip()
            if coach_name:
                project_info["Coaches"][f"Coach {index + 1}"] = coach_name
        
        return project_info
    def build_interior_condition_data(self, main_window):
        """
        Builds a structured dictionary for interior conditions where each field contains both default and custom values.
        """
        interior_data = {}

        # Iterate through all default values
        for key, default_value in main_window.original_default_interior_values.items():
            custom_value = main_window.custom_values_interior.get(key, None)  # Get custom value or None

            # Handle curve dictionaries separately
            if isinstance(default_value, dict):
                interior_data[key] = self.build_curve_data(default_value, main_window, key)
            else:
                # Store both default and custom values in structured format
                interior_data[key] = {
                    "default": default_value,
                    "custom": custom_value if custom_value is not None else default_value  # Use default if custom is missing
                }

        # Handle Regulation Curves
        interior_data["RegulationCurveSaloon"] = {
            "default": "Norm",
            "custom": main_window.custom_values_interior.get("RegulationCurveSaloon", "Norm")
        }
        interior_data["RegulationCurveCabin"] = {
            "default": "Norm",
            "custom": main_window.custom_values_interior.get("RegulationCurveCabin", "Norm")
        }

        # Print Interior Condition Data for verification
    

        return interior_data

    def build_curve_data(self, default_curve, main_window, curve_key):
        """
        Handles curve data separately to ensure missing values are filled correctly.
        """
        if curve_key == "saloon_curve":
            custom_curve = main_window.custom_saloon_curve
        elif curve_key == "cabin_curve":
            custom_curve = main_window.custom_cabin_curve
        else:
            custom_curve = {}  # Default empty if not recognized

        merged_curve = {}

        for limit_key, default_values in default_curve.items():
            merged_curve[limit_key] = {}

            for point, default_value in default_values.items():
                custom_value = custom_curve.get(limit_key, {}).get(point, None)
                merged_curve[limit_key][point] = {
                    "default": default_value,
                    "custom": custom_value if custom_value is not None else default_value
                }

        return merged_curve
    def build_exterior_condition_saloon(self, main_window):
        """Builds and returns exterior condition saloon data with default and custom values."""
        default_values = main_window.transform_default_values(main_window.original_default_exterior_values)
        custom_values = main_window.saloon_custom_values

        key_mappings = {
            "WinterNormal": "CustomWinterNormalMin",
            "SummerNormal": "CustomSummerNormalMax",
            "WinterDesignHumidity": "CustomWinterDesignHumi",
            "SummerDesignHumidity": "CustomSummerDesignHumi",
            "WinterExtremeHumidity": "CustomWinterExtremeHumi",
            "SummerExtremeHumidity": "CustomSummerExtremeHumi",
            "WinterOperationalHumidity": "CustomWinterOperationalHumi",
            "SummerOperationalHumidity": "CustomSummerOperationalHumi",
            "WinterDesignHeatFlux": "CustomWinterDesignSolar",
            "SummerDesignHeatFlux": "CustomSummerDesignSolar",
            "WinterExtremeHeatFlux": "CustomWinterExtremeSolar",
            "SummerExtremeHeatFlux": "CustomSummerExtremeSolar",
            "WinterOperationalHeatFlux": "CustomWinterOperationalSolar",
            "SummerOperationalHeatFlux": "CustomSummerOperationalSolar",
        }

        exterior_condition_saloon = {}
        for default_key, default_value in default_values.items():
            custom_key = key_mappings.get(default_key, f"Custom{default_key}")
            exterior_condition_saloon[default_key] = {
                "default": default_value,
                "custom": custom_values.get(custom_key, "None")  # Default to "None" if no custom value
            }

        return exterior_condition_saloon


    def build_exterior_condition_cabin(self, main_window):
        """Builds and returns exterior condition cabin data with default and custom values."""
        default_values = main_window.transform_default_cabin_values(main_window.original_default_exterior_values)
        custom_values = main_window.cabin_custom_values

        key_mappings = {
            "WinterNormal": "CustomWinterNormalMin",
            "SummerNormal": "CustomSummerNormalMax",
            "WinterDesignHumidity": "CustomWinterDesignHumi",
            "SummerDesignHumidity": "CustomSummerDesignHumi",
            "WinterExtremeHumidity": "CustomWinterExtremeHumi",
            "SummerExtremeHumidity": "CustomSummerExtremeHumi",
            "WinterOperationalHumidity": "CustomWinterOperationalHumi",
            "SummerOperationalHumidity": "CustomSummerOperationalHumi",
            "WinterDesignHeatFlux": "CustomWinterDesignSolar",
            "SummerDesignHeatFlux": "CustomSummerDesignSolar",
            "WinterExtremeHeatFlux": "CustomWinterExtremeSolar",
            "SummerExtremeHeatFlux": "CustomSummerExtremeSolar",
            "WinterOperationalHeatFlux": "CustomWinterOperationalSolar",
            "SummerOperationalHeatFlux": "CustomSummerOperationalSolar",
        }

        exterior_condition_cabin = {}
        for default_key, default_value in default_values.items():
            custom_key = key_mappings.get(default_key, f"Custom{default_key}")
            exterior_condition_cabin[default_key] = {
                "default": default_value,
                "custom": custom_values.get(custom_key, "None")  # Default to "None" if no custom value
            }

        return exterior_condition_cabin
