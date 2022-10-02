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

import IMUtility_old as imuu
reload(imu)

#import IMTool.IMP4xpf as imp4xpf
#reload(imp4xpf)

import IMTool.IMFbx as imfbx
#reload(imfbx)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr

class DesignerUI(QtWidgets.QDialog):
    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;FBX (*.fbx);;All Files (*.*)"
    selected_filter = "Maya (*ma *.mb)"
    # IMTool에서 사용하는 아이콘 폴더 경로
    ICON_PATH = os.path.join(imu.getPathIMTool(), 'images')

    # --------------------------------------------------------------------------------------------------
    # 저장 할 것들
    # --------------------------------------------------------------------------------------------------
    # WorkFolder
    #DIRECTORY_PATH = os.path.join(imp4xpf.get_clientRoot(), 'depot\master\Art\Source').replace("\\", '/')
    DIRECTORY_PATH = r'D:\Work2020'
    DIRECTORY_PATH_LIST = []  # 작업폴더 List 담는 용
    WorkFolder_LASTINDEX = 1  # 마지막으로 선택했던 작업폴더를 저장했다가 복구시켜준다
    LASTEXPORT_PATH_LIST = []  # 마지막 Export 경로를 5개까지 저장해두는 곳
    LASTEXPORT_PATH_INDEX = 0  # 마지막 Export 경로 복구용
    LASTITEMINDEX = QtCore.QModelIndex()  # TreeWidget에서 마지막으로 선택한 아이템
    CURRENTITEM = QtWidgets.QTreeWidgetItem()

    # --------------------------------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------------------------------
    def __init__(self, ui_path=None, title_name='IMTool Exporter', parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        # 윈도우 설정
        self.setWindowTitle(title_name)
        self.setMinimumSize(655, 565)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # 설정
        self.test_in_progress = False
        self.callback_id = None
        self.callback_id2 = None
        self.file_path = ''
        self.perforce_checkout = True
        self.includeMayafile = False

        # 순차적 실행
        self.init_ui(ui_path)
        self.load_perforceInfo()
        self.load_info()
        self.setTreeView()
        self.create_layout()
        self.Load_Option()
        self.create_connection()
        self.callback_init()

    # ------------------------------------------------------------------------------------------
    # UI Load
    # ------------------------------------------------------------------------------------------
    def init_ui(self, ui_path=None):
        # UI 파일을 넣지 않을 경우 코드와 같은 이름의 ui파일로 대신 불러온다.
        if ui_path:
            f = QtCore.QFile(ui_path)
        else:
            try:
                # ui_path가 없으면 현재파일위치를 찾아 확장자만 ui로 바꿔서 불러오는 것을 시도한다.
                f = QtCore.QFile(abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('1.py', '3.ui'))
            except:
                print u'호출시 ui_path에 ui파일경로를 적어주거나, 같은 파일이름의 ui파일을 만들어주시면 됩니다.'
                return
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)
        f.close()

    # ------------------------------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------------------------------
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)
        self.ui.cb_workfolder.addItem(u"새 작업폴더 추가하기")
        self.ui.cb_workfolder.addItem(self.DIRECTORY_PATH)
        self.ui.cb_workfolder.setCurrentIndex(1)
        self.ui.pb_selectJoint.setStyleSheet("background-color:rgb(51, 102, 204)")
        dirIcon = os.path.join(self.ICON_PATH, "maya_joint.png")
        self.ui.pb_selectJoint.setIcon(QIcon(dirIcon))
        self.ui.pb_selectMesh.setStyleSheet("background-color:rgb(51, 102, 204)")
        dirIcon = os.path.join(self.ICON_PATH, "maya_polygon.png")
        self.ui.pb_selectMesh.setIcon(QIcon(dirIcon))
        self.ui.pb_setSelect.setStyleSheet("background-color:rgb(51, 102, 204)")
        self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(168, 60, 50)")
        self.ui.pb_OBJExport.setVisible(False)

    # ------------------------------------------------------------------------------------------
    # Connect Methods
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        # 작업폴더 오른버튼 옵션
        self.show_in_folder_action.triggered.connect(self.show_in_folder)
        self.make_in_folder_action.triggered.connect(self.make_in_folder)
        self.open_in_folder_action.triggered.connect(self.open_in_folder)
        self.import_in_folder_action.triggered.connect(self.import_in_folder)
        self.set_in_folder_action.triggered.connect(self.set_in_folder)
        self.create_in_folder_action.triggered.connect(self.create_in_folder)
        self.checkout_in_folder_action.triggered.connect(self.checkout_in_folder)

        # 작업폴더 변경
        self.ui.cb_workfolder.currentIndexChanged.connect(self.changed_workfolder)

        # 마지막 익스포트 경로 콤보박스
        self.ui.cb_lastExportlist.currentIndexChanged.connect(self.changed_lastExportFolder)

        # Fbx Preset 선택
        self.ui.cb_FBXPreset.currentIndexChanged.connect(self.changed_FbxPreset)

        # export 폴더 선택하기
        self.ui.toolButton_export.clicked.connect(self.select_export_folder)

        # Preset / Select Set 세팅
        self.ui.pb_selectJoint.clicked.connect(self.selectJoint)
        self.ui.pb_selectMesh.clicked.connect(self.selectMesh)
        self.ui.pb_setCreate.clicked.connect(self.setCreate)
        self.ui.pb_setAdd.clicked.connect(self.setAdd)
        self.ui.pb_setRemove.clicked.connect(self.setRemove)
        self.ui.pb_setSelect.clicked.connect(self.setSelect)

        # 작업폴더 콤보박스 리스트 지우기
        self.ui.pb_delfolder.clicked.connect(self.del_workfolder)
        self.ui.pushButton_refresh.clicked.connect(self.refresh_list)

        # 익스포트 시키기
        self.ui.pb_FBXExport.clicked.connect(self.export_fbx_select)
        self.ui.pb_OBJExport.clicked.connect(self.export_obj_select)

    def selectMesh(self):
        allShapes = cmds.ls(sl=1, dag=1, type='mesh')
        myTransformNodes = cmds.listRelatives(allShapes, p=True)
        cmds.select(list(set(myTransformNodes)))

    def selectJoint(self):
        children_joints = cmds.listRelatives(allDescendents=True, type='joint')
        cmds.select(children_joints, add=True)

    def setCreate(self):
        try:
            cmds.select('ExportSet_Anim', noExpand=1)
        except:
            selected = cmds.ls(sl=1)
            cmds.sets(selected, name='ExportSet_Anim')

    def setAdd(self):
        selected = cmds.ls(sl=1)
        cmds.sets(selected, add='ExportSet_Anim')

    def setRemove(self):
        selected = cmds.ls(sl=1)
        cmds.sets(selected, rm='ExportSet_Anim')

    def setSelect(self):
        try:
            cmds.select('ExportSet_Anim')
        except:
            print u'ExportSet을 찾을 수 없습니다, Create ExportSet버튼으로 생성해주세요'

    def check_login(self):
        pass
        #imp4xpf.run_login()

    # ------------------------------------------------------------------------------------------
    # 작업 디렉토리 설정하기
    # ------------------------------------------------------------------------------------------
    def changed_workfolder(self):
        # 새작업폴더를 선택하면
        if self.ui.cb_workfolder.currentText() == u"새 작업폴더 추가하기":
            self.add_workfolder()
        else:
            # 기존 워크폴더를 선택하면
            self.DIRECTORY_PATH = self.ui.cb_workfolder.currentText()
            self.WorkFolder_LASTINDEX = self.ui.cb_workfolder.currentIndex()
            self.refresh_list()

    def changed_lastExportFolder(self):
        if self.ui.cb_lastExportlist.currentText():
            self.ui.line_exportfolder.setText(self.ui.cb_lastExportlist.currentText())
            self.LASTEXPORT_PATH_INDEX = self.ui.cb_lastExportlist.currentIndex()

    def changed_FbxPreset(self):
        self.LAST_PRESET = self.ui.cb_FBXPreset.currentIndex()
        self.fbxOption_init()
        #print self.LAST_PRESET

    def add_workfolder(self):
        self.DIRECTORY_PATH = QtWidgets.QFileDialog.getExistingDirectory()
        if self.DIRECTORY_PATH != '':
            # 콤보박스에 없는 폴더경로라면 추가해라
            if self.ui.cb_workfolder.findText(self.DIRECTORY_PATH) == -1:
                self.ui.cb_workfolder.addItem(self.DIRECTORY_PATH)
                self.WorkFolder_LASTINDEX = self.ui.cb_workfolder.count() - 1
                self.ui.cb_workfolder.setCurrentIndex(self.ui.cb_workfolder.count() - 1)
                self.DIRECTORY_PATH_LIST.append(self.DIRECTORY_PATH)

            else:
                # 기존에 있던 디렉토리라면 해당 index 받은다음 그냥 갱신만 시켜주자
                self.ui.cb_workfolder.setCurrentIndex(self.ui.cb_workfolder.findText(self.DIRECTORY_PATH))
                self.WorkFolder_LASTINDEX = self.ui.cb_workfolder.findText(self.DIRECTORY_PATH)
                self.refresh_list()
        else:
            print ('Nothing')
            self.ui.cb_workfolder.setCurrentIndex(self.WorkFolder_LASTINDEX)

    def del_workfolder(self):
        print u"현재 폴더목록 개수:", (self.ui.cb_workfolder.count() - 1)
        if self.ui.cb_workfolder.count() > 2:
            self.DIRECTORY_PATH_LIST.remove(self.DIRECTORY_PATH)
            self.ui.cb_workfolder.removeItem(self.WorkFolder_LASTINDEX)
            self.DIRECTORY_PATH = self.ui.cb_workfolder.currentText()
            self.WorkFolder_LASTINDEX = self.ui.cb_workfolder.currentIndex()

        else:
            print u'폴더목록이 최소한 한개 이상 있어야 지울 수 있습니다.'

    # ------------------------------------------------------------------------------------------
    # Load Info
    # ------------------------------------------------------------------------------------------
    def load_info(self):
        # 파일이름 설정
        if imu.getPathMayaFile():
            self.ui.line_filename.setText(
                imu.getNameMayaFile().replace('.mb', '').replace('.ma', '').replace('.fbx', '').strip())
        else:
            self.ui.line_filename.setText(u'현재 열린 파일이 없어요')

        # 마지막 익스포트 폴더 설정
        # last_export_path = os.path.join(imp4xpf.get_clientRoot(), 'depot', 'master', 'Art', 'Source',
        #                                 'Animation').replace("\\", '/')
        # self.ui.line_exportfolder.setText(last_export_path)

        # Animation Range
        self.ui.line_startFrame.setText(str(int(cmds.playbackOptions(query=True, min=True))))
        self.ui.line_endFrame.setText(str(int(cmds.playbackOptions(query=True, max=True))))

    def load_perforceInfo(self):
        pass
        # 퍼포스 기본 정보 표시하기
        #self.ui.label_p4user.setText('USER: ' + imp4xpf.get_user() + '      ')
        #self.ui.label_p4ClientName.setText('Workspace: ' + imp4xpf.get_client() + '      ')
        #self.ui.label_p4cwd.setText('WorkRoot: ' + imp4xpf.get_clientRoot())


    # ------------------------------------------------------------------------------------------
    # Perforce
    # ------------------------------------------------------------------------------------------

    def add_changeList(self, _file):
        pass
        #imp4xpf.add_changelist_default(_file)


    # ------------------------------------------------------------------------------------------
    # Select Export Folder
    # ------------------------------------------------------------------------------------------
    def select_export_folder(self):
        _folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        if _folder_path:
            self.ui.line_exportfolder.setText(_folder_path)

    # ------------------------------------------------------------------------------------------
    # Open Select File
    # ------------------------------------------------------------------------------------------

    # 이건 사용 안하는 녀석
    # def show_file_select_dialog(self):
    # 파일 선택창에서 선택한 파일 이름
    #    _file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
    #    if _file_path:
    #        self.file_path = _file_path

    # 지금은 사용하지 말고, 강제로 열지 물어볼때 고르게 하는걸로 일단 이녀석은 보류
    # def update_force_visibility(self, checked):
    #    self.ui.force_cb.setVisible(checked)

    def load_file(self, isOpen):
        # 빈 파일경로면 그냥 리턴
        print "load_file"
        if not self.file_path:
            return

        # 파일이름과 확장자 분리하기
        name, ext = os.path.splitext(self.file_path)
        # 확장자가 안맞으면 걸러내기
        canOpenExtension = ['.ma', '.mb', '.fbx', '.obj']
        if not ext.lower() in canOpenExtension:
            print "Different Extension"
            return

        # 파일 경로가 존재하는 경로니?
        file_info = QtCore.QFileInfo(self.file_path)
        if not file_info.exists():
            print "Not exist folder"
            om.MGlobal.displayError("File does not exist: {0}".format(self.file_path))
            return

        # 자! 아무문제 없으면 열어보자꾸나!
        #self.open_file(self.file_path)

        if isOpen:
            self.open_file(self.file_path)
            print "Open!!!!!"
        else:
            self.import_file(self.file_path)
            print "import!!!!"


        '''
        일단 아래 기능은 안쓰는 걸로
        if self.open_rb.isChecked():
            self.open_file(file_path)
        elif self.import_rb.isChecked():
            self.import_file(file_path)
        else:
            self.reference_file(file_path)
        '''



    def open_file(self, file_path):


        force = True
        # 강제로 열리도록 수정함
        # if not force and cmds.file(q=True, modified=True):
        #     result = QtWidgets.QMessageBox.question(self, u"현재 파일이 수정되었음", u"현재 Scene을 저장하지 않고 그냥~ 열까요?")
        #     if result == QtWidgets.QMessageBox.StandardButton.Yes:
        #         force = True
        #     else:
        #         return
        if file_path.lower().endswith('obj'):
            cmds.file(file_path, open=True, type="OBJ", rnn=True, ignoreVersion=True, options="mo=0", force=force)
        else:
            cmds.file(file_path, open=True, ignoreVersion=True, force=force)

    def import_file(self, file_path):
        if file_path.lower().endswith('obj'):
            cmds.file(file_path, i = True, type = "OBJ", rnn=True, ignoreVersion = True, options = "mo=0")
        else:
            cmds.file(file_path, i=True, ignoreVersion=True)



    def reference_file(self, file_path):
        cmds.file(file_path, reference=True, ignoreVersion=True)

    # ------------------------------------------------------------------------------------------
    # Folder TreeView
    # ------------------------------------------------------------------------------------------
    def setTreeView(self):
        self.ui.tree_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tree_wdg.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.tree_wdg.setHeaderHidden(True)
        self.ui.tree_wdg.setIconSize(QtCore.QSize(24, 24))
        self.ui.tree_wdg.itemClicked.connect(self.tree_clickEvent)
        self.open_in_folder_action = QtWidgets.QAction(u"Open", self)
        self.import_in_folder_action = QtWidgets.QAction(u"Import", self)
        self.set_in_folder_action = QtWidgets.QAction(u"Set to Export Folder", self)
        self.make_in_folder_action = QtWidgets.QAction(u"New Folder", self)
        self.show_in_folder_action = QtWidgets.QAction(u"Open Explore", self)
        self.create_in_folder_action = QtWidgets.QAction(u"Make Workfolder", self)
        self.checkout_in_folder_action = QtWidgets.QAction(u"Checkout file", self)
        self.refresh_list()

    def tree_clickEvent(self,item):
        # print ('clicked item: ',item.text(0))
        self.LASTITEMINDEX = QtCore.QModelIndex(self.ui.tree_wdg.selectedIndexes()[0])
        self.CURRENTITEM = self.ui.tree_wdg.currentItem()

        # print type(LASTITEMINDEX)
        # print self.LASTITEMINDEX
        # print self.CURRENTITEM
        # parentIndex = self.categoryModel.indexFromItem(item)
        # self.CURRENTITEM = self.categoryProxyModel.mapFromSource(parentIndex)

        # print type(self.ui.tree_wdg.selectedIndexes())




    def refresh_list(self):
        self.ui.tree_wdg.clear()
        self.add_children(None, self.DIRECTORY_PATH)

    def add_children(self, parent_item, dir_path):
        directory = QtCore.QDir(dir_path)
        files_in_directory = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                                 QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        for file_name in files_in_directory:
            self.add_child(parent_item, dir_path, file_name)

    # File0409.png
    def add_child(self, parent_item, dir_path, file_name):
        file_path = u"{0}/{1}".format(dir_path, file_name)
        file_info = QtCore.QFileInfo(file_path)

        if file_info.suffix().lower() == "pyc":
            return

        item = QtWidgets.QTreeWidgetItem(parent_item, [file_name])
        item.setData(0, QtCore.Qt.UserRole, file_path)
        fileIcon = os.path.join(self.ICON_PATH, "File0294.png")

        if file_info.isDir():
            self.add_children(item, file_info.absoluteFilePath())
            dirIcon = os.path.join(self.ICON_PATH, "im_folder01.png")

            item.setIcon(0, QIcon(dirIcon))
        else:
            if file_info.suffix().lower() == "fbx":
                fileIcon = os.path.join(self.ICON_PATH, "im_fbx.png")
            elif file_info.suffix().lower() == "mb":
                fileIcon = os.path.join(self.ICON_PATH, "im_mb.png")
            elif file_info.suffix().lower() == "ma":
                fileIcon = os.path.join(self.ICON_PATH, "im_ma.png")
            item.setIcon(0, QIcon(fileIcon))

        if not parent_item:
            self.ui.tree_wdg.addTopLevelItem(item)

    def show_context_menu(self, pos):
        item = self.ui.tree_wdg.itemAt(pos)
        if not item:
            return

        file_path = item.data(0, QtCore.Qt.UserRole)
        self.show_in_folder_action.setData(file_path)

        context_menu = QtWidgets.QMenu()
        context_menu.setFont(QtGui.QFont('SansSerif', 11))

        context_menu.addAction(self.open_in_folder_action)
        context_menu.addAction(self.import_in_folder_action)
        context_menu.addAction(self.make_in_folder_action)
        context_menu.addAction(self.show_in_folder_action)
        # context_menu.addAction(self.create_in_folder_action)
        context_menu.addAction(self.set_in_folder_action)
        context_menu.addAction(self.checkout_in_folder_action)
        context_menu.exec_(self.ui.tree_wdg.mapToGlobal(pos))

    def set_in_folder(self):
        # QTreeView에서 바로 Export폴더로 지정하기
        file_path = self.show_in_folder_action.data()
        if os.path.isdir(file_path):
            self.ui.line_exportfolder.setText(file_path)
        else:
            self.ui.line_exportfolder.setText(os.path.dirname(file_path))
            self.ui.line_filename.setText(os.path.basename(file_path).split('.')[0])

    def select_Sync(self):
        imp4xpf.get_sync()

    # 파일 퍼포스 체크아웃시키기
    def checkout_in_folder(self):
        file_path = self.show_in_folder_action.data()
        if not os.path.isdir:
            toarray = [file_path]
            # 현재 퍼포스 Description 내용을 저장하기
            self.PERFORCE_DESCRIPTION = self.ui.text_perforceDesc.toPlainText()
            if self.ui.text_perforceDesc.toPlainText() == '':
                pass
                #imp4xpf.add_changelist_default(toarray)
            else:
                pass
                #imp4xpf.add_changelist_descript(toarray, self.ui.text_perforceDesc.toPlainText())

    # 마야 파일 열기
    def open_in_folder(self):
        file_path = self.show_in_folder_action.data()
        if file_path:
            self.file_path = file_path
            self.load_file(isOpen=True)

    def import_in_folder(self):
        file_path = self.show_in_folder_action.data()
        if file_path:
            self.file_path = file_path
            self.load_file(isOpen=False)
            print "import_in_folder"

    def make_in_folder(self):
        # 여기다가 폴더만드는기능을 넣을 거임
        file_path = self.show_in_folder_action.data()
        self.new_folder(file_path)

    def create_in_folder(self):
        # 작업폴더를 자동으로 만들어줍니다.
        pass

    # 탐색창 열기1
    def show_in_folder(self):
        # TreeView에서 선택한 곳의 경로를 가져온다
        file_path = self.show_in_folder_action.data()

        # OS specific implementations to show in folder (Explorer or Finder) and select the file
        if cmds.about(windows=True):
            if self.open_in_explorer(file_path):
                return

        # Qt fallback for Linux or if the OS-specific implementation fails.
        # This only open the directory. It does not select the file.
        file_info = QtCore.QFileInfo(file_path)
        if file_info.isDir():
            QtGui.QDesktopServices.openUrl(file_path)
        else:
            QtGui.QDesktopServices.openUrl(file_info.path())

    # 탐색창 열기2
    def open_in_explorer(self, file_path):
        # Windows specific implementation
        file_info = QtCore.QFileInfo(file_path)
        args = []
        if not file_info.isDir():
            args.append("/select,")
        args.append(QtCore.QDir.toNativeSeparators(file_path))

        if QtCore.QProcess.startDetached("explorer", args):
            return True
        return False

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

    # ------------------------------------------------------------------------------------------
    # 쓸데없는 거
    # ------------------------------------------------------------------------------------------
    def show_about(self):
        about_dialog = QtUiTools.QUiLoader().load(os.path.join(imu.getPathIMTool(), 'IMWin_about.ui'),
                                                  parentWidget=self)
        result = about_dialog.exec_()

    # 텍스트를 받는 새 팝업 열기
    def new_folder(self, _path):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter New folder name:')

        if ok:
            if not os.path.isdir(_path):
                result = os.path.dirname(_path)
            if os.path.isdir(os.path.join(_path, name)):
                print u'이미 같은 이름의 폴더가 있어요'
                return
            os.makedirs(os.path.join(_path, name))
            self.refresh_list()
            self.ui.tree_wdg.setExpanded(self.LASTITEMINDEX, True)

            # self.ui.tree_wdg.setCurrentItem(self.CURRENTITEM)


    def selectDirectory(self):
        selected_directory = QtWidgets.QFileDialog.getExistingDirectory()
        print selected_directory

    # ------------------------------------------------------------------------------------------
    # CallBack
    # ------------------------------------------------------------------------------------------
    def callback_init(self):
        try:
            self.callback_id = om.MEventMessage.addEventCallback("SceneOpened", self.on_new_scene)
            self.callback_id2 = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterExport, self.after_export)
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
            self.Save_Option()
            om.MMessage.removeCallback(self.callback_id)
            om.MMessage.removeCallback(self.callback_id2)
        except:
            pass

    # ------------------------------------------------------------------------------------------
    # Shelve 저장
    # ------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------------
    # Save Options
    # ---------------------------------------------------------------------------------------------------
    def Save_Option(self):
        try:
            d = shelve.open(os.path.join(imu.getPathIMTool(), 'IMWin_Export_v1.db'))
            d['DIRECTORY_PATH_LIST'] = self.DIRECTORY_PATH_LIST  # 작업폴더
            d['COMBOBOX_LASTINDEX'] = self.WorkFolder_LASTINDEX  # 작업폴더
            d['LASTEXPORT_PATH_LIST'] = self.LASTEXPORT_PATH_LIST  # 마지막 Export경로
            d['LASTEXPORT_PATH_INDEX'] = self.LASTEXPORT_PATH_INDEX  # 마지막 Export경로
            d['LASTEXPORT_PATH'] = self.ui.line_exportfolder.text()  # Export경로 입력창

            d['LAST_PRESET'] = self.ui.cb_FBXPreset.currentIndex()

            d['FBXOPTION_TRIANGULATE'] = self.ui.cb_triangulate.isChecked()
            d['FBXOPTION_SKINNING'] = self.ui.cb_skinning.isChecked()
            d['FBXOPTION_BLENDSHAPE'] = self.ui.cb_blendshape.isChecked()
            d['FBXOPTION_BAKEANIMATION'] = self.ui.cb_bakeAnimation.isChecked()
            d['FBXOPTION_CONNECTION'] = self.ui.cb_connection.isChecked()

            d['FBXOPTION_SMOOTH'] = self.ui.cb_smooth.isChecked()
            d['FBXOPTION_SMOOTHMESH'] = self.ui.cb_smoothmesh.isChecked()
            d['FBXOPTION_TANGENT'] = self.ui.cb_tangent.isChecked()
            d['FBXOPTION_INSTANCE'] = self.ui.cb_preserveInstances.isChecked()
            d['FBXOPTION_MOVETOORIGIN'] = self.ui.cb_movetoorigin.isChecked()
            d['FBXOPTION_RESAMPLEALL'] = self.ui.cb_resampleAll.isChecked()

            d['FBXOPTION_CHILDREN'] = self.ui.cb_includeChildren.isChecked()
            d['FBXOPTION_MEDIA'] = self.ui.cb_embeddedMedia.isChecked()
            d['FBXOPTION_UPAXIS'] = self.ui.cb_upAxis.currentIndex()
            d['FBXOPTION_FBXVERSION'] = self.ui.cb_fbxversion.currentIndex()
            d['FBXOPTION_ASCII'] = self.ui.cb_binary.currentIndex()

            d['PERFORCE_AUTO'] = self.ui.cb_perforce.isChecked()
            d['PERFORCE_DESCRIPTION'] = self.ui.text_perforceDesc.toPlainText()

            d.close()

        except:
            print 'Error: Save Option'

    # ---------------------------------------------------------------------------------------------------
    # Load Options
    # ---------------------------------------------------------------------------------------------------
    def Load_Option(self):
        try:
            d = shelve.open(os.path.join(imu.getPathIMTool(), 'IMWin_Export_v1.db'), 'r')

            self.DIRECTORY_PATH_LIST = d['DIRECTORY_PATH_LIST']
            self.WorkFolder_LASTINDEX = d['COMBOBOX_LASTINDEX']
            self.LASTEXPORT_PATH_LIST = d['LASTEXPORT_PATH_LIST']
            self.LASTEXPORT_PATH_INDEX = d['LASTEXPORT_PATH_INDEX']
            self.ui.line_exportfolder.setText(d['LASTEXPORT_PATH'])
            self.ui.cb_FBXPreset.setCurrentIndex(d['LAST_PRESET'])

            if self.ui.cb_FBXPreset.currentIndex() == 0:  # Animation
                self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(156, 45, 207)")
            elif self.ui.cb_FBXPreset.currentIndex() == 1:  # SkeletalMesh
                self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(168, 60, 50)")
            elif self.ui.cb_FBXPreset.currentIndex() == 2:  # StaticMesh
                self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(79, 135, 214)")
                self.ui.pb_OBJExport.setVisible(True)


            self.ui.cb_triangulate.setChecked(d['FBXOPTION_TRIANGULATE'])
            self.ui.cb_skinning.setChecked(d['FBXOPTION_SKINNING'])
            self.ui.cb_blendshape.setChecked(d['FBXOPTION_BLENDSHAPE'])
            self.ui.cb_bakeAnimation.setChecked(d['FBXOPTION_BAKEANIMATION'])
            self.ui.cb_connection.setChecked(d['FBXOPTION_CONNECTION'])

            self.ui.cb_smooth.setChecked(d['FBXOPTION_SMOOTH'])
            self.ui.cb_smoothmesh.setChecked(d['FBXOPTION_SMOOTHMESH'])
            self.ui.cb_tangent.setChecked(d['FBXOPTION_TANGENT'])
            self.ui.cb_preserveInstances.setChecked(d['FBXOPTION_INSTANCE'])
            self.ui.cb_movetoorigin.setChecked(d['FBXOPTION_MOVETOORIGIN'])
            self.ui.cb_resampleAll.setChecked(d['FBXOPTION_RESAMPLEALL'])

            self.ui.cb_includeChildren.setChecked(d['FBXOPTION_CHILDREN'])
            self.ui.cb_embeddedMedia.setChecked(d['FBXOPTION_MEDIA'])
            self.ui.cb_upAxis.setCurrentIndex(d['FBXOPTION_UPAXIS'])
            self.ui.cb_fbxversion.setCurrentIndex(d['FBXOPTION_FBXVERSION'])
            self.ui.cb_binary.setCurrentIndex(d['FBXOPTION_ASCII'])

            self.ui.cb_perforce.setChecked(d['PERFORCE_AUTO'])
            self.ui.text_perforceDesc.setText(d['PERFORCE_DESCRIPTION'])

            d.close()

            # 작업폴더 리스트의 길이가 1이상이라면 복구하고,
            if len(self.DIRECTORY_PATH_LIST) > 0:
                for item in self.DIRECTORY_PATH_LIST:
                    self.ui.cb_workfolder.addItem(item)

            # 작업폴더 마지막 인덱스로 돌려준다음
            self.ui.cb_workfolder.setCurrentIndex(self.WorkFolder_LASTINDEX)

            # 작업폴더를 갱신시켜준다
            self.changed_workfolder()

            # 마지막Export 경로를 복구시켜준다
            if len(self.LASTEXPORT_PATH_LIST) > 0:
                for last in self.LASTEXPORT_PATH_LIST:
                    self.ui.cb_lastExportlist.addItem(last)
                # 마지막으로 선택했던 Export경로를 다시 복구시켜준다
                self.ui.cb_lastExportlist.setCurrentIndex(self.LASTEXPORT_PATH_INDEX)

        except:
            print 'Error: Load Option'

    # ------------------------------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------------------------------
    def export_fbx_select(self):
        if self.ui.cb_FBXPreset.currentIndex() == 0:
            self.export_fbx_animation()

        elif self.ui.cb_FBXPreset.currentIndex() == 1:
            self.export_fbx_animation()

        elif self.ui.cb_FBXPreset.currentIndex() == 2:
            self.export_fbx_animation()

    def export_obj_select(self):
        ime = imuu.IMExport()
        sys.stdout.write('# Preparing to write OBJ file...\n')

        # Export 경로 가져오기
        exportPath = self.ui.line_exportfolder.text()
        exportFileName = self.ui.line_filename.text() + '.obj'
        self.ExportPath = os.path.join(exportPath, exportFileName).replace("\\", "/")
        print exportPath
        ime.objExport(path=exportPath, filename=exportFileName, separate=False)

        # cmds.file(self.ExportPath, pr=1, typ="OBJexport", es=1,
        #           op="groups=1; ptgroups=0; materials=0; smoothing=1; normals=0")


    def fbxOption_init(self):
        if self.ui.cb_FBXPreset.currentIndex() == 0:  # Animation
            self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(156, 45, 207)")
            self.ui.pb_OBJExport.setVisible(False)
            self.ui.cb_triangulate.setChecked(False)
            self.ui.cb_skinning.setChecked(True)
            self.ui.cb_blendshape.setChecked(True)
            self.ui.cb_bakeAnimation.setChecked(True)
            self.ui.cb_connection.setChecked(False)  # because baking animation
            self.ui.cb_includeChildren.setChecked(False)
            self.ui.cb_preserveInstances.setChecked(False)

        elif self.ui.cb_FBXPreset.currentIndex() == 1:  # SkeletalMesh
            self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(168, 60, 50)")
            self.ui.pb_OBJExport.setVisible(False)
            self.ui.cb_triangulate.setChecked(True)
            self.ui.cb_skinning.setChecked(True)
            self.ui.cb_blendshape.setChecked(True)
            self.ui.cb_bakeAnimation.setChecked(False)
            self.ui.cb_connection.setChecked(True)
            self.ui.cb_includeChildren.setChecked(True)
            self.ui.cb_preserveInstances.setChecked(False)

        elif self.ui.cb_FBXPreset.currentIndex() == 2:  # StaticMesh
            self.ui.cb_FBXPreset.setStyleSheet("background-color:rgb(79, 135, 214)")
            self.ui.pb_OBJExport.setVisible(True)
            self.ui.cb_triangulate.setChecked(False)
            self.ui.cb_skinning.setChecked(False)
            self.ui.cb_blendshape.setChecked(False)
            self.ui.cb_bakeAnimation.setChecked(False)
            self.ui.cb_connection.setChecked(True)
            self.ui.cb_includeChildren.setChecked(True)
            self.ui.cb_preserveInstances.setChecked(True)

        self.ui.cb_smooth.setChecked(True)
        self.ui.cb_smoothmesh.setChecked(False)
        self.ui.cb_tangent.setChecked(False)
        self.ui.cb_movetoorigin.setChecked(False)
        self.ui.cb_resampleAll.setChecked(False)

        self.ui.cb_embeddedMedia.setChecked(False)
        self.ui.cb_upAxis.setCurrentIndex(0)  # Y
        self.ui.cb_fbxversion.setCurrentIndex(0)  # FBX2018
        self.ui.cb_binary.setCurrentIndex(0)  # Binary

    def export_fbx_animation(self):
        sys.stdout.write('# Preparing to write FBX file...\n')

        # Export 경로 가져오기
        exportPath = self.ui.line_exportfolder.text()
        exportFileName = self.ui.line_filename.text() + '.fbx'

        # 익스포트 경로가 비워 있다면
        if self.LASTEXPORT_PATH_LIST == []:
            self.LASTEXPORT_PATH_LIST.append(exportPath)
            self.ui.cb_lastExportlist.addItem(exportPath)
            self.LASTEXPORT_PATH_INDEX = self.ui.cb_lastExportlist.currentIndex()

        # 익스포트 경로가 하나라도 들어 있다면
        else:
            # Export폴더가 5개 미만이고
            if len(self.LASTEXPORT_PATH_LIST) < 5:
                # 같은 폴더가 없다면
                if self.ui.cb_lastExportlist.findText(exportPath) == -1:
                    self.LASTEXPORT_PATH_LIST.append(exportPath)
                    self.ui.cb_lastExportlist.addItem(exportPath)
                    self.LASTEXPORT_PATH_INDEX = self.ui.cb_lastExportlist.currentIndex()

            # Export폴더가 5개 이상이고
            else:
                # 같은 폴더가 없다면
                if self.ui.cb_lastExportlist.findText(exportPath) == -1:
                    self.ui.cb_lastExportlist.removeItem(0)
                    self.LASTEXPORT_PATH_LIST.pop(0)
                    self.LASTEXPORT_PATH_LIST.append(exportPath)
                    self.ui.cb_lastExportlist.addItem(exportPath)
                    self.LASTEXPORT_PATH_INDEX = self.ui.cb_lastExportlist.currentIndex()

        # 경로와 이름을 합쳐라
        self.ExportPath = os.path.join(exportPath, exportFileName).replace("\\", "/")

        # 경로가 존재하지 않다면 만들어라
        if not os.path.exists(os.path.dirname(self.ExportPath)):
            os.makedirs(os.path.dirname(self.ExportPath))

        # FBX 옵션세팅을 하나 꺼낸다
        mel.eval('FBXPushSettings;')

        # set fbx options
        try:
            # reset
            mel.eval('FBXResetExport')
            mel.eval('FBXExportSmoothMesh -v %d' % int(self.ui.cb_smoothmesh.isChecked()))
            # needed for skins and blend shapes
            mel.eval('FBXExportShapes -v %d' % int(self.ui.cb_blendshape.isChecked()))
            mel.eval('FBXExportSkins -v %d' % int(self.ui.cb_skinning.isChecked()))
            # BakeAnimation
            mel.eval('FBXExportBakeComplexAnimation -v %d' % int(self.ui.cb_bakeAnimation.isChecked()))
            mel.eval('FBXExportBakeComplexStart -v %d' % int(self.ui.line_startFrame.text()))
            mel.eval('FBXExportBakeComplexEnd -v %d' % int(self.ui.line_endFrame.text()))
            mel.eval('FBXExportBakeResampleAnimation -v %d' % int(self.ui.cb_resampleAll.isChecked()))
            mel.eval('FBXExportEmbeddedTextures -v %d' % int(self.ui.cb_embeddedMedia.isChecked()))
            mel.eval('FBXExportInputConnections -v %d' % int(self.ui.cb_connection.isChecked()))
            mel.eval('FBXExportInstances -v %d' % int(
                self.ui.cb_preserveInstances.isChecked()))  # preserve instances by sharing same mesh

            # Ascii
            if self.ui.cb_binary.currentIndex() == 0:
                mel.eval('FBXExportInAscii -v 0')
            else:
                mel.eval('FBXExportInAscii -v 1')

            # UpAxis
            if self.ui.cb_upAxis.currentIndex() == 0:
                mel.eval("FBXExportUpAxis y")
                print 'Y Axis'
            else:
                mel.eval("FBXExportUpAxis z")
                print 'Z Axis'

            # FBX Version
            if self.ui.cb_fbxversion.currentIndex() == 0:
                mel.eval('FBXExportFileVersion "FBX201800"')
            elif self.ui.cb_fbxversion.currentIndex() == 1:
                mel.eval('FBXExportFileVersion "FBX201900"')
            elif self.ui.cb_fbxversion.currentIndex() == 2:
                mel.eval('FBXExportFileVersion "FBX201600"')

            mel.eval('FBXExportQuaternion -v resample')  # quaternion / euler / resample
            mel.eval('FBXExportAxisConversionMethod none')
            mel.eval('FBXExportConstraints -v 0')
            mel.eval('FBXExportSkeletonDefinitions -v 0')
            mel.eval("FBXExportReferencedAssetsContent -v true")
            mel.eval('FBXExportUseSceneName -v 1')
            mel.eval('FBXExportSplitAnimationIntoTakes -c')  # clear previous clips
            mel.eval('FBXExportSplitAnimationIntoTakes -v \"tata\" %d %d' % int(self.ui.line_startFrame.text()),int(self.ui.line_endFrame.text()))

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
        try:
            mel.eval('FBXExport -f "%s" -s' % self.ExportPath)
        except Exception as e:
            sys.stdout.write(str(e) + '\n')

        # Export 세팅을 이전상태로 되돌린다
        mel.eval('FBXPopSettings;')

        # -------------------------------------------
        # Perforce
        # -------------------------------------------
        if self.ui.cb_perforce.isChecked():
            # 퍼포스에 등록시키기
            toarray = [self.ExportPath]
            if self.ui.text_perforceDesc.toPlainText() == '':

                #imp4xpf.add_changelist_default(toarray)
                print 'add default changeList'

            else:

                #imp4xpf.add_changelist_descript(toarray, self.ui.text_perforceDesc.toPlainText())
                print 'add changeList'

        else:
            print 'nothing perforce'

        # 작업폴더에 fbx 파일이 추가되었을테니 갱신시켜준다
        self.refresh_list()


def main():
    pass


if __name__ == "__main__":
    try:
        exporter_dialog.close()
        exporter_dialog.deleteLater()
    except:
        pass

    exporter_dialog = DesignerUI()
    exporter_dialog.show()
