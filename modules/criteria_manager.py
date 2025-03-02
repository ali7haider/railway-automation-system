import json
from PyQt5.QtWidgets import QComboBox, QMessageBox

class CriteriaManager:
    """Handles project-related data loading and processing."""

    @staticmethod
    def load_multiple_json(combo_mapping: dict):
        """
        Loads data from multiple JSON files into corresponding combo boxes.

        :param combo_mapping: Dictionary mapping QComboBox objects to JSON file paths.
        """
        for combo_box, json_file in combo_mapping.items():
            if isinstance(combo_box, QComboBox):  
                CriteriaManager.load_project_data(combo_box, json_file)

    @staticmethod
    def get_criteria_values(standard, category, range_type):
        """
        Retrieve criteria values from Criteria_standards.json.

        :param standard: The standard to look up (e.g., "EN14750:2006").
        :param category: The category to look up (e.g., "Category A").
        :param range_type: The range type to look up (e.g., "Normal range" or "Extended range").
        :return: Dictionary of criteria values if found, else an empty dictionary.
        """
        try:
            with open("data/Criteria_standards.json", "r") as file:
                data = json.load(file)
            if category == "-":
                category = ""

            standard, category, range_type = standard.strip(), category.strip(), range_type.strip()


            criteria_values = (
                data.get("Standard", {})
                .get(standard, {})
                .get("Category", {})
                .get(category, {})
                .get("Range", {})
                .get(range_type, {})
                .get("Criteria", {})
            )

            return criteria_values

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading Criteria_standards.json: {e}")
            return {}



    @staticmethod
    def show_message_box(title: str, message: str):
        """Displays a QMessageBox for errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
