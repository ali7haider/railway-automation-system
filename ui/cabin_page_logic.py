from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,QFileDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
import math
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

class CabinScreen(QtWidgets.QMainWindow):
    custom_values_updated = pyqtSignal(dict)  # Signal to send custom values
    def __init__(self, parent,cabin_index):
        super().__init__()
        self.parent = parent
        try:
            uic.loadUi("ui/ui_files/cabin_setting.ui", self)  # Load custom UI
            # self.btnSave.clicked.connect(self.save_custom_values)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading Custom Interior Conditions UI: {str(e)}")