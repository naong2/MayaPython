# -*- coding: UTF-8 -*-
import os
from inspect import getsourcefile
from os.path import abspath

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtUiTools
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

import IMTool.IMUtil as imu

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class DesignerUI(QtWidgets.QDialog):

    def __init__(self, ui_path=None, title_name='IM Tool', parent=maya_main_window()):
        super(DesignerUI,self).__init__(parent)

        self.setWindowTitle(title_name)
        self.setMinimumSize(300, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setProperty("saveWindowPref", True)  # Save Position

        self.init_ui(ui_path)
        self.create_layout()
        self.create_connection()

    def init_ui(self, ui_path=None):
        # UI 파일을 넣지 않을 경우 코드와 같은 이름의 ui파일로 대신 불러온다.
        if ui_path:
            f = QtCore.QFile(ui_path)
        else:
            try:
                f = QtCore.QFile(abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui'))
            except:
                print '호출시 ui_path에 ui파일경로를 적어주거나, 같은 파일이름의 ui파일을 만들어주시면 됩니다.'
                return
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)
        f.close()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.ui)

    def create_connection(self):
        self.ui.pb_FBXExport.clicked.connect(self.doSomething)

    def doSomething(self):
        print "Good!!"

if __name__ =="__main__":

    try:
        IMMBF_dialog.close()
        IMMBF_dialog.deleteLater()
    except:
        pass

    IMMBF_dialog = DesignerUI(ui_path=None, title_name='IM Make Blendshape Face')
    IMMBF_dialog.show()