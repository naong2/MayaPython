from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui

def maya_main_window():
    maya_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(maya_window_ptr), QtWidgets.QWidget)

class testDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(testDialog, self).__init__(parent)

        self.setWindowTitle('Sample Title')
        self.setMinimumSize(200,100)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)


if __name__ =='__main__':
    d = testDialog()
    d.show()