# -*- coding: UTF-8 -*-
import os
import shelve
from inspect import getsourcefile
from os.path import abspath
import maya.OpenMaya as om
#import pymel.core as pm
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon
from shiboken2 import wrapInstance
#import json
import maya.mel as mel
import time
import random
import sys


import IMTool.IMUtility as imu
reload(imu)


# if (cmds.window("Rig_Manager_wnd", exists=True)):
#     from Snappers.rig_manager import snappers_rig_manager
#     # snappers_rig_manager.showRigManagerWindow()
# else:
#     if cmds.objExists('Head_geo'):
#         from Snappers.rig_manager import snappers_rig_manager
#         snappers_rig_manager.showRigManagerWindow()
from Snappers.rig_manager import snappers_rig_manager

from IMTool.IMUtility import BlendShapeList
reload(BlendShapeList)
from IMTool.IMUtility.BlendShapeList import *

# 개발용
if imu.isShiftModifier():
    from IMTool.IMUtility import IMFile
    from IMTool.IMUtility import IMUtils
    from IMTool.IMUtility import IMExport
    from IMTool.IMUtility import IMMaya
    from IMTool.IMUtility import IMViewport
    from IMTool.IMUtility import BlendShapeList
    reload(IMFile)
    reload(IMUtils)
    reload(IMExport)
    reload(IMMaya)
    reload(IMViewport)
    reload(BlendShapeList)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr

class DesignerUI(QtWidgets.QDialog):
    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;FBX (*.fbx);;All Files (*.*)"
    selected_filter = "Maya (*ma *.mb)"
    # IMTool에서 사용하는 아이콘 폴더 경로
    ICON_PATH = os.path.join(imu.getPath_scriptRoot(), 'images')

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

    #블랜드쉐입 추출
    BlendshapeMesh =''
    BlendshapeNode = ''
    AddMesh = ''
    isBlendshapeNewObject = False
    ExtractedBlendshapes = []
    ReadyColor = "background-color:rgb(171, 29, 90)"
    CompleteColor = "background-color:rgb(20, 117, 49)"

    #Snappers
    SNAPPERS_SLIDER_SHOW = True
    SNAPPERS_SLIDER_ACTIVE = False
    SNAPPERS_ADJUST_ACTIVE = False
    CntrAttrMap = []
    SNAPPERS_POSE_DIC = {}
    SNAPPERS_POSE_CUSTOM_DIC = {}
    LAST_BLENDSHAPE_INDEX = 0
    CustomBlendshapeList = []
    is_head = False
    is_eyebrow = False
    is_eyelash = False
    is_eye_AO = False

    # 나중에 눈썹, 입 등등 되도록
    SNAPPERS_HEAD = 'Head_geo'
    SNAPPERS_BlendshapeNode = 'Head_blendShape'
    SNAPPERS_NEWMESH = None
    isKeyingPoseAsset = False
    isMakingBlendshapes = False

    #Pose Set
    SNAPPERS_POSESET_LASTINDEX = 0
    SNAPPERS_EXTRACTMESH_LIST = ['Head_geo','Eyes','Teeth','Extract_eyelash','Extract_eye_AO','Extract_eyebrow']


    FaceTexturePath = 'D:/Perforce2/Art/TA/RND/P3_NPC_Sources/Texture_Head'

    # ICT_Random
    faceTextures = [
        FaceTexturePath + '/Wraped_Male01_color.jpg',
        FaceTexturePath + '/Wraped_Male02_color.jpg',
        FaceTexturePath + '/Wraped_Male03_color.jpg',
        FaceTexturePath + '/Wraped_Male04_color.jpg',
        FaceTexturePath + '/Wraped_Male05_color.jpg',
        FaceTexturePath + '/Wraped_Male06_color.jpg',
        FaceTexturePath + '/Wraped_Male07_color.jpg',
        FaceTexturePath + '/Wraped_Male08_color.jpg',
        FaceTexturePath + '/Wraped_Male011_color.jpg',
        FaceTexturePath + '/Wraped_Male012_color.jpg',

        FaceTexturePath + '/Wraped_Female_01_color.jpg',
        FaceTexturePath + '/Wraped_Female_02_color.jpg',
        FaceTexturePath + '/Wraped_Female_03_color.jpg',
        FaceTexturePath + '/Wraped_Female_04_color.jpg',
        FaceTexturePath + '/Wraped_Female_05_color.jpg',
        FaceTexturePath + '/Wraped_Female_06_color.jpg',
        FaceTexturePath + '/Wraped_Female_011_color.jpg',
        FaceTexturePath + '/Wraped_Female_012_color.jpg'

    ]
    ICT_SELECTED_ITEM = ''


    # --------------------------------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------------------------------
    def __init__(self, ui_path=None, title_name='IM Blendshape Maker', parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        print 'Start IM Blendshape Maker'

        # 윈도우 설정
        self.setWindowTitle(title_name)
        self.setMinimumSize(635, 735)
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
        self.load_info()
        self.Load_WindowOption()
        # if os.path.exists(os.path.join(imu.getPath_IMTool(), abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.pose'))):
        #     self.poseLoad_Snappers() # 스내퍼용으로 저장된 pose 파일 불러오기
        self.setTreeView()
        self.set_ListView_Blendshapes() # Snappers 블랜드쉐입 리스트 셋업
        self.init_Snappers_Weights() # eye, ao, brow 웨이트 조절을 위한 초기화

        # Snappers  CntrAttrMap 리스트 셋업
        # self.createMap()
        self.CntrAttrMap = CntrAttrMap_list

        self.create_layout() # 배치및 컬러 적용
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
                f = QtCore.QFile(abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui'))
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
        dirIcon = os.path.join(self.ICON_PATH, "File0338.png")
        self.ui.pb_newfolder.setIcon(QIcon(dirIcon))
        self.ui.pb_delfolder.setIcon(QIcon(dirIcon))

        # 블렌드쉐입 추출
        self.ui.pb_addBlendshape.setStyleSheet(self.ReadyColor)
        self.ui.pb_addObject.setStyleSheet(self.ReadyColor)
        self.ui.pb_addNewObjectToBlendshape.setEnabled(False)
        #self.ui.Slider_addObjectWeight.setEnabled(False)
        # self.ui.pb_selectBlendshapes.setEnabled(False)

    # ------------------------------------------------------------------------------------------
    # Connect Methods
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        #CopyMode : 블랜드쉐입 추출
        self.ui.pb_alignObject.clicked.connect(self.alignObjects)
        self.ui.pb_unlock.clicked.connect(self.unlockTransform)
        self.ui.pb_lock.clicked.connect(self.lockTransform)
        self.ui.pb_unbind.clicked.connect(self.unBindSkin)
        self.ui.pb_unbind2.clicked.connect(self.unBindSkin) # 똑같은 기능
        self.ui.pb_bind.clicked.connect(self.bindSkin)
        self.ui.pb_bind2.clicked.connect(self.bindSkin) # 똑같은 기능
        self.ui.pb_matchtransform.clicked.connect(self.matchTransformAll)
        self.ui.pb_matchtransform2.clicked.connect(self.matchTransformAll) # 똑같은 기능
        self.ui.pb_resetbindpose.clicked.connect(self.resetBindPose)
        self.ui.pb_addObject.clicked.connect(self.registNewObject)
        self.ui.pb_addBlendshape.clicked.connect(self.registBlendshapeObject)
        self.ui.pb_addNewObjectToBlendshape.clicked.connect(self.addNewObjectToBlendshape)
        self.ui.pb_addNewObjectToBlendshapeIndex.clicked.connect(self.addNewObjectToBlendshapeIndex)
        self.ui.pb_removeNewObject.clicked.connect(self.removeNewObjectFromBlendshape)
        self.ui.pb_selectCurrentBSNode.clicked.connect(self.selectCurrentBSNode)
        self.ui.pb_copyBlendshapes.clicked.connect(self.copy_blendshapes)

        # 특정 Blendshape 지우기
        self.ui.pb_printBSList.clicked.connect(self.printBSList)
        self.ui.pb_delete_SelectedBS.clicked.connect(self.delete_SelectedBS)
        self.ui.pb_renameBlendshape.clicked.connect(self.rename_blendshape_target)

        # 추가했던 메쉬 추출하기
        #self.ui.pb_ExtractNewMesh.clicked.connect(self.ExtractNewMesh)

        self.ui.pb_jointToVertex.clicked.connect(self.CreateJointToVertex)
        self.ui.pb_resetBlendshapeWeight.clicked.connect(self.resetAllBlendshapeWeight)
        self.ui.pb_extractBlendshapes.clicked.connect(self.registedExtractBlendshapes)
        self.ui.pb_selectBlendshapes.clicked.connect(self.selectBlendshapes)
        self.ui.Slider_addObjectWeight.valueChanged.connect(self.addNewObjectWeight)
        self.ui.pb_makeBlendshape.clicked.connect(self.makeBlendshapes)
        self.ui.pb_counter.clicked.connect(self.selectCounter)



        self.ui.pb_clearScriptEditor.clicked.connect(self.clearScriptEditor)
        self.ui.pb_breakConnection.clicked.connect(self.breakConnections)
        self.ui.pb_importControlrigMayafile.clicked.connect(self.importControlrigMayafile)
        self.ui.pb_connectBsWithControl.clicked.connect(self.connectBsWithControl)
        self.ui.pb_resetSlider.clicked.connect(self.resetSlider)
        self.ui.pb_autoControlRig.clicked.connect(self.autoControlRig)

        self.ui.pb_printSelect.clicked.connect(self.printSelect)
        self.ui.pb_veiwBlendshapes.clicked.connect(self.veiwBlendshapes)
        self.ui.pb_viewControlrig.clicked.connect(self.viewControlrig)
        self.ui.pb_printBSConnectInfo2.clicked.connect(self.getBlendshapeConnects)
        self.ui.pb_AddBlendshapeToOrder.clicked.connect(self.AddBlendshapeToOrder)
        self.ui.pb_printNoneBSList.clicked.connect(self.printNoneBSList)

        # 작업폴더 오른버튼 옵션
        self.show_in_folder_action.triggered.connect(self.show_in_folder)
        self.make_in_folder_action.triggered.connect(self.make_in_folder)
        self.open_in_folder_action.triggered.connect(self.open_in_folder)
        self.import_in_folder_action.triggered.connect(self.import_in_folder)
        self.set_in_folder_action.triggered.connect(self.set_in_folder)
        self.create_in_folder_action.triggered.connect(self.create_in_folder)

        # 작업폴더 변경
        self.ui.cb_workfolder.currentIndexChanged.connect(self.changed_workfolder)

        # 마지막 익스포트 경로 콤보박스
        self.ui.cb_lastExportlist.currentIndexChanged.connect(self.changed_lastExportFolder)

        # export 폴더 선택하기
        self.ui.toolButton_export.clicked.connect(self.select_export_folder)

        # 작업폴더 콤보박스 리스트 지우기
        self.ui.pb_delfolder.clicked.connect(self.del_workfolder)

        # Export FBX / OBJ
        self.ui.pb_ExportFBX.clicked.connect(self.export_fbx)
        self.ui.pb_ExportOBJ.clicked.connect(self.export_obj)


        # Snappers
        self.ui.pb_Snappers_UIShow.clicked.connect(self.showHideSliders)
        self.ui.pb_Snappers_AdjustShow.clicked.connect(self.showAdjustment)
        self.ui.pb_Snappers_AdjustReset.clicked.connect(self.AdjustResetAll)
        self.ui.pb_Snappers_FacsReset.clicked.connect(self.FACSResetAll)

        self.ui.pb_Snappers_FACS_B.clicked.connect(self.selectFACSBrow)
        self.ui.pb_Snappers_FACS_E.clicked.connect(self.selectFACSEye)
        self.ui.pb_Snappers_FACS_M.clicked.connect(self.selectFACSMouse)
        self.ui.pb_Snappers_SelectAll.clicked.connect(self.selectAllSliders)
        self.ui.pb_Snappers_Adj_B.clicked.connect(self.selectAdjustBrow)
        self.ui.pb_Snappers_Adj_E.clicked.connect(self.selectAdjustEye)
        self.ui.pb_Snappers_Adj_M.clicked.connect(self.selectAdjustMouse)
        self.ui.pb_Snappers_AdjustSelectAll.clicked.connect(self.selectAdjustAllSliders)

        self.ui.pb_defaultPoseLoad.clicked.connect(self.Load_PoseSet_Default)
        self.ui.pb_selectedPoseLoad.clicked.connect(self.Load_PoseSet_Selected)
        self.ui.pb_poseSave.clicked.connect(self.Save_PoseSet_ToFile)
        self.ui.pb_snappersLoadKey.clicked.connect(self.Load_Pose_Key)
        self.ui.pb_snappersSetKey.clicked.connect(self.Save_Pose_Key)

        self.ui.pb_animationKey.clicked.connect(self.Set_KeyAnimation)
        self.ui.pb_animationKeyDel.clicked.connect(self.DeleteAll_KeyAnimation)
        #self.ui.pb_setRange.clicked.connect(self.setFrameRange)
        self.ui.pb_PoseAssetKey.clicked.connect(self.SetKeyForPoseAsset)

        # 자동등록
        self.ui.pb_createBSSet.clicked.connect(self.createBSSet)
        self.ui.pb_RegistNewFace.clicked.connect(self.RegistNewFace)
        self.ui.pb_RegistNewFace_All.clicked.connect(self.RegistNewFace_All)
        self.ui.pb_RegistNewFaceDelete.clicked.connect(self.RegistNewFaceDelete)
        self.ui.pb_RegistNewFaceDelete_All.clicked.connect(self.RegistNewFaceDelete_All)
        # self.ui.pb_update.clicked.connect(self.init_Snappers_Weights)
        self.ui.Slider_NewMeshWeight.valueChanged.connect(self.Snappers_addNewObjectWeight)

        self.ui.cb_selectionHorizontal.stateChanged.connect(self.selection_Horizontal)
        self.ui.cb_selectionVertical.stateChanged.connect(self.selection_Vertical)

        # Blendshape List
        self.ui.pb_addBlendshapeToList.clicked.connect(self.addBlendshapeToList)
        self.ui.pb_deleteBlendshapeToList.clicked.connect(self.deleteBlendshapeToList)
        self.ui.pb_printCurrentPoseAssetList.clicked.connect(self.printPoseAssetList)
        self.ui.pb_scriptEditor.clicked.connect(self.Popup_ScriptEditor)


        # blendshape
        # self.ui.listWidget_blendshape.itemClicked[QtCore.QModelIndex].connect(self.blendshape_clicked)
        #self.ui.listWidget_blendshape.itemClicked.connect(self.blendshape_clicked)
        self.ui.listWidget_blendshape.itemSelectionChanged.connect(self.blendshape_clicked)
        self.ui.pb_Snappers_ExtractBlendshape.clicked.connect(self.ExtractBlendshape)
        #self.ui.pb_Snappers_ExtractBlendshape_select.clicked.connect(self.ExtractBlendshape_Selected)
        self.ui.pb_editBlendshape.clicked.connect(self.editBlendshape)

        self.ui.pb_defaultImage.pressed.connect(self.viewDefaultImage)
        self.ui.pb_defaultImage.released.connect(self.viewOriginalImage)

        # 선택 눈, 치아
        self.ui.pb_selectRightEye.clicked.connect(self.selectRightEye)
        self.ui.pb_selectLeftEye.clicked.connect(self.selectLeftEye)
        self.ui.pb_selectTeeth.clicked.connect(self.selectTeeth)

        # Head Pose Settings File
        self.ui.pb_selectPosePath.clicked.connect(self.selectPosePath)
        self.ui.pb_PoseFileCreate.clicked.connect(self.CreatePoseFile)
        self.ui.cb_headList.currentIndexChanged.connect(self.select_PoseFile)

        # Extract Blendshapes for Snappers
        self.ui.cb_brow.stateChanged.connect(self.Show_Brow)
        self.ui.cb_eyelash.stateChanged.connect(self.Show_Eyelash)
        self.ui.cb_eyeAO.stateChanged.connect(self.Show_EyeAO)
        self.ui.cb_eyes.stateChanged.connect(self.Show_Eyes)
        self.ui.cb_teeth.stateChanged.connect(self.Show_Teeth)

        #ProgressBar를 위한 Timer 설정
        self.timerVar = QtCore.QTimer()
        self.timerVar.setInterval(2000)
        self.timerVar.timeout.connect(self.progressBarEndTimer)

        #기타 유틸스러운것들
        self.ui.pb_make_7885.clicked.connect(self.make_7885)
        self.ui.pb_make_7887.clicked.connect(self.make_7887)

        # ICT Random
        self.ui.pb_ICT_randomAll.clicked.connect(self.ICT_randomAll)
        self.ui.pb_ICT_random10.clicked.connect(self.ICT_random10)
        self.ui.pb_ICT_random20.clicked.connect(self.ICT_random20)
        self.ui.pb_ICT_random30.clicked.connect(self.ICT_random30)
        self.ui.pb_ICT_random40.clicked.connect(self.ICT_random40)
        self.ui.pb_ICT_random50.clicked.connect(self.ICT_random50)
        self.ui.pb_ICT_random60.clicked.connect(self.ICT_random60)
        self.ui.pb_ICT_random70.clicked.connect(self.ICT_random70)
        self.ui.pb_ICT_random80.clicked.connect(self.ICT_random80)
        self.ui.pb_ICT_random90.clicked.connect(self.ICT_random90)
        self.ui.pb_ICT_random99.clicked.connect(self.ICT_random99)
        self.ui.pb_ICT_randomMaterial.clicked.connect(self.ICT_randomMaterial)
        self.ui.pb_ICT_resetControlrig.clicked.connect(self.ICT_resetControlrig)
        self.ui.pb_ICT_resetIdentity.clicked.connect(self.ICT_resetIdentity)
        self.ui.pb_ICT_resetIdentity.clicked.connect(self.ICT_resetAllblendshape)

        self.ui.hSlider_identity00.valueChanged.connect(self.ICT_SliderSetValue0)
        self.ui.hSlider_identity01.valueChanged.connect(self.ICT_SliderSetValue1)
        self.ui.hSlider_identity02.valueChanged.connect(self.ICT_SliderSetValue2)
        self.ui.hSlider_identity03.valueChanged.connect(self.ICT_SliderSetValue3)
        self.ui.hSlider_identity04.valueChanged.connect(self.ICT_SliderSetValue4)
        self.ui.hSlider_identity05.valueChanged.connect(self.ICT_SliderSetValue5)
        self.ui.hSlider_identity06.valueChanged.connect(self.ICT_SliderSetValue6)
        self.ui.hSlider_identity07.valueChanged.connect(self.ICT_SliderSetValue7)
        self.ui.hSlider_identity08.valueChanged.connect(self.ICT_SliderSetValue8)
        self.ui.hSlider_identity09.valueChanged.connect(self.ICT_SliderSetValue9)

        # ICT Make Blendshape
        self.ui.pb_ICT_makeBlendshapeMesh.clicked.connect(self.ICT_makeBlendshapeMesh_JB)

        # Save/Load Identity
        self.ui.pb_ICT_identityPath.clicked.connect(self.ICT_identityPath)
        self.ui.pb_ICT_IdentitySave.clicked.connect(self.ICT_IdentitySave)
        self.ui.pb_ICT_IdentityModify.clicked.connect(self.ICT_IdentityModify)
        self.ui.pb_ICT_IdentityDelete.clicked.connect(self.ICT_IdentityDelete)
        self.ui.pb_ICT_selectRightEye.clicked.connect(self.ICT_selectRightEye)
        self.ui.pb_ICT_selectLeftEye.clicked.connect(self.ICT_selectLeftEye)
        self.ui.pb_ICT_selectTeeth.clicked.connect(self.ICT_selectTeeth)

        self.ui.listWidget_ICT_IdentityList.itemDoubleClicked.connect(self.ICT_handleDoubleClick)
        self.ui.listWidget_ICT_IdentityList.itemClicked.connect(self.ICT_handleClick)

    def ICT_selectRightEye(self):
        # sel = cmds.ls(sl=1)[0]
        # cmds.select(sel+'.f[23894:24691]')
        if imu.isShiftModifier():
            cmds.select(['ICT_R_eye_joint','ICT_L_eye_joint'])
        else:
            cmds.select('ICT_R_eye_joint')

    def ICT_selectLeftEye(self):
        # sel = cmds.ls(sl=1)[0]
        # cmds.select(sel + '.f[22296:23093]')
        if imu.isShiftModifier():
            cmds.select(['ICT_R_eye_joint','ICT_L_eye_joint'])
        else:
            cmds.select('ICT_L_eye_joint')

    def ICT_selectTeeth(self):
        cmds.select(['ICT_teeth_down_joint','ICT_teeth_up_joint'])

    def ICT_IdentityDelete(self):
        pass

    def createMaterialAssign(self):
        sel = cmds.ls(sl=1)[0]
        cmds.select(sel+'.f[0:14033]')
        shape = cmds.ls(sl=True, o=True)[0]
        print 'shape: ',shape
        faces = cmds.ls(sl=True)
        print 'faces: ',faces
        x = 0
        # assign shader
        sha = cmds.shadingNode('lambert', asShader=True, name="{}_{}_lambert".format(shape, x))
        sg = cmds.sets(empty=True, renderable=True, noSurfaceShader=True, name="{}_{}_sg".format(shape, x))
        cmds.connectAttr(sha + ".outColor", sg + ".surfaceShader", f=True)
        cmds.sets(faces, e=True, forceElement=sg)
        # get texture file name
        fileNode = cmds.shadingNode('file', name='fileTexture', asTexture=True)
        TextureFile = cmds.getAttr("M_Face2_C.fileTextureName")
        cmds.setAttr(fileNode+".fileTextureName", TextureFile, type="string")
        cmds.connectAttr('%s.outColor' %fileNode,'%s.color' %sha)
        cmds.setAttr('%s.ambientColor' %sha, 0.5, 0.5, 0.5)






    def ICT_setSlider(self, index=0, value=0):
        if index == 0:
            if not self.ui.cb_00.isChecked():
                self.ui.hSlider_identity00.setValue(value * 100)
        elif index == 1:
            if not self.ui.cb_01.isChecked():
                self.ui.hSlider_identity01.setValue(value * 100)
        elif index == 2:
            if not self.ui.cb_02.isChecked():
                self.ui.hSlider_identity02.setValue(value * 100)
        elif index == 3:
            if not self.ui.cb_03.isChecked():
                self.ui.hSlider_identity03.setValue(value * 100)
        elif index == 4:
            if not self.ui.cb_04.isChecked():
                self.ui.hSlider_identity04.setValue(value * 100)
        elif index == 5:
            if not self.ui.cb_05.isChecked():
                self.ui.hSlider_identity05.setValue(value * 100)
        elif index == 6:
            if not self.ui.cb_06.isChecked():
                self.ui.hSlider_identity06.setValue(value * 100)
        elif index == 7:
            if not self.ui.cb_07.isChecked():
                self.ui.hSlider_identity07.setValue(value * 100)
        elif index == 8:
            if not self.ui.cb_08.isChecked():
                self.ui.hSlider_identity08.setValue(value * 100)
        elif index == 9:
            if not self.ui.cb_09.isChecked():
                self.ui.hSlider_identity09.setValue(value * 100)
        else:
            pass

    def ICT_handleClick(self, item):
        self.ICT_SELECTED_ITEM = item.text()
        #self.ui.pb_ICT_IdentityModify.setText('Modify:   '+item.text())
        #self.ui.pb_ICT_IdentityDelete.setText('Delete:   '+item.text())

    # Load Identity
    def ICT_handleDoubleClick(self, item):
        name = item.text()

        identityValues = []
        TextureFile = ''

        filePath = imu.path_Cleanup(
            os.path.join(self.ui.lineEdit_ICT_IdentityPath.text(), name + '.identity'))
        if os.path.exists(filePath):
            try:
                d = shelve.open(filePath)

                # 눈, 치아 위치를 머리별로 불러오기
                try:
                    identityValues = d['IDENTITY_VALUES']
                    TextureFile = d['TEXTURE_NAME']
                    jointPositions = d['JOINT_POSITION']

                    mesh = 'BaseMesh_identity'
                    meshHistory = cmds.listHistory(mesh)
                    bsNode = cmds.ls(meshHistory, type='blendShape')[0]
                    bsName = cmds.listAttr(bsNode + '.w', m=True)
                    for index, bs in enumerate(bsName):
                        cmds.setAttr(bsNode + '.' + bs, identityValues[index])
                        if index >=0 and index <=9:
                            self.ICT_setSlider(index=index, value=identityValues[index])

                    # 메터리얼 불러오기
                    cmds.setAttr("M_Face2_C.fileTextureName", TextureFile, type="string")

                    # eye, teeth joint 위치 보정
                    if cmds.objExists('ICT_R_eye_joint'):
                        cmds.setAttr('ICT_R_eye_joint.tx',jointPositions[0][0])
                        cmds.setAttr('ICT_R_eye_joint.ty',jointPositions[0][1])
                        cmds.setAttr('ICT_R_eye_joint.tz',jointPositions[0][2])

                    if cmds.objExists('ICT_L_eye_joint'):
                        cmds.setAttr('ICT_L_eye_joint.tx', jointPositions[1][0])
                        cmds.setAttr('ICT_L_eye_joint.ty', jointPositions[1][1])
                        cmds.setAttr('ICT_L_eye_joint.tz', jointPositions[1][2])

                    if cmds.objExists('ICT_teeth_up_joint'):
                        cmds.setAttr('ICT_teeth_up_joint.tx', jointPositions[2][0])
                        cmds.setAttr('ICT_teeth_up_joint.ty', jointPositions[2][1])
                        cmds.setAttr('ICT_teeth_up_joint.tz', jointPositions[2][2])

                    if cmds.objExists('ICT_teeth_down_joint'):
                        cmds.setAttr('ICT_teeth_down_joint.tx', jointPositions[3][0])
                        cmds.setAttr('ICT_teeth_down_joint.ty', jointPositions[3][1])
                        cmds.setAttr('ICT_teeth_down_joint.tz', jointPositions[3][2])


                except:
                    pass

                om.MGlobal.displayInfo(u'{} Identity파일을 잘 불러왔습니다.'.format(item.text()))

                d.close()

            except:
                om.MGlobal.displayError(u'{}을 불러오는데 실패했습니다.'.format(filePath))


    def ICT_IdentitySave(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Identity', u'Identity 파일이름을 적으세요')
        # 얼굴변형 블랜드쉐입 값들
        identityValues = []
        # Texture 파일 이름을 얻어온다
        TextureFile = cmds.getAttr("M_Face2_C.fileTextureName")

        # 눈, 치아의 조인트 위치
        jointPositions = []
        if cmds.objExists('ICT_R_eye_joint'):
            jointPositions.append((cmds.getAttr('ICT_R_eye_joint.tx'),cmds.getAttr('ICT_R_eye_joint.ty'),cmds.getAttr('ICT_R_eye_joint.tz')))
        if cmds.objExists('ICT_L_eye_joint'):
            jointPositions.append((cmds.getAttr('ICT_L_eye_joint.tx'),cmds.getAttr('ICT_L_eye_joint.ty'),cmds.getAttr('ICT_L_eye_joint.tz')))
        if cmds.objExists('ICT_teeth_up_joint'):
            jointPositions.append((cmds.getAttr('ICT_teeth_up_joint.tx'),cmds.getAttr('ICT_teeth_up_joint.ty'),cmds.getAttr('ICT_teeth_up_joint.tz')))
        if cmds.objExists('ICT_teeth_down_joint'):
            jointPositions.append((cmds.getAttr('ICT_teeth_down_joint.tx'),cmds.getAttr('ICT_teeth_down_joint.ty'),cmds.getAttr('ICT_teeth_down_joint.tz')))

        if ok:
            if os.path.exists(os.path.join(self.ui.lineEdit_ICT_IdentityPath.text(), name)):
                om.MGlobal.displayError(u'{} 같은 이름의 파일이 이미 존재합니다.'.format(name))
                return
            else:
                # 경로가 비워있지 않다면
                if not self.ui.lineEdit_ICT_IdentityPath.text() == '':
                    mesh = 'BaseMesh_identity'
                    meshHistory = cmds.listHistory(mesh)
                    bsNode = cmds.ls(meshHistory, type='blendShape')[0]
                    bsName = cmds.listAttr(bsNode + '.w', m=True)

                    for bs in bsName:
                        identityValues.append(cmds.getAttr(bsNode + '.' + bs))
                    print identityValues

                    try:
                        # filePath = os.path.join(imu.getPath_IMTool(), abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.pose'))
                        filePath = imu.path_Cleanup(
                            os.path.join(self.ui.lineEdit_ICT_IdentityPath.text(), name + '.identity'))
                        d = shelve.open(filePath)

                        # identity 저장
                        d['IDENTITY_VALUES'] = identityValues
                        # 메터리얼 저장
                        d['TEXTURE_NAME'] = TextureFile
                        # joint 위치 저장
                        d['JOINT_POSITION'] = jointPositions

                        d.close()
                        # print 'Save Success: ', filePath
                        om.MGlobal.displayInfo(u'{} 잘 저장되었습니다.'.format(filePath))

                        self.ui.listWidget_ICT_IdentityList.addItem(name)

                    except:
                        om.MGlobal.displayError(u'{}을 저장하지 못했습니다.'.format(filePath))

                else:
                    om.MGlobal.displayWarning(u'Pose파일이 저장될 경로를 먼저 설정해 주세요')

    def ICT_IdentityModify(self):
        if self.ICT_SELECTED_ITEM != '':
            name = self.ICT_SELECTED_ITEM
            identityValues = []
            TextureFile = cmds.getAttr("M_Face2_C.fileTextureName")
            # 눈, 치아의 조인트 위치
            jointPositions = []
            if cmds.objExists('ICT_R_eye_joint'):
                jointPositions.append((cmds.getAttr('ICT_R_eye_joint.tx'), cmds.getAttr('ICT_R_eye_joint.ty'),
                                       cmds.getAttr('ICT_R_eye_joint.tz')))
            if cmds.objExists('ICT_L_eye_joint'):
                jointPositions.append((cmds.getAttr('ICT_L_eye_joint.tx'), cmds.getAttr('ICT_L_eye_joint.ty'),
                                       cmds.getAttr('ICT_L_eye_joint.tz')))
            if cmds.objExists('ICT_teeth_up_joint'):
                jointPositions.append((cmds.getAttr('ICT_teeth_up_joint.tx'), cmds.getAttr('ICT_teeth_up_joint.ty'),
                                       cmds.getAttr('ICT_teeth_up_joint.tz')))
            if cmds.objExists('ICT_teeth_down_joint'):
                jointPositions.append((cmds.getAttr('ICT_teeth_down_joint.tx'), cmds.getAttr('ICT_teeth_down_joint.ty'),
                                       cmds.getAttr('ICT_teeth_down_joint.tz')))

            if os.path.exists(os.path.join(self.ui.lineEdit_ICT_IdentityPath.text(), name)):
                om.MGlobal.displayError(u'{} 같은 이름의 파일이 이미 존재합니다.'.format(name))
                return
            # 경로가 비워있지 않다면
            if not self.ui.lineEdit_ICT_IdentityPath.text() == '':
                mesh = 'BaseMesh_identity'
                meshHistory = cmds.listHistory(mesh)
                bsNode = cmds.ls(meshHistory, type='blendShape')[0]
                bsName = cmds.listAttr(bsNode + '.w', m=True)

                for bs in bsName:
                    identityValues.append(cmds.getAttr(bsNode + '.' + bs))
                #print identityValues

                try:
                    filePath = imu.path_Cleanup(
                        os.path.join(self.ui.lineEdit_ICT_IdentityPath.text(), name + '.identity'))
                    d = shelve.open(filePath)

                    # identity 저장
                    d['IDENTITY_VALUES'] = identityValues
                    # 메터리얼 저장
                    d['TEXTURE_NAME'] = TextureFile
                    # joint 위치 저장
                    d['JOINT_POSITION'] = jointPositions

                    d.close()
                    # print 'Save Success: ', filePath
                    om.MGlobal.displayInfo(u'{} 잘 저장되었습니다.'.format(filePath))

                    #self.ui.listWidget_ICT_IdentityList.addItem(name)

                except:
                    om.MGlobal.displayError(u'{}을 저장하지 못했습니다.'.format(filePath))

            else:
                om.MGlobal.displayWarning(u'Pose파일이 저장될 경로를 먼저 설정해 주세요')

    def ICT_identityPath(self):
        _folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        if _folder_path:
            self.ui.lineEdit_ICT_IdentityPath.setText(_folder_path)

            # ICT Identity 파일이 있을 경우 리스트위젯에 불러온다
            if os.path.exists(_folder_path):
                identityFiles = cmds.getFileList(folder=_folder_path, filespec='*.identity')
                if identityFiles:
                    self.ui.listWidget_ICT_IdentityList.clear()
                    for i in identityFiles:
                        self.ui.listWidget_ICT_IdentityList.addItem(i.split('.')[0])

    def ICT_makeBlendshapeMesh(self):

        # BS메쉬 등록하고
        BaseMesh = self.ui.lineEdit_ICTBaseMesh.text()
        # 이 녀석들은 값을 1을 유지해야 한다
        identityMesh = self.ui.lineEdit_ICTIdentityMesh.text()
        BodyFitMesh = self.ui.lineEdit_ICTBodyFitMesh.text()

        self.ExtractedBlendshapes = []

        position = []
        position.append(cmds.getAttr(BaseMesh+'.tx'))
        position.append(cmds.getAttr(BaseMesh+'.ty'))
        position.append(cmds.getAttr(BaseMesh+'.tz'))

        # Reset
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(BaseMesh)
        for bs in bsNames:
            if bs == identityMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            elif bs == BodyFitMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            else:
                cmds.setAttr(bsNode + '.' + bs, 0)

        # Duplication
        for bs in bsNames:
            cmds.setAttr(bsNode + '.' + bs, 1)
            dup = cmds.duplicate(BaseMesh)
            renamed = cmds.rename(dup, bs)
            self.ExtractedBlendshapes.append(renamed)
            if bs == identityMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            elif bs == BodyFitMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            else:
                cmds.setAttr(bsNode + '.' + bs, 0)




        # 기존 하나 복사해서
        dup = cmds.duplicate(BaseMesh)
        cmds.showHidden(dup)
        reNamed = cmds.rename(dup, 'BS_Mesh_Result')

        # 표정 BS 추가하고
        cmds.blendShape(self.ExtractedBlendshapes, reNamed)


        # 블랜드쉐입 이름 변경해준다
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(reNamed)
        cmds.rename(bsNode,'BS_node')

        cmds.setAttr(reNamed+'.tx',position[0])
        cmds.setAttr(reNamed+'.ty',position[1])
        cmds.setAttr(reNamed+'.tz',position[2])

        cmds.delete(self.ExtractedBlendshapes)
        self.ExtractedBlendshapes = []
        cmds.select(reNamed)
        self.createMaterialAssign()
        cmds.select(reNamed)

    # 2020/12/14 속눈썹 관련 같이
    def ICT_makeBlendshapeMesh_JB(self):

        # BS메쉬 등록하고
        BaseMesh = self.ui.lineEdit_ICTBaseMesh.text()
        # 이 녀석들은 값을 1을 유지해야 한다
        identityMesh = self.ui.lineEdit_ICTIdentityMesh.text()
        BodyFitMesh = self.ui.lineEdit_ICTBodyFitMesh.text()

        #같이 합쳐질 메쉬 수동 등록
        AddMeshes = ['eye_Lashes_Upper','eye_Lashes_Lower','eye_Occlusion','eye_LacrimalFluid','eye_Blend']

        # groupName = 'BS_Result'
        # cmds.parent(groupName)


        self.ExtractedBlendshapes = []

        #기본메쉬의 위치를 기억해 둔다
        # position = []
        # position.append(cmds.getAttr(BaseMesh+'.tx'))
        # position.append(cmds.getAttr(BaseMesh+'.ty'))
        # position.append(cmds.getAttr(BaseMesh+'.tz'))

        # Reset
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(BaseMesh)
        for bs in bsNames:
            # 랜덤얼굴값 1
            if bs == identityMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            # 바디핏값 1
            elif bs == BodyFitMesh:
                cmds.setAttr(bsNode + '.' + bs, 1)
            # 나머지 블랜드쉐입들은 모두 0
            else:
                cmds.setAttr(bsNode + '.' + bs, 0)

        # Duplication
        for bs in bsNames:
            # 패스~
            if bs == identityMesh:
                continue
            # 패스~
            elif bs == BodyFitMesh:
                continue
            # 블랜드쉐입 복사
            else:
                # 블랜드쉐입중 하나를 1로 고치고
                cmds.setAttr(bsNode + '.' + bs, 1)

                combineMeshes = []

                # 기본메쉬 복사
                combineMeshes.append(cmds.duplicate(BaseMesh)[0])

                # AddMeshes에 하나라도 있다면
                if AddMeshes:
                    for mesh in AddMeshes:
                        combineMeshes.append(cmds.duplicate(mesh)[0])

                    cmds.select(combineMeshes)
                    combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
                    renamed = cmds.rename(combined, bs)
                    # cmds.parent(renamed, groupName)
                    self.ExtractedBlendshapes.append(renamed)
                    cmds.setAttr(bsNode + '.' + bs, 0)
                else:
                    dup = cmds.duplicate(BaseMesh)
                    renamed = cmds.rename(dup, bs)
                    # cmds.parent(renamed, groupName)
                    self.ExtractedBlendshapes.append(renamed)
                    cmds.setAttr(bsNode + '.' + bs, 0)



        # 기존 하나 복사해서
        # dup = cmds.duplicate(BaseMesh)
        # cmds.showHidden(dup)
        # reNamed = cmds.rename(dup, 'BS_Mesh_Result')

        combineMeshes = []

        # 기본메쉬 복사
        combineMeshes.append(cmds.duplicate(BaseMesh)[0])

        # AddMeshes에 하나라도 있다면
        if AddMeshes:
            for mesh in AddMeshes:
                combineMeshes.append(cmds.duplicate(mesh)[0])

            cmds.select(combineMeshes)
            combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            Head_Result = cmds.rename(combined, 'Head_Result')
            #cmds.setAttr(bsNode + '.' + bs, 0)
        else:
            dup = cmds.duplicate(BaseMesh)
            Head_Result = cmds.rename(dup, 'Head_Result')
            #cmds.setAttr(bsNode + '.' + bs, 0)


        # 표정 BS 추가하고
        cmds.blendShape(self.ExtractedBlendshapes, Head_Result)


        # 블랜드쉐입 이름 변경해준다
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(Head_Result)
        cmds.rename(bsNode,'BS_node')

        # cmds.setAttr(Head_Result+'.tx',position[0])
        # cmds.setAttr(Head_Result+'.ty',position[1])
        # cmds.setAttr(Head_Result+'.tz',position[2])

        cmds.delete(self.ExtractedBlendshapes)
        self.ExtractedBlendshapes = []
        cmds.select(Head_Result)
        self.createMaterialAssign()
        cmds.select(Head_Result)


    def ICT_resetSliderMinMax(self):
        self.ui.hSlider_identity00.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity00.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity01.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity01.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity02.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity02.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity03.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity03.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity04.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity04.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity05.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity05.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity06.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity06.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity07.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity07.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity08.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity08.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)
        self.ui.hSlider_identity09.setMinimum(float(self.ui.lineEdit_ICT_min.text()) * 100)
        self.ui.hSlider_identity09.setMaximum(float(self.ui.lineEdit_ICT_max.text()) * 100)


    def ICT_SliderSetValue0(self, value=0):
        cmds.setAttr('BS_identity.identity000', (value * 0.01))
    def ICT_SliderSetValue1(self, value=0):
        cmds.setAttr('BS_identity.identity001', (value * 0.01))
    def ICT_SliderSetValue2(self, value=0):
        cmds.setAttr('BS_identity.identity002', (value * 0.01))
    def ICT_SliderSetValue3(self, value=0):
        cmds.setAttr('BS_identity.identity003', (value * 0.01))
    def ICT_SliderSetValue4(self, value=0):
        cmds.setAttr('BS_identity.identity004', (value * 0.01))
    def ICT_SliderSetValue5(self, value=0):
        cmds.setAttr('BS_identity.identity005', (value * 0.01))
    def ICT_SliderSetValue6(self, value=0):
        cmds.setAttr('BS_identity.identity006', (value * 0.01))
    def ICT_SliderSetValue7(self, value=0):
        cmds.setAttr('BS_identity.identity007', (value * 0.01))
    def ICT_SliderSetValue8(self, value=0):
        cmds.setAttr('BS_identity.identity008', (value * 0.01))
    def ICT_SliderSetValue9(self, value=0):
        cmds.setAttr('BS_identity.identity009', (value * 0.01))



    def ICT_randomAll(self):
        if self.ui.cb_withMaterial.isChecked():
            self.ICT_randomMaterial()
        self.ICT_resetSliderMinMax()
        for index, bsName in enumerate(IdentityAll):

            randomValue = random.uniform(float(self.ui.lineEdit_ICT_min.text()), float(self.ui.lineEdit_ICT_max.text()))

            if index == 0:
                if not self.ui.cb_00.isChecked():
                    self.ui.hSlider_identity00.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 1:
                if not self.ui.cb_01.isChecked():
                    self.ui.hSlider_identity01.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 2:
                if not self.ui.cb_02.isChecked():
                    self.ui.hSlider_identity02.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 3:
                if not self.ui.cb_03.isChecked():
                    self.ui.hSlider_identity03.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 4:
                if not self.ui.cb_04.isChecked():
                    self.ui.hSlider_identity04.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 5:
                if not self.ui.cb_05.isChecked():
                    self.ui.hSlider_identity05.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 6:
                if not self.ui.cb_06.isChecked():
                    self.ui.hSlider_identity06.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 7:
                if not self.ui.cb_07.isChecked():
                    self.ui.hSlider_identity07.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 8:
                if not self.ui.cb_08.isChecked():
                    self.ui.hSlider_identity08.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 9:
                if not self.ui.cb_09.isChecked():
                    self.ui.hSlider_identity09.setValue(randomValue*100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            else:
                cmds.setAttr('BS_identity' + '.' + bsName, randomValue)


    def ICT_random10(self):
        for index, bsName in enumerate(Identity10):
            randomValue = random.uniform(float(self.ui.lineEdit_ICT_min.text()), float(self.ui.lineEdit_ICT_max.text()))

            if index == 0:
                if not self.ui.cb_00.isChecked():
                    self.ui.hSlider_identity00.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 1:
                if not self.ui.cb_01.isChecked():
                    self.ui.hSlider_identity01.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 2:
                if not self.ui.cb_02.isChecked():
                    self.ui.hSlider_identity02.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 3:
                if not self.ui.cb_03.isChecked():
                    self.ui.hSlider_identity03.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 4:
                if not self.ui.cb_04.isChecked():
                    self.ui.hSlider_identity04.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 5:
                if not self.ui.cb_05.isChecked():
                    self.ui.hSlider_identity05.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 6:
                if not self.ui.cb_06.isChecked():
                    self.ui.hSlider_identity06.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 7:
                if not self.ui.cb_07.isChecked():
                    self.ui.hSlider_identity07.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 8:
                if not self.ui.cb_08.isChecked():
                    self.ui.hSlider_identity08.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            elif index == 9:
                if not self.ui.cb_09.isChecked():
                    self.ui.hSlider_identity09.setValue(randomValue * 100)
                    cmds.setAttr('BS_identity' + '.' + bsName, randomValue)
            else:
                cmds.setAttr('BS_identity' + '.' + bsName, randomValue)

    def ICT_random20(self):
        for bsName in Identity20:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random30(self):
        for bsName in Identity30:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random40(self):
        for bsName in Identity40:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random50(self):
        for bsName in Identity50:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random60(self):
        for bsName in Identity60:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random70(self):
        for bsName in Identity70:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random80(self):
        for bsName in Identity80:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random90(self):
        for bsName in Identity90:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))
    def ICT_random99(self):
        for bsName in Identity99:
            cmds.setAttr('BS_identity' + '.' + bsName, random.uniform(float(self.ui.lineEdit_ICT_min.text()),float(self.ui.lineEdit_ICT_max.text())))

    def ICT_randomMaterial(self):
        textureFile = random.choice(self.faceTextures)
        cmds.setAttr("M_Face2_C.fileTextureName", textureFile, type="string")
        #cmds.connectAttr('M_Face2_C' + '.outColor', 'M_Face2' + '.color', force=True)

    def ICT_resetControlrig(self):
        self.resetSlider()

    def ICT_resetAllblendshape(self):
        for bsName in ICTBlendShapeList:
            cmds.setAttr('BS_node' + '.' + bsName, 0)

    def ICT_resetIdentity(self):
        for bsName in IdentityAll:
            cmds.setAttr('BS_identity' + '.' + bsName, 0)


    # Snappers Weight Initialize
    def init_Snappers_Weights(self):
        if cmds.objExists('Head_geo'):
            head_bsName = cmds.listAttr('Head_blendShape' + '.w', m=True)
            if len(head_bsName) > 620:
                self.is_head = True
            else:
                self.is_head = False
        if cmds.objExists('eyebrow'):
            eyebrow_bsName = cmds.listAttr('eyebrowe_blendShape' + '.w', m=True)
            if len(eyebrow_bsName) > 620:
                self.is_eyebrow = True
            else:
                self.is_eyebrow = False
        if cmds.objExists('eyelash'):
            eyelash_bsName = cmds.listAttr('eye_lashes_blendShape' + '.w', m=True)
            if len(eyelash_bsName) > 620:
                self.is_eyelash = True
            else:
                self.is_eyelash = False
        if cmds.objExists('eye_AO'):
            eye_AO_bsName = cmds.listAttr('ao_blendShape' + '.w', m=True)
            if len(eye_AO_bsName) > 620:
                self.is_eye_AO = True
            else:
                self.is_eye_AO = False

    def progressBarEndTimer(self):
        self.ui.progressBar.reset()
        self.timerVar.stop()


    # ------------------------------------------------------------------------------------------
    # Blendshape List Add/Remove
    # ------------------------------------------------------------------------------------------
    def Popup_ScriptEditor(self):
        mel.eval('ScriptEditor')
        cmds.scriptEditorInfo(clearHistory=True)

    def printPoseAssetList(self):
        for index in range(self.ui.listWidget_blendshape.count()):
            print self.ui.listWidget_blendshape.item(index).text()


    def addBlendshapeToList(self):
        # ListWidget에서 item을 리스트에 넣기
        name, ok = QtWidgets.QInputDialog.getText(self, u'표정추가', u'커스텀 Blendshape 이름을 적으세요')
        if ok:
            if name in self.CustomBlendshapeList:
                om.MGlobal.displayWarning(u'이미 {}와 같은 이름의 블랜드쉐입이 존재합니다'.format(name))
                return
            else:
                # 커스텀리스트에 추가
                self.CustomBlendshapeList.append(name)
                # 리스트위젯에 추가
                self.ui.listWidget_blendshape.addItem(name)

    def deleteBlendshapeToList(self):
        # default 를 지우려 한다면 나가
        if self.ui.listWidget_blendshape.currentItem().text() == 'default':
            om.MGlobal.displayError(u' default 는 제거 할 수 없습니다.')
            return
        # 기본 ARkit 중에 지우려 한다면 나가
        if self.ui.listWidget_blendshape.currentItem().text() in ARKitBlendShapeList:
            om.MGlobal.displayError(u'커스텀Blendshape만 제거 할 수 있습니다.')
            return

        try:
            # 저장될 최종 딕셔너리에서 제거
            if self.ui.listWidget_blendshape.currentItem().text() in self.SNAPPERS_POSE_DIC.keys():
                del self.SNAPPERS_POSE_DIC[self.ui.listWidget_blendshape.currentItem().text()]
            # 커스텀리스트에서도 제거
            if len(self.CustomBlendshapeList) <= 1:
                self.CustomBlendshapeList = []
            else:
                self.CustomBlendshapeList.remove(self.ui.listWidget_blendshape.currentItem().text())
            # 최종적으로 리스트위젯에서 제거해준다
            self.ui.listWidget_blendshape.takeItem(self.ui.listWidget_blendshape.currentRow())
        except:
            om.MGlobal.displayError(u'SNAPPERS_POSE_DIC에서 {}를 삭제하지 못했습니다.'.format(self.ui.listWidget_blendshape.currentItem().text()))






    # ------------------------------------------------------------------------------------------
    # Extract Ojbects Show/Hide
    # ------------------------------------------------------------------------------------------
    def Show_Brow(self, state):
        if state:
            cmds.showHidden('eyebrow')
        else:
            cmds.hide('eyebrow')
    def Show_Eyelash(self, state):
        if state:
            cmds.showHidden('eyelash')
        else:
            cmds.hide('eyelash')
    def Show_EyeAO(self, state):
        if state:
            cmds.showHidden('eye_AO')
        else:
            cmds.hide('eye_AO')
    def Show_Eyes(self, state):
        if state:
            cmds.showHidden('Eyes')
        else:
            cmds.hide('Eyes')
    def Show_Teeth(self, state):
        if state:
            cmds.showHidden('Teeth')
        else:
            cmds.hide('Teeth')


    # ------------------------------------------------------------------------------------------
    # HeadPose Set Load/Save
    # ------------------------------------------------------------------------------------------
    def selectPosePath(self):
        _folderPath = QtWidgets.QFileDialog.getExistingDirectory()
        if _folderPath:
            self.ui.lineEdit_PosePath.setText(_folderPath)
            if os.path.exists(_folderPath):
                poseFiles = cmds.getFileList(folder=_folderPath, filespec='*.pose')
                if poseFiles:
                    self.ui.cb_headList.clear()
                    for pose in poseFiles:
                        self.ui.cb_headList.addItem(pose.split('.')[0])
                else:
                    self.ui.cb_headList.clear()

    def CreatePoseFile(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'PoseSET', u'Pose셋 파일이름을 적으세요')

        if ok:
            if os.path.exists(os.path.join(self.ui.lineEdit_PosePath.text(),name)):
                om.MGlobal.displayError(u'{} 같은 이름의 파일이 이미 존재합니다.'.format(name))
                return
            else:
                if not self.ui.lineEdit_PosePath == '':
                    if self.ui.cb_headList.findText(name) == -1:
                        self.ui.cb_headList.addItem(name)
                        self.ui.cb_headList.setCurrentIndex(self.ui.cb_headList.findText(name))
                        self.SNAPPERS_POSESET_LASTINDEX = self.ui.cb_headList.findText(name)
                else:
                    om.MGlobal.displayWarning(u'Pose파일이 저장될 경로를 먼저 설정해 주세요')

    def select_PoseFile(self, index):
        if not cmds.objExists(self.SNAPPERS_HEAD):
            return
        self.SNAPPERS_POSESET_LASTINDEX = index

    def getFaceName(self):
        meshBlendshapeName = cmds.listAttr('Head_blendShape' + '.w', m=True)
        for bs in meshBlendshapeName:
            if bs not in snappersBlendshape620:
                return bs[:-5]



    # ------------------------------------------------------------------------------------------
    # Extract & Export
    # ------------------------------------------------------------------------------------------
    def editBlendshape(self):
        groupName = self.getFaceName()+'_Result'
        newHeadMesh = self.getFaceName()+'_final'
        try:
            if cmds.objExists(newHeadMesh):
                print 'ok HeadMesh'
                meshHistory = cmds.listHistory(newHeadMesh)
                meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')[0]
                if meshBlendshapeNode:
                    print 'ok Blendshape'
                    bsMesh, bsNode, bsNames = self.getBlendshapeNames(newHeadMesh)
                    bsName = self.ui.listWidget_blendshape.currentItem().text()
                    print 'bsName :',bsName

                    # 해당 BS의 인덱스를 알아내서 저장시켜놓은 후에
                    bsIndex = self.getTargetIndex(bsNode,bsName)
                    print 'bsIndex :',bsIndex

                    # 기존 BS 제거
                    cmds.blendShape(bsNode, e=1, rm=1, t=[(bsMesh, bsIndex, bsName, 1)])
                    # 기존 BS 메쉬 제거
                    cmds.delete(bsName)
                    print 'delete :',bsName

                    # 현재
                    combineMeshes = []
                    if self.ui.cb_brow.isChecked() or self.ui.cb_brow.isChecked() or self.ui.cb_eyeAO.isChecked() or self.ui.cb_eyes.isChecked() or self.ui.cb_teeth.isChecked():
                        combineMeshes.append(cmds.duplicate('Head_geo')[0])
                        if self.ui.cb_brow.isChecked():
                            combineMeshes.append(cmds.duplicate('eyebrow')[0])
                        if self.ui.cb_eyelash.isChecked():
                            combineMeshes.append(cmds.duplicate('eyelash')[0])
                        if self.ui.cb_eyeAO.isChecked():
                            combineMeshes.append(cmds.duplicate('eye_AO')[0])
                        if self.ui.cb_eyes.isChecked():
                            combineMeshes.append(cmds.duplicate('Eyes')[0])
                        if self.ui.cb_teeth.isChecked():
                            combineMeshes.append(cmds.duplicate('Teeth')[0])
                        cmds.select(combineMeshes)
                        combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
                        cmds.rename(combined, bsName)
                    else:
                        # 스마트컴바인 에러때문에 예외처리
                        dup = cmds.duplicate('Head_geo')[0]
                        cmds.select(dup)
                        self.unlockTransform()
                        cmds.manipPivot(p='center')
                        cmds.rename(dup, bsName)

                    # 기존에 알아낸 인덱스 자리에 다시 넣기
                    cmds.blendShape(bsNode, e=1, t=[bsMesh, bsIndex, bsName, 1])
                    print 'ok Add Blendshape'
                    cmds.parent(bsName, groupName)
                    cmds.hide(bsName)
                    # 완료후 결과 보여주기
                    for bs in bsNames:
                        cmds.setAttr(bsNode + '.' + bs, 0)
                    cmds.setAttr(bsNode + '.' + bsName, 1)

                    # 혹시 모르니 저장까지 해주자
                    self.Save_Pose_Key()

        except:
            om.MGlobal.displayError(u'추출후 블랜드쉐입제거하기를 체크해제 해서 다시 만든 후에 하세요')



    def ExtractBlendshape_Selected(self):
        combineMeshes = []
        if self.ui.cb_brow.isChecked() or self.ui.cb_brow.isChecked() or self.ui.cb_eyeAO.isChecked() or self.ui.cb_eyes.isChecked() or self.ui.cb_teeth.isChecked():
            combineMeshes.append(cmds.duplicate('Head_geo')[0])
            if self.ui.cb_brow.isChecked():
                combineMeshes.append(cmds.duplicate('eyebrow')[0])
            if self.ui.cb_eyelash.isChecked():
                combineMeshes.append(cmds.duplicate('eyelash')[0])
            if self.ui.cb_eyeAO.isChecked():
                combineMeshes.append(cmds.duplicate('eye_AO')[0])
            if self.ui.cb_eyes.isChecked():
                combineMeshes.append(cmds.duplicate('Eyes')[0])
            if self.ui.cb_teeth.isChecked():
                combineMeshes.append(cmds.duplicate('Teeth')[0])
            cmds.select(combineMeshes)
            combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            cmds.rename(combined, self.ui.listWidget_blendshape.currentItem().text())
        else:
            # SmartCombine때문에 예외처리시킴, 아무것도 같이 포함 안시키면 SmartCombine을 사용하지 않겠다!!
            dup = cmds.duplicate('Head_geo')[0]
            cmds.select(dup)
            self.unlockTransform()
            cmds.manipPivot(p='center')
            cmds.rename(dup, self.ui.listWidget_blendshape.currentItem().text())

    # 스내퍼 블렌드쉐입 추출하기
    def ExtractBlendshape(self):
        self.ExtractedBlendshapes = []
        self.isMakingBlendshapes = True
        combineMeshes = []
        groupName = self.getFaceName()+'_Result'

        # 만들고 나서 생성된 BS쉐입들 지울지
        if cmds.objExists(groupName):
            cmds.delete(groupName)
        cmds.group(em=True, n=groupName)
        # if self.ui.cb_deleteBlendshapeAfter.isChecked():
        #     pass
        # else:
        #
        #     if cmds.objExists(groupName):
        #         cmds.delete(groupName)
        #     cmds.group(em=True, n=groupName)

        # 기본 얼굴 만들기 #####################################
        self.FACSResetAll()
        self.AdjustResetAll()

        combineMeshes.append(cmds.duplicate('Head_geo')[0])
        if self.ui.cb_brow.isChecked():
            combineMeshes.append(cmds.duplicate('eyebrow')[0])
        if self.ui.cb_eyelash.isChecked():
            combineMeshes.append(cmds.duplicate('eyelash')[0])
        if self.ui.cb_eyeAO.isChecked():
            combineMeshes.append(cmds.duplicate('eye_AO')[0])
        if self.ui.cb_eyes.isChecked():
            combineMeshes.append(cmds.duplicate('Eyes')[0])
        if self.ui.cb_teeth.isChecked():
            combineMeshes.append(cmds.duplicate('Teeth')[0])
        cmds.select(combineMeshes)
        combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
        renamed = cmds.rename(combined, self.getFaceName()+'_final')
        cmds.parent(renamed, groupName)
        # if self.ui.cb_deleteBlendshapeAfter.isChecked():
        #     pass
        # else:
        #     cmds.parent(renamed, groupName)
        # 기본 얼굴 만들기 #####################################

        # 현재 로드되어있는 ListWidget item을 기준으로 Blendshape List 추출
        ExtractList = []
        for index in range(self.ui.listWidget_blendshape.count()):
            ExtractList.append(self.ui.listWidget_blendshape.item(index).text())

        # ProgressBar
        Progress_maximum = len(ExtractList) + 1
        self.ui.progressBar.setRange(0, Progress_maximum)
        Progress_Value = 1
        self.ui.progressBar.setValue(Progress_Value)


        # Pose별 얼굴 메쉬 추출하기 ##############################
        for index, pose in enumerate(ExtractList):
            Progress_Value += 1
            self.ui.progressBar.setValue(Progress_Value)

            # 미리 만들어둔 Blendshape이 있다면 건너뛰자 / 지우자
            if cmds.objExists(pose):
                # self.ExtractedBlendshapes.append(pose)
                # print u'이미 {}가 있습니다.'.format(pose)
                # continue
                cmds.delete(pose)

            # 저장된 사전안에 blendname이 있다면
            if pose in self.SNAPPERS_POSE_DIC.keys():

                # 그 이름으로 되어 있는 blendshape 딕셔너리를 통째로 가져온다
                tempDic = self.SNAPPERS_POSE_DIC[pose]
                # 표정을 바꾼다
                for i in tempDic:
                    cmds.setAttr(i, tempDic[i])
                # 얼굴
                combineMeshes.append(cmds.duplicate('Head_geo')[0])
                if self.ui.cb_brow.isChecked():
                    combineMeshes.append(cmds.duplicate('eyebrow')[0])
                if self.ui.cb_eyelash.isChecked():
                    combineMeshes.append(cmds.duplicate('eyelash')[0])
                if self.ui.cb_eyeAO.isChecked():
                    combineMeshes.append(cmds.duplicate('eye_AO')[0])
                if self.ui.cb_eyes.isChecked():
                    combineMeshes.append(cmds.duplicate('Eyes')[0])
                if self.ui.cb_teeth.isChecked():
                    combineMeshes.append(cmds.duplicate('Teeth')[0])
                cmds.select(combineMeshes)
                combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
                finalMesh = cmds.rename(combined, pose)
                if self.ui.cb_deleteBlendshapeAfter.isChecked():
                    pass
                else:
                    cmds.parent(finalMesh, groupName)
                    cmds.hide(finalMesh)

                self.ExtractedBlendshapes.append(finalMesh)
        # Pose별 얼굴 메쉬 추출하기 ##############################



        # 최종 블랜드쉐입 만들기 #################################
        cmds.blendShape(self.ExtractedBlendshapes, self.getFaceName()+'_final')
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(self.getFaceName()+'_final')
        cmds.rename(bsNode, 'BS_node')
        # 최종 블랜드쉐입 만들기 #################################

        if self.ui.cb_deleteBlendshapeAfter.isChecked():
            cmds.delete(self.ExtractedBlendshapes)

        cmds.select(self.getFaceName()+'_final')

        Progress_Value += 1
        self.ui.progressBar.setValue(Progress_Value)
        if self.ui.progressBar.value() == Progress_maximum:
            self.timerVar.start()
        self.isMakingBlendshapes = False
        om.MGlobal.displayInfo(u'블랜드세입 추출 완료!')



    def createMap(self):
        # 안쓰는 코드
        # pose 저장할때 목록으로 쓰인다
        #save 파일이 없어질 경우 다시 생성해야해서 남겨둠
        for i in range(len(sliders_list)):
            attrs = []
            # 슬라이더에 연결된 항목이 있다면 저장
            if (cmds.getAttr(sliders_list[i] + ".translateX", l=1) == False):
                attrs.append('translateX')
            if (cmds.getAttr(sliders_list[i] + ".translateY", l=1) == False):
                attrs.append('translateY')
            if (cmds.getAttr(sliders_list[i] + ".translateZ", l=1) == False):
                attrs.append('translateZ')

            if sliders_list[i] in slider_attr_list:
                index = slider_attr_list.index(sliders_list[i])
                attrs = attrs + slider_attr_list[index]

            for attr in attrs:
                self.CntrAttrMap.append([sliders_list[i], attr])

        for i in range(len(adj_cntr_list)):
            self.CntrAttrMap.append([adj_cntr_list[i], "translateX"])
            self.CntrAttrMap.append([adj_cntr_list[i], "translateY"])
            self.CntrAttrMap.append([adj_cntr_list[i], "translateZ"])

        for item in self.CntrAttrMap:
            print item

    def selectRightEye(self):
        if cmds.objExists('RightEye'):
            if imu.isShiftModifier():
                cmds.select('RightEye','LeftEye')
            else:
                cmds.select('RightEye')
    def selectLeftEye(self):
        if cmds.objExists('LeftEye'):
            if imu.isShiftModifier():
                cmds.select('RightEye', 'LeftEye')
            else:
                cmds.select('LeftEye')
    def selectTeeth(self):
        if cmds.objExists('Teeth'):
            cmds.select('Teeth')
            imu.unlockTransform()



    # ------------------------------------------------------------------------------------------
    # Snappers
    # ------------------------------------------------------------------------------------------

    def selection_Horizontal(self, state):
        snappers_rig_manager.bMirrorLeftRight = True if state else False

    def selection_Vertical(self, state):
        snappers_rig_manager.bMirrorUpDown = True if state else False

    def createBSSet(self):
        if cmds.objExists('Head_geo') and cmds.objExists('Ref_Head_geo'):

            # 복사 위치
            init_pos = [-20,0,0]
            self.FACSResetAll()
            self.AdjustResetAll()

            newMesh = cmds.ls(sl=1)[0]
            if newMesh:
                if cmds.polyEvaluate('Head_geo', f=True) != cmds.polyEvaluate(newMesh, f=True):
                    om.MGlobal.displayWarning(u'{}의 폴리곤수가 Head_geo와 다릅니다.'.format(newMesh))
                    return
            else:
                return

            # 이름에 이미 _head가 있다면 제거하고 이름으로 쓴다
            if newMesh.endswith('_head'):
                newMesh_head = newMesh
                newMesh = newMesh_head.replace('_head','')
            else:
                newMesh_head = cmds.rename(newMesh, newMesh+'_head')

            # 그룹이름
            groupName = newMesh + '_source'

            # 미리 만들어둔게 있다면 메쉬만 남기고 다 지우고 다시 하도록 한다.
            if cmds.objExists(groupName):
                om.MGlobal.displayWarning(u'얼굴메쉬만 남기고 기존의 {}Group과 안의 구성물을 모두 삭제 시켜주세요.'.format(groupName))
                return


            imu.setTranslate(newMesh_head, init_pos)
            cmds.group(em=1, n=groupName)
            cmds.parent(newMesh_head, groupName)

            dup = cmds.duplicate('eyebrow')
            newMesh_eyebrow = cmds.rename(dup, newMesh + '_eyebrow')
            cmds.select(newMesh_eyebrow)
            self.unlockTransform()
            imu.setTranslate(newMesh_eyebrow, init_pos)
            cmds.parent(newMesh_eyebrow, groupName)

            dup = cmds.duplicate('eyelash')
            newMesh_eyelash = cmds.rename(dup, newMesh + '_eyelash')
            cmds.select(newMesh_eyelash)
            self.unlockTransform()
            imu.setTranslate(newMesh_eyelash, init_pos)
            cmds.parent(newMesh_eyelash, groupName)

            dup = cmds.duplicate('eye_AO')
            newMesh_eye_AO = cmds.rename(dup, newMesh + '_eye_AO')
            cmds.select(newMesh_eye_AO)
            self.unlockTransform()
            imu.setTranslate(newMesh_eye_AO, init_pos)
            cmds.parent(newMesh_eye_AO, groupName)

            cmds.blendShape('Ref_Head_geo',newMesh_head)
            meshHistory = cmds.listHistory(newMesh_head)
            meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')[0]
            cmds.setAttr(meshBlendshapeNode + '.Ref_Head_geo', 1)

            # Auto Constrain Vertex to Joint
            NewMeshVertices = []
            for vtx in Constrain_Vertices:
                NewMeshVertices.append(vtx.replace('newMesh', newMesh_head))
            cmds.select(NewMeshVertices)
            joints = self.CreateJointToVertex()
            cmds.skinCluster(joints, newMesh_eyelash, n='eyelash_skinCluster', tsb=True, bm=0, sm=0, nw=1)
            cmds.skinCluster(joints, newMesh_eyebrow, n='eyebrow_skinCluster', tsb=True, bm=0, sm=0, nw=1)
            cmds.skinCluster(joints, newMesh_eye_AO, n='eye_AO_skinCluster', tsb=True, bm=0, sm=0, nw=1)

            cmds.setAttr(meshBlendshapeNode + '.Ref_Head_geo', 0)
            cmds.select(newMesh_head, newMesh_eyebrow, newMesh_eyelash, newMesh_eye_AO)
            mel.eval("DeleteHistory")
            cmds.delete(joints)
            self.SNAPPERS_NEWMESH = newMesh
            cmds.select(clear=1)
            if self.ui.cb_autoRegist.isChecked():
                try:
                    cmds.select(newMesh_head)
                    self.RegistNewFace()
                except:
                    om.MGlobal.displayWarning(u'{}를 추가하지 못했습니다.'.format(newMesh_head))
                try:
                    cmds.select(newMesh_eyebrow)
                    self.RegistNewFace()
                except:
                    om.MGlobal.displayWarning(u'{}를 추가하지 못했습니다.'.format(newMesh_eyebrow))
                try:
                    cmds.select(newMesh_eyelash)
                    self.RegistNewFace()
                except:
                    om.MGlobal.displayWarning(u'{}를 추가하지 못했습니다.'.format(newMesh_eyelash))
                try:
                    cmds.select(newMesh_eye_AO)
                    self.RegistNewFace()
                except:
                    om.MGlobal.displayWarning(u'{}를 추가하지 못했습니다.'.format(newMesh_eye_AO))
        else:
            om.MGlobal.displayWarning(u'자동구성할 수 있는 환경이 아닙니다.')

    # 스내퍼 전용
    def RegistNewFaceDelete_All(self):
        snapperObjects = ['Head_geo','eyelash','eyebrow','eye_AO']
        for object in snapperObjects:
            bsMesh, bsNode, bsNames = self.getBlendshapeNames(object)
            for bs in bsNames:
                if not bs in snappersBlendshape620:
                    try:
                        # 삭제
                        cmds.blendShape(bsNode, e=1, rm=1, t=[bsMesh, self.getTargetIndex(bsNode, bs), bs, 1])

                        # Slider 업데이트
                        if bs.endswith('_head'):
                            self.is_head = False
                        elif bs.endswith('_eyebrow'):
                            self.is_eyebrow = False
                        elif bs.endswith('_eyelash'):
                            self.is_eyelash = False
                        elif bs.endswith('_eye_AO'):
                            self.is_eye_AO = False
                        self.init_Snappers_Weights()

                        om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제했습니다.'.format(bsNode, bs))

                    except:
                        try:
                            self.delete_blendshape_target(bsNode, self.getTargetIndex(bsNode, bs))

                            # Slider 업데이트
                            if bs.endswith('_head'):
                                self.is_head = False
                            elif bs.endswith('_eyebrow'):
                                self.is_eyebrow = False
                            elif bs.endswith('_eyelash'):
                                self.is_eyelash = False
                            elif bs.endswith('_eye_AO'):
                                self.is_eye_AO = False
                            self.init_Snappers_Weights()

                            om.MGlobal.displayInfo(u'{0}에서 {1}를 강제로 삭제했습니다.'.format(bsNode, bs))
                        except:
                            om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제하지 못했습니다.'.format(bsNode, bs))



    def RegistNewFaceDelete(self):
        # 선택한 녀석
        sel = cmds.ls(sl=1)
        if sel == []:
            om.MGlobal.displayError(u'아무것도 선택하지 않았습니다.')
            return

        selected_blendshape = sel[0]
        meshHistory = cmds.listHistory(selected_blendshape)
        meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')

        # 블랜드 쉐입이 아니면 나가
        if not meshBlendshapeNode:
            om.MGlobal.displayError(u'블랜드쉐입이 아닙니다.')
            return

        # 블랜드쉐입 노드명 알아냄
        bsMesh, bsNode, bsName = self.getBlendshapeNames(selected_blendshape)


        # 추가한 메쉬가 있는지 알아보자. 없음 나가
        if len(bsName) <= 620:
            om.MGlobal.displayError(u'자동으로 삭제할 블랜드쉐입이 없습니다.')
            return

        for index, bs in enumerate(bsName):
            # 기존 스내퍼에서 사용하는 블랜드쉐입이 아니면 '아마도' 추가했던 메쉬겠지?
            if not bs in snappersBlendshape620:

                try:
                    # 삭제
                    cmds.blendShape(bsNode, e=1, rm=1, t=[bsMesh, self.getTargetIndex(bsNode, bs), bs, 1])

                    # Slider 업데이트
                    if bs.endswith('_head'):
                        self.is_head =False
                    elif bs.endswith('_eyebrow'):
                        self.is_eyebrow = False
                    elif bs.endswith('_eyelash'):
                        self.is_eyelash = False
                    elif bs.endswith('_eye_AO'):
                        self.is_eye_AO = False
                    self.init_Snappers_Weights()

                    om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제했습니다.'.format(bsNode, bs))

                except:
                    try:
                        self.delete_blendshape_target(bsNode, self.getTargetIndex(bsNode, bs))

                        # Slider 업데이트
                        if bs.endswith('_head'):
                            self.is_head = False
                        elif bs.endswith('_eyebrow'):
                            self.is_eyebrow = False
                        elif bs.endswith('_eyelash'):
                            self.is_eyelash = False
                        elif bs.endswith('_eye_AO'):
                            self.is_eye_AO = False
                        self.init_Snappers_Weights()

                        om.MGlobal.displayInfo(u'{0}에서 {1}를 강제로 삭제했습니다.'.format(bsNode, bs))
                    except:
                        om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제하지 못했습니다.'.format(bsNode, bs))

    def RegistNewFace_All(self):
        selectMesh = cmds.ls(sl=1)[0]
        # 아무것도 선택하지 않았다면 나가
        if not selectMesh:
            om.MGlobal.displayWarning(u'추가할 새 얼굴메쉬를 선택하세요')
            return
        if selectMesh.endswith('_source'):
            om.MGlobal.displayWarning(u'그룹말고 메쉬를 선택해 주세요')
            return

        # 선택한 메쉬에서 이름 가져오기
        headName = ''
        if selectMesh.endswith('_head'):
            headName = selectMesh[:-5]
        else:
            headName = selectMesh

        AddMeshes = [headName+'_head',headName+'_eyebrow',headName+'_eyelash',headName+'_eye_AO' ]

        for check in AddMeshes:
            if cmds.objExists(check):
                pass
            else:
                om.MGlobal.displayWarning(u'{} 모두 이렇게 있어야 합니다. 자동생성부터 먼저 하시던가요'.format(AddMeshes))
                return

        # 추가하기전에 기존꺼 제거
        self.RegistNewFaceDelete_All()

        # 자 이제 하나씩 등록!!
        for mesh in AddMeshes:
            if cmds.objExists(mesh):
                cmds.select(mesh)
                self.RegistNewFace()
                print u'{} 추가 완료'.format(mesh)
            else:
                print u'{}는 씬안에 없음'.format(mesh)

        self.SNAPPERS_NEWMESH = self.getFaceName()


    def RegistNewFace(self):
        selectMesh = cmds.ls(sl=1)[0]
        # 아무것도 선택하지 않았다면 나가
        if not selectMesh:
            om.MGlobal.displayWarning(u'추가할 새 얼굴메쉬를 선택하세요')
            return
        # 선택한게 스내퍼스 얼굴이면 나가
        if self.SNAPPERS_HEAD == selectMesh:
            om.MGlobal.displayError(u'Snapper용 Head메쉬는 등록하지 못합니다.')
            return

        # 머리
        if selectMesh.endswith('_head'):
            blendMesh, blendshapeNode, blendNames = self.getBlendshapeNames('Head_geo')
            if cmds.objExists(blendshapeNode + '.' + selectMesh):
                om.MGlobal.displayError(u'{} <- 이미 같은 이름의 쉐입이 존재합니다.'.format(blendshapeNode + '.' + selectMesh))
                return
            else:
                nextIndex = self.nextAvailableTargetIndex(blendshapeNode)
                try:
                    cmds.blendShape(blendshapeNode, e=1, tc=True, t=[blendMesh, nextIndex, selectMesh, 1])
                except:
                    om.MGlobal.displayError(u'{0}에서 {1}를 추가하는데 실패했습니다.'.format(blendshapeNode, selectMesh))
                cmds.setAttr(blendshapeNode + '.' + selectMesh, 1)
                self.is_head = True
                om.MGlobal.displayInfo(u'{0}에서 {1}를 추가했습니다.'.format(blendshapeNode, selectMesh))

        # 눈썹
        elif selectMesh.endswith('_eyebrow'):
            blendMesh, blendshapeNode, blendNames = self.getBlendshapeNames('eyebrow')
            if cmds.objExists(blendshapeNode + '.' + selectMesh):
                om.MGlobal.displayError(u'{} <- 이미 같은 이름의 쉐입이 존재합니다.'.format(blendshapeNode + '.' + selectMesh))
                return
            else:
                nextIndex = self.nextAvailableTargetIndex(blendshapeNode)
                try:
                    cmds.blendShape(blendshapeNode, e=1, tc=True, t=[blendMesh, nextIndex, selectMesh, 1])
                except:
                    om.MGlobal.displayError(u'{0}에서 {1}를 추가하는데 실패했습니다.'.format(blendshapeNode, selectMesh))
                cmds.setAttr(blendshapeNode + '.' + selectMesh, 1)
                self.is_eyebrow = True
                om.MGlobal.displayInfo(u'{0}에서 {1}를 추가했습니다.'.format(blendshapeNode, selectMesh))
        # 속눈썹
        elif selectMesh.endswith('_eyelash'):
            blendMesh, blendshapeNode, blendNames = self.getBlendshapeNames('eyelash')
            if cmds.objExists(blendshapeNode + '.' + selectMesh):
                om.MGlobal.displayError(u'{} <- 이미 같은 이름의 쉐입이 존재합니다.'.format(blendshapeNode + '.' + selectMesh))
                return
            else:
                nextIndex = self.nextAvailableTargetIndex(blendshapeNode)
                try:
                    cmds.blendShape(blendshapeNode, e=1, tc=True, t=[blendMesh, nextIndex, selectMesh, 1])
                except:
                    om.MGlobal.displayError(u'{0}에서 {1}를 추가하는데 실패했습니다.'.format(blendshapeNode, selectMesh))
                cmds.setAttr(blendshapeNode + '.' + selectMesh, 1)
                self.is_eyelash = True
                om.MGlobal.displayInfo(u'{0}에서 {1}를 추가했습니다.'.format(blendshapeNode, selectMesh))
        # AO
        elif selectMesh.endswith('_eye_AO'):
            blendMesh, blendshapeNode, blendNames = self.getBlendshapeNames('eye_AO')
            if cmds.objExists(blendshapeNode + '.' + selectMesh):
                om.MGlobal.displayError(u'{} <- 이미 같은 이름의 쉐입이 존재합니다.'.format(blendshapeNode + '.' + selectMesh))
                return
            else:
                nextIndex = self.nextAvailableTargetIndex(blendshapeNode)
                try:
                    cmds.blendShape(blendshapeNode, e=1, tc=True, t=[blendMesh, nextIndex, selectMesh, 1])
                except:
                    om.MGlobal.displayError(u'{0}에서 {1}를 추가하는데 실패했습니다.'.format(blendshapeNode, selectMesh))
                cmds.setAttr(blendshapeNode + '.' + selectMesh, 1)
                self.is_eye_AO = True
                om.MGlobal.displayInfo(u'{0}에서 {1}를 추가했습니다.'.format(blendshapeNode, selectMesh))


    def SetKeyForPoseAsset(self):
        self.isKeyingPoseAsset = True
        self.setFrameRange()

        # Default
        self.DeleteAll_KeyAnimation()
        self.FACSResetAll()
        self.AdjustResetAll()
        cmds.currentTime(0)
        self.Set_KeyAnimation()

        ExtractList = []
        for index in range(self.ui.listWidget_blendshape.count()):
            ExtractList.append(self.ui.listWidget_blendshape.item(index).text())

        Progress_Value = 0
        self.ui.progressBar.setValue(Progress_Value)
        Progress_maximum = len(ExtractList)
        self.ui.progressBar.setRange(0, Progress_maximum)

        # Load Pose
        for index, pose in enumerate(ExtractList):
            if ExtractList[index] in self.SNAPPERS_POSE_DIC.keys():
                if index == 0:
                    continue
                cmds.currentTime(index)
                tempDic = self.SNAPPERS_POSE_DIC[ExtractList[index]]
                for i in tempDic:
                    cmds.setAttr(i, tempDic[i])
                self.Set_KeyAnimation()

            Progress_Value += 1
            self.ui.progressBar.setValue(Progress_Value)
        if self.ui.progressBar.value() == Progress_maximum:
            self.timerVar.start()

        self.ui.cb_keyAnimationMode.setChecked(True)
        self.isKeyingPoseAsset = False
        om.MGlobal.displayInfo(u'키프레임에 모든 표정의 키값을 적용하였습니다.')


        # if ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1] in self.SNAPPERS_POSE_DIC.keys():
        #     tempDic = self.SNAPPERS_POSE_DIC[ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1]]
        #     for i in tempDic:
        #         cmds.setAttr(i, tempDic[i])


    def setFrameRange(self):
        cmds.playbackOptions(minTime=0, maxTime=self.ui.listWidget_blendshape.count()-1)

    def on_ChangeFrame(self, *args):
        # 포즈에셋 키 주고 있는 상황에서는 작동하지 않기
        if self.isKeyingPoseAsset == False:
            if self.ui.cb_keyAnimationMode.checkState():
                # 키애니메이션 모드라면 그냥 리스트만 갱신해준다
                self.ui.listWidget_blendshape.setCurrentRow(int(cmds.currentTime(query=True)))
            else:
                # 키애니메이션 모드가 아니라면 불러와서 표정을 지어주자
                self.blendshape_clicked(self)

    def blendshape_clicked(self, *args):
        if not cmds.objExists('Head_geo'):
            return

        # 포즈에셋 키 주고 있는 상황에서는 작동하지 않기
        if self.isKeyingPoseAsset:
            pass
        else:
            if self.ui.listWidget_blendshape.currentItem():
                # 현재 선택된 Blendshape 의 Index 번호 표시
                self.ui.label_frame.setText(str(self.ui.listWidget_blendshape.currentRow()))
                # 현재 선택된 Blendshape 이름 표시

                self.ui.label_blendshapeName.setText(str(self.ui.listWidget_blendshape.currentItem().text()))

                # # 현재 선택된 Blendshape의 이미지 불러오기
                imagePath = os.path.join(os.path.dirname(imu.getPath_IMTool()), 'blendshapes', str(self.ui.listWidget_blendshape.currentItem().text()) + '.png')
                imagePath = imu.path_Cleanup(imagePath)
                picture = QtGui.QPixmap(imagePath)
                picture_default = QtGui.QPixmap(imagePath.replace('.png','_d.png'))
                self.ui.label_image.setPixmap(picture)
                self.RefImage_Current = picture
                self.RefImage_Default = picture_default
                self.LAST_BLENDSHAPE_INDEX = self.ui.listWidget_blendshape.currentRow()
                # KeyAnimation Mode일 경우 표정을 로드하는 대신에 이미 찍혀있는 프레임으로 이동시킨다
                if self.ui.cb_keyAnimationMode.checkState():
                    # auto selecting frame
                    cmds.currentTime(self.ui.listWidget_blendshape.currentRow())
                else:
                    # KeyAnimation Mode가 아닐 경우 표정을 로드 시킨다
                    self.Load_Pose_Key()





    def DeleteAll_KeyAnimation(self):
        snappers_rig_manager.selectAllSliders()
        cmds.cutKey()
        snappers_rig_manager.selectAllAdjustment()
        cmds.cutKey()
        cmds.select(cl=1)
        om.MGlobal.displayInfo(u'모든 프레임의 키를 제거하였습니다.')

    def Set_KeyAnimation(self):
        snappers_rig_manager.selectAllSliders()
        cmds.setKeyframe()
        snappers_rig_manager.selectAllAdjustment()
        cmds.setKeyframe()
        cmds.select(cl=1)
        if self.isKeyingPoseAsset:
            om.MGlobal.displayInfo(u'{} 키를 적용하였습니다.'.format(self.ui.listWidget_blendshape.item(int(cmds.currentTime(query=True))).text()))

        else:
            om.MGlobal.displayInfo(u'{} 키를 적용하였습니다.'.format(self.ui.listWidget_blendshape.currentItem().text()))
            if self.ui.cb_autoSaveExpression.isChecked():
                self.Save_Pose_Key()


    def Delete_KeyAnimation(self):
        pass


    # 시작할때 셋업하는 곳
    def set_ListView_Blendshapes(self):
        self.ui.listWidget_blendshape.clear()
        # default 등록
        self.ui.listWidget_blendshape.addItem('default')
        # ARKit의 블랜드쉐입 리스트를 리스트위젯에 담는다
        for idx, i in enumerate(ARKitBlendShapeList):
            self.ui.listWidget_blendshape.addItem(i)

        # 기본 이외의 블랜드쉐입을 추가하려면 아래에 추가해 주자
        if self.CustomBlendshapeList != []:
            for bs in self.CustomBlendshapeList:
                self.ui.listWidget_blendshape.addItem(bs)

        imagePath = os.path.join(os.path.dirname(imu.getPath_IMTool()), 'blendshapes', 'default.png')
        imagePath = imu.path_Cleanup(imagePath)
        picture = QtGui.QPixmap(imagePath)
        self.ui.label_image.setPixmap(picture)
        self.ui.label_image.setScaledContents(True)
        self.ui.label_image.setGeometry(QtCore.QRect(16, 16, 260, 160))



    # 
    def Load_PoseSet_Selected(self):
        posefile = imu.path_Cleanup(
            os.path.join(self.ui.lineEdit_PosePath.text(), self.ui.cb_headList.currentText() + '.pose'))
        if os.path.exists(posefile):
            try:
                d = shelve.open(posefile)
                # PoseSET 불러오기
                self.SNAPPERS_POSE_DIC = d['SNAPPERS_POSE_DIC']

                # 눈, 치아 위치를 머리별로 불러오기
                try:
                    if not d['RightEye'] == []:
                        cmds.setAttr('RightEye.translateX', d['RightEye'][0])
                        cmds.setAttr('RightEye.translateY', d['RightEye'][1])
                        cmds.setAttr('RightEye.translateZ', d['RightEye'][2])

                    if not d['LeftEye'] == []:
                        cmds.setAttr('LeftEye.translateX', d['LeftEye'][0])
                        cmds.setAttr('LeftEye.translateY', d['LeftEye'][1])
                        cmds.setAttr('LeftEye.translateZ', d['LeftEye'][2])

                    if not d['Teeth'] == []:
                        cmds.setAttr('Teeth.translateX', d['Teeth'][0])
                        cmds.setAttr('Teeth.translateY', d['Teeth'][1])
                        cmds.setAttr('Teeth.translateZ', d['Teeth'][2])
                except:
                    pass

                om.MGlobal.displayInfo(u'{} Pose파일을 잘 불러왔습니다.'.format(self.ui.cb_headList.currentText()))

                # 커스텀 블랜드쉐입이 있다면 불러와
                # 초기화
                self.CustomBlendshapeList = []
                if 'CustomBlendshapeList' in d.keys():
                    self.CustomBlendshapeList = d['CustomBlendshapeList']

                # ListWidget 다시 만듬
                self.set_ListView_Blendshapes()

                d.close()
                # Pose 파일을 불러온 후에 표정 자동 적용
                # if self.ui.listWidget_blendshape.currentItem().text() in ARKitBlendShapeList:
                #     self.Load_Pose_Key()
            except:
                om.MGlobal.displayError(u'{}을 불러오는데 실패했습니다.'.format(posefile))

    # pose 파일 불러오기, shift키와 함께 클릭하면 저장하기
    def Load_PoseSet_Default(self):
        if not cmds.objExists(self.SNAPPERS_HEAD):
            return
        if imu.isShiftModifier():
            try:
                d = shelve.open(os.path.join(imu.getPath_IMTool(),
                                             abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py',
                                                                                                          '.pose')))
                # 스내퍼 포즈 저장
                if self.SNAPPERS_POSE_DIC:
                    d['SNAPPERS_POSE_DIC'] = self.SNAPPERS_POSE_DIC

                # 눈, 치아 위치를 머리별로 저장
                if cmds.objExists('RightEye'):
                    d['RightEye'] = [cmds.getAttr('RightEye.translateX'), cmds.getAttr('RightEye.translateY'),
                                     cmds.getAttr('RightEye.translateZ')]
                if cmds.objExists('LeftEye'):
                    d['LeftEye'] = [cmds.getAttr('LeftEye.translateX'), cmds.getAttr('LeftEye.translateY'),
                                    cmds.getAttr('LeftEye.translateZ')]
                if cmds.objExists('Teeth'):
                    d['Teeth'] = [cmds.getAttr('Teeth.translateX'), cmds.getAttr('Teeth.translateY'),
                                  cmds.getAttr('Teeth.translateZ')]

                d.close()
                om.MGlobal.displayInfo(u'{} 잘 저장되었습니다.'.format(os.path.join(imu.getPath_IMTool(),
                                                                            abspath(getsourcefile(lambda: 0)).replace(
                                                                                "\\", "/").replace('.py', '.pose'))))
            except:
                om.MGlobal.displayError(u'{}을 저장하지 못했습니다.'.format(os.path.join(imu.getPath_IMTool(), abspath(
                    getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.pose'))))
        else:
            try:
                d = shelve.open(os.path.join(imu.getPath_IMTool(),
                                             abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py',
                                                                                                          '.pose')))
                self.SNAPPERS_POSE_DIC = d['SNAPPERS_POSE_DIC']
                try:
                    if not d['RightEye'] == []:
                        cmds.setAttr('RightEye.translateX', d['RightEye'][0])
                        cmds.setAttr('RightEye.translateY', d['RightEye'][1])
                        cmds.setAttr('RightEye.translateZ', d['RightEye'][2])

                    if not d['LeftEye'] == []:
                        cmds.setAttr('LeftEye.translateX', d['LeftEye'][0])
                        cmds.setAttr('LeftEye.translateY', d['LeftEye'][1])
                        cmds.setAttr('LeftEye.translateZ', d['LeftEye'][2])

                    if not d['Teeth'] == []:
                        cmds.setAttr('Teeth.translateX', d['Teeth'][0])
                        cmds.setAttr('Teeth.translateY', d['Teeth'][1])
                        cmds.setAttr('Teeth.translateZ', d['Teeth'][2])
                except:
                    pass
                d.close()
                om.MGlobal.displayInfo(u'기본 Pose 파일을 불러왔습니다.')

            except:
                om.MGlobal.displayError(u'기본 Pose파일을 불러오는데 실패하였습니다.')
            #self.Load_Pose_Key()


    def Load_Pose_Key(self):

        # 기본 표정일 경우
        if self.ui.listWidget_blendshape.currentItem().text() in ARKitBlendShapeList:
            if ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1] in self.SNAPPERS_POSE_DIC.keys():
                tempDic = self.SNAPPERS_POSE_DIC[ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1]]
                for i in tempDic:
                    cmds.setAttr(i, tempDic[i])

                if not self.isMakingBlendshapes:
                    ###################### ICT_neutral_mesh 레퍼런스용 ###################################
                    if cmds.objExists('ICT_neutral_mesh'):
                        bsMesh, bsNode, bsName = self.getBlendshapeNames('ICT_neutral_mesh')
                    else:
                        return
                    if not cmds.objExists(bsNode): return
                    # all set to 0
                    for bs in bsName:
                        cmds.setAttr(bsNode + '.' + bs, 0)
                    # mouseClose일 경우에만 하나 더 켜줘
                    if ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1] == 'mouthClose':
                        cmds.setAttr(bsNode + '.' + ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 2], 1)
                        cmds.setAttr('JawCntr.translateY',3.5)
                    cmds.setAttr(bsNode + '.' + ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1], 1)
                    ###################### ICT_neutral_mesh 레퍼런스용 ####################################


        # 커스텀 표정일 경우
        else:
            # 커스텀 리스트에 있다면
            if self.ui.listWidget_blendshape.currentItem().text() in self.CustomBlendshapeList:
                # 저장된 값이 있다면
                if self.ui.listWidget_blendshape.currentItem().text() in self.SNAPPERS_POSE_DIC.keys():
                    tempDic = self.SNAPPERS_POSE_DIC[self.ui.listWidget_blendshape.currentItem().text()]
                    for i in tempDic:
                        cmds.setAttr(i, tempDic[i])

                # 저장된 값이 없다면
                else:
                    om.MGlobal.displayWarning(u'아직 저장되어 있는 값이 없습니다.')
                if not self.isMakingBlendshapes:
                    ###################### ICT_neutral_mesh 레퍼런스용 ###################################
                    if cmds.objExists('ICT_neutral_mesh'):
                        bsMesh, bsNode, bsName = self.getBlendshapeNames('ICT_neutral_mesh')
                    else:
                        return
                    if not cmds.objExists(bsNode): return
                    # all set to 0
                    for bs in bsName:
                        cmds.setAttr(bsNode + '.' + bs, 0)
                    ###################### ICT_neutral_mesh 레퍼런스용 ####################################

            else:
                if self.ui.listWidget_blendshape.currentItem().text() == 'default':
                    self.FACSResetAll()
                    self.AdjustResetAll()

                    if not self.isMakingBlendshapes:
                        ###################### ICT_neutral_mesh 레퍼런스용 ###################################
                        if cmds.objExists('ICT_neutral_mesh'):
                            bsMesh, bsNode, bsName = self.getBlendshapeNames('ICT_neutral_mesh')
                        else:
                            return
                        if not cmds.objExists(bsNode): return
                        # all set to 0
                        for bs in bsName:
                            cmds.setAttr(bsNode + '.' + bs, 0)
                        ###################### ICT_neutral_mesh 레퍼런스용 ####################################



    # 현재 Pose 딕셔너리에 저장하기
    def Save_Pose_Key(self):
        # 우선 각각의 컨트롤러 값들을 tempDic에 저장한다
        # 여기서는 eye나 teeth의 위치값은 저장하지 않는다. 그건 file로 저장할 때만
        tempDic = {}

        # 닫은 입 예외처리 - 저장하기전에 0으로 맞추고
        if self.ui.listWidget_blendshape.currentItem().text() == 'mouthClose':
            cmds.setAttr('JawCntr.translateY', 0)

        for attr in self.CntrAttrMap:
            valueName = attr[0] + '.' + attr[1]
            value = cmds.getAttr(valueName)
            tempDic[valueName] = value

        # 기본 표정인 경우
        if self.ui.listWidget_blendshape.currentItem().text() in ARKitBlendShapeList:
            # Arkit에서 사용중인 블랜드쉐입 이름으로 표정수치값들을 딕셔너리에 저장시킨다 (-1은 default 때문에)
            self.SNAPPERS_POSE_DIC[ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX-1]] = tempDic

            # 닫은 입 예외처리, 저장하고 나서 다시 원래대로 열어놓는다
            if ARKitBlendShapeList[self.LAST_BLENDSHAPE_INDEX - 1] == 'mouthClose':
                cmds.setAttr('JawCntr.translateY', 3.5)

            om.MGlobal.displayInfo('Save Pose: {}'.format(self.ui.listWidget_blendshape.currentItem().text()))


        # 커스텀 표정인 경우
        else:
            #
            if self.ui.listWidget_blendshape.currentItem().text() in self.CustomBlendshapeList:
                self.SNAPPERS_POSE_DIC[self.ui.listWidget_blendshape.currentItem().text()] = tempDic
                om.MGlobal.displayInfo('Save Pose: {}'.format(self.ui.listWidget_blendshape.currentItem().text()))


    # pose 파일 저장하기
    def Save_PoseSet_ToFile(self):
        try:
            #filePath = os.path.join(imu.getPath_IMTool(), abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.pose'))
            if self.ui.lineEdit_PosePath.text() == '':
                om.MGlobal.displayWarning(u'Pose가 저장될 경로설정을 먼저 해주세요')
                return
            if self.ui.cb_headList.currentText() == '':
                om.MGlobal.displayWarning(u'저장할 Pose파일을 먼저 생성해 주세요')
                return
            filePath = imu.path_Cleanup(os.path.join(self.ui.lineEdit_PosePath.text(), self.ui.cb_headList.currentText()+'.pose'))
            d = shelve.open(filePath)
            # 스내퍼 포즈 저장
            if self.SNAPPERS_POSE_DIC:
                # if d['SNAPPERS_POSE_DIC'] in d.keys():
                #     d['SNAPPERS_POSE_DIC'] = {}
                d['SNAPPERS_POSE_DIC'] = self.SNAPPERS_POSE_DIC

            if self.CustomBlendshapeList:
                # if d['CustomBlendshapeList'] in d.keys():
                #     d['CustomBlendshapeList'] = []
                d['CustomBlendshapeList'] = self.CustomBlendshapeList
            else:
                d['CustomBlendshapeList'] = []

            # 눈, 치아 위치를 머리별로 저장
            if cmds.objExists('RightEye'):
                d['RightEye'] = [cmds.getAttr('RightEye.translateX'), cmds.getAttr('RightEye.translateY'), cmds.getAttr('RightEye.translateZ')]
            if cmds.objExists('LeftEye'):
                d['LeftEye'] = [cmds.getAttr('LeftEye.translateX'), cmds.getAttr('LeftEye.translateY'), cmds.getAttr('LeftEye.translateZ')]
            if cmds.objExists('Teeth'):
                d['Teeth'] = [cmds.getAttr('Teeth.translateX'), cmds.getAttr('Teeth.translateY'), cmds.getAttr('Teeth.translateZ')]

            d.close()
            #print 'Save Success: ', filePath
            om.MGlobal.displayInfo(u'{} 잘 저장되었습니다.'.format(filePath))
        except:
            om.MGlobal.displayError(u'{}을 저장하지 못했습니다.'.format(filePath))



    def viewDefaultImage(self):
        if self.RefImage_Default:
            self.ui.label_image.setPixmap(self.RefImage_Default)
            snappers_rig_manager.resetAllSliders()
            snappers_rig_manager.resetAllAdjustment()
            ###################### ICT_neutral_mesh 레퍼런스용 ###################################
            if cmds.objExists('ICT_neutral_mesh'):
                bsMesh, bsNode, bsName = self.getBlendshapeNames('ICT_neutral_mesh')
            else:
                return
            # all set to 0
            for bs in bsName:
                cmds.setAttr(bsNode + '.' + bs, 0)
            ###################### ICT_neutral_mesh 레퍼런스용 ####################################


    def viewOriginalImage(self):
        # 디폴드이미지 보기전에 선택했었던 이미지로 다시 보여주기
        if self.RefImage_Current:
            self.ui.label_image.setPixmap(self.RefImage_Current)
            self.Load_Pose_Key()

    # Snappers Select
    def selectFACSBrow(self):
        snappers_rig_manager.selectBrowsSliders()
    def selectFACSEye(self):
        snappers_rig_manager.selectEyeSliders()
    def selectFACSMouse(self):
        snappers_rig_manager.selectMouthSliders()
    def selectAdjustBrow(self):
        snappers_rig_manager.selectBrowsAdjustment()
    def selectAdjustEye(self):
        snappers_rig_manager.selectEyeAdjustment()
    def selectAdjustMouse(self):
        snappers_rig_manager.selectMouthAdjustment()
    def selectAllSliders(self):
        snappers_rig_manager.selectAllSliders()
    def selectAdjustAllSliders(self):
        snappers_rig_manager.selectAllAdjustment()
    def FACSResetAll(self):
        snappers_rig_manager.resetAllSliders()
    def AdjustResetAll(self):
        snappers_rig_manager.resetAllAdjustment()
    def showAdjustment(self):
        if self.SNAPPERS_ADJUST_ACTIVE:
            snappers_rig_manager.showHideAdjLayer(False)
            self.SNAPPERS_ADJUST_ACTIVE = False
        else:
            snappers_rig_manager.showHideAdjLayer(True)
            self.SNAPPERS_ADJUST_ACTIVE = True

    def showHideSliders(self):
        if imu.isShiftModifier():
            self.toggleNurbsCurves()
        else:
            if self.SNAPPERS_SLIDER_SHOW:
                snappers_rig_manager.showHideSliders(False)
                self.SNAPPERS_SLIDER_SHOW = False
            else:
                snappers_rig_manager.showHideSliders(True)
                self.SNAPPERS_SLIDER_SHOW = True

    # ------------------------------------------------------------------------------------------
    # Check Blendshape
    # ------------------------------------------------------------------------------------------

    def nextAvailableTargetIndex(self, blendShape):
        '''
        Get the next available blendShape target index
        @param blendShape: Name of blendShape to get next available target index for
        @type blendShape: str
        '''
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Get blendShape target list
        targetList = self.getTargetList(blendShape)
        if not targetList: return 0

        # Get last index
        lastIndex = self.getTargetIndex(blendShape,targetList[-1])
        nextIndex = lastIndex + 1

        # Return result
        return nextIndex

    def getTargetIndex(self, blendShape, target):
        '''
        Get the target index of the specified blendShape and target name
        @param blendShape: Name of blendShape to get target index for
        @type blendShape: str
        @param target: BlendShape target to get the index for
        @type target: str
        '''
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Check target
        if not cmds.objExists(blendShape+'.'+target):
            raise Exception('Blendshape "'+blendShape+'" has no target "'+target+'"!')

        # Get attribute alias
        aliasList = cmds.aliasAttr(blendShape,q=True)
        aliasIndex = aliasList.index(target)
        aliasAttr = aliasList[aliasIndex+1]

        # Get index
        targetIndex = int(aliasAttr.split('[')[-1].split(']')[0])

        # Return result
        return targetIndex

    def getTargetList(self, blendShape):
        '''
        Return the target list for the input blendShape
        @param blendShape: Name of blendShape to get target list for
        @type blendShape: str
        '''
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Get attribute alias
        targetList = cmds.listAttr(blendShape+'.w',m=True)
        if not targetList: targetList = []

        # Return result
        return targetList



    # ------------------------------------------------------------------------------------------
    # JBControlRig
    # ------------------------------------------------------------------------------------------

    def veiwBlendshapes(self):
        if self.ui.cb_ictOriginal.isChecked():
            BlendShapes = ICTBlendShapeList
        else:
            BlendShapes = ARKitBlendShapeList
        count=0
        print ''
        print '-----------------' + 'ARKit Blendshape List' + '-----------------'
        if imu.isShiftModifier():
            for idx, i in enumerate(BlendShapes):
                print i
                count += 1
            print '---------------------------------------------------------'
            print 'Count: {}'.format(count)
        else:
            print BlendShapes
            print '-------------------------------------------------------'


    def viewControlrig(self):
        if self.ui.cb_ictOriginal.isChecked():
            ControlRigs = JBControlRigList_v2
        else:
            ControlRigs = JBControlRigList
        count = 0
        print ''
        print '-----------------' + 'JBControlRig Shape List' + '-----------------'
        if imu.isShiftModifier():
            for idx, i in enumerate(ControlRigs):
                print i
                count += 1
            print '-----------------------------------------------------------'
            print 'Count: {}'.format(count)
        else:
            print ControlRigs
            print '---------------------------------------------------------'

    # 블렌드쉐입과 연결된 녀석들 리스트 뽑아주는 곳
    def getBlendshapeConnects(self):
        bsName = self.ui.lineEdit_blendshapenodeName.text()
        BSList = []
        CtrlList = []
        blendshapes = cmds.listAttr(bsName + '.w', m=True)
        for bs in blendshapes:
            connect = cmds.listConnections(bsName + '.' + bs, d=False, s=True, p=True)
            if connect:
                BSList.append(bsName + '.' + bs)
                CtrlList.append(connect[0])
        print BSList
        print CtrlList
        return BSList, CtrlList

    def printBSConnectInfo(self):
        count = 0
        print ''
        print '-----------------' + 'Connection with BlendshapeNode' + '-----------------'
        if imu.isShiftModifier():
            for bs, ctrl in zip(JBC_BSList, JBC_CtrlList):
                print '{0}.output -> {1}'.format(bs,ctrl)

            print '--------------------------------------------------------------'
            print 'Count: {}'.format(count)
        else:
            print JBC_BSList
            print JBC_CtrlList
            print '----------------------------------------------------------------'

    def printNoneBSList(self):
        if self.ui.cb_ictOriginal.isChecked():
            BlendShapes = ICTBlendShapeList
        else:
            BlendShapes = ARKitBlendShapeList
        count = 0
        for i in BlendShapes:
            if cmds.objExists(i):
                pass
            else:
                print u'없는 메쉬는 {} 입니다.'.format(i)
                count += 1
        if count == 0:
            print u'씬안에 모든 메쉬가 존재합니다.'
        else:
            print u'씬안에 {}개의 메쉬가 없습니다.'.format(count)

    def AddBlendshapeToOrder(self):
        if self.ui.cb_ictOriginal.isChecked():
            BlendShapes = ICTBlendShapeList
        else:
            BlendShapes = ARKitBlendShapeList
        selectedMesh = cmds.ls(sl=1)[0]
        if selectedMesh and cmds.objExists('eyeBlinkLeft'):
            cmds.blendShape('eyeBlinkLeft', selectedMesh)
            bsMesh, bsNode, bsNames = self.getBlendshapeNames(selectedMesh)
            for index, bs in enumerate(BlendShapes):
                if bs == 'eyeBlinkLeft':
                    continue
                cmds.blendShape(bsNode, e=1, t=[bsMesh, index, bs, 1])
                print 'Add {}'.format(bs)


    def printSelect(self):
        print cmds.ls(sl=1)

    def clearScriptEditor(self):
        cmds.scriptEditorInfo(clearHistory=True)

    def resetSlider(self):
        if self.ui.cb_ictOriginal.isChecked():
            ControlRigs = JBControlRigList_v2
        else:
            ControlRigs = JBControlRigList
        for slider in ControlRigs:
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

    def breakConnections(self):
        if self.ui.cb_ictOriginal.isChecked():
            BlendShapes = ICTBlendShapeList
        else:
            BlendShapes = ARKitBlendShapeList
        mesh = cmds.ls(sl=1)
        if not mesh:
            return
        count = 0
        meshHistory = cmds.listHistory(mesh)
        meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')
        if not meshBlendshapeNode:
            return

        for idx, attr in enumerate(BlendShapes):
            imu.BreakConnection(meshBlendshapeNode[0] + '.' + attr)
            count = idx

        print 'Complete! {0} break connections'.format(count)

    def importControlrigMayafile(self):
        if self.ui.cb_ictOriginal.isChecked():
            mayafile = 'JBControlRigV0.2.mb'
        else:
            mayafile = 'JBControlRigV0.1.ma'
        controlrigFile = imu.path_Cleanup(os.path.join(os.path.dirname(imu.getPath_IMTool()), mayafile))
        cmds.file(controlrigFile, i=True, ignoreVersion=True)



    # 연결하기
    def connectBsWithControl(self):
        if self.ui.cb_ictOriginal.isChecked():
            for bs, ctrl in zip(JBC_BSList, JBC_CtrlList):
                cmds.connectAttr(ctrl, bs)
                print bs, ctrl
        else:
            for info in JBControlConnectionInfo:
                sour = ''
                for index, node in enumerate(info):
                    if index % 2 == 0:
                        sour = node
                    else:
                        print 'Connect: {} -> {}'.format(node + '.output', sour)
                        cmds.connectAttr(node + '.output', sour)



    def autoControlRig(self):
        # 기존에 이미 리그오브젝트가 있다면 실행하지마
        if cmds.objExists('Face_Controllers_Root'):
            print u'이미 JBControlRig 가 있습니다.'
            return
        # Blendshape 오브젝트가 하나라도 있어야지 실행되
        if len(cmds.ls(type='blendShape')) > 0:
            self.importControlrigMayafile()
            self.connectBsWithControl()



    # ------------------------------------------------------------------------------------------
    # ARKit
    # ------------------------------------------------------------------------------------------
    def alignObjects(self):
        # 카테고리별로 분류
        #self.ui.cb_alignCategory.isChecked()

        if not cmds.ls(sl=1):
            return

        imu.AlignObjects(
            _sel=cmds.ls(sl=1),
            _startPos=(int(self.ui.lineEdit_startX.text()),int(self.ui.lineEdit_startY.text()),int(self.ui.lineEdit_startZ.text())),
            _useStartPosition=self.ui.cb_startPositionObject.isChecked(),
            _maxRows=int(self.ui.lineEdit_lineMaxCount.text()),
            _disX=int(self.ui.lineEdit_intervalX.text()),
            _disY=int(self.ui.lineEdit_intervalY.text())
        )

    def unlockTransform(self):
        if not cmds.ls(sl=1):
            return
        imu.unlockTransform()

    def lockTransform(self):
        if not cmds.ls(sl=1):
            return
        imu.lockTransform()

    def unBindSkin(self):
        if not cmds.ls(sl=1):
            return
        imu.unBindSkin()

    def matchTransformAll(self):
        if not cmds.ls(sl=1):
            return
        imu.matchTransform()

    def bindSkin(self):
        if not cmds.ls(sl=1):
            return
        imu.bindSkin()

    def resetBindPose(self):
        imu.getSelectedObjectSkinnedJoints()

    # 블랜드쉐입 오브젝트 등록
    def registBlendshapeObject(self):
        mesh = cmds.ls(sl=True)
        if not mesh:
            return

        meshHistory = cmds.listHistory(mesh)
        meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')

        if meshBlendshapeNode:
            self.BlendshapeMesh = mesh
            bsMesh, bsNode, bsName = self.getBlendshapeNames(self.BlendshapeMesh)
            self.ui.lineEdit_blendshapeCount.setText(str(len(bsName)))
            self.ui.lineEdit_meshName.setText(str(bsMesh[0]))
            self.ui.lineEdit_blendshapeName.setText(str(bsNode))
            # 체크용
            self.BlendshapeMesh = bsMesh[0]
            self.BlendshapeNode = bsNode
            self.ui.pb_addBlendshape.setStyleSheet(self.CompleteColor)
            self.ui.lineEdit_lastBlendshape.setText(str(len(bsName)))

        else:
            self.ui.lineEdit_blendshapeCount.setText(u'블랜드쉐입이 아닙니다.')
    def selectCurrentBSNode(self):
        if self.ui.lineEdit_blendshapeName.text():
            if cmds.objExists(self.ui.lineEdit_blendshapeName.text()):
                cmds.select(self.ui.lineEdit_blendshapeName.text())


    # CopyMode : 새 오브젝트 등록
    def registNewObject(self):
        if imu.isShiftModifier():
            self.AddMesh = ''
            self.ui.pb_addObject.setStyleSheet(self.ReadyColor)
            self.ui.pb_addNewObjectToBlendshape.setEnabled(False)
            self.ui.lineEdit_addObjectName.setText('')
        else:
            mesh = cmds.ls(sl=True)
            if self.BlendshapeMesh == '':
                self.ui.lineEdit_addObjectName.setText(u'블랜드쉐입 오브젝트를 먼저 등록해주세요.')
                return
            if not mesh:
                self.ui.lineEdit_addObjectName.setText(u'아무것도 선택하지 않았습니다.')
                return
            if self.BlendshapeMesh == mesh[0]:
                self.ui.lineEdit_addObjectName.setText(u'블랜드쉐입과 같은 오브젝트는 등록이 안됩니다.')
                return
            if cmds.polyEvaluate(self.BlendshapeMesh, f=True) == cmds.polyEvaluate(mesh[0], f=True):
                self.ui.lineEdit_addObjectName.setText(mesh[0])
                self.AddMesh = mesh[0]
                #print self.AddMesh
                self.ui.pb_addObject.setStyleSheet(self.CompleteColor)
                self.ui.pb_addNewObjectToBlendshape.setEnabled(True)
            else:
                self.ui.lineEdit_addObjectName.setText(u'폴리곤 개수가 틀립니다.')

    # CopyMode : 새오브젝트를 블랜드쉐입으로 추가
    def addNewObjectToBlendshape(self):
        if self.BlendshapeMesh and self.AddMesh:
            bsMesh, bsNode, bsName = self.getBlendshapeNames(self.BlendshapeMesh)
            if self.AddMesh not in bsName:
                cmds.select(self.BlendshapeMesh)
                index = self.nextAvailableTargetIndex(bsNode)
                cmds.blendShape(self.BlendshapeNode, e=1, t=[self.BlendshapeMesh, index, self.AddMesh, 1])
                self.ui.pb_removeNewObject.setEnabled(True)
                self.ui.Slider_addObjectWeight.setEnabled(True)
                self.isBlendshapeNewObject = True
                cmds.setAttr(bsNode + '.' + self.AddMesh, 1)
                # cmds.select(self.BlendshapeMesh)
                # self.registBlendshapeObject()
                # cmds.select(bsNode)

            else:
                om.MGlobal.displayError(u'{0}에 이미 {1}이 있습니다.'.format(bsNode, self.AddMesh))
    # CopyMode : 새오브젝트를 블랜드쉐입으로 추가
    def addNewObjectToBlendshapeIndex(self):
        if self.BlendshapeMesh and self.ui.lineEdit_bsName.text() and self.ui.lineEdit_availableIndex.text() and cmds.objExists(self.ui.lineEdit_bsName.text()):
            bsMesh, bsNode, bsNames = self.getBlendshapeNames(self.BlendshapeMesh)

            # 입력받는 인덱스가 추가 가능한 번호인지 검토
            availableIndex = list(range(0, self.nextAvailableTargetIndex(bsNode) + 1))
            for bs in bsNames:
                availableIndex.remove(self.getTargetIndex(bsNode, bs))
            if int(self.ui.lineEdit_availableIndex.text()) in availableIndex:
                if self.ui.lineEdit_bsName.text() not in bsNames:
                    cmds.select(self.BlendshapeMesh)
                    index = int(self.ui.lineEdit_availableIndex.text())
                    cmds.blendShape(self.BlendshapeNode, e=1, t=[self.BlendshapeMesh, index, self.ui.lineEdit_bsName.text(), 1])
                    self.ui.pb_removeNewObject.setEnabled(True)
                    self.ui.Slider_addObjectWeight.setEnabled(True)
                    self.isBlendshapeNewObject = True
                    cmds.setAttr(bsNode + '.' + self.ui.lineEdit_bsName.text(), 1)

                    #편리한 기능, bsNode 갱신해주고, 보여주고
                    # cmds.select(self.BlendshapeMesh)
                    # self.registBlendshapeObject()
                    # cmds.select(bsNode)
                    self.AddMesh = self.ui.lineEdit_bsName.text()
                else:
                    om.MGlobal.displayError(u'{0}에 이미 {1}이 있습니다.'.format(bsNode, self.AddMesh))
            else:
                om.MGlobal.displayError(u'인덱스: {}번 에는 추가할 수 없습니다.'.format(self.ui.lineEdit_availableIndex.text()))

        else:
            om.MGlobal.displayError(u'블렌드쉐입, 이름, 인덱스정보가 충분치 않습니다.')

    # CopyMode : 추출한 블랜드쉐입 오브젝트들 삭제
    def removeNewObjectFromBlendshape(self):
        # 선택한 녀석
        if self.BlendshapeMesh and self.AddMesh:
            # 블랜드쉐입 노드명 알아냄
            bsMesh, bsNode, bsName = self.getBlendshapeNames(self.BlendshapeMesh)

            if self.AddMesh in bsName:
                for index, bs in enumerate(bsName):
                    if bs == self.AddMesh:
                        cmds.blendShape(bsNode, e=1, rm=1, t=[bsMesh, self.getTargetIndex(bsNode, bs), bs, 1])
                        self.ui.lineEdit_bsName.setText('')
                        om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제했습니다.'.format(bsNode, bs))
                        cmds.select(bsNode)
            else:
                om.MGlobal.displayError(u'{0}에서 {1}를 찾을 수 없습니다.'.format(bsNode, self.AddMesh))

        else:
            om.MGlobal.displayError(u'오브젝트 등록을 해주세요.')




    def printBSList(self):
        '''
        등록된 녀석의 블랜드세입 리스트 출력
        :return:
        '''
        if self.BlendshapeMesh:

            bsMesh, bsNode, bsNames = self.getBlendshapeNames(self.BlendshapeMesh)

            # 특정 문자열을 포함한 리스트만 출력
            if self.ui.lineEdit_bsName.text():
                for bs in bsNames:
                    if self.ui.lineEdit_bsName.text() in bs:
                        print '{} : {}'.format(self.getTargetIndex(bsNode,bs), bs)

            else:
                # 모든 리스트 출력
                # 마지막인덱스까지 숫자를 리스트로 만들어 둔 다음
                availableIndex = list(range(0, self.nextAvailableTargetIndex(bsNode) + 1))
                for bs in bsNames:
                    print '{} : {}'.format(self.getTargetIndex(bsNode,bs), bs)
                    # 존재하는 블렌드쉐입의 Index를 지워주면
                    availableIndex.remove(self.getTargetIndex(bsNode, bs))
                    # 리스트에 남아있는 인덱스가 중간에 넣을 수 있는 인덱스 리스트가 된다
                print 'Available Index: {}'.format(availableIndex)
                # 모든 숫자를 str로 바꿔서 리스트에 다시 담는다
                strList = list(map(str, availableIndex))
                self.ui.lineEdit_availableIndex2.setText(str(','.join(strList)))


        else:
            om.MGlobal.displayError(u'블랜드쉐입 오브젝트를 먼저 등록해 주세요')

    # CopyMode 수동제거
    def delete_SelectedBS(self):
        if self.BlendshapeMesh and self.ui.lineEdit_bsName.text():
            bsMesh, bsNode, bsNames = self.getBlendshapeNames(self.BlendshapeMesh)
            if self.ui.lineEdit_bsName.text() in bsNames:
                for index, bs in enumerate(bsNames):
                    # 기존 스내퍼에서 사용하는 블랜드쉐입이 아니면 '아마도' 추가했던 메쉬겠지?
                    if bs == self.ui.lineEdit_bsName.text():
                        try:
                            cmds.blendShape(bsNode, e=1, rm=1, t=[bsMesh, self.getTargetIndex(bsNode, bs), bs, 1])
                            self.init_Snappers_Weights()
                            self.ui.lineEdit_bsName.setText('')
                            om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제했습니다.'.format(bsNode, bs))
                        except:
                            try:
                                self.delete_blendshape_target(bsNode, self.getTargetIndex(bsNode, bs))
                                self.init_Snappers_Weights()
                                self.ui.lineEdit_bsName.setText('')
                                om.MGlobal.displayInfo(u'{0}에서 {1}를 강제로 삭제했습니다.'.format(bsNode, bs))
                            except:
                                om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제하지 못했습니다.'.format(bsNode, bs))

            else:
                om.MGlobal.displayError(u'{}노드에서 {}는 찾을 수 없습니다.'.format(bsNode, self.ui.lineEdit_bsName.text()))
        else:
            om.MGlobal.displayWarning(u'삭제하고 싶은 블랜드쉐입이름을 적어 주세요.')






    # 기존 추가했던 메쉬를 추출
    def ExtractNewMesh(self):
        if not cmds.objExists(self.SNAPPERS_HEAD):
            return

        # reset
        snappers_rig_manager.resetAllSliders()
        snappers_rig_manager.resetAllAdjustment()

        # 선택한 녀석
        selected_blendshape = cmds.ls(sl=1)[0]
        if not selected_blendshape:
            om.MGlobal.displayWarning(u'새로 적용시킬 메쉬를 선택해주세요')
            return

        # 블랜드쉐입 노드명 알아냄
        bsMesh, bsNode, bsName = self.getBlendshapeNames(selected_blendshape)
        # 선택한게 블랜드 쉐입이 아니면
        if not bsNode:
            om.MGlobal.displayError(u' {}는 블랜드쉐입을 가지고 있지 않습니다.'.format(bsMesh))
            return

        # 추가한 메쉬가 있는지 알아보자. 없음 나가
        if len(bsName) == 620:
            print 'Nothing to extract mesh'
            return

        for bs in bsName:
            # 기존 스내퍼에서 사용하는 블랜드쉐입이 아니면 '아마도' 추가했던 메쉬겠지?
            if not bs in snappersBlendshape620:
                if cmds.objExists(bs):
                    om.MGlobal.displayError(u'이미 {} 이름의 동일한 오브젝트가 있습니다'.format(bs))
                    return
                else:
                    dup = cmds.duplicate(bsMesh)
                    renameDup = cmds.rename(dup, bs)
                    imu.unlockTransform(renameDup)
                    imu.setTranslate(renameDup,[-20,0,0])



    def selectBlendshapes(self):
        cmds.select(self.ExtractedBlendshapes)

    def deleteAllExtractedBlendshapes(self):
        cmds.delete(self.ExtractedBlendshapes)
        #self.ui.pb_selectBlendshapes.setEnabled(False)
        print 'Delete All Target OK!'

    # 블랜드쉐입 Weight 초기화
    def resetAllBlendshapeWeight(self):
        if self.BlendshapeMesh:
            bsMesh, bsNode, bsName = self.getBlendshapeNames(self.BlendshapeMesh)
        else:
            return
        # all set to 0
        for bs in bsName:
            print bs
            if bs == self.AddMesh:
                continue
            cmds.setAttr(bsNode + '.' + bs, 0)

    def addNewObjectWeight(self, value=0):
        if cmds.objExists(self.BlendshapeNode + '.' + self.AddMesh):
            cmds.setAttr(self.BlendshapeNode + '.' + self.AddMesh, (value*0.01))

    def Snappers_addNewObjectWeight(self, value=0):
        if self.is_head:
            cmds.setAttr('Head_blendShape.' + self.getFaceName() + '_head', (value * 0.01+0.01))
        if self.is_eyebrow:
            cmds.setAttr('eyebrowe_blendShape.' + self.getFaceName() + '_eyebrow', (value * 0.01+0.01))
        if self.is_eyelash:
            cmds.setAttr('eye_lashes_blendShape.' + self.getFaceName() + '_eyelash', (value * 0.01+0.01))
        if self.is_eye_AO:
            cmds.setAttr('ao_blendShape.' + self.getFaceName() + '_eye_AO', (value * 0.01+0.01))
        if self.is_head or self.is_eyebrow or self.is_eyelash or self.is_eye_AO:
            self.ui.label_Snappers_Weight.setText('Weight: {}'.format(value * 0.01+0.01))



    def rename_blendshape_target(self):
        bsMesh = self.BlendshapeMesh
        bsName = self.ui.lineEdit_bsName.text()
        rename_bsName = self.ui.lineEdit_bsRename.text()
        if bsMesh and bsName and rename_bsName:
            bsMesh, bsNode, bsNames = self.getBlendshapeNames(self.BlendshapeMesh)
            for bsIndex, bs in enumerate(bsNames):
                if bsName == bs:
                    try:

                        cmds.aliasAttr(rename_bsName, bsNode + '.weight[%s]' % self.getTargetIndex(bsNode, bs))
                        self.ui.lineEdit_bsName.setText('')
                        om.MGlobal.displayInfo(u'{}을 {}로 변경하였습니다.'.format(bsName, rename_bsName))
                    except:
                        om.MGlobal.displayError(u'변경하지 못했습니다.')
        else:
            om.MGlobal.displayError(u'bs메쉬, bs이름, 변경할 bs이름 모두 넣어주어야 합니다.')


    def delete_blendshape_target(self, bsNode, bsIndex):
        cmds.select(d=1)
        cmds.removeMultiInstance(bsNode + '.weight[%s]' % bsIndex, b=True)
        cmds.removeMultiInstance(bsNode +'.inputTarget[0].inputTargetGroup[%s]' % bsIndex, b=True)


    def getBlendshapeNames(self, mesh):
        # if self.BlendshapeMesh:
        #     cmds.select(self.BlendshapeMesh)
        # mesh = cmds.ls(sl=1)

        if not mesh:
            print('Select Blendshape Mesh')
            return

        meshHistory = cmds.listHistory(mesh)
        meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')[0]
        meshBlendshapeName = cmds.listAttr(meshBlendshapeNode + '.w', m=True)
        return mesh, meshBlendshapeNode, meshBlendshapeName

    # ICT, Polywink 블랜드쉐입 추출 ######################################################################
    def registedExtractBlendshapes(self):
        self.ExtractedBlendshapes = []
        combineMeshes = []
        BaseMesh = ''
        # 얼굴과 같이 합쳐지 Mesh들 미리 설정하는 곳
        # mesh_eyeR = 'Sam_Eye_Right'
        # mesh_eyeL = 'Sam_Eye_Left'
        # mesh_eyeLash = 'Sam_Eyelash'
        # mesh_teethUp = 'teeth'
        # mesh_teethDown = 'Sam_Teeth_Down'
        # mesh_teethTongue = 'Sam_Teeth_Tongue'

        # 헤드메쉬, 노드 List, 이름 List
        if not self.BlendshapeMesh:
            return
        bsMesh, bsNode, bsName = self.getBlendshapeNames(self.BlendshapeMesh)

        # 블렌드쉐입 초기화
        if cmds.objExists('Face_Ctrl'):
            self.resetSlider()
        for index, bs in enumerate(bsName):
            if bs == self.AddMesh:
                continue
            cmds.setAttr(bsNode + '.' + bs, 0)

        # 기본 얼굴
        #combineMeshes.append(cmds.duplicate(self.BlendshapeMesh)[0])
        # 눈
        # combineMeshes.append(cmds.duplicate(mesh_eyeR)[0])
        # combineMeshes.append(cmds.duplicate(mesh_eyeL)[0])
        # combineMeshes.append(cmds.duplicate(mesh_eyeLash)[0])
        # # 치아
        #combineMeshes.append(cmds.duplicate(mesh_teethUp)[0])
        # combineMeshes.append(cmds.duplicate(mesh_teethDown)[0])
        # combineMeshes.append(cmds.duplicate(mesh_teethTongue)[0])

        # 합치기
        # cmds.select(combineMeshes)
        # combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')

        #BaseMesh = cmds.rename(combined, self.AddMesh+'_Final')


        #combineMeshes = []

        for index, bs in enumerate(bsName):
            if bs == self.AddMesh:
                print u'건너뛰자!'
                continue
            if index >= int(self.ui.lineEdit_firstBlendshape.text())-1 and index <= int(self.ui.lineEdit_lastBlendshape.text())-1:
                cmds.setAttr(bsNode + '.' + bs, 1)

            ##얼굴
            # combineMeshes.append(cmds.duplicate(self.BlendshapeMesh)[0])
            ##눈
            # combineMeshes.append(cmds.duplicate(mesh_eyeR)[0])
            # combineMeshes.append(cmds.duplicate(mesh_eyeL)[0])
            # combineMeshes.append(cmds.duplicate(mesh_eyeLash)[0])
            ##치아
            # combineMeshes.append(cmds.duplicate(mesh_teethUp)[0])
            # combineMeshes.append(cmds.duplicate(mesh_teethDown)[0])
            # combineMeshes.append(cmds.duplicate(mesh_teethTongue)[0])


            #합치기
            #cmds.select(combineMeshes)
            #combined = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            combined = cmds.duplicate(self.BlendshapeMesh)
            finalMesh = cmds.rename(combined, bs)
            cmds.setAttr(bsNode + '.' + bs, 0)
            self.ExtractedBlendshapes.append(finalMesh)
            #combineMeshes =[]

        imu.AlignObjects(
            _sel=self.ExtractedBlendshapes,
            _startPos=(int(self.ui.lineEdit_startX.text()), int(self.ui.lineEdit_startY.text()),
                       int(self.ui.lineEdit_startZ.text())),
            _useStartPosition=False,
            _maxRows=int(self.ui.lineEdit_lineMaxCount.text()),
            _disX=int(self.ui.lineEdit_intervalX.text()),
            _disY=int(self.ui.lineEdit_intervalY.text())
        )

        #cmds.blendShape(self.ExtractedBlendshapes, BaseMesh)
        #self.ui.pb_selectBlendshapes.setEnabled(True)
        self.ui.pb_extractBlendshapes.setText('블랜드쉐입 추출  (마지막결과:{0}개)'.format(len(self.ExtractedBlendshapes)))

    def makeBlendshapes(self):
        dup = cmds.duplicate(self.AddMesh)
        cmds.blendShape(self.ExtractedBlendshapes, dup)
        reNamed = cmds.rename(dup, 'BS_Mesh_Result')
        # 최종 블랜드쉐입 만들기
        bsMesh, bsNode, bsNames = self.getBlendshapeNames(reNamed)
        cmds.rename(bsNode,'BS_node')

    def selectCounter(self):
        sel = cmds.ls(sl=1)
        self.ui.pb_counter.setText('갯수확인(결과:{0}개'.format(len(sel)))

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
        if imu.getPath_MayaFile():
            self.ui.line_filename.setText(
                imu.getName_MayaFile().replace('.mb', '').replace('.ma', '').replace('.fbx', '').strip())
        else:
            self.ui.line_filename.setText(u'현재 열린 파일이 없어요')


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

        if isOpen:
            self.open_file(self.file_path)
            print "Open!!!!!"
        else:
            self.import_file(self.file_path)
            print "import!!!!"


    def open_file(self, file_path):
        force = False
        if not force and cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, u"현재 파일이 수정되었음", u"현재 Scene을 저장하지 않고 그냥~ 열까요?")
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True
            else:
                return
        if file_path.lower().endswith('obj'):
            cmds.file(file_path, open=True, type="OBJ", rnn=True, ignoreVersion=True, options="mo=0", force=force)
        else:
            cmds.file(file_path, open=True, ignoreVersion=True, force=force)

    def import_file(self, file_path):
        if file_path.lower().endswith('obj'):
            cmds.file(file_path, i=True, type="OBJ", rnn=True, ignoreVersion=True, options="mo=0")
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
        self.head = self.ui.tree_wdg.header()
        self.head.sectionClicked.connect(self.tree_clickEvent)
        #self.ui.tree_wdg.sectionClicked.connect(self.tree_clickEvent)
        self.open_in_folder_action = QtWidgets.QAction(u"Open", self)
        self.import_in_folder_action = QtWidgets.QAction(u"Import", self)
        self.set_in_folder_action = QtWidgets.QAction(u"Set to Export Folder", self)
        self.make_in_folder_action = QtWidgets.QAction(u"폴더생성", self)
        self.show_in_folder_action = QtWidgets.QAction(u"탐색창 열기", self)
        self.create_in_folder_action = QtWidgets.QAction(u"작업폴더만들기", self)
        self.checkout_in_folder_action = QtWidgets.QAction(u"Checkout file", self)
        self.refresh_list()

    def tree_clickEvent(self,item):
        # print ('clicked item: ',item.text(0))
        self.LASTITEMINDEX = QtCore.QModelIndex(self.ui.tree_wdg.selectedIndexes()[0])
        self.CURRENTITEM = self.ui.tree_wdg.currentItem()



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
    def on_new_scene(self, client_data):
        self.load_info()
        self.BlendshapeMesh = ''
        self.AddMesh = ''
        self.ExtractedBlendshapes = []
        print"Changed file"


    def callback_init(self):
        try:
            self.callback_id = om.MEventMessage.addEventCallback("SceneOpened", self.on_new_scene)
            self.callback_id2 = om.MEventMessage.addEventCallback("timeChanged", self.on_ChangeFrame)

        except:
            print 'error : callback init'


    def closeEvent(self, *event):
        # removes the callback from memory
        try:
            print 'Close Blendshape Maker'
            self.Save_WindowOption()
            om.MMessage.removeCallback(self.callback_id)
            om.MMessage.removeCallback(self.callback_id2)
        except:
            pass

    def toggleNurbsCurves(self):
        try:

            myPanel = cmds.getPanel(withFocus=True)

            if (cmds.modelEditor(myPanel, query=True, nurbsCurves=True)):
                cmds.modelEditor(myPanel, edit=True, nurbsCurves=False)
            else:
                cmds.modelEditor(myPanel, edit=True, nurbsCurves=True)
        except:
            pass

    # ------------------------------------------------------------------------------------------
    # Shelve 저장
    # ------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------------
    # Save Options
    # ---------------------------------------------------------------------------------------------------
    def Save_WindowOption(self):
        try:
            d = shelve.open(os.path.join(imu.getPath_IMTool(), abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.conf')))

            # 블렌드쉐입 추출
            d['cb_alignCategory'] = self.ui.cb_alignCategory.isChecked()
            d['cb_startPositionObject'] = self.ui.cb_startPositionObject.isChecked()
            d['lineEdit_startX'] = self.ui.lineEdit_startX.text()
            d['lineEdit_startY'] = self.ui.lineEdit_startY.text()
            d['lineEdit_startZ'] = self.ui.lineEdit_startZ.text()
            d['lineEdit_intervalX'] = self.ui.lineEdit_intervalX.text()
            d['lineEdit_intervalY'] = self.ui.lineEdit_intervalY.text()
            d['lineEdit_lineMaxCount'] = self.ui.lineEdit_lineMaxCount.text()
            d['cb_removeAddObject'] = self.ui.cb_removeAddObject.isChecked()
            d['cb_applyMaterialCategory'] = self.ui.cb_applyMaterialCategory.isChecked()

            # Snappers
            d['lineEdit_PosePath'] = self.ui.lineEdit_PosePath.text() # Pose 루트폴더
            d['SNAPPERS_POSESET_LASTINDEX'] = self.SNAPPERS_POSESET_LASTINDEX

            d['cb_brow'] = self.ui.cb_brow.isChecked()
            d['cb_eyelash'] = self.ui.cb_eyelash.isChecked()
            d['cb_eyeAO'] = self.ui.cb_eyeAO.isChecked()
            d['cb_eyes'] = self.ui.cb_eyes.isChecked()
            d['cb_teeth'] = self.ui.cb_teeth.isChecked()

            #기타 저장할 것들
            d['cb_autoSaveExpression'] = self.ui.cb_autoSaveExpression.isChecked()
            d['cb_autoRegist'] = self.ui.cb_autoRegist.isChecked()
            d['cb_deleteBlendshapeAfter'] = self.ui.cb_deleteBlendshapeAfter.isChecked()

            # ICT 저장할것들
            d['lineEdit_ICT_IdentityPath'] = self.ui.lineEdit_ICT_IdentityPath.text()


            d['DIRECTORY_PATH_LIST'] = self.DIRECTORY_PATH_LIST  # 작업폴더
            d['COMBOBOX_LASTINDEX'] = self.WorkFolder_LASTINDEX  # 작업폴더



            d.close()
        except:
            print 'Error: Save Option'

    # ---------------------------------------------------------------------------------------------------
    # Load Options
    # ---------------------------------------------------------------------------------------------------
    def Load_WindowOption(self):
        try:
            d = shelve.open(
                os.path.join(imu.getPath_IMTool(),
                             abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.conf')),
                'r'
            )
            # 블렌드쉐입 추출 옵션 불러오기
            self.ui.cb_alignCategory.setChecked(d['cb_alignCategory'])
            self.ui.cb_startPositionObject.setChecked(d['cb_startPositionObject'])
            self.ui.lineEdit_startX.setText(d['lineEdit_startX'])
            self.ui.lineEdit_startY.setText(d['lineEdit_startY'])
            self.ui.lineEdit_startZ.setText(d['lineEdit_startZ'])
            self.ui.lineEdit_intervalX.setText(d['lineEdit_intervalX'])
            self.ui.lineEdit_intervalY.setText(d['lineEdit_intervalY'])
            self.ui.lineEdit_intervalY.setText(d['lineEdit_intervalY'])
            self.ui.lineEdit_lineMaxCount.setText(d['lineEdit_lineMaxCount'])
            self.ui.cb_removeAddObject.setChecked(d['cb_removeAddObject'])
            self.ui.cb_applyMaterialCategory.setChecked(d['cb_applyMaterialCategory'])

            # Snappers
            self.ui.lineEdit_PosePath.setText(d['lineEdit_PosePath'])  # Pose 루트폴더

            # 기타 불러올 것들
            self.ui.cb_autoSaveExpression.setChecked(d['cb_autoSaveExpression'])
            self.ui.cb_autoRegist.setChecked(d['cb_autoRegist'])
            self.ui.cb_deleteBlendshapeAfter.setChecked(d['cb_deleteBlendshapeAfter'])


            # PoseSET 파일 콤보박스에 추가하고, 안의 설정값 불러오기
            if os.path.exists(d['lineEdit_PosePath']):
                poseFiles = cmds.getFileList(folder=d['lineEdit_PosePath'], filespec='*.pose')
                #print poseFiles
                if poseFiles:
                    for pose in poseFiles:
                        self.ui.cb_headList.addItem(pose.split('.')[0])
                    self.SNAPPERS_POSESET_LASTINDEX = d['SNAPPERS_POSESET_LASTINDEX']
                    self.ui.cb_headList.setCurrentIndex(self.SNAPPERS_POSESET_LASTINDEX)
                    self.select_PoseFile(0)
                    
            else:
                self.Load_PoseSet_Default() #기본Pose파일을 불러온다


            # ICT Identity 파일이 있을 경우 리스트위젯에 불러온다
            self.ui.lineEdit_ICT_IdentityPath.setText(d['lineEdit_ICT_IdentityPath'])
            if os.path.exists(d['lineEdit_ICT_IdentityPath']):
                identityFiles = cmds.getFileList(folder=d['lineEdit_ICT_IdentityPath'], filespec='*.identity')
                if identityFiles:
                    for i in identityFiles:
                        self.ui.listWidget_ICT_IdentityList.addItem(i.split('.')[0])


            # 추출 메쉬 추가항목
            self.ui.cb_brow.setChecked(d['cb_brow'])
            self.ui.cb_eyelash.setChecked(d['cb_eyelash'])
            self.ui.cb_eyeAO.setChecked(d['cb_eyeAO'])
            self.ui.cb_eyes.setChecked(d['cb_eyes'])
            self.ui.cb_teeth.setChecked(d['cb_teeth'])

            # 다시 열었을 때 NewMesh 자동등록
            if cmds.objExists('Head_geo'):
                bsMesh, bsNode, bsNames = self.getBlendshapeNames('Head_geo')
                for bsname in bsNames:
                    if bsname not in snappersBlendshape620:
                        if cmds.objExists(bsname):
                            self.SNAPPERS_NEWMESH = self.getFaceName()




            # 작업폴더 불러오기
            self.DIRECTORY_PATH_LIST = d['DIRECTORY_PATH_LIST']
            self.WorkFolder_LASTINDEX = d['COMBOBOX_LASTINDEX']

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

            d.close()

        except:
            print 'Error: Load Option'

    def export_obj(self):
        selected = cmds.ls(sl=1)
        exportPath = imu.path_Cleanup(self.ui.line_exportfolder.text())
        exportFileName = self.ui.line_filename.text()

        #########################################################################
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
        #########################################################################


        # 혹시 경로가 존재하지 않다면 만들어라
        if not os.path.exists(os.path.dirname(exportPath)):
            os.makedirs(os.path.dirname(exportPath))

        self.objExport(path=exportPath,filename=self.ui.line_filename.text(),separate=self.ui.cb_isSeparateExport.isChecked(),zero=self.ui.cb_MoveToOrigin.isChecked())
        self.changed_workfolder()


    def objExport(self, path='', filename='', separate=True, zero=True):
        '''
        :param path: 익스포트 경로
        :param filename: 파일 이름, 나눠서 출력하지 않을 경우만 필요
        :param separate: 나눠서 익스포트 할지
        :param zero: 익스포트 직전에 0점에 맞추고 제자리로 돌려놓음
        :return:
        '''

        #기존 위치로 돌려주기 위해
        translate = []


        # 오브젝트 선택 되어 있는지 체크
        sel = cmds.ls(sl=1)
        if not sel:
            print u'익스포트 실패: 선택한 오브젝트가 없습니다'
            return

        # 경로가 설정 되어 있는지 체크
        if not path:
            print u'익스포트 경로가 설정되어 있지 않습니다'
            return

        # 각각 나눠서 익스포트 시킬려면
        if separate:
            cmds.select(clear=1)

            for i in sel:

                # 기존 위치값 저장
                if zero:
                    translate = imu.getTranslate(i)
                    imu.zero(i)

                #폴더가 없다면 만들기
                imu.makefolder(path)

                # 하나씩 obj 익스포트 시키기
                path_result = os.path.join(path, i + '.obj')
                cmds.select(i)
                cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                          op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")

                # 원래 위치값으로 돌림
                if zero:
                    imu.setTranslate(i, translate)

                print path_result
            print "Finish!!"

        # 하나의 파일로 익스포트 시키기, 이녀석은 0점으로 맞추면 안된다
        else:
            if not filename:
                print u'파일이름이 없어서 익스포트 시키지 못했습니다.'
                return
            else:
                path_result = os.path.join(path, filename + '.obj')
                # 폴더가 없다면 만들기
                imu.makefolder(path)

                cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                          op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
                print path_result
                print "Finish!!"



    def export_fbx(self):
        #sys.stdout.write('# Preparing to write FBX file...\n')

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

    def copy_blendshapes(self):
        mesh = cmds.ls(sl=1)[0]
        if mesh:
            self.resetSlider()
            BS_Node_Name = self.ui.lineEdit_blendshapenodeName.text()
            if self.ui.cb_ictOriginal.isChecked():
                meshBlendshapeNames = ICTBlendShapeList
            else:
                meshBlendshapeNames = ARKitBlendShapeList
                #meshBlendshapeNames = cmds.listAttr(BS_Node_Name + '.w', m=True)

            for index, bs in enumerate(meshBlendshapeNames):
                if cmds.objExists(bs):
                    print u'미리 만들어 둔건 건너뛰자! : ', bs
                    continue
                cmds.setAttr(BS_Node_Name + '.' + bs, 1)
                # 복사
                dup = cmds.duplicate(mesh)
                cmds.setAttr(BS_Node_Name + '.' + bs, 0)
                cmds.rename(dup, bs)

    def make_7885(self):
        pass


    def make_7887(self):
        sel = cmds.ls(sl=1)[0]
        cmds.polySplitVertex(sel + '.vtx[3464]', sel + '.vtx[3465]')

        vfList = cmds.polyListComponentConversion(sel + '.f[7387]', ff=True, tvf=True)
        vfList = cmds.ls(vfList, flatten=True)
        vfList2 = cmds.polyListComponentConversion(sel + '.f[7383]', ff=True, tvf=True)
        vfList += cmds.ls(vfList2, flatten=True)
        cmds.select(vfList)
        cmds.polyMergeVertex(d=0.25)

        vfList = cmds.polyListComponentConversion(sel + '.f[7927]', ff=True, tvf=True)
        vfList = cmds.ls(vfList, flatten=True)
        vfList2 = cmds.polyListComponentConversion(sel + '.f[7923]', ff=True, tvf=True)
        vfList += cmds.ls(vfList2, flatten=True)
        cmds.select(vfList)
        cmds.polyMergeVertex(d=0.25)

        vfList = cmds.polyListComponentConversion(sel + '.f[7383]', ff=True, tvf=True)
        vfList = cmds.ls(vfList, flatten=True)
        vfList2 = cmds.polyListComponentConversion(sel + '.f[7397]', ff=True, tvf=True)
        vfList += cmds.ls(vfList2, flatten=True)
        cmds.select(vfList)
        cmds.polyMergeVertex(d=0.25)

        vfList = cmds.polyListComponentConversion(sel + '.f[7923]', ff=True, tvf=True)
        vfList = cmds.ls(vfList, flatten=True)
        vfList2 = cmds.polyListComponentConversion(sel + '.f[7937]', ff=True, tvf=True)
        vfList += cmds.ls(vfList2, flatten=True)
        cmds.select(vfList)
        cmds.polyMergeVertex(d=0.25)
        '''
        
sel = cmds.ls(sl=1)[0]
cmds.polySplitVertex(sel + '.vtx[4042]', sel + '.vtx[4043]')

vfList = cmds.polyListComponentConversion(sel + '.f[7923]', ff=True, tvf=True)
vfList = cmds.ls(vfList, flatten=True)
vfList2 = cmds.polyListComponentConversion(sel + '.f[7927]', ff=True, tvf=True)
vfList += cmds.ls(vfList2, flatten=True)
cmds.select(vfList)
cmds.polyMergeVertex(d=0.25)

vfList = cmds.polyListComponentConversion(sel + '.f[7923]', ff=True, tvf=True)
vfList = cmds.ls(vfList, flatten=True)
vfList2 = cmds.polyListComponentConversion(sel + '.f[7937]', ff=True, tvf=True)
vfList += cmds.ls(vfList2, flatten=True)
cmds.select(vfList)
cmds.polyMergeVertex(d=0.25)

vfList = cmds.polyListComponentConversion(sel + '.f[3942]', ff=True, tvf=True)
vfList = cmds.ls(vfList, flatten=True)
vfList2 = cmds.polyListComponentConversion(sel + '.f[3946]', ff=True, tvf=True)
vfList += cmds.ls(vfList2, flatten=True)
cmds.select(vfList)
cmds.polyMergeVertex(d=0.25)

vfList = cmds.polyListComponentConversion(sel + '.f[3942]', ff=True, tvf=True)
vfList = cmds.ls(vfList, flatten=True)
vfList2 = cmds.polyListComponentConversion(sel + '.f[3956]', ff=True, tvf=True)
vfList += cmds.ls(vfList2, flatten=True)
cmds.select(vfList)
cmds.polyMergeVertex(d=0.25)
        '''




if __name__ == "__main__":
    try:
        imblendshapemaker.close()
        imblendshapemaker.deleteLater()
    except:
        pass

    imblendshapemaker = DesignerUI()
    imblendshapemaker.show()
