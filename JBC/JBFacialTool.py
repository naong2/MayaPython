import os
from inspect import getsourcefile
import webbrowser
from functools import partial

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2 import QtWidgets, QtGui
from PySide2 import QtCore
from PySide2 import QtUiTools

class JBFacialToolWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    '''

    '''
    CURRENT_WORKFOLDER = ''

    def __init__(self):
        super(JBFacialToolWindow, self).__init__()
        # Load UI
        file_path = os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui')
        if os.path.exists(file_path):
            ui_file = QtCore.QFile(file_path)
            try:
                ui_file.open(QtCore.QFile.ReadOnly)
                loader = QtUiTools.QUiLoader()
                self.win = loader.load(ui_file)
            finally:
                ui_file.close()
        else:
            raise ValueError("cant find ui file")

        self.setWindowTitle("JBFacialTool 0.0.1")
        self.setCentralWidget(self.win)

        # Work Folder Settings
        self.win.combobox_workfolder.addItem('Add WorkFolder')
        self.win.combobox_workfolder.addItem('Add WorkFolder2')
        # add work folder
        self.win.combobox_workfolder.currentIndexChanged.connect(self.changed_workfolder)



        self.show(dockable=True)

    def changed_workfolder(self):
        # get current path
        current_path = self.win.combobox_workfolder.currentText()
        if current_path == 'Add WorkFolder':
            # get new path
            workfolder = QtWidgets.QFileDialog.getExistingDirectory()
            if workfolder:
                # add new path
                self.win.combobox_workfolder.addItem(workfolder)
        else:
            # invalid path
            if QtCore.QFileInfo(current_path).exists():
                self.win.combobox_workfolder.setCurrentIndex(self.win.combobox_workfolder.findText(current_path))
            else:
                # remove wrong path
                self.win.combobox_workfolder.removeItem(current_path)
                # set current path
                self.win.combobox_workfolder.setCurrentIndex(self.win.combobox_workfolder.findText(self.CURRENT_WORKFOLDER))
            self.refresh_workfolder()

    def refresh_workfolder(self):
        pass


JBFacialToolWindow()

