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

        WINDOWNAME = 'Sample Title'

        for widgetName in maya_main_window().findChildren(QtWidgets.QWidget):
            if widgetName.objectName() == WINDOWNAME:
                widgetName.deleteLater()

        self.setWindowTitle(WINDOWNAME)
        self.setObjectName(WINDOWNAME)
        self.setProperty('saveWindowPref', True)

        self.setMinimumSize(200,100)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def closeEvent(self,e):
        print 'Exit'

    def create_widgets(self):
        self.button1 = QtWidgets.QPushButton('PushButton')
        self.combobox1 = QtWidgets.QComboBox()
        self.combobox1.addItems(['first','second','third'])

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.button1)
        main_layout.addWidget(self.combobox1)

    def create_connections(self):
        self.button1.clicked.connect(self.testFunc)
        self.combobox1.activated.connect(self.test_int)
        self.combobox1.activated[str].connect(self.test_string)

    def testFunc(self):
        print 'hello'

    @QtCore.Slot(int)
    def test_int(self, index):
        print('selected Index :{0}'.format(index))

    @QtCore.Slot(str)
    def test_string(self, string):
        print('selected String :{0}'.format(string))


if __name__ =='__main__':
    d = testDialog()
    d.show()