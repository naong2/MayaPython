# -*- coding: UTF-8 -*-
from PySide2 import QtCore, QtWidgets

def isShiftModifier():
    #Shift 키가 눌렸다면 True 반환
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.ShiftModifier
