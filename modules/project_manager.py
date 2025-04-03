import json
import os
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
            if category == "-":
                category = ""

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
            tic_max = "None"
            tic_min = "None"

            # Search for matching standard and category
            for entry in tic_data["Standard"]:
                if standard in entry:
                    if "Δtic" in entry[standard] and compartment in entry[standard]["Δtic"]:
                        tic_max = entry[standard]["Δtic"][compartment].get("ΔTic Max", "None")
                        tic_min = entry[standard]["Δtic"][compartment].get("ΔTic Min", "None")
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
                    return entry[standard].get("Summer", "None°C"), entry[standard].get("Winter", "None°C")

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

            # Extract and format values
            def format_conditions(condition_data):
                degree_symbol = "°"  # Correct degree symbol
                temp_key = "Temperature [\u00baC]"  # Use exact key from JSON
                humidity_key = "Relative humidity [%]"
                solar_load_key = "Solar load [W/m2]"

                return {
                    "Temperature": f"{condition_data.get(temp_key, 'None')}{degree_symbol}C",
                    "Humidity": f"{condition_data.get(humidity_key, 'None')}%",
                    "Solar Load": f"{condition_data.get(solar_load_key, 'None')} W/m2"
            }

            return {
                "Design": format_conditions(season_data.get("Design conditions", {})),
                "Extreme": format_conditions(season_data.get("Extreme conditions", {})),
                "Operational": format_conditions(season_data.get("Operational limit", {})),
            }

        except Exception as e:
            print(f"Error loading temperature conditions: {e}")

        return {
            "Design": {"Temperature": "None°C", "Humidity": "None%", "Solar Load": "None W/m2"},
            "Extreme": {"Temperature": "None°C", "Humidity": "None%", "Solar Load": "None W/m2"},
            "Operational": {"Temperature": "None°C", "Humidity": "None%", "Solar Load": "None W/m2"},
        }

    @staticmethod
    def get_zone_temperature(standard, season, range_type, zone):
        """
        Retrieve temperature values from Zone_ranges.json.
        
        :param standard: Standard type (e.g., "EN13129:2016")
        :param season: "Winter" or "Summer"
        :param range_type: "Normal_Range" or "Extended_Range"
        :param zone: Zone level ("I", "II", "III")
        :return: Dictionary with Min/Max temperature or "NA" if not found
        """
        try:
            # Load the JSON file
            with open("data/Zone_ranges.json", "r") as file:
                data = json.load(file)
            # Extract temperature data
            return data.get(standard, {}).get(season, {}).get(range_type, {}).get(zone, {"Min": "NA", "Max": "NA"})

        except Exception as e:
            print(f"Error reading Zone_ranges.json: {e}")
            return {"Min": "None", "Max": "None"}

    @staticmethod
    def get_curve_values(standard, category):
        """
        Fetch all curve values (Text/Tin Upper Limit, Lower Limit, Curve Limit) for a given standard and category.

        :param standard: The selected standard (e.g., "EN13129:2016", "EN14750:2006")
        :param category: The selected category (e.g., "Category A", "Category B")
        :return: A dictionary containing values for the given category, or None if not found.
        """
        try:
            with open("data/Curve.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            if standard not in data:
                print(f"Standard '{standard}' not found in curve.json")
                return None  # No data available for the given standard

            standard_data = data[standard]  # Extract standard-specific data
            category_values = {}

            # Iterate over all limits and extract only values for the given category
            for limit_type, limit_data in standard_data.items():
                category_values[limit_type] = {}

                for subcategory, values in limit_data.items():
                    if isinstance(values, dict) and category in values:
                        category_values[limit_type][subcategory] = values[category]
                    else:
                        category_values[limit_type][subcategory] = None  # No data available

            return category_values  # Return filtered values
        except Exception as e:
            print(f"Error reading curve.json: {e}")
            return None

    @staticmethod
    def get_test_data(filename):
        """
        Dynamically build the file path based on the filename and load the corresponding JSON data.

        :param filename: The name of the file to load (e.g., 'Zone_ranges.json')
        :return: Loaded data from the file, or None if there is an error.
        """
        try:
            # Build the file path dynamically
            file_path = os.path.join("data", filename)

            # Check if the file exists
            if os.path.exists(file_path):
                # Load the JSON file
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                return data
            else:
                print(f"File {file_path} does not exist.")
                return None  # Return None if file does not exist

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None  # Return None in case of any error
    @staticmethod
    def show_message_box(title: str, message: str):
        """Displays a QMessageBox for errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
