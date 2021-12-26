# -*- coding: UTF-8 -*-
import os
import shelve
import sys
import time
from inspect import getsourcefile
from os.path import abspath

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon
from shiboken2 import wrapInstance

import IMTool.IMUtil as imu
#reload(imu)
#import IMTool.IMP4xpf as imp4xpf
#reload(imp4xpf)
import IMTool.IMFbx as imfbx
#reload(imfbx)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr

class IMMulti_Exporter(QtWidgets.QDialog):

    # --------------------------------------------------------------------------------------------------
    # 저장 할 것들
    # --------------------------------------------------------------------------------------------------
    # WorkFolder
    #DIRECTORY_PATH = os.path.join(imp4xpf.get_clientRoot(), 'depot\master\Art\Source').replace("\\", '/')
    DIRECTORY_PATH = r'D:\Work2020'

    ExportFiles = []

    # --------------------------------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------------------------------
    def __init__(self, ui_path=None, title_name='IMTool Exporter', parent=maya_main_window()):
        super(IMMulti_Exporter, self).__init__(parent)

        WINDOW_NAME = 'IM Animation Multi Exporter v0.1'

        for wins in maya_main_window().findChildren(QtWidgets.QWidget):
            if wins.objectName() == WINDOW_NAME:
                wins.deleteLater()

        # 윈도우 설정
        self.setObjectName(WINDOW_NAME)
        self.setWindowTitle(WINDOW_NAME)
        self.setMinimumSize(300,400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setProperty('saveWindowPref', True)

        self.init_ui()
        self.create_layout()
        self.create_connection()


    # ------------------------------------------------------------------------------------------
    # UI Load
    # ------------------------------------------------------------------------------------------
    def init_ui(self, ui_path=None):
        try:
            # ui_path가 없으면 현재 파일위치를 찾아 확장자만 ui로 바꿔서 불러오는 것을 시도한다.
            f = QtCore.QFile(abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui'))
            print 'loaded default ui'
        except:
            print u'호출시 ui_path에 ui파일경로를 적어주거나, 같은 파일이름의 ui파일을 만들어주시면 됩니다.'
            return
        try:
            f.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            self.ui = loader.load(f, parentWidget=self)
        finally:
            f.close()

    # ------------------------------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------------------------------
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.addWidget(self.ui)

    # ------------------------------------------------------------------------------------------
    # Connect Methods
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        self.ui.pb_setSourceFolder.clicked.connect(self.select_source_folder)
        self.ui.pb_setTargetFolder.clicked.connect(self.select_target_folder)
        self.ui.cb_includeChildfolder.clicked.connect(self.get_maya_files)
        # 익스포트 시키기
        self.ui.pb_multiExport.clicked.connect(self.export_fbx_animation)

    def setSelect(self):
        try:
            cmds.select('ExportSet')
        except:
            print u'ExportSet을 찾을 수 없습니다, Create ExportSet버튼으로 생성해주세요'

    # ------------------------------------------------------------------------------------------
    # Select Export Folder
    # ------------------------------------------------------------------------------------------
    def select_source_folder(self):
        _folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        if _folder_path:
            self.ui.lineEdit_sourceFolder.setText(_folder_path)
            self.get_maya_files()

    def select_target_folder(self):
        _folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        if _folder_path:
            self.ui.lineEdit_targetFolder.setText(_folder_path)

    def get_maya_files(self):
        _folder_path = self.ui.lineEdit_sourceFolder.text()
        if _folder_path:
            self.ExportFiles = []
            if self.ui.cb_includeChildfolder.isChecked():
                temp_files = imu.get_dirfiles_sub(_folder_path)
            else:
                temp_files = imu.get_dirfiles(_folder_path)

            for maya_file in temp_files:
                extension = os.path.splitext(maya_file)[1][1:]
                if extension == 'mb' or extension =='ma':
                    self.ExportFiles.append(maya_file)
            self.add_listview()
        else:
            print 'select source folder'


    def add_listview(self):
        model = QtGui.QStandardItemModel()

        for file in self.ExportFiles:
            model.appendRow(QtGui.QStandardItem(file))

        self.ui.listView_files.setModel(model)



    # 파일 퍼포스 체크아웃시키기
    def checkout_in_folder(self):
        file_path = self.show_in_folder_action.data()
        if not os.path.isdir:
            toarray = [file_path]
            # 현재 퍼포스 Description 내용을 저장하기
            self.PERFORCE_DESCRIPTION = self.ui.text_perforceDesc.toPlainText()
            if self.ui.text_perforceDesc.toPlainText() == '':
                imp4xpf.add_changelist_default(toarray)
            else:
                imp4xpf.add_changelist_descript(toarray, self.ui.text_perforceDesc.toPlainText())


    def run_progress_test(self):
        if self.test_in_progress:
            return

        number_of_operation = 10
        self.ui.progress_bar.setRange(0, number_of_operation)
        self.ui.progress_bar.setValue(0)
        # self.ui.progress_bar_label.setText("Operation Progress")
        self.test_in_progress = True
        self.update_visibility()

        for i in range(1, number_of_operation + 1):
            if not self.test_in_progress:
                break
            # self.ui.progress_bar_label.setText("Processing operation: {0} (of {1})".format(i, number_of_operation))
            self.ui.progress_bar.setValue(i)
            time.sleep(0.2)
            QtCore.QCoreApplication.processEvents()
        self.test_in_progress = False
        self.update_visibility()

    def update_visibility(self):
        # self.progress_bar_label.setVisible(self.test_in_progress)
        self.ui.progress_bar.setVisible(self.test_in_progress)

        # self.ui.pb_FBXExport.setHidden(self.test_in_progress)
        self.ui.pb_FBXExport.setDisabled(self.test_in_progress)

    def selectDirectory(self):
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory()
        print selected_directory

    # ------------------------------------------------------------------------------------------
    # CallBack
    # ------------------------------------------------------------------------------------------
    def callback_init(self):
        try:
            self.callback_id = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterExport, self.after_export)
        except:
            print 'error : callback init'

    # 기본 메뉴에 있는 익스포트일 경우 받아오는 콜백
    def after_export(self, *args):
        print 'export Complete !'

    def on_new_scene(self, client_data):
        self.load_info()
        print"Changed file"

    def closeEvent(self, *event):
        # removes the callback from memory
        try:
            om.MMessage.removeCallback(self.callback_id)
        except:
            pass

    def export_fbx_animation(self):
        sys.stdout.write('# Preparing to write FBX file...\n')
        if not self.ui.lineEdit_sourceFolder.text():
            print 'select source folder'
            return
        if not self.ui.lineEdit_targetFolder.text():
            print 'select target folder'
            return
        self.get_maya_files()
        for file in self.ExportFiles:
            #open file
            cmds.file(file, o=True, f=True)
            # Export
            self.export_fbx_file(file)

    def export_fbx_file(self, file):

        # Export 경로 가져오기
        exportPath = file.replace(self.ui.lineEdit_sourceFolder.text(), self.ui.lineEdit_targetFolder.text())
        extension = os.path.splitext(file)[1][1:]
        if extension == 'mb':
            exportPath = exportPath.replace('mb','fbx')
        else:
            exportPath = exportPath.replace('ma','fbx')

        # 경로와 이름을 합쳐라
        # self.ExportPath = os.path.join(exportPath, exportFileName).replace("\\", "/")
        self.ExportPath = exportPath

        # 경로가 존재하지 않다면 만들어라
        if not os.path.exists(os.path.dirname(self.ExportPath)):
            os.makedirs(os.path.dirname(self.ExportPath))

        # FBX 옵션세팅을 하나 꺼낸다
        mel.eval('FBXPushSettings;')



        # set fbx options
        try:
            # reset
            mel.eval('FBXResetExport')
            mel.eval('FBXExportSmoothMesh -v 1')
            # needed for skins and blend shapes
            mel.eval('FBXExportShapes -v 1')
            mel.eval('FBXExportSkins -v 1')
            # BakeAnimation
            mel.eval('FBXExportBakeComplexAnimation -v 1')

            mel.eval('FBXExportBakeComplexStart -v %d' % int(cmds.playbackOptions(query=True, min=True)))
            mel.eval('FBXExportBakeComplexEnd -v %d' % int(cmds.playbackOptions(query=True, max=True)))

            mel.eval('FBXExportBakeResampleAnimation -v 0')
            mel.eval('FBXExportEmbeddedTextures -v 0')
            mel.eval('FBXExportInputConnections -v 0')
            mel.eval('FBXExportInstances -v 0')
            mel.eval('FBXExportInAscii -v 0')
            mel.eval("FBXExportUpAxis y")
            mel.eval('FBXExportFileVersion "FBX201800"')

            mel.eval('FBXExportQuaternion -v resample')  # quaternion / euler / resample
            mel.eval('FBXExportAxisConversionMethod none')
            mel.eval('FBXExportConstraints -v 0')
            mel.eval('FBXExportSkeletonDefinitions -v 0')
            mel.eval("FBXExportReferencedAssetsContent -v true")
            mel.eval('FBXExportUseSceneName -v 1')
            mel.eval('FBXExportSplitAnimationIntoTakes -c')  # clear previous clips
            mel.eval('FBXExportApplyConstantKeyReducer -v 0')
            mel.eval('FBXExportCameras -v 0')
            mel.eval('FBXExportLights -v 0')

            # Log 생성하지마
            mel.eval('FBXExportGenerateLog -v 0')

        except Exception as e:
            sys.stdout.write(str(e) + '\n')

        # -------------------------------------------
        # FBX Export
        # -------------------------------------------
        # Select Set
        cmds.select('ExportSet_Anim')
        try:
            mel.eval('FBXExport -f "%s" -s' % self.ExportPath)
        except Exception as e:
            sys.stdout.write(str(e) + '\n')

        # Export 세팅을 이전상태로 되돌린다
        mel.eval('FBXPopSettings;')
        sys.stdout.write('Success '+str(self.ExportPath) + '\n')


        # -------------------------------------------
        # Perforce
        # -------------------------------------------
        # if self.ui.cb_perforce.isChecked():
        #     퍼포스에 등록시키기
            # toarray = [self.ExportPath]
            # if self.ui.text_perforceDesc.toPlainText() == '':
            #     imp4xpf.add_changelist_default(toarray)
            #     print 'add default changeList'
            #     pass
            # else:
            #     imp4xpf.add_changelist_descript(toarray, self.ui.text_perforceDesc.toPlainText())
            #     print 'add changeList'
            #     pass
        # else:
        #     print 'nothing perforce'


if __name__ == "__main__":

    exporter_dialog = IMMulti_Exporter()
    exporter_dialog.show()
