import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QMainWindow,
    QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QMainWindow
import os
import sys
import os
from PyQt5 import uic
from PyQt5 import QtWidgets, uic


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

            self.menu_button_offset_grabber.setStyleSheet(UIFunctions.selectMenu(self.menu_button_offset_grabber.styleSheet()))

            self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
        #     # Initialize individual pages
            self.init_pages()

            self.menu_buttons = [
            self.menu_button_offset_grabber,  # Replace with your actual button objects
            self.menu_button_menu_compiler,
            self.menu_button_game_update,
            self.menu_button_multi_tool,
            self.menu_button_offset_grabber,
            self.menu_button_pairip_pass,
            self.menu_button_offset_leech
        ]

            # Assign menu button clicks
            self.menu_button_offset_grabber.clicked.connect(self.show_config_system)
            self.menu_button_menu_compiler.clicked.connect(self.show_menu_compiler)
            self.menu_button_game_update.clicked.connect(self.show_game_update_menu)
            self.menu_button_multi_tool.clicked.connect(self.show_multi_tool_menu)
            self.menu_button_pairip_pass.clicked.connect(self.show_pairip_pass_menu)
            self.menu_button_offset_leech.clicked.connect(self.show_offset_leech_menu)
        except Exception as e:
            self.show_message_box("Error", f"Error loading UI: {str(e)}")
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
        self.handleMenuClick(self.menu_button_offset_grabber, 0)

    def show_menu_compiler(self):
        self.handleMenuClick(self.menu_button_menu_compiler,2)
    def show_game_update_menu(self):
        self.handleMenuClick(self.menu_button_game_update,3)
    def show_pairip_pass_menu(self):
        """Show the Pair IP Pass page."""
        self.handleMenuClick(self.menu_button_pairip_pass, 4)

    def show_offset_leech_menu(self):
        """Show the Offset Leech page."""
        # self.current_page = self.offset_leech
        self.handleMenuClick(self.menu_button_offset_leech, 5)
    def show_multi_tool_menu(self):
        """Show the Multi-Tool page."""
        self.handleMenuClick(self.menu_button_multi_tool, 6)    
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


    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MasterScreen()
    main_window.show()
    sys.exit(app.exec_())
