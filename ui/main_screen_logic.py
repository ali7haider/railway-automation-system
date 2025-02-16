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
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("ui/ui_files/main.ui", self)  # Load UI file dynamically
            from modules.ui_functions import UIFunctions
            self.ui=self
            self.set_buttons_cursor()
            

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

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load train data: {str(e)}")


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
