import json
from PyQt5.QtWidgets import QComboBox, QMessageBox

class ProjectManager:
    """Handles project-related data loading and processing."""

    @staticmethod
    def load_multiple_json(combo_mapping: dict):
        """
        Loads data from multiple JSON files into corresponding combo boxes.

        :param combo_mapping: Dictionary mapping QComboBox objects to JSON file paths.
        """
        for combo_box, json_file in combo_mapping.items():
            if isinstance(combo_box, QComboBox):  
                ProjectManager.load_project_data(combo_box, json_file)

    @staticmethod
    def load_project_data(comboBox: QComboBox, json_file: str):
        """
        Loads project-related data from a JSON file into a combo box.

        :param comboBox: The QComboBox to populate.
        :param json_file: Path to the JSON file.
        """
        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            comboBox.clear()  # Clear previous items

            # Handle different structures separately
            if "Countries_zones.json" in json_file:
                ProjectManager.load_countries_zones(comboBox, data)
            elif "TrainType_standars.json" in json_file:
                ProjectManager.load_train_types(comboBox, data)
            else:
                ProjectManager.show_message_box("Error", f"Unsupported JSON structure in {json_file}")

        except Exception as e:
            ProjectManager.show_message_box("JSON Load Error", f"Could not load {json_file}: {str(e)}")

    @staticmethod
    def load_countries_zones(comboBox: QComboBox, data):
        """
        Parses and loads country names into a combo box.

        Expected JSON structure:
        {
            "countries": [
                { "name": "Austria", "regulations": { ... } },
                { "name": "Belgium", "regulations": { ... } }
            ]
        }
        """
        if isinstance(data, dict) and "countries" in data:
            comboBox.addItem("--- Select Country ---")  # Placeholder

            for country in data["countries"]:
                if isinstance(country, dict) and "name" in country:
                    comboBox.addItem(country["name"])  # Add country names

    @staticmethod
    def load_train_types(comboBox: QComboBox, data):
        """
        Parses and loads train types into a combo box.

        Expected JSON structure:
        {
            "TrainType": [
                {
                    "Urban": {...},
                    "Suburban": {...},
                    "Regional": {...},
                    "Main line": {...}
                }
            ]
        }
        """
        if isinstance(data, dict) and "TrainType" in data and isinstance(data["TrainType"], list):
            comboBox.addItem("--- Select Train Type ---")  # Placeholder

            train_types = data["TrainType"][0]  # Extract first object
            for train_type in train_types.keys():
                comboBox.addItem(train_type)  # Add each train type

    @staticmethod
    def get_train_standards(train_type):
        """Fetches Standard Saloon & Standard Cabin info for a given train type."""
        try:
            with open("data/TrainType_standars.json", "r") as file:
                train_data = json.load(file)

            train_types = train_data.get("TrainType", [{}])[0]
            train_info = train_types.get(train_type, {})

            standard_saloon = train_info.get("Standard Saloon", {})
            standard_cabin = train_info.get("Standard Cabin", {})

            return standard_saloon, standard_cabin

        except Exception as e:
            print(f"Error loading train data: {e}")
            return {}, {}
    
    @staticmethod

    def get_winter_zone(country, train_standard):
        """Retrieves the Winter Zone for the selected country and train standard."""
        try:
            with open("data/Countries_zones.json", "r", encoding="utf-8") as file:
                country_data = json.load(file)

            for entry in country_data.get("countries", []):
                if entry.get("name") == country:
                    return entry.get("regulations", {}).get(train_standard, {}).get("Winter Zone", "")

        except Exception as e:
            print(f"Error loading winter zone data: {e}")
        
        return ""  # Return empty string if not found

    # Example usage:
    # winter_zone = get_winter_zone("Austria", "EN14750:2006")
    # print(winter_zone)  # Output: "II"

    @staticmethod
    def get_summer_zone(country, train_standard):
        """
        Retrieves the Summer Zone for the selected country and train standard.
        
        Args:
            country (str): Selected country name.
            train_standard (str): The train standard (e.g., EN14750:2006).
        
        Returns:
            str: The Summer Zone for the given country and train standard.
        """
        try:
            with open("data/Countries_zones.json", "r", encoding="utf-8") as file:
                country_data = json.load(file)

            for entry in country_data.get("countries", []):
                if entry.get("name") == country:
                    return entry.get("regulations", {}).get(train_standard, {}).get("Summer Zone", "")

        except Exception as e:
            print(f"Error loading summer zone data: {e}")
        
        return ""  # Return empty string if not found

    @staticmethod
    def get_max_mean_interior_temp(train_standard, summer_zone, category, subcategory):
        """
        Retrieves the maximum mean interior temperature for the given train standard, summer zone, category, and subcategory.

        Args:
            train_standard (str): The train standard (e.g., EN14750:2006).
            summer_zone (str): The summer zone (e.g., "Summer zone").
            category (str): The category (e.g., "Category A").
            subcategory (str): The subcategory (e.g., "I", "II", "III" or "LS.1", "LS.2").

        Returns:
            int or None: The max mean interior temperature value if found, else None.
        """
        print(train_standard, summer_zone, category, subcategory)
        try:
            with open("data/Ti_max.json", "r", encoding="utf-8") as file:
                temp_data = json.load(file)

            return (
                temp_data
                .get(train_standard, {})
                .get(summer_zone, {})
                .get(category, {})
                .get(subcategory, None)  # Fetch temperature value
            )

        except Exception as e:
            print(f"Error loading max mean interior temperature data: {e}")
        
        return None  # Return None if not found

    @staticmethod
    def get_k_coefficient(standard, category, deck, winter_zone):
        """Fetches the k coefficient based on train standard, category, deck type, and winter zone."""
        try:
            with open("data/K_coefficient.json", "r") as file:
                k_data = json.load(file)

            # Navigate the JSON structure
            category_data = k_data.get(standard, {}).get("Category", {}).get(category, {})
            deck_data = category_data.get("Deck", {}).get(deck, {})
            winter_data = deck_data.get("Winter zone", {}).get(winter_zone, {})

            return winter_data.get("k coefficient", "N/A")

        except Exception as e:
            print(f"Error loading k coefficient data: {e}")

        return "N/A"


    @staticmethod
    def get_tic_coefficients(standard: str, compartment: str):
        """
        Fetches ΔTic Max and ΔTic Min values from Tic_coefficient.json.
        
        :param standard: The selected standard (e.g., "EN13129:2016").
        :param category: The selected compartment (e.g., "No sleeping coaches").
        :return: Tuple (ΔTic Max, ΔTic Min) or ("N/A", "N/A") if not found.
        """
        try:
            # Load JSON file
            with open("data/Delta_tic_data.json", "r", encoding="utf-8") as file:
                tic_data = json.load(file)

            # Validate JSON structure
            if "Standard" not in tic_data:
                raise KeyError("Invalid JSON format: 'Standard' key missing.")

            # Default values
            tic_max = "N/A"
            tic_min = "N/A"

            # Search for matching standard and category
            for entry in tic_data["Standard"]:
                if standard in entry:
                    if "Δtic" in entry[standard] and compartment in entry[standard]["Δtic"]:
                        tic_max = entry[standard]["Δtic"][compartment].get("ΔTic Max", "N/A")
                        tic_min = entry[standard]["Δtic"][compartment].get("ΔTic Min", "N/A")
                        break  # Exit loop after finding first match

            return tic_max, tic_min

        except FileNotFoundError:
            QMessageBox.critical(None, "Error", "Tic_coefficient.json file not found.")
            return "N/A", "N/A"

        except json.JSONDecodeError:
            QMessageBox.critical(None, "Error", "Error decoding Tic_coefficient.json. Invalid JSON format.")
            return "N/A", "N/A"

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to fetch Tic coefficients: {str(e)}")
            return "N/A", "N/A"
    @staticmethod
    def get_standby_operator_temp(standard):
        """Fetch standby operator temperature values for the given standard."""
        try:
            # Load JSON data
            with open("data/Standby.json", "r", encoding="utf-8") as file:
                standby_data = json.load(file)

            # Check if the standard exists in the data
            for entry in standby_data.get("Standard", []):
                if standard in entry:
                    return entry[standard].get("Summer", "NA"), entry[standard].get("Winter", "NA")

        except Exception as e:
            print(f"Error loading standby operator temperature data: {e}")

        return "NA", "NA"  # Default return if data is missing or standard not found

    @staticmethod
    def get_temperature_conditions(standard, season, zone):
        """Fetch temperature conditions for the given standard, season, and zone."""
        try:
            # Load JSON data
            with open("data/Conditions_standard.json", "r", encoding="utf-8") as file:
                temp_data = json.load(file)

            # Navigate JSON structure
            season_data = temp_data.get(standard, {}).get(season, {}).get(zone, {}).get("Conditions", {})

            return {
                "Design": season_data.get("Design conditions", {}).get("Temperature [ºC]", "NA"),
                "Extreme": season_data.get("Extreme conditions", {}).get("Temperature [ºC]", "NA"),
                "Operational": season_data.get("Operational limit", {}).get("Temperature [ºC]", "NA"),
            }

        except Exception as e:
            print(f"Error loading temperature conditions: {e}")

        return {"Design": "NA", "Extreme": "NA", "Operational": "NA"}

    
    @staticmethod
    def show_message_box(title: str, message: str):
        """Displays a QMessageBox for errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
