# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import os
import shelve
from inspect import getsourcefile

import JBControlRig_Info as JBC
reload(JBC)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr

class DesignerUI(QtWidgets.QDialog):
    # Setup
    BS_Data_Maya_File = '/JBControlRig/Blendshape_CC3_v1.mb'
    BS_Data = os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace(
        getsourcefile(lambda: 0).split('/')[-1], BS_Data_Maya_File)

    # just for list
    JBConrolRig = JBC.ControlRig_V1()

    BLENDSHAPEMESH = ''
    WRAPEDMESH = ''
    EYELEFT = ''
    EYERIGHT = ''
    TEETHBOTTOM = ''
    EXTRAMESH = []
    BlendNodeIndex = 0

    #savePosition Dictionary
    CustomTransform = {}

    ColorDefault = "background-color:rgb(95, 95, 95)"
    ColorComplete = "background-color:rgb(0, 102, 51)"



    # --------------------------------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------------------------------
    def __init__(self, ui_path=None, title_name='JBControlRig', parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        print 'Start JBControlRig_BS_Copy'

        # 윈도우 설정
        self.setWindowTitle(title_name)
        self.setMinimumSize(200, 250)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # 순차적 실행
        self.init_ui(ui_path)
        self.create_layout()  # 배치및 컬러 적용
        self.load_options()
        self.create_connection()

        # ------------------------------------------------------------------------------------------
        # UI Load
        # ------------------------------------------------------------------------------------------

    def closeEvent(self, event):
        # removes the callback from memory
        self.save_options()
        print 'Close!!'


    def init_ui(self, ui_path=None):
        # UI 파일을 넣지 않을 경우 코드와 같은 이름의 ui파일로 대신 불러온다.
        if ui_path:
            f = QtCore.QFile(ui_path)
        else:
            try:
                # ui_path가 없으면 현재파일위치를 찾아 확장자만 ui로 바꿔서 불러오는 것을 시도한다.
                f = QtCore.QFile(os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui'))

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

    def load_options(self):
        try:
            d = shelve.open(getsourcefile(lambda: 0).replace('.py','.db'), 'r')
            self.BS_Data = d['BS_Data']
            self.BLENDSHAPEMESH = d['BLENDSHAPEMESH']
            self.ui.label_blendshapemesh.setText(d['BLENDSHAPEMESH'])
            if self.BLENDSHAPEMESH == '' or self.BLENDSHAPEMESH == 'None':
                self.ui.pushButton_add_bsmesh.setStyleSheet(self.ColorDefault)
                self.ui.label_blendshapemesh.setText('None')
            else:
                self.ui.pushButton_add_bsmesh.setStyleSheet(self.ColorComplete)

            self.WRAPEDMESH = d['WRAPEDMESH']
            self.ui.label_wrapmesh.setText(d['WRAPEDMESH'])
            if self.WRAPEDMESH == '' or self.WRAPEDMESH == 'None':
                self.ui.pushButton_add_WrapMesh.setStyleSheet(self.ColorDefault)
                self.ui.label_wrapmesh.setText('None')
            else:
                self.ui.pushButton_add_WrapMesh.setStyleSheet(self.ColorComplete)

            self.EYELEFT = d['EYELEFT']
            self.ui.label_eyeLmesh.setText(d['EYELEFT'])
            if self.EYELEFT == '' or self.EYELEFT == 'None':
                self.ui.pushButton_add_eyeL_mesh.setStyleSheet(self.ColorDefault)
                self.ui.label_eyeLmesh.setText('None')
            else:
                self.ui.pushButton_add_eyeL_mesh.setStyleSheet(self.ColorComplete)

            self.EYERIGHT = d['EYERIGHT']
            self.ui.label_eyeRmesh.setText(d['EYERIGHT'])
            if self.EYERIGHT == '' or self.EYERIGHT == 'None':
                self.ui.pushButton_add_eyeR_mesh.setStyleSheet(self.ColorDefault)
                self.ui.label_eyeRmesh.setText('None')
            else:
                self.ui.pushButton_add_eyeR_mesh.setStyleSheet(self.ColorComplete)

            self.TEETHBOTTOM = d['TEETHBOTTOM']
            self.ui.label_jawmesh.setText(d['TEETHBOTTOM'])
            if self.TEETHBOTTOM == '' or self.TEETHBOTTOM == 'None':
                self.ui.pushButton_add_jaw_mesh.setStyleSheet(self.ColorDefault)
                self.ui.label_jawmesh.setText('None')
            else:
                self.ui.pushButton_add_jaw_mesh.setStyleSheet(self.ColorComplete)

            self.EXTRAMESH = d['EXTRAMESH']
            if len(self.EXTRAMESH) > 0:
                self.ui.pushButton_addExtraMesh.setStyleSheet(self.ColorComplete)
                for item in self.EXTRAMESH:
                    self.ui.listWidget.addItem(item)
            else:
                self.ui.pushButton_addExtraMesh.setStyleSheet(self.ColorDefault)

            d.close()
        except:
            print('cannot load .db')

        BS_Version = self.BS_Data.split('/')[-1]
        self.ui.label_bs_version.setText(BS_Version.replace('.mb',''))

    def save_options(self):
        try:
            d = shelve.open(getsourcefile(lambda: 0).replace('.py','.db'))
            d['BS_Data'] = self.BS_Data  # 작업폴더
            d['BLENDSHAPEMESH'] = self.BLENDSHAPEMESH
            d['WRAPEDMESH'] = self.WRAPEDMESH
            d['EYELEFT'] = self.EYELEFT
            d['EYERIGHT'] = self.EYERIGHT
            d['TEETHBOTTOM'] = self.TEETHBOTTOM
            d['EXTRAMESH'] = self.EXTRAMESH


            d.close()
        except:
            print('cannot save .db')



    # ------------------------------------------------------------------------------------------
    # Connect Methods
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        # Utility
        self.ui.pushButton_addblendshape.clicked.connect(self.add_blendshape_data)
        self.ui.pushButton_objExport.clicked.connect(self.objExport)
        self.ui.pushButton_jointToVertext.clicked.connect(self.CreateJointToVertex)
        self.ui.pushButton_uvsetMap1.clicked.connect(self.rename_UVs)
        self.ui.pushButton_uv_snapshot.clicked.connect(self.save_uv_snapshot)

        # Add Meshes
        self.ui.pushButton_add_bsmesh.clicked.connect(self.add_bsmesh)
        self.ui.spinBox_bs_index.valueChanged.connect(self.spinbox_changed)
        self.ui.pushButton_add_WrapMesh.clicked.connect(self.add_wrapmesh)
        self.ui.pushButton_add_jaw_mesh.clicked.connect(self.add_jawmesh)
        self.ui.pushButton_add_eyeL_mesh.clicked.connect(self.add_eyeLmesh)
        self.ui.pushButton_add_eyeR_mesh.clicked.connect(self.add_eyeRmesh)

        self.ui.pushButton_addExtraMesh.clicked.connect(self.add_extramesh)
        self.ui.pushButton_clearExtramesh.clicked.connect(self.clear_extramesh)

        # Extract
        self.ui.pushButton_bsCopy.clicked.connect(self.bs_copy)
        # AutoRig
        self.ui.pushButton_autorig.clicked.connect(self.autoControlRig)
        self.ui.pushButton_printConnectionInfo.clicked.connect(self.print_connection_info)
        self.ui.pushButton_reset.clicked.connect(self.resetSlider)

        # reset
        self.ui.pushButton_allResetBS.clicked.connect(self.allResetBS)

        # Calc
        self.ui.pushButton_eyeUp.clicked.connect(self.calc_eyeUp)
        self.ui.pushButton_eyeDown.clicked.connect(self.calc_eyeDown)
        self.ui.pushButton_eyeLeft.clicked.connect(self.calc_eyeLeft)
        self.ui.pushButton_eyeRight.clicked.connect(self.calc_eyeRight)
        self.ui.pushButton_jawOpen.clicked.connect(self.calc_jawOpen)
        self.ui.pushButton_jawForward.clicked.connect(self.calc_jawForward)
        self.ui.pushButton_jawLeft.clicked.connect(self.calc_jawLeft)
        self.ui.pushButton_jawRight.clicked.connect(self.calc_jawRight)
        self.ui.pushButton_closeEye.clicked.connect(self.calc_closeEye)

        # save pos
        self.ui.pushButton_eyeUpSave.clicked.connect(self.eyeUpSave)
        self.ui.pushButton_eyeDownSave.clicked.connect(self.eyeDownSave)
        self.ui.pushButton_eyeLeftSave.clicked.connect(self.eyeLeftSave)
        self.ui.pushButton_eyeRightSave.clicked.connect(self.eyeRightSave)
        self.ui.pushButton_jawOpenSave.clicked.connect(self.jawOpenSave)
        self.ui.pushButton_jawForwardSave.clicked.connect(self.jawForwardSave)
        self.ui.pushButton_jawLeftSave.clicked.connect(self.jawLeftSave)
        self.ui.pushButton_jawRightSave.clicked.connect(self.jawRightSave)
        self.ui.pushButton_closeEyeSave.clicked.connect(self.closeEyeSave)
        self.ui.pushButton_saveDefaultPos.clicked.connect(self.forceSave_OriginalPosition)

    def save_uv_snapshot(self):
        selectedObj = cmds.ls(sl=True)[0]
        if selectedObj:
            fullPath = cmds.file(q=True, sn=True)
            mayaFileName = cmds.file(q=True, sn=True).split('/')[-1]
            savePath = fullPath.replace(mayaFileName,'UV.TGA')
            print savePath
            cmds.uvSnapshot(o=True, n=savePath, xr=4096, yr=4096, ff='tga')

    def spinbox_changed(self, i):
        self.BlendNodeIndex = i
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            try:
                bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
                self.ui.label_bsNode.setText(bsNodeName)
            except:
                self.ui.label_bsNode.setText('None')

    def print_connection_info(self):
        sel = cmds.ls(sl=1)[0]
        meshHistory = cmds.listHistory(sel)
        bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
        BSList = []
        CtrlList = []
        blendshapes = cmds.listAttr(bsNodeName + '.w', m=True)
        for bs in blendshapes:
            connect = cmds.listConnections(bsNodeName + '.' + bs, d=False, s=True, p=True)
            if connect:
                BSList.append(bsNodeName + '.' + bs)
                CtrlList.append(connect[0])
        print '[BSList] = '
        print BSList
        print '[CtrlList] = '
        print CtrlList

    def allResetBS(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            self.allResetTransformExtraMesh()

    def forceSave_OriginalPosition(self):
        self.CustomTransform.clear()
        self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
        self.CustomTransform['EYELEFT_Original_r'] = self.getRotation(self.EYELEFT)
        self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
        self.CustomTransform['EYERIGHT_Original_r'] = self.getRotation(self.EYERIGHT)
        self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
        self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
        self.ui.pushButton_eyeUpSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_eyeDownSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_eyeLeftSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_eyeRightSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_jawOpenSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_jawForwardSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_jawLeftSave.setStyleSheet(self.ColorDefault)
        self.ui.pushButton_jawRightSave.setStyleSheet(self.ColorDefault)

    def allResetTransformExtraMesh(self):
        if 'EYELEFT_Original_t' in self.CustomTransform:
            cmds.setAttr(self.EYELEFT + '.translate',
                         self.CustomTransform['EYELEFT_Original_t'][0],
                         self.CustomTransform['EYELEFT_Original_t'][1],
                         self.CustomTransform['EYELEFT_Original_t'][2])
        if 'EYELEFT_Original_r' in self.CustomTransform:
            cmds.setAttr(self.EYELEFT + '.rotate',
                         self.CustomTransform['EYELEFT_Original_r'][0],
                         self.CustomTransform['EYELEFT_Original_r'][1],
                         self.CustomTransform['EYELEFT_Original_r'][2])

        if 'EYERIGHT_Original_t' in self.CustomTransform:
            cmds.setAttr(self.EYERIGHT + '.translate',
                         self.CustomTransform['EYERIGHT_Original_t'][0],
                         self.CustomTransform['EYERIGHT_Original_t'][1],
                         self.CustomTransform['EYERIGHT_Original_t'][2])
        if 'EYERIGHT_Original_r' in self.CustomTransform:
            cmds.setAttr(self.EYERIGHT + '.rotate',
                         self.CustomTransform['EYERIGHT_Original_r'][0],
                         self.CustomTransform['EYERIGHT_Original_r'][1],
                         self.CustomTransform['EYERIGHT_Original_r'][2])
        
        if 'TEETHBOTTOM_Original_t' in self.CustomTransform:
            cmds.setAttr(self.TEETHBOTTOM + '.translate',
                         self.CustomTransform['TEETHBOTTOM_Original_t'][0],
                         self.CustomTransform['TEETHBOTTOM_Original_t'][1],
                         self.CustomTransform['TEETHBOTTOM_Original_t'][2])
        if 'TEETHBOTTOM_Original_r' in self.CustomTransform:
            cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                         self.CustomTransform['TEETHBOTTOM_Original_r'][0],
                         self.CustomTransform['TEETHBOTTOM_Original_r'][1],
                         self.CustomTransform['TEETHBOTTOM_Original_r'][2])
    #Up
    def calc_eyeUp(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.eyeLookUpLeft', 1)
            cmds.setAttr(bsNodeName + '.eyeLookUpRight', 1)
            if 'EYELEFT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
                self.CustomTransform['EYELEFT_Original_r'] = self.getRotate(self.EYELEFT)
            if 'EYERIGHT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
                self.CustomTransform['EYERIGHT_Original_r'] = self.getRotate(self.EYERIGHT)
            if 'EYELEFT_eyeUp_t' in self.CustomTransform:
                cmds.setAttr(self.EYELEFT + '.translate',
                             self.CustomTransform['EYELEFT_eyeUp_t'][0],
                             self.CustomTransform['EYELEFT_eyeUp_t'][1],
                             self.CustomTransform['EYELEFT_eyeUp_t'][2])
                cmds.setAttr(self.EYELEFT + '.rotate',
                             self.CustomTransform['EYELEFT_eyeUp_r'][0],
                             self.CustomTransform['EYELEFT_eyeUp_r'][1],
                             self.CustomTransform['EYELEFT_eyeUp_r'][2])
            if 'EYERIGHT_eyeUp_t' in self.CustomTransform:
                cmds.setAttr(self.EYERIGHT + '.translate',
                             self.CustomTransform['EYERIGHT_eyeUp_t'][0],
                             self.CustomTransform['EYERIGHT_eyeUp_t'][1],
                             self.CustomTransform['EYERIGHT_eyeUp_t'][2])
                cmds.setAttr(self.EYERIGHT + '.rotate',
                             self.CustomTransform['EYERIGHT_eyeUp_r'][0],
                             self.CustomTransform['EYERIGHT_eyeUp_r'][1],
                             self.CustomTransform['EYERIGHT_eyeUp_r'][2])

    def eyeUpSave(self):
        if self.EYELEFT:
            self.CustomTransform['EYELEFT_eyeUp_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_eyeUp_r'] = self.getRotation(self.EYELEFT)
        if self.EYERIGHT:
            self.CustomTransform['EYERIGHT_eyeUp_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_eyeUp_r'] = self.getRotation(self.EYERIGHT)
            self.ui.pushButton_eyeUpSave.setStyleSheet(self.ColorComplete)

    #Down
    def calc_eyeDown(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.eyeLookDownLeft', 1)
            cmds.setAttr(bsNodeName + '.eyeLookDownRight', 1)
            if 'EYELEFT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
                self.CustomTransform['EYELEFT_Original_r'] = self.getRotate(self.EYELEFT)
            if 'EYERIGHT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
                self.CustomTransform['EYERIGHT_Original_r'] = self.getRotate(self.EYERIGHT)
            if 'EYELEFT_eyeDown_t' in self.CustomTransform:
                cmds.setAttr(self.EYELEFT + '.translate',
                             self.CustomTransform['EYELEFT_eyeDown_t'][0],
                             self.CustomTransform['EYELEFT_eyeDown_t'][1],
                             self.CustomTransform['EYELEFT_eyeDown_t'][2])
                cmds.setAttr(self.EYELEFT + '.rotate',
                             self.CustomTransform['EYELEFT_eyeDown_r'][0],
                             self.CustomTransform['EYELEFT_eyeDown_r'][1],
                             self.CustomTransform['EYELEFT_eyeDown_r'][2])
            if 'EYERIGHT_eyeDown_t' in self.CustomTransform:
                cmds.setAttr(self.EYERIGHT + '.translate',
                             self.CustomTransform['EYERIGHT_eyeDown_t'][0],
                             self.CustomTransform['EYERIGHT_eyeDown_t'][1],
                             self.CustomTransform['EYERIGHT_eyeDown_t'][2])
                cmds.setAttr(self.EYERIGHT + '.rotate',
                             self.CustomTransform['EYERIGHT_eyeDown_r'][0],
                             self.CustomTransform['EYERIGHT_eyeDown_r'][1],
                             self.CustomTransform['EYERIGHT_eyeDown_r'][2])


    def eyeDownSave(self):
        if self.EYELEFT:
            self.CustomTransform['EYELEFT_eyeDown_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_eyeDown_r'] = self.getRotation(self.EYELEFT)
        if self.EYERIGHT:
            self.CustomTransform['EYERIGHT_eyeDown_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_eyeDown_r'] = self.getRotation(self.EYERIGHT)
            self.ui.pushButton_eyeDownSave.setStyleSheet(self.ColorComplete)
    #CloseEye
    def calc_closeEye(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.eyeBlinkLeft', 1)
            cmds.setAttr(bsNodeName + '.eyeBlinkRight', 1)
            if 'EYELEFT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
                self.CustomTransform['EYELEFT_Original_r'] = self.getRotate(self.EYELEFT)
            if 'EYERIGHT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
                self.CustomTransform['EYERIGHT_Original_r'] = self.getRotate(self.EYERIGHT)
            # Left
            if 'EYELEFT_eyeClose_t' in self.CustomTransform:
                cmds.setAttr(self.EYELEFT + '.translate',
                             self.CustomTransform['EYELEFT_eyeClose_t'][0],
                             self.CustomTransform['EYELEFT_eyeClose_t'][1],
                             self.CustomTransform['EYELEFT_eyeClose_t'][2])
                cmds.setAttr(self.EYELEFT + '.rotate',
                             self.CustomTransform['EYELEFT_eyeClose_r'][0],
                             self.CustomTransform['EYELEFT_eyeClose_r'][1],
                             self.CustomTransform['EYELEFT_eyeClose_r'][2])
            # Right
            if 'EYERIGHT_eyeClose_t' in self.CustomTransform:
                cmds.setAttr(self.EYERIGHT + '.translate',
                             self.CustomTransform['EYERIGHT_eyeClose_t'][0],
                             self.CustomTransform['EYERIGHT_eyeClose_t'][1],
                             self.CustomTransform['EYERIGHT_eyeClose_t'][2])
                cmds.setAttr(self.EYERIGHT + '.rotate', 
                             self.CustomTransform['EYERIGHT_eyeClose_r'][0],
                             self.CustomTransform['EYERIGHT_eyeClose_r'][1],
                             self.CustomTransform['EYERIGHT_eyeClose_r'][2])

    def closeEyeSave(self):
        if self.EYELEFT:
            self.CustomTransform['EYELEFT_eyeClose_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_eyeClose_r'] = self.getRotation(self.EYELEFT)
        if self.EYERIGHT:
            self.CustomTransform['EYERIGHT_eyeClose_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_eyeClose_r'] = self.getRotation(self.EYERIGHT)
            self.ui.pushButton_closeEyeSave.setStyleSheet(self.ColorComplete)


    #Left
    def calc_eyeLeft(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.eyeLookOutLeft', 1)
            cmds.setAttr(bsNodeName + '.eyeLookInRight', 1)
            if 'EYELEFT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
                self.CustomTransform['EYELEFT_Original_r'] = self.getRotate(self.EYELEFT)
            if 'EYERIGHT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
                self.CustomTransform['EYERIGHT_Original_r'] = self.getRotate(self.EYERIGHT)
            if 'EYELEFT_eyeLeft_t' in self.CustomTransform:
                cmds.setAttr(self.EYELEFT + '.translate',
                             self.CustomTransform['EYELEFT_eyeLeft_t'][0],
                             self.CustomTransform['EYELEFT_eyeLeft_t'][1],
                             self.CustomTransform['EYELEFT_eyeLeft_t'][2])
                cmds.setAttr(self.EYELEFT + '.rotate',
                             self.CustomTransform['EYELEFT_eyeLeft_r'][0],
                             self.CustomTransform['EYELEFT_eyeLeft_r'][1],
                             self.CustomTransform['EYELEFT_eyeLeft_r'][2])
            if 'EYERIGHT_eyeLeft_t' in self.CustomTransform:
                cmds.setAttr(self.EYERIGHT + '.translate',
                             self.CustomTransform['EYERIGHT_eyeLeft_t'][0],
                             self.CustomTransform['EYERIGHT_eyeLeft_t'][1],
                             self.CustomTransform['EYERIGHT_eyeLeft_t'][2])
                cmds.setAttr(self.EYERIGHT + '.rotate',
                             self.CustomTransform['EYERIGHT_eyeLeft_r'][0],
                             self.CustomTransform['EYERIGHT_eyeLeft_r'][1],
                             self.CustomTransform['EYERIGHT_eyeLeft_r'][2])



    def eyeLeftSave(self):
        if self.EYELEFT:
            self.CustomTransform['EYELEFT_eyeLeft_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_eyeLeft_r'] = self.getRotation(self.EYELEFT)
        if self.EYERIGHT:
            self.CustomTransform['EYERIGHT_eyeLeft_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_eyeLeft_r'] = self.getRotation(self.EYERIGHT)
            self.ui.pushButton_eyeLeftSave.setStyleSheet(self.ColorComplete)

    #Right
    def calc_eyeRight(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.eyeLookInLeft', 1)
            cmds.setAttr(bsNodeName + '.eyeLookOutRight', 1)
            if 'EYELEFT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
                self.CustomTransform['EYELEFT_Original_r'] = self.getRotate(self.EYELEFT)
            if 'EYERIGHT_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
                self.CustomTransform['EYERIGHT_Original_r'] = self.getRotate(self.EYERIGHT)
            if 'EYELEFT_eyeRight_t' in self.CustomTransform:
                cmds.setAttr(self.EYELEFT + '.translate',
                             self.CustomTransform['EYELEFT_eyeRight_t'][0],
                             self.CustomTransform['EYELEFT_eyeRight_t'][1],
                             self.CustomTransform['EYELEFT_eyeRight_t'][2])
                cmds.setAttr(self.EYELEFT + '.rotate',
                             self.CustomTransform['EYELEFT_eyeRight_r'][0],
                             self.CustomTransform['EYELEFT_eyeRight_r'][1],
                             self.CustomTransform['EYELEFT_eyeRight_r'][2])
            if 'EYERIGHT_eyeRight_t' in self.CustomTransform:
                cmds.setAttr(self.EYERIGHT + '.translate',
                             self.CustomTransform['EYERIGHT_eyeRight_t'][0],
                             self.CustomTransform['EYERIGHT_eyeRight_t'][1],
                             self.CustomTransform['EYERIGHT_eyeRight_t'][2])
                cmds.setAttr(self.EYERIGHT + '.rotate',
                             self.CustomTransform['EYERIGHT_eyeRight_r'][0],
                             self.CustomTransform['EYERIGHT_eyeRight_r'][1],
                             self.CustomTransform['EYERIGHT_eyeRight_r'][2])
    def eyeRightSave(self):
        if self.EYELEFT:
            self.CustomTransform['EYELEFT_eyeRight_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_eyeRight_r'] = self.getRotation(self.EYELEFT)
        if self.EYERIGHT:
            self.CustomTransform['EYERIGHT_eyeRight_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_eyeRight_r'] = self.getRotation(self.EYERIGHT)
            self.ui.pushButton_eyeRightSave.setStyleSheet(self.ColorComplete)

    # JawOpen
    def calc_jawOpen(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.jawOpen', 1)
            if 'TEETHBOTTOM_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
                self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
            if 'TEETHBOTTOM_jawOpen_t' in self.CustomTransform:
                cmds.setAttr(self.TEETHBOTTOM + '.translate',
                             self.CustomTransform['TEETHBOTTOM_jawOpen_t'][0],
                             self.CustomTransform['TEETHBOTTOM_jawOpen_t'][1],
                             self.CustomTransform['TEETHBOTTOM_jawOpen_t'][2])
                cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                             self.CustomTransform['TEETHBOTTOM_jawOpen_r'][0],
                             self.CustomTransform['TEETHBOTTOM_jawOpen_r'][1],
                             self.CustomTransform['TEETHBOTTOM_jawOpen_r'][2])

    def jawOpenSave(self):
        print ('jawOpen Save')
        if self.TEETHBOTTOM:
            self.CustomTransform['TEETHBOTTOM_jawOpen_t'] = self.getTranslate(self.TEETHBOTTOM)
            self.CustomTransform['TEETHBOTTOM_jawOpen_r'] = self.getRotation(self.TEETHBOTTOM)
            self.ui.pushButton_jawOpenSave.setStyleSheet(self.ColorComplete)

    # JawForward
    def calc_jawForward(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.jawForward', 1)
            if 'TEETHBOTTOM_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
                self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
            if 'TEETHBOTTOM_jawForward_t' in self.CustomTransform:
                cmds.setAttr(self.TEETHBOTTOM + '.translate',
                             self.CustomTransform['TEETHBOTTOM_jawForward_t'][0],
                             self.CustomTransform['TEETHBOTTOM_jawForward_t'][1],
                             self.CustomTransform['TEETHBOTTOM_jawForward_t'][2])
                cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                             self.CustomTransform['TEETHBOTTOM_jawForward_r'][0],
                             self.CustomTransform['TEETHBOTTOM_jawForward_r'][1],
                             self.CustomTransform['TEETHBOTTOM_jawForward_r'][2])

    def jawForwardSave(self):
        if self.TEETHBOTTOM:
            self.CustomTransform['TEETHBOTTOM_jawForward_t'] = self.getTranslate(self.TEETHBOTTOM)
            self.CustomTransform['TEETHBOTTOM_jawForward_r'] = self.getRotation(self.TEETHBOTTOM)
            self.ui.pushButton_jawForwardSave.setStyleSheet(self.ColorComplete)

    # jawLeft
    def calc_jawLeft(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.jawLeft', 1)
            if 'TEETHBOTTOM_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
                self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
            if 'TEETHBOTTOM_jawLeft_t' in self.CustomTransform:
                cmds.setAttr(self.TEETHBOTTOM + '.translate',
                             self.CustomTransform['TEETHBOTTOM_jawLeft_t'][0],
                             self.CustomTransform['TEETHBOTTOM_jawLeft_t'][1],
                             self.CustomTransform['TEETHBOTTOM_jawLeft_t'][2])
                cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                             self.CustomTransform['TEETHBOTTOM_jawLeft_r'][0],
                             self.CustomTransform['TEETHBOTTOM_jawLeft_r'][1],
                             self.CustomTransform['TEETHBOTTOM_jawLeft_r'][2])


    def jawLeftSave(self):
        if self.TEETHBOTTOM:
            self.CustomTransform['TEETHBOTTOM_jawLeft_t'] = self.getTranslate(self.TEETHBOTTOM)
            self.CustomTransform['TEETHBOTTOM_jawLeft_r'] = self.getRotation(self.TEETHBOTTOM)
            self.ui.pushButton_jawLeftSave.setStyleSheet(self.ColorComplete)

    # jawRight
    def calc_jawRight(self):
        if self.BLENDSHAPEMESH:
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            self.reset_blendshape(bsNodeName)
            cmds.setAttr(bsNodeName + '.jawRight', 1)
            if 'TEETHBOTTOM_Original_t' in self.CustomTransform:
                self.allResetTransformExtraMesh()
            else:
                self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
                self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
            if 'TEETHBOTTOM_jawRight_t' in self.CustomTransform:
                cmds.setAttr(self.TEETHBOTTOM + '.translate',
                             self.CustomTransform['TEETHBOTTOM_jawRight_t'][0],
                             self.CustomTransform['TEETHBOTTOM_jawRight_t'][1],
                             self.CustomTransform['TEETHBOTTOM_jawRight_t'][2])
                cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                             self.CustomTransform['TEETHBOTTOM_jawRight_r'][0],
                             self.CustomTransform['TEETHBOTTOM_jawRight_r'][1],
                             self.CustomTransform['TEETHBOTTOM_jawRight_r'][2])
    def jawRightSave(self):
        if self.TEETHBOTTOM:
            self.CustomTransform['TEETHBOTTOM_jawRight_t'] = self.getTranslate(self.TEETHBOTTOM)
            self.CustomTransform['TEETHBOTTOM_jawRight_r'] = self.getRotation(self.TEETHBOTTOM)
            self.ui.pushButton_jawRightSave.setStyleSheet(self.ColorComplete)

    def getTranslate(self, mesh):
        return [cmds.getAttr(mesh + '.tx'),cmds.getAttr(mesh + '.ty'),cmds.getAttr(mesh + '.tz')]
    def getRotation(self, mesh):
        return [cmds.getAttr(mesh + '.rx'),cmds.getAttr(mesh + '.ry'),cmds.getAttr(mesh + '.rz')]

    def setTranslate(self, meshName='', dic_key=''):
        pass


    def setRotate(self, mesh, dic_key):
        pass




    def add_bsmesh(self):
        sel = cmds.ls(sl=1)
        if sel:
            self.BLENDSHAPEMESH = sel[0]
            self.ui.label_blendshapemesh.setText(sel[0])
            # initialize
            meshHistory = cmds.listHistory(self.BLENDSHAPEMESH)
            self.ui.spinBox_bs_index.setValue(0)
            self.BlendNodeIndex = 0
            try:
                bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
                self.ui.label_bsNode.setText(bsNodeName)
            except:
                self.ui.label_bsNode.setText('None')
            self.ui.pushButton_add_bsmesh.setStyleSheet(self.ColorComplete)
        else:
            self.BLENDSHAPEMESH = ''
            self.ui.label_blendshapemesh.setText('None')
            self.ui.spinBox_bs_index.setValue(0)
            self.BlendNodeIndex = 0
            self.ui.label_bsNode.setText('None')
            self.ui.pushButton_add_bsmesh.setStyleSheet(self.ColorDefault)

    def add_wrapmesh(self):
        sel = cmds.ls(sl=1)
        if sel:
            self.WRAPEDMESH = sel[0]
            self.ui.label_wrapmesh.setText(sel[0])
            self.ui.pushButton_add_WrapMesh.setStyleSheet(self.ColorComplete)
        else:
            self.WRAPEDMESH = ''
            self.ui.label_wrapmesh.setText('None')
            self.ui.pushButton_add_WrapMesh.setStyleSheet(self.ColorDefault)

    def add_jawmesh(self):
        sel = cmds.ls(sl=1)
        if sel:
            self.TEETHBOTTOM = sel[0]
            self.ui.label_jawmesh.setText(sel[0])
            self.ui.pushButton_add_jaw_mesh.setStyleSheet(self.ColorComplete)
            self.CustomTransform['TEETHBOTTOM_Original_t'] = self.getTranslate(self.TEETHBOTTOM)
            self.CustomTransform['TEETHBOTTOM_Original_r'] = self.getRotation(self.TEETHBOTTOM)
        else:
            self.TEETHBOTTOM = ''
            self.ui.label_jawmesh.setText('None')
            self.ui.pushButton_add_jaw_mesh.setStyleSheet(self.ColorDefault)
            self.CustomTransform['TEETHBOTTOM_Original_t'] = []
            self.CustomTransform['TEETHBOTTOM_Original_r'] = []

    def add_eyeLmesh(self):
        sel = cmds.ls(sl=1)
        if sel:
            self.EYELEFT = sel[0]
            self.ui.label_eyeLmesh.setText(sel[0])
            self.ui.pushButton_add_eyeL_mesh.setStyleSheet(self.ColorComplete)
            self.CustomTransform['EYELEFT_Original_t'] = self.getTranslate(self.EYELEFT)
            self.CustomTransform['EYELEFT_Original_r'] = self.getRotation(self.EYELEFT)
        else:
            self.EYELEFT = ''
            self.ui.label_eyeLmesh.setText('None')
            self.ui.pushButton_add_eyeL_mesh.setStyleSheet(self.ColorDefault)
            self.CustomTransform['EYELEFT_Original_t'] = []
            self.CustomTransform['EYELEFT_Original_r'] = []

    def add_eyeRmesh(self):
        sel = cmds.ls(sl=1)
        if sel:
            self.EYERIGHT = sel[0]
            self.ui.label_eyeRmesh.setText(sel[0])
            self.ui.pushButton_add_eyeR_mesh.setStyleSheet(self.ColorComplete)
            self.CustomTransform['EYERIGHT_Original_t'] = self.getTranslate(self.EYERIGHT)
            self.CustomTransform['EYERIGHT_Original_r'] = self.getRotation(self.EYERIGHT)
        else:
            self.EYERIGHT = ''
            self.ui.label_eyeRmesh.setText('None')
            self.ui.pushButton_add_eyeR_mesh.setStyleSheet(self.ColorDefault)
            self.CustomTransform['EYERIGHT_Original_t'] = []
            self.CustomTransform['EYERIGHT_Original_r'] = []

    ## add blend shape
    def add_blendshape_data(self):
        # import maya file
        file_path = self.BS_Data
        cmds.file(file_path, i=True, ignoreVersion=True)

    def reset_blendshape(self, bsNodeName):
        for bs in self.JBConrolRig.BSList:
            cmds.setAttr(bsNodeName + '.' + bs, 0)

    ## Result #############################
    #######################################
    def bs_copy(self):
        baseMesh = self.BLENDSHAPEMESH
        if self.WRAPEDMESH == '':
            wrapedMesh = self.BLENDSHAPEMESH
        else:
            wrapedMesh = self.WRAPEDMESH

        extractedBS = []
        meshHistory = cmds.listHistory(baseMesh)
        bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]

        bsNameList = cmds.listAttr(bsNodeName + '.w', m=True)

        # JBConrolRig.BSList 기반 블랜드세입들만 0으로, 눈이나 턱 위치값 원위치
        self.allResetBS()

        ########################### 베이스 메쉬 만들기 #########################
        dupList = []
            # ICT_Base의 복사본 생성
        dup = cmds.duplicate(wrapedMesh)
        redup = cmds.rename(dup, baseMesh + '_dup')
        dupList.append(redup)
            # 눈, 눈썹, 치아, 혀, 눈물, AO등도 복사본 생성
        otherMeshes = self.EXTRAMESH
        for mesh in otherMeshes:
            dup = cmds.duplicate(mesh)
            redup = cmds.rename(dup,mesh+'_dup')
            dupList.append(redup)

            # 기본 표정의 복사본들을 모두 하나의 메쉬로 만듬
        cmds.select(dupList)
        resultBaseMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            # 최종 결과물의 베이스 메쉬
        resultBaseMesh = cmds.rename(resultBaseMesh, 'resultBaseMesh')
        #######################################################################


        ############################## 블렌드쉐입 추출 하기 #############################
        for bs in self.JBConrolRig.BSList:
            if bs == 'jawOpen':
                if 'TEETHBOTTOM_jawOpen_t' in self.CustomTransform:
                    cmds.setAttr(self.TEETHBOTTOM + '.translate',
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_t'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_t'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_t'][2])
                    cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_r'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_r'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawOpen_r'][2])

            elif bs == 'jawRight':
                if 'TEETHBOTTOM_jawRight_t' in self.CustomTransform:
                    cmds.setAttr(self.TEETHBOTTOM + '.translate',
                                 self.CustomTransform['TEETHBOTTOM_jawRight_t'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawRight_t'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawRight_t'][2])
                    cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                                 self.CustomTransform['TEETHBOTTOM_jawRight_r'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawRight_r'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawRight_r'][2])
            elif bs == 'jawLeft':
                if 'TEETHBOTTOM_jawLeft_t' in self.CustomTransform:
                    cmds.setAttr(self.TEETHBOTTOM + '.translate',
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_t'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_t'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_t'][2])
                    cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_r'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_r'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawLeft_r'][2])

            elif bs == 'jawForward':
                if 'TEETHBOTTOM_jawForward_t' in self.CustomTransform:
                    cmds.setAttr(self.TEETHBOTTOM + '.translate',
                                 self.CustomTransform['TEETHBOTTOM_jawForward_t'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawForward_t'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawForward_t'][2])
                    cmds.setAttr(self.TEETHBOTTOM + '.rotate',
                                 self.CustomTransform['TEETHBOTTOM_jawForward_r'][0],
                                 self.CustomTransform['TEETHBOTTOM_jawForward_r'][1],
                                 self.CustomTransform['TEETHBOTTOM_jawForward_r'][2])

            elif bs == 'eyeLookDownLeft':
                if 'EYELEFT_eyeDown_t' in self.CustomTransform:
                    cmds.setAttr(self.EYELEFT + '.translate',
                                 self.CustomTransform['EYELEFT_eyeDown_t'][0],
                                 self.CustomTransform['EYELEFT_eyeDown_t'][1],
                                 self.CustomTransform['EYELEFT_eyeDown_t'][2])
                    cmds.setAttr(self.EYELEFT + '.rotate',
                                 self.CustomTransform['EYELEFT_eyeDown_r'][0],
                                 self.CustomTransform['EYELEFT_eyeDown_r'][1],
                                 self.CustomTransform['EYELEFT_eyeDown_r'][2])

            elif bs == 'eyeLookDownRight':
                if 'EYERIGHT_eyeDown_t' in self.CustomTransform:
                    cmds.setAttr(self.EYERIGHT + '.translate',
                                 self.CustomTransform['EYERIGHT_eyeDown_t'][0],
                                 self.CustomTransform['EYERIGHT_eyeDown_t'][1],
                                 self.CustomTransform['EYERIGHT_eyeDown_t'][2])
                    cmds.setAttr(self.EYERIGHT + '.rotate',
                                 self.CustomTransform['EYERIGHT_eyeDown_r'][0],
                                 self.CustomTransform['EYERIGHT_eyeDown_r'][1],
                                 self.CustomTransform['EYERIGHT_eyeDown_r'][2])

            elif bs == 'eyeLookInLeft':
                if 'EYELEFT_eyeRight_t' in self.CustomTransform:
                    cmds.setAttr(self.EYELEFT + '.translate',
                                 self.CustomTransform['EYELEFT_eyeRight_t'][0],
                                 self.CustomTransform['EYELEFT_eyeRight_t'][1],
                                 self.CustomTransform['EYELEFT_eyeRight_t'][2])
                    cmds.setAttr(self.EYELEFT + '.rotate',
                                 self.CustomTransform['EYELEFT_eyeRight_r'][0],
                                 self.CustomTransform['EYELEFT_eyeRight_r'][1],
                                 self.CustomTransform['EYELEFT_eyeRight_r'][2])

            elif bs == 'eyeLookInRight':
                if 'EYERIGHT_eyeLeft_t' in self.CustomTransform:
                    cmds.setAttr(self.EYERIGHT + '.translate',
                                 self.CustomTransform['EYERIGHT_eyeLeft_t'][0],
                                 self.CustomTransform['EYERIGHT_eyeLeft_t'][1],
                                 self.CustomTransform['EYERIGHT_eyeLeft_t'][2])
                    cmds.setAttr(self.EYERIGHT + '.rotate',
                                 self.CustomTransform['EYERIGHT_eyeLeft_r'][0],
                                 self.CustomTransform['EYERIGHT_eyeLeft_r'][1],
                                 self.CustomTransform['EYERIGHT_eyeLeft_r'][2])

            elif bs == 'eyeLookOutLeft':
                if 'EYELEFT_eyeLeft_t' in self.CustomTransform:
                    cmds.setAttr(self.EYELEFT + '.translate',
                                 self.CustomTransform['EYELEFT_eyeLeft_t'][0],
                                 self.CustomTransform['EYELEFT_eyeLeft_t'][1],
                                 self.CustomTransform['EYELEFT_eyeLeft_t'][2])
                    cmds.setAttr(self.EYELEFT + '.rotate',
                                 self.CustomTransform['EYELEFT_eyeLeft_r'][0],
                                 self.CustomTransform['EYELEFT_eyeLeft_r'][1],
                                 self.CustomTransform['EYELEFT_eyeLeft_r'][2])

            elif bs == 'eyeLookOutRight':
                if 'EYERIGHT_eyeRight_t' in self.CustomTransform:
                    cmds.setAttr(self.EYERIGHT + '.translate',
                                 self.CustomTransform['EYERIGHT_eyeRight_t'][0],
                                 self.CustomTransform['EYERIGHT_eyeRight_t'][1],
                                 self.CustomTransform['EYERIGHT_eyeRight_t'][2])
                    cmds.setAttr(self.EYERIGHT + '.rotate',
                                 self.CustomTransform['EYERIGHT_eyeRight_r'][0],
                                 self.CustomTransform['EYERIGHT_eyeRight_r'][1],
                                 self.CustomTransform['EYERIGHT_eyeRight_r'][2])

            elif bs == 'eyeLookUpLeft':
                if 'EYELEFT_eyeUp_t' in self.CustomTransform:
                    cmds.setAttr(self.EYELEFT + '.translate',
                                 self.CustomTransform['EYELEFT_eyeUp_t'][0],
                                 self.CustomTransform['EYELEFT_eyeUp_t'][1],
                                 self.CustomTransform['EYELEFT_eyeUp_t'][2])
                    cmds.setAttr(self.EYELEFT + '.rotate',
                                 self.CustomTransform['EYELEFT_eyeUp_r'][0],
                                 self.CustomTransform['EYELEFT_eyeUp_r'][1],
                                 self.CustomTransform['EYELEFT_eyeUp_r'][2])

            elif bs == 'eyeLookUpRight':
                if 'EYERIGHT_eyeUp_t' in self.CustomTransform:
                    cmds.setAttr(self.EYERIGHT + '.translate',
                                 self.CustomTransform['EYERIGHT_eyeUp_t'][0],
                                 self.CustomTransform['EYERIGHT_eyeUp_t'][1],
                                 self.CustomTransform['EYERIGHT_eyeUp_t'][2])
                    cmds.setAttr(self.EYERIGHT + '.rotate',
                                 self.CustomTransform['EYERIGHT_eyeUp_r'][0],
                                 self.CustomTransform['EYERIGHT_eyeUp_r'][1],
                                 self.CustomTransform['EYERIGHT_eyeUp_r'][2])
            elif bs == 'eyeBlinkRight':
                if 'EYERIGHT_eyeClose_t' in self.CustomTransform:
                    cmds.setAttr(self.EYERIGHT + '.translate',
                                 self.CustomTransform['EYERIGHT_eyeClose_t'][0],
                                 self.CustomTransform['EYERIGHT_eyeClose_t'][1],
                                 self.CustomTransform['EYERIGHT_eyeClose_t'][2])
                    cmds.setAttr(self.EYERIGHT + '.rotate',
                                 self.CustomTransform['EYERIGHT_eyeClose_r'][0],
                                 self.CustomTransform['EYERIGHT_eyeClose_r'][1],
                                 self.CustomTransform['EYERIGHT_eyeClose_r'][2])
            elif bs == 'eyeBlinkLeft':
                if 'EYELEFT_eyeClose_t' in self.CustomTransform:
                    cmds.setAttr(self.EYELEFT + '.translate',
                                 self.CustomTransform['EYELEFT_eyeClose_t'][0],
                                 self.CustomTransform['EYELEFT_eyeClose_t'][1],
                                 self.CustomTransform['EYELEFT_eyeClose_t'][2])
                    cmds.setAttr(self.EYELEFT + '.rotate',
                                 self.CustomTransform['EYELEFT_eyeClose_r'][0],
                                 self.CustomTransform['EYELEFT_eyeClose_r'][1],
                                 self.CustomTransform['EYELEFT_eyeClose_r'][2])

            ######################### Modify Custom Value ##########################
            # if 'eyeBlink' in bsNodeName:
            #     cmds.setAttr(bsNodeName + '.' + bs, 0.76)
            # else:

            cmds.setAttr(bsNodeName + '.' + bs, 1)

            # 얼굴 복사
            dupList = []
            dup = cmds.duplicate(wrapedMesh)
            redup = cmds.rename(dup, baseMesh + '_dup')
            dupList.append(redup)
            # 눈, 눈썹, 치아, AO, 혀 등등 복사
            for mesh in otherMeshes:
                dup = cmds.duplicate(mesh)
                redup = cmds.rename(dup, mesh + '_dup')
                dupList.append(redup)
            # 얼굴과 눈, 눈썹등등을 하나로 만들기
            cmds.select(dupList)
            resultBSMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            resultBSMesh = cmds.rename(resultBSMesh, bs)
            cmds.setAttr(bsNodeName + '.' + bs, 0)
            extractedBS.append(resultBSMesh)


            # 원래 위치로 복원
            self.allResetBS()

    ################################################################################

    ##################### 최종메쉬에 BlendShape 추가하기 ###############################

        cmds.blendShape(extractedBS, resultBaseMesh, tc=False)


    def autoControlRig(self):
        # 기존에 이미 리그오브젝트가 있다면 실행하지마
        # BS_node 로 이름을 변경해야함
        if cmds.objExists('Face_Controllers_Root'):
            print u'이미 JBControlRig 가 있습니다.'
            return
        # Blendshape 오브젝트가 하나라도 있어야지 실행되
        if len(cmds.ls(type='blendShape')) > 0:
            ## Auto Rig Load
            sel = cmds.ls(sl=1)[0]
            meshHistory = cmds.listHistory(sel)
            bsNodeName = cmds.ls(meshHistory, type='blendShape')[self.BlendNodeIndex]
            JBCControlRig = JBC.ControlRig_V1(bsNodeName)
            controlrigFile = os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace(getsourcefile(lambda: 0).split('/')[-1], '/JBControlRig/'+JBCControlRig.ControlRigMayaFileName)
            print 'log: '+controlrigFile
            cmds.file(controlrigFile, i=True, ignoreVersion=True)

            for bs, ctrl in zip(JBCControlRig.ConnectInfo_BS, JBCControlRig.ConnectInfo_Ctrl):
                cmds.connectAttr(ctrl, bs)
                print bs, ctrl

    def resetSlider(self):
        for slider in self.JBConrolRig.JBController:
            if cmds.objExists(slider):
                extra_attr = cmds.listAttr(slider, ud=True)
                try:
                    cmds.setAttr(slider + ".tx", 0)
                except:
                    pass

                try:
                    cmds.setAttr(slider + ".ty", 0)
                except:
                    pass
                try:
                    cmds.setAttr(slider + ".tz", 0)
                except:
                    pass
                if extra_attr:
                    for attr in extra_attr:
                        try:
                            cmds.setAttr(slider + "." + attr, 0)
                        except:
                            pass

    # UTILITY
    def setTranslate(self, _sel, _trans):
        count = 0

        if len(_trans) != 3:
            print _trans, '3 values'
            return


        if not isinstance(_sel, list):
            cmds.setAttr(_sel + '.tx', _trans[0])
            cmds.setAttr(_sel + '.ty', _trans[1])
            cmds.setAttr(_sel + '.tz', _trans[2])
            return 'Moved: 1'

        else:
            for i in _sel:
                cmds.setAttr(i + '.tx', _trans[0])
                cmds.setAttr(i + '.ty', _trans[1])
                cmds.setAttr(i + '.tz', _trans[2])
                count += 1
            return 'Moved: ' + str(count)

    def objExport(self):
        '''
        '''
        # 오브젝트 선택 되어 있는지 체크
        sel = cmds.ls(sl=1)
        # maya 파일이 있는 같은 폴더 위치에 생성
        filename = cmds.file(q=True, sn=True).split('/')[-1]
        path = cmds.file(q=True, sn=True).replace(filename,'')

        if not sel:
            print u'익스포트 실패: 선택한 오브젝트가 없습니다'
            return

        # mesh 이름으로 생성됨
        for obj in sel:
            cmds.select(clear=1)
            path_result = os.path.join(path, obj + '.obj')
            cmds.select(obj)
            cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                      op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
            print(obj + ' Exported')

    def CreateJointToVertex(center='', fromCenter=False, step=1):
        """ creates joints based on vertices positions or curve.cvs """
        vtx = cmds.ls(sl=1, fl=1)
        # is selection curve?
        jnt = []
        n = 0
        newVtxList = []
        # loop rebuilds vtx list, encase of high topo
        for i in range(0, len(vtx), step):
            newVtxList.append(vtx[i])

        # get vtx pos, set jnt to pos

        for v in vtx:
            cmds.select(cl=1)
            jnt.append(cmds.joint(n='joint_Vertex'))

            # 버텍스의 위치를 가져와서
            # pos = cmds.xform(v, q=1, ws=1, t=1)
            pos = cmds.pointPosition(v)
            # 조인트의 위치를 변경한다
            cmds.xform(jnt[n], ws=1, t=pos)

            cmds.select(v)
            cmds.select(jnt[n], add=True)
            #cmds.setAttr('%s.radius' % (jnt[n]), .1)
            #######self.follicle_mesh(jnt[n], v.split('.')[0])
            mel.eval('pointOnPolyConstraint -offset 0 0 0  -weight 1;')
            # currently has to use PYMEL implentation as python cmds does not work 'because maya'
            #pm.runtime.PointOnPolyConstraint(v, jnt[n])

            if fromCenter:
                posC = cmds.xform(center, q=1, ws=1, t=1)
                cmds.select(cl=1)
                jntC = cmds.joint()
                cmds.xform(jntC, ws=1, t=posC)
                cmds.parent(jnt[n], jntC)
                cmds.joint(jntC, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
            n = n + 1
        return jnt

    def add_extramesh(self):
        items = cmds.ls(sl=1)
        for item in items:
            # 히스토리 지우기
            # cmds.delete(item, constructionHistory=True)
            # 리스트위젯에 추가
            if item not in self.EXTRAMESH:
                self.ui.listWidget.addItem(item)
                self.EXTRAMESH.append(item)
                self.ui.pushButton_addExtraMesh.setStyleSheet(self.ColorComplete)

    def clear_extramesh(self):
        self.ui.listWidget.clear()
        self.EXTRAMESH = []
        self.ui.pushButton_addExtraMesh.setStyleSheet(self.ColorDefault)

    def rename_UVs(self):
        meshes = cmds.ls(sl=1)

        for mesh in meshes:
            # all UVs
            uvset = cmds.polyUVSet(mesh, q=True, allUVSets=True)
            if len(uvset) > 1:
                for i in range(1, len(uvset)):
                    # delete
                    cmds.polyUVSet(mesh, uvSet=uvset[i], delete=1)
            try:
                cmds.polyUVSet(rename=True, newUVSet='map1')
            except:
                pass


if __name__ == "__main__":
    try:
        JBCWindow.close()
        JBCWindow.deleteLater()
    except:
        pass

    JBCWindow = DesignerUI()
    JBCWindow.show()
