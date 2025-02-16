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
    def show_message_box(title: str, message: str):
        """Displays a QMessageBox for errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
