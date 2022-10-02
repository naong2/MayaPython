import logging
from PySide2 import QtWidgets, QtCore, QtGui

class LogWidget(logging.Handler):
    def __init__(self):
        super(LogWidget, self).__init__()