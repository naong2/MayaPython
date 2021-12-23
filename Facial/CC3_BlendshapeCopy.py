# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import socket
import pymel.core as pm

import os
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from inspect import getsourcefile
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr


class DesignerUI(QtWidgets.QDialog):

    # AutoRig용 마야 파일
    CONTROLRIG_MAYA_FILE = r'C:\Users\naong\Documents\maya\2020\scripts\IMTool\IMUtility\JBControlRigV0.2.mb'
    
    ICTBlendShapeList = ['eyeBlinkLeft', 'eyeBlinkRight', 'eyeLookDownLeft', 'eyeLookDownRight', 'eyeLookInLeft',
                         'eyeLookInRight', 'eyeLookOutLeft', 'eyeLookOutRight', 'eyeLookUpLeft', 'eyeLookUpRight',
                         'eyeSquintLeft', 'eyeSquintRight', 'eyeWideLeft', 'eyeWideRight', 'browDownLeft',
                         'browDownRight', 'browInnerUp', 'browInnerUpLeft', 'browInnerUpRight', 'browOuterUpLeft',
                         'browOuterUpRight', 'jawOpen', 'jawRight', 'jawForward', 'jawLeft', 'mouthClose',
                         'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthFunnel',
                         'mouthLeft', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight',
                         'mouthPucker', 'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
                         'mouthShrugUpper', 'mouthSmileLeft', 'mouthSmileRight', 'mouthStretchLeft',
                         'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'cheekPuff', 'cheekPuffLeft',
                         'cheekPuffRight', 'cheekRaiserLeft', 'cheekRaiserRight', 'cheekSquintLeft', 'cheekSquintRight',
                         'noseSneerLeft', 'noseSneerRight', 'tongueOut']

    # 블렌드쉐입을 추가하고, Merge시켜질 애들리스트
    otherMeshes = ['cc_base_eye', 'cc_base_teeth', 'cc_base_tongue', 'cc_base_tearline', 'cc_base_eyeocclusion',
                   'combine_eyePoint', 'combine_eyelash_upper', 'combine_eyelash_lower']
    hairMeshes = []
    result_hairMeshes = []
    Face = [u'cc_base_body1.f[0:1637]', u'cc_base_body1.f[1668:3690]', u'cc_base_body1.f[3721:4157]']
    EyelashUpper = [u'cc_base_body1.f[13513:13538]', u'cc_base_body1.f[13540:13583]', u'cc_base_body1.f[13638:13642]',
                    u'cc_base_body1.f[13647:13651]', u'cc_base_body1.f[13655:13734]', u'cc_base_body1.f[13813:13838]',
                    u'cc_base_body1.f[13840:13883]', u'cc_base_body1.f[13938:13942]', u'cc_base_body1.f[13947:13951]',
                    u'cc_base_body1.f[13955:14034]']
    EyelashLower = [u'cc_base_body1.f[13446:13512]', u'cc_base_body1.f[13539]', u'cc_base_body1.f[13584:13637]',
                    u'cc_base_body1.f[13643:13646]', u'cc_base_body1.f[13652:13654]',
                    u'cc_base_body1.f[13735:13812]', u'cc_base_body1.f[13839]', u'cc_base_body1.f[13884:13937]',
                    u'cc_base_body1.f[13943:13946]', u'cc_base_body1.f[13952:13954]',
                    u'cc_base_body1.f[14035:14045]']
    EyePoint = [u'cc_base_body1.f[1638:1667]', u'cc_base_body1.f[3691:3720]']

    JBControlRigList_v2 = [u'mouth_press_R_ctl', u'mouth_press_L_ctl', u'cheekRaiser_R_ctl', u'eyelid_Up_L_ctl',
                           u'eyeSquint_R_ctl', u'eyeSquint_L_ctl', u'mouthPucker_ctl', u'mouthDimple_L_ctl',
                           u'cheekRaiser_L_ctl', u'cheekSquint_L_ctl', u'cheekSquint_R_ctl', u'browOuterUp_L_ctl',
                           u'browOuterUp_R_ctl', u'browInnerUp_L_ctl', u'browInnerUp_R_ctl', u'eyelid_Up_R_ctl',
                           u'eye_control', u'mouthClose_ctl', u'mouth_end_R_ctrl', u'mouth_end_L_ctrl',
                           u'mouthLowerDown_R_ctl', u'cheekPuff_R_ctl', u'cheekPuff_L_ctl', u'noseSneer_R_ctl',
                           u'noseSneer_L_ctl', u'jaw_ctl', u'mouthDimple_R_ctl', u'mouth_L_R_ctl',
                           u'mouthLowerDown_L_ctl', u'mouthShrugLower_ctl', u'mouthShrugUpper_ctl',
                           u'mouthUpperUp_R_ctl', u'mouthUpperUp_L_ctl', u'mouthRollUpper_ctl', u'mouthFunnel_ctl',
                           u'mouthRollLower_ctl', u'Jaw_F_ctl']

    # Control rig와 Blendshape 연결 정보
    JBControlConnectionInfo = [[u'BS_node.eyeBlinkLeft', u'BS_node_eyeBlinkLeft'],
                               [u'BS_node.eyeLookDownLeft', u'BS_node_eyeLookDownLeft'],
                               [u'BS_node.eyeLookInLeft', u'BS_node_eyeLookInLeft'],
                               [u'BS_node.eyeLookOutLeft', u'BS_node_eyeLookOutLeft'],
                               [u'BS_node.eyeLookUpLeft', u'BS_node_eyeLookUpLeft'],
                               [u'BS_node.eyeSquintLeft', u'BS_node_eyeSquintLeft'],
                               [u'BS_node.eyeWideLeft', u'BS_node_eyeWideLeft'],
                               [u'BS_node.eyeBlinkRight', u'BS_node_eyeBlinkRight'],
                               [u'BS_node.eyeLookDownRight', u'BS_node_eyeLookDownRight'],
                               [u'BS_node.eyeLookInRight', u'BS_node_eyeLookInRight'],
                               [u'BS_node.eyeLookOutRight', u'BS_node_eyeLookOutRight'],
                               [u'BS_node.eyeLookUpRight', u'BS_node_eyeLookUpRight'],
                               [u'BS_node.eyeSquintRight', u'BS_node_eyeSquintRight'],
                               [u'BS_node.eyeWideRight', u'BS_node_eyeWideRight'],
                               [u'BS_node.jawForward', u'BS_node_jawForward'], [u'BS_node.jawLeft', u'BS_node_jawLeft'],
                               [u'BS_node.jawRight', u'BS_node_jawRight'], [u'BS_node.jawOpen', u'BS_node_jawOpen'],
                               [u'BS_node.mouthClose', u'BS_node_mouthClose'],
                               [u'BS_node.mouthFunnel', u'blendWeighted2'], [u'BS_node.mouthPucker', u'blendWeighted3'],
                               [u'BS_node.mouthRight', u'BS_node_mouthRight'],
                               [u'BS_node.mouthLeft', u'BS_node_mouthLeft'],
                               [u'BS_node.mouthSmileLeft', u'BS_node_mouthSmileLeft'],
                               [u'BS_node.mouthSmileRight', u'BS_node_mouthSmileRight'],
                               [u'BS_node.mouthFrownRight', u'BS_node_mouthFrownRight'],
                               [u'BS_node.mouthFrownLeft', u'BS_node_mouthFrownLeft'],
                               [u'BS_node.mouthDimpleLeft', u'BS_node_mouthDimpleLeft'],
                               [u'BS_node.mouthDimpleRight', u'BS_node_mouthDimpleRight'],
                               [u'BS_node.mouthStretchLeft', u'BS_node_mouthStretchLeft'],
                               [u'BS_node.mouthStretchRight', u'BS_node_mouthStretchRight'],
                               [u'BS_node.mouthRollLower', u'BS_node_mouthRollLower'],
                               [u'BS_node.mouthRollUpper', u'BS_node_mouthRollUpper'],
                               [u'BS_node.mouthShrugLower', u'blendWeighted4'],
                               [u'BS_node.mouthShrugUpper', u'BS_node_mouthShrugUpper'],
                               [u'BS_node.mouthLowerDownLeft', u'BS_node_mouthLowerDownLeft'],
                               [u'BS_node.mouthLowerDownRight', u'BS_node_mouthLowerDownRight'],
                               [u'BS_node.mouthUpperUpLeft', u'BS_node_mouthUpperUpLeft'],
                               [u'BS_node.mouthUpperUpRight', u'BS_node_mouthUpperUpRight'],
                               [u'BS_node.browDownLeft', u'BS_node_browDownLeft1'],
                               [u'BS_node.browDownRight', u'BS_node_browDownRight'],
                               [u'BS_node.browInnerUp', u'BS_node_browInnerUp'],
                               [u'BS_node.browOuterUpLeft', u'BS_node_browOuterUpLeft1'],
                               [u'BS_node.browOuterUpRight', u'BS_node_browOuterUpRight'],
                               [u'BS_node.cheekPuff', u'BS_node_cheekPuff'],
                               [u'BS_node.cheekSquintLeft', u'BS_node_cheekSquintLeft'],
                               [u'BS_node.cheekSquintRight', u'blendWeighted1'],
                               [u'BS_node.noseSneerLeft', u'BS_node_noseSneerLeft'],
                               [u'BS_node.noseSneerRight', u'BS_node_noseSneerRight'],
                               [u'BS_node.tongueOut', u'BS_node_tongueOut']]

    # Control rig와 Blendshape 연결 정보 ICT 최신 컨트롤 리그 2020년 12월9일 추가
    JBC_BSList = [u'BS_node.mouthFrownLeft', u'BS_node.mouthDimpleRight', u'BS_node.mouthDimpleLeft',
                  u'BS_node.mouthClose', u'BS_node.jawRight', u'BS_node.jawOpen', u'BS_node.jawLeft',
                  u'BS_node.jawForward', u'BS_node.mouthFunnel', u'BS_node.mouthFrownRight', u'BS_node.eyeWideRight',
                  u'BS_node.cheekRaiserLeft', u'BS_node.cheekPuffRight', u'BS_node.cheekPuffLeft',
                  u'BS_node.browOuterUpRight', u'BS_node.browOuterUpLeft', u'BS_node.browInnerUpRight',
                  u'BS_node.browInnerUpLeft', u'BS_node.browDownRight', u'BS_node.browDownLeft',
                  u'BS_node.noseSneerRight', u'BS_node.noseSneerLeft', u'BS_node.mouthUpperUpRight',
                  u'BS_node.mouthUpperUpLeft', u'BS_node.mouthStretchRight', u'BS_node.mouthStretchLeft',
                  u'BS_node.eyeLookInLeft', u'BS_node.eyeLookDownRight', u'BS_node.eyeLookDownLeft',
                  u'BS_node.eyeBlinkRight', u'BS_node.eyeBlinkLeft', u'BS_node.cheekSquintRight',
                  u'BS_node.cheekSquintLeft', u'BS_node.cheekRaiserRight', u'BS_node.eyeWideLeft',
                  u'BS_node.eyeSquintRight', u'BS_node.eyeSquintLeft', u'BS_node.eyeLookUpRight',
                  u'BS_node.eyeLookUpLeft', u'BS_node.eyeLookOutRight', u'BS_node.eyeLookOutLeft',
                  u'BS_node.eyeLookInRight', u'BS_node.mouthPucker', u'BS_node.mouthLowerDownRight',
                  u'BS_node.mouthPressRight', u'BS_node.mouthPressLeft', u'BS_node.mouthRollLower',
                  u'BS_node.mouthRight', u'BS_node.mouthRollUpper', u'BS_node.mouthSmileLeft',
                  u'BS_node.mouthShrugUpper', u'BS_node.mouthShrugLower', u'BS_node.mouthSmileRight',
                  u'BS_node.mouthLowerDownLeft', u'BS_node.mouthLeft']
    JBC_CtrlList = [u'blendShape1_mouthFrown_L_Mesh.output', u'mouthDimple_R_ctl.translateY',
                    u'mouthDimple_L_ctl.translateY', u'mouthClose_ctl.translateY', u'blendShape1_jawRight_Mesh.output',
                    u'jaw_ctl.translateY', u'blendShape1_jawLeft_Mesh.output', u'Jaw_F_ctl.translateY',
                    u'mouthFunnel_ctl.translateY', u'blendShape1_mouthFrown_R_Mesh1.output',
                    u'blendShape1_eyeWide_R_Mesh.output', u'cheekRaiser_L_ctl.translateY',
                    u'cheekPuff_R_ctl.translateY', u'cheekPuff_L_ctl.translateY',
                    u'blendShape1_browOuterUp_R_Mesh.output', u'blendShape1_browOuterUp_L_Mesh.output',
                    u'browInnerUp_R_ctl.translateY', u'browInnerUp_L_ctl.translateY',
                    u'blendShape1_browDown_R_Mesh.output', u'blendShape1_browDown_L_Mesh.output',
                    u'noseSneer_R_ctl.translateY', u'noseSneer_L_ctl.translateY', u'mouthUpperUp_R_ctl.translateY',
                    u'mouthUpperUp_L_ctl.translateY', u'mouth_end_R_ctrl.translateY', u'mouth_end_L_ctrl.translateY',
                    u'blendShape1_eyeLookIn_L_Mesh.output', u'blendShape1_eyeLookDown_R_Mesh.output',
                    u'blendShape1_eyeLookDown_L_Mesh.output', u'blendShape1_eyeBlink_R_Mesh.output',
                    u'blendShape1_eyeBlink_L_Mesh.output', u'cheekSquint_R_ctl.translateY',
                    u'cheekSquint_L_ctl.translateY', u'cheekRaiser_R_ctl.translateY',
                    u'blendShape1_eyeWide_L_Mesh.output', u'eyeSquint_R_ctl.translateY', u'eyeSquint_L_ctl.translateY',
                    u'blendShape1_eyeLookUp_R_Mesh.output', u'blendShape1_eyeLookUp_L_Mesh.output',
                    u'blendShape1_eyeLookOut_R_Mesh.output', u'blendShape1_eyeLookOut_L_Mesh.output',
                    u'blendShape1_eyeLookIn_R_Mesh.output', u'mouthPucker_ctl.translateY',
                    u'mouthLowerDown_R_ctl.translateY', u'mouth_press_R_ctl.translateY',
                    u'mouth_press_L_ctl.translateY', u'mouthRollLower_ctl.translateY',
                    u'blendShape1_mouthRight_Mesh.output', u'mouthRollUpper_ctl.translateY',
                    u'blendShape1_mouthSmile_L_Mesh.output', u'mouthShrugUpper_ctl.translateY',
                    u'mouthShrugLower_ctl.translateY', u'blendShape1_mouthSmile_R_Mesh1.output',
                    u'mouthLowerDown_L_ctl.translateY', u'blendShape1_mouthLeft_Mesh.output']

    # 기본 Transform

    jawTrans = None
    jawRot = None

    # 블랜드쉐입별 Transform
    jawTransOpen = None
    jawRotOpen = None
    jawRotLeft = None
    jawRotRight = None
    jawTransForward = None

    # Complete버튼 컬러
    buttonColor = "background-color:rgb(0, 102, 51)"

    # --------------------------------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------------------------------
    def __init__(self, ui_path=None, title_name='ICT2CC3', parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        print 'Start ICT2CC3'

        # 윈도우 설정
        self.setWindowTitle(title_name)
        self.setMinimumSize(200, 250)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # 순차적 실행
        self.init_ui(ui_path)
        self.get_Host_name_IP()
        self.create_layout() # 배치및 컬러 적용
        self.create_connection()


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
                f = QtCore.QFile( os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('.py', '.ui'))
            except:
                print u'호출시 ui_path에 ui파일경로를 적어주거나, 같은 파일이름의 ui파일을 만들어주시면 됩니다.'
                return
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)
        f.close()

    def get_Host_name_IP(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            result = "IP : " + host_ip
            self.ui.label_myIP.setText(result)
        except:
            print("Unable to get Hostname and IP")

    # ------------------------------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------------------------------
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    # ------------------------------------------------------------------------------------------
    # Connect Methods
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        #CopyMode : 블랜드쉐입 추출
        self.ui.pushButton_detachMeshes.clicked.connect(self.detachMeshes)
        self.ui.pushButton_importICT.clicked.connect(self.importICT)
        self.ui.pushButton_autoBindSkin.clicked.connect(self.autoBindSkin)
        self.ui.pushButton_extractBlendshape.clicked.connect(self.copy_blendshape_withEyeTeeth)
        self.ui.pushButton_copyWeight.clicked.connect(self.skinCopyWeight)


        self.ui.pushButton_resetBS.clicked.connect(self.resetBS)
        self.ui.pushButton_alignNormal.clicked.connect(self.alignNormal)
        self.ui.pushButton_autoRig.clicked.connect(self.autoControlRig)
        self.ui.pushButton_resetRig.clicked.connect(self.resetSlider)


        self.ui.pushButton_saveJawOpen.clicked.connect(self.saveJawOpen)
        self.ui.pushButton_saveJawLeft.clicked.connect(self.saveJawLeft)
        self.ui.pushButton_saveJawRight.clicked.connect(self.saveJawRight)
        self.ui.pushButton_saveJawForward.clicked.connect(self.saveJawForward)
        self.ui.pushButton_jawOpen.clicked.connect(self.change_jawOpen)
        self.ui.pushButton_jawLeft.clicked.connect(self.change_jawLeft)
        self.ui.pushButton_jawRight.clicked.connect(self.change_jawRight)
        self.ui.pushButton_jawForward.clicked.connect(self.change_jawForward)

        # 헤어 추가
        self.ui.pb_addHair.clicked.connect(self.add_hairMesh)
        self.ui.pb_listWidgetClear.clicked.connect(self.listWidget_clear)
        self.ui.pb_addHairBS.clicked.connect(self.make_blendshape_hairs)
        self.ui.listWidget.itemDoubleClicked.connect(self.select_item)
        self.ui.pb_bindSkinHair.clicked.connect(self.bindSkinHair)

    def bindSkinHair(self):
        if not cmds.ls(sl=1)[0]:
            print('Select Hair')
            return

        # ICT_Base에 주둥이에 붙어있는 Joint들
        mouthJoints = [u'MouthUp_Joint', u'MouthUp_Joint1', u'MouthUp_Joint2', u'MouthUp_Joint3', u'MouthUp_Joint4',
                       u'MouthUp_Joint5', u'MouthUp_Joint6', u'MouthUp_Joint7', u'MouthUp_Joint8', u'MouthUp_Joint9',
                       u'MouthUp_Joint10', u'MouthUp_Joint11', u'MouthUp_Joint12', u'MouthUp_Joint13',
                       u'MouthUp_Joint14', u'MouthUp_Joint15', u'MouthUp_Joint16', u'MouthUp_Joint17',
                       u'MouthUp_Joint18', u'MouthUp_Joint19', u'MouthUp_Joint20', u'MouthUp_Joint21',
                       u'MouthUp_Joint22', u'MouthUp_Joint23', u'MouthUp_Joint24', u'MouthUp_Joint25',
                       u'MouthUp_Joint26', u'MouthUp_Joint27', u'MouthUp_Joint28', u'MouthUp_Joint29',
                       u'MouthUp_Joint30', u'MouthUp_Joint31', u'MouthUp_Joint32', u'MouthUp_Joint33',
                       u'MouthUp_Joint34', u'MouthUp_Joint35', u'MouthUp_Joint36', u'MouthUp_Joint37',
                       u'MouthUp_Joint38', u'MouthUp_Joint39', u'MouthUp_Joint40', u'MouthUp_Joint41',
                       u'MouthUp_Joint42', u'MouthUp_Joint43', u'MouthUp_Joint44', u'MouthUp_Joint45',
                       u'MouthUp_Joint46', u'MouthUp_Joint47', u'MouthUp_Joint48', u'MouthUp_Joint49',
                       u'MouthUp_Joint50', u'MouthUp_Joint51', u'MouthUp_Joint52', u'MouthUp_Joint53',
                       u'MouthUp_Joint54', u'MouthUp_Joint55', u'MouthUp_Joint56', u'MouthUp_Joint57',
                       u'MouthUp_Joint58', u'MouthUp_Joint59', u'MouthUp_Joint60', u'MouthUp_Joint61',
                       u'MouthUp_Joint62', u'MouthUp_Joint63', u'MouthUp_Joint64', u'MouthUp_Joint65',
                       u'MouthUp_Joint66', u'MouthUp_Joint67', u'MouthUp_Joint68', u'MouthUp_Joint69',
                       u'MouthUp_Joint70', u'MouthUp_Joint71', u'MouthUp_Joint72', u'MouthUp_Joint73',
                       u'MouthUp_Joint74', u'MouthUp_Joint75', u'MouthUp_Joint76', u'MouthUp_Joint77',
                       u'MouthUp_Joint78', u'MouthUp_Joint79', u'MouthUp_Joint80', u'MouthUp_Joint81',
                       u'MouthUp_Joint82', u'MouthUp_Joint83', u'MouthUp_Joint84', u'MouthUp_Joint85',
                       u'MouthUp_Joint86', u'MouthUp_Joint87', u'MouthUp_Joint88', u'MouthUp_Joint89',
                       u'MouthUp_Joint90', u'MouthUp_Joint91', u'MouthUp_Joint92', u'MouthUp_Joint93',
                       u'MouthUp_Joint94', u'MouthUp_Joint95', u'MouthUp_Joint96', u'MouthUp_Joint97',
                       u'MouthUp_Joint98', u'MouthUp_Joint99', u'MouthUp_Joint100', u'MouthUp_Joint101',
                       u'MouthUp_Joint102', u'MouthUp_Joint103', u'MouthUp_Joint104', u'MouthUp_Joint105',
                       u'MouthUp_Joint106', u'MouthUp_Joint107', u'MouthUp_Joint108', u'MouthUp_Joint109',
                       u'MouthUp_Joint110', u'MouthUp_Joint111', u'MouthUp_Joint112']

        mouthJoints.append(cmds.ls(sl=1)[0])
        try:
            cmds.skinCluster(mouthJoints, skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'
        self.ui.pb_bindSkinHair.setStyleSheet(self.buttonColor)
        # 선택못하도록 숨긴다
        cmds.hide('resultBaseMesh')

    def add_hairMesh(self):
        items = cmds.ls(sl=1)
        for item in items:
            # 히스토리 지우기
            cmds.delete(item, constructionHistory=True)
            # 리스트위젯에 추가
            if item not in self.hairMeshes:
                self.ui.listWidget.addItem(item)
                self.hairMeshes.append(item)
        self.ui.pb_addHair.setStyleSheet(self.buttonColor)


    def listWidget_clear(self):
        self.ui.listWidget.clear()
        self.hairMeshes= []


    def select_item(self, item):
        cmds.select(item.text())

    def createWrap(self, *args, **kwargs):

        influence = args[0]
        surface = args[1]

        shapes = cmds.listRelatives(influence, shapes=True)
        influenceShape = shapes[0]

        shapes = cmds.listRelatives(surface, shapes=True)
        surfaceShape = shapes[0]

        # create wrap deformer
        weightThreshold = kwargs.get('weightThreshold', 0.0)
        maxDistance = kwargs.get('maxDistance', 0.1)
        exclusiveBind = kwargs.get('exclusiveBind', False)
        autoWeightThreshold = kwargs.get('autoWeightThreshold', True)
        falloffMode = kwargs.get('falloffMode', 0)

        wrapData = cmds.deformer(surface, type='wrap')
        wrapNode = wrapData[0]

        cmds.setAttr(wrapNode + '.weightThreshold', weightThreshold)
        cmds.setAttr(wrapNode + '.maxDistance', maxDistance)
        cmds.setAttr(wrapNode + '.exclusiveBind', exclusiveBind)
        cmds.setAttr(wrapNode + '.autoWeightThreshold', autoWeightThreshold)
        cmds.setAttr(wrapNode + '.falloffMode', falloffMode)

        cmds.connectAttr(surface + '.worldMatrix[0]', wrapNode + '.geomMatrix')

        # add influence
        duplicateData = cmds.duplicate(influence, name=influence + 'Base')
        base = duplicateData[0]
        shapes = cmds.listRelatives(base, shapes=True)
        baseShape = shapes[0]
        cmds.hide(base)

        # create dropoff attr if it doesn't exist
        if not cmds.attributeQuery('dropoff', n=influence, exists=True):
            # cmds.addAttr(influence, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=20.0)
            cmds.addAttr(influence, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=1.0)
            cmds.setAttr(influence + '.dr', k=True)

        # if type mesh
        if cmds.nodeType(influenceShape) == 'mesh':
            # create smoothness attr if it doesn't exist
            if not cmds.attributeQuery('smoothness', n=influence, exists=True):
                cmds.addAttr(influence, sn='smt', ln='smoothness', dv=0.0, min=0.0)
                cmds.setAttr(influence + '.smt', k=True)

            # create the inflType attr if it doesn't exist
            if not cmds.attributeQuery('inflType', n=influence, exists=True):
                cmds.addAttr(influence, at='short', sn='ift', ln='inflType', dv=2, min=1, max=2)

            cmds.connectAttr(influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]')
            cmds.connectAttr(baseShape + '.worldMesh', wrapNode + '.basePoints[0]')
            cmds.connectAttr(influence + '.inflType', wrapNode + '.inflType[0]')
            cmds.connectAttr(influence + '.smoothness', wrapNode + '.smoothness[0]')

        # if type nurbsCurve or nurbsSurface
        if cmds.nodeType(influenceShape) == 'nurbsCurve' or cmds.nodeType(influenceShape) == 'nurbsSurface':
            # create the wrapSamples attr if it doesn't exist
            if not cmds.attributeQuery('wrapSamples', n=influence, exists=True):
                cmds.addAttr(influence, at='short', sn='wsm', ln='wrapSamples', dv=10, min=1)
                cmds.setAttr(influence + '.wsm', k=True)

            cmds.connectAttr(influenceShape + '.ws', wrapNode + '.driverPoints[0]')
            cmds.connectAttr(baseShape + '.ws', wrapNode + '.basePoints[0]')
            cmds.connectAttr(influence + '.wsm', wrapNode + '.nurbsSamples[0]')

        cmds.connectAttr(influence + '.dropoff', wrapNode + '.dropoff[0]')
        # I want to return a pyNode object for the wrap deformer.
        # I do not see the reason to rewrite the code here into pymel.
        # return wrapNode
        #return pm.nt.Wrap(wrapNode)

    def make_blendshape_hairs(self):

        # ICT_Base 가 아직 있다는 가정
        if self.hairMeshes:
            for hairmesh in self.hairMeshes:
                # 얼굴에 사용했던 리스트를 초기화
                baseMesh = 'ICT_Base'
                # baseMesh = 'resultBaseMesh'
                extractedBS = []

                meshHistory = cmds.listHistory(baseMesh)
                bsNodeName = cmds.ls(meshHistory, type='blendShape')[0]
                bsNameList = cmds.listAttr(bsNodeName + '.w', m=True)

                baseHair = cmds.duplicate(hairmesh)
                # 원래 이름앞에 Result라고 붙인다
                baseHair = cmds.rename(baseHair, 'result_' + hairmesh)

                # 혹시 모르니 BS들을 초기화
                for bs in bsNameList:
                    if bs in self.ICTBlendShapeList:
                        cmds.setAttr(bsNodeName + '.' + bs, 0)
                    else:
                        cmds.setAttr(bsNodeName + '.' + bs, 1)

                # hair에 대한 bs 복사 시작
                for bs in self.ICTBlendShapeList:
                    cmds.setAttr(bsNodeName + '.' + bs, 1)
                    # 복사
                    dup = cmds.duplicate(hairmesh)
                    # Blendshape 이름으로 변경
                    resultBSMesh = cmds.rename(dup, bs)
                    cmds.setAttr(bsNodeName + '.' + bs, 0)
                    extractedBS.append(resultBSMesh)

                # 블렌드쉐입 추가
                cmds.blendShape(extractedBS, baseHair, tc=True)
                # 블렌드쉐입 메쉬들 삭제
                cmds.delete(extractedBS)
                # 완료된 수염들을 나중에 skin을 위해서 따로 저장해둔다
                self.result_hairMeshes.append(baseHair)

            # 작업된 헤어와 헷깔리지 않게 지우자
            # for hair in self.hairMeshes:
            #     cmds.delete(hair)

    def change_jawOpen(self):
        # 원래값으로 돌림
        if self.jawTrans:
            # jawTrans에 값이 있다면, 즉 한번이라도 설정한적이 있다면, 그값으로 만들어라
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2],
                         type='double3')
        else:
            # 그값이 없다면, 저장해라
            self.saveJawTransform()

        bsNode, bsNames = self.getBlendshapeNames('ICT_Base')
        self.resetBS('ICT_Base')
        cmds.setAttr(bsNode + '.' + 'jawOpen', 1)

        # 값이 적절하게 들어갔는지 확인용
        if self.jawRotOpen:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRotOpen[0], self.jawRotOpen[1], self.jawRotOpen[2],
                         type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTransOpen[0], self.jawTransOpen[1], self.jawTransOpen[2],
                         type='double3')
        cmds.select('cc_base_jawroot')


    def change_jawLeft(self):
        if self.jawTrans:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2],
                         type='double3')
        else:
            self.saveJawTransform()

        bsNode, bsNames = self.getBlendshapeNames('ICT_Base')
        self.resetBS('ICT_Base')
        cmds.setAttr(bsNode + '.' + 'jawLeft', 1)
        if self.jawRotLeft:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRotLeft[0], self.jawRotLeft[1], self.jawRotLeft[2],
                         type='double3')
        cmds.select('cc_base_jawroot')


    def change_jawRight(self):
        if self.jawTrans:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2],
                         type='double3')
        else:
            self.saveJawTransform()
        bsNode, bsNames = self.getBlendshapeNames('ICT_Base')
        self.resetBS('ICT_Base')
        cmds.setAttr(bsNode + '.' + 'jawRight', 1)
        if self.jawRotRight:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRotRight[0], self.jawRotRight[1], self.jawRotRight[2],
                         type='double3')
        cmds.select('cc_base_jawroot')


    def change_jawForward(self):
        if self.jawTrans:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2],
                         type='double3')
        else:
            self.saveJawTransform()
        bsNode, bsNames = self.getBlendshapeNames('ICT_Base')
        self.resetBS('ICT_Base')
        cmds.setAttr(bsNode + '.' + 'jawForward', 1)
        if self.jawTransForward:
            cmds.setAttr('cc_base_jawroot.translate', self.jawTransForward[0], self.jawTransForward[1], self.jawTransForward[2],
                         type='double3')
        cmds.select('cc_base_jawroot')


    def saveJawOpen(self):
        self.jawTransOpen = cmds.getAttr('cc_base_jawroot.translate')[0]
        self.jawRotOpen = cmds.getAttr('cc_base_jawroot.rotate')[0]
        self.ui.lineEdit_jawValue.setText(str(self.jawRotOpen))
        self.ui.pushButton_saveJawOpen.setStyleSheet(self.buttonColor)
        self.resetBS('ICT_Base')

    def saveJawLeft(self):
        self.jawRotLeft = cmds.getAttr('cc_base_jawroot.rotate')[0]
        self.ui.lineEdit_jawValue.setText(str(self.jawRotLeft))
        self.ui.pushButton_saveJawLeft.setStyleSheet(self.buttonColor)
        self.resetBS('ICT_Base')

    def saveJawRight(self):
        self.jawRotRight = cmds.getAttr('cc_base_jawroot.rotate')[0]
        self.ui.lineEdit_jawValue.setText(str(self.jawRotRight))
        self.ui.pushButton_saveJawRight.setStyleSheet(self.buttonColor)
        self.resetBS('ICT_Base')

    def saveJawForward(self):
        self.jawTransForward = cmds.getAttr('cc_base_jawroot.translate')[0]
        self.ui.lineEdit_jawValue.setText(str(self.jawTransForward))
        self.ui.pushButton_saveJawForward.setStyleSheet(self.buttonColor)
        self.resetBS('ICT_Base')


    def resetBS(self, *args):
        if self.jawTrans:
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2],
                         type='double3')
        else:
            self.saveJawTransform()

        if not args:
            sel = cmds.ls(sl=1)[0]
        else:
            sel = args

        bsNode, bsNames = self.getBlendshapeNames(sel)
        for bs in self.ICTBlendShapeList:
            cmds.setAttr(bsNode+'.'+bs, 0)

    def importControlrigMayafile(self):
        controlrigFile = self.CONTROLRIG_MAYA_FILE
        cmds.file(controlrigFile, i=True, ignoreVersion=True)


    # 연결하기
    def connectBsWithControl(self):
        for bs, ctrl in zip(self.JBC_BSList, self.JBC_CtrlList):
            cmds.connectAttr(ctrl, bs)
            print bs, ctrl


    def autoControlRig(self):
        # 기존에 이미 리그오브젝트가 있다면 실행하지마
        if cmds.objExists('Face_Controllers_Root'):
            print u'이미 JBControlRig 가 있습니다.'
            return
        # Blendshape 오브젝트가 하나라도 있어야지 실행되
        if len(cmds.ls(type='blendShape')) > 0:
            self.importControlrigMayafile()
            self.connectBsWithControl()


    def resetSlider(self):
        for slider in self.JBControlRigList_v2:
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


    def getSkinCluster(self, mesh=''):
        if mesh == '':
            return
        objHist = cmds.listHistory(mesh, pdo=True)
        skinCluster = cmds.ls(objHist, type="skinCluster") or [None]
        cluster = skinCluster[0]
        return cluster

    def skinCopyWeight(self):
        # skin
        jointForSkin = [u'pelvis', u'cc_base_pelvis', u'spine_01', u'spine_02', u'spine_03', u'neck_01', u'cc_base_necktwist02',
         u'head', u'cc_base_facialbone', u'cc_base_jawroot', u'cc_base_tongue01', u'cc_base_tongue02',
         u'cc_base_tongue03', u'cc_base_teeth02', u'cc_base_r_eye', u'cc_base_l_eye', u'cc_base_upperjaw',
         u'cc_base_teeth01', u'clavicle_l', u'upperarm_l', u'lowerarm_l', u'cc_base_l_forearmtwist01',
         u'cc_base_l_elbowsharebone', u'hand_l', u'pinky_01_l', u'pinky_02_l', u'pinky_03_l', u'ring_01_l',
         u'ring_02_l', u'ring_03_l', u'middle_01_l', u'middle_02_l', u'middle_03_l', u'index_01_l', u'index_02_l',
         u'index_03_l', u'thumb_01_l', u'thumb_02_l', u'thumb_03_l', u'lowerarm_twist_01_l', u'upperarm_twist_01_l',
         u'cc_base_l_upperarmtwist02', u'cc_base_l_ribstwist', u'cc_base_l_breast', u'cc_base_r_ribstwist',
         u'cc_base_r_breast', u'clavicle_r', u'upperarm_r', u'lowerarm_r', u'cc_base_r_elbowsharebone',
         u'cc_base_r_forearmtwist01', u'hand_r', u'ring_01_r', u'ring_02_r', u'ring_03_r', u'middle_01_r',
         u'middle_02_r', u'middle_03_r', u'thumb_01_r', u'thumb_02_r', u'thumb_03_r', u'index_01_r', u'index_02_r',
         u'index_03_r', u'pinky_01_r', u'pinky_02_r', u'pinky_03_r', u'lowerarm_twist_01_r', u'upperarm_twist_01_r',
         u'cc_base_r_upperarmtwist02', u'thigh_l', u'calf_l', u'foot_l', u'cc_base_l_toebasesharebone', u'ball_l',
         u'cc_base_l_pinkytoe1', u'cc_base_l_ringtoe1', u'cc_base_l_midtoe1', u'cc_base_l_indextoe1',
         u'cc_base_l_bigtoe1', u'calf_twist_01_l', u'cc_base_l_kneesharebone', u'cc_base_l_calftwist02',
         u'thigh_twist_01_l', u'cc_base_l_thightwist02', u'thigh_r', u'calf_r', u'cc_base_r_kneesharebone', u'foot_r',
         u'ball_r', u'cc_base_r_bigtoe1', u'cc_base_r_pinkytoe1', u'cc_base_r_ringtoe1', u'cc_base_r_indextoe1',
         u'cc_base_r_midtoe1', u'cc_base_r_toebasesharebone', u'calf_twist_01_r', u'cc_base_r_calftwist02',
         u'thigh_twist_01_r', u'cc_base_r_thightwist02']

        # 몸통 스킨
        try:
            cmds.skinCluster(jointForSkin, 'resultBaseMesh',skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'
        # 몸통 스킨 카피
        cmds.copySkinWeights(ss=self.getSkinCluster('cc_base_body'), ds=self.getSkinCluster('resultBaseMesh'), noMirror=True)

        # 헤어 스킨
        if self.result_hairMeshes:
            for i in self.result_hairMeshes:
                try:
                    cmds.skinCluster(jointForSkin, i, skinMethod=0, toSelectedBones=1)
                    cmds.copySkinWeights(ss=self.getSkinCluster('cc_base_body'),
                                         ds=self.getSkinCluster(i), noMirror=True)
                except:
                    print'can not skin'



        if self.result_hairMeshes:
            for i in self.result_hairMeshes:
                cmds.copySkinWeights(ss=self.getSkinCluster('cc_base_body'), ds=self.getSkinCluster(i), noMirror=True)

        self.ui.pushButton_copyWeight.setStyleSheet(self.buttonColor)


    def autoBindSkin(self):

        upper = [u'upperR_joint2', u'upperR_joint3', u'upperR_joint4', u'upperR_joint5', u'upperR_joint6', u'upperR_joint7', u'upperR_joint8', u'upperR_joint9', u'upperR_joint10', u'upperR_joint11', u'upperR_joint13', u'upperL_joint27', u'upperL_joint28', u'upperL_joint29', u'upperL_joint30', u'upperL_joint31', u'upperL_joint32', u'upperL_joint34', u'upperL_joint35', u'upperL_joint36', u'upperL_joint37', u'upperL_joint38', u'combine_eyelash_upper']
        try:
            cmds.skinCluster(upper, skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'

        lower = [u'lowerR_joint16', u'lowerR_joint17', u'lowerR_joint18', u'lowerR_joint19', u'lowerR_joint20',
         u'lowerR_joint22', u'lowerR_joint23', u'lowerR_joint24', u'lowerR_joint25', u'lowerR_joint26',
         u'lowerL_joint40', u'lowerL_joint41', u'lowerL_joint42', u'lowerL_joint43', u'lowerL_joint44',
         u'lowerL_joint46', u'lowerL_joint47', u'lowerL_joint48', u'lowerL_joint49', u'lowerL_joint50',
         u'combine_eyelash_lower']
        try:
            cmds.skinCluster(lower, skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'

        tearline = [u'upperR_joint1', u'upperR_joint2', u'upperR_joint3', u'upperR_joint4', u'upperR_joint5',
                    u'upperR_joint6', u'upperR_joint7', u'upperR_joint8', u'upperR_joint9', u'upperR_joint10',
                    u'upperR_joint11', u'upperR_joint12', u'upperR_joint13', u'upperL_joint27', u'upperL_joint28',
                    u'upperL_joint29', u'upperL_joint30', u'upperL_joint31', u'upperL_joint32', u'upperL_joint33',
                    u'upperL_joint34', u'upperL_joint35', u'upperL_joint36', u'upperL_joint37', u'upperL_joint38',
                    u'upperL_joint39', u'lowerR_joint14', u'lowerR_joint15', u'lowerR_joint16', u'lowerR_joint17',
                    u'lowerR_joint18', u'lowerR_joint19', u'lowerR_joint20', u'lowerR_joint21', u'lowerR_joint22',
                    u'lowerR_joint23', u'lowerR_joint24', u'lowerR_joint25', u'lowerR_joint26', u'lowerL_joint40',
                    u'lowerL_joint41', u'lowerL_joint42', u'lowerL_joint43', u'lowerL_joint44', u'lowerL_joint45',
                    u'lowerL_joint46', u'lowerL_joint47', u'lowerL_joint48', u'lowerL_joint49', u'lowerL_joint50',
                    u'lowerL_joint51', u'lowerL_joint52', u'cc_base_tearline']
        try:
            cmds.skinCluster(tearline, skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'

        eyeocclusion = [u'upperR_joint1', u'upperR_joint2', u'upperR_joint3', u'upperR_joint4', u'upperR_joint5',
                        u'upperR_joint6', u'upperR_joint7', u'upperR_joint8', u'upperR_joint9', u'upperR_joint10',
                        u'upperR_joint11', u'upperR_joint12', u'upperR_joint13', u'upperL_joint27', u'upperL_joint28',
                        u'upperL_joint29', u'upperL_joint30', u'upperL_joint31', u'upperL_joint32', u'upperL_joint33',
                        u'upperL_joint34', u'upperL_joint35', u'upperL_joint36', u'upperL_joint37', u'upperL_joint38',
                        u'upperL_joint39', u'lowerR_joint14', u'lowerR_joint15', u'lowerR_joint16', u'lowerR_joint17',
                        u'lowerR_joint18', u'lowerR_joint19', u'lowerR_joint20', u'lowerR_joint21', u'lowerR_joint22',
                        u'lowerR_joint23', u'lowerR_joint24', u'lowerR_joint25', u'lowerR_joint26', u'lowerL_joint40',
                        u'lowerL_joint41', u'lowerL_joint42', u'lowerL_joint43', u'lowerL_joint44', u'lowerL_joint45',
                        u'lowerL_joint46', u'lowerL_joint47', u'lowerL_joint48', u'lowerL_joint49', u'lowerL_joint50',
                        u'lowerL_joint51', u'lowerL_joint52', u'cc_base_eyeocclusion']
        try:
            cmds.skinCluster(eyeocclusion, skinMethod=0, toSelectedBones=1)
        except:
            print'can not skin'

        self.ui.pushButton_autoBindSkin.setStyleSheet(self.buttonColor)





    def importICT(self):
        file_path = r'D:/MOSE/Character/ICT2CC3/CC3_AddBS_Final04.mb'
        cmds.file(file_path, i=True, ignoreVersion=True)
        self.addBlendshape()
        self.saveJawTransform()
        self.ui.pushButton_importICT.setStyleSheet(self.buttonColor)


    def saveJawTransform(self):
        # cc_base_jawroot 원래 가지고 있던 값을 저장
        self.jawTrans = cmds.getAttr('cc_base_jawroot.translate')[0]
        self.jawRot = cmds.getAttr('cc_base_jawroot.rotate')[0]


    def detachMeshes(self):

        #clearUVs
        cmds.select(u'cc_base_body', u'cc_base_teeth', u'cc_base_tongue', u'cc_base_tearline', u'cc_base_eyeocclusion', u'cc_base_eye')
        self.clear_UVs()

        # 아래 두녀석은 기존에 있던 skin을 없애줘야 한다
        cmds.delete('cc_base_eyeocclusion', ch=1)
        cmds.delete('cc_base_tearline', ch=1)


        copyBody = cmds.duplicate('cc_base_body')
        cmds.select(copyBody)
        self.unlockTransform()

        # 각 요소별로 Face들을 뜯어낸다
        cmds.select(self.Face)
        dup = mel.eval('source dpSmartMeshTools; dpSmartExtractDuplicate(0);')
        cmds.rename(dup, 'original')

        cmds.select(self.EyelashUpper)
        dup = mel.eval('source dpSmartMeshTools; dpSmartExtractDuplicate(0);')
        cmds.rename(dup, 'combine_eyelash_upper')

        cmds.select(self.EyelashLower)
        dup = mel.eval('source dpSmartMeshTools; dpSmartExtractDuplicate(0);')
        cmds.rename(dup, 'combine_eyelash_lower')

        cmds.select(self.EyePoint)
        dup = mel.eval('source dpSmartMeshTools; dpSmartExtractDuplicate(0);')
        cmds.rename(dup, 'combine_eyePoint')

        cmds.delete(self.Face,self.EyelashUpper,self.EyelashLower,self.EyePoint)

        self.setTranslate('original',(-40,0,0))
        cmds.hide('cc_base_body')

        self.ui.pushButton_detachMeshes.setStyleSheet(self.buttonColor)


    def alignNormal(self):
        import AlignNormal
        AlignNormal.main()

    def getBlendshapeNames(self, mesh):
        meshHistory = cmds.listHistory(mesh)
        bsNode = cmds.ls(meshHistory, type='blendShape')[0]
        bsNames = cmds.listAttr(bsNode + '.w', m=True)
        return bsNode, bsNames

    def nextAvailableTargetIndex(self, blendShape):
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Get blendShape target list
        targetList = self.getTargetList(blendShape)
        if not targetList: return 0

        # Get last index
        lastIndex = self.getTargetIndex(blendShape, targetList[-1])
        nextIndex = lastIndex + 1

        # Return result
        return nextIndex

    def getTargetIndex(self, blendShape, target):
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Check target
        if not cmds.objExists(blendShape + '.' + target):
            raise Exception('Blendshape "' + blendShape + '" has no target "' + target + '"!')

        # Get attribute alias
        aliasList = cmds.aliasAttr(blendShape, q=True)
        aliasIndex = aliasList.index(target)
        aliasAttr = aliasList[aliasIndex + 1]

        # Get index
        targetIndex = int(aliasAttr.split('[')[-1].split(']')[0])

        # Return result
        return targetIndex

    def getTargetList(self, blendShape):
        # Check blendShape
        # if not self.isBlendShape(blendShape):
        #     raise Exception('Object "'+blendShape+'" is not a valid blendShape node!')

        # Get attribute alias
        targetList = cmds.listAttr(blendShape + '.w', m=True)
        if not targetList: targetList = []

        # Return result
        return targetList

    def addBlendshape(self):
        try:
            bsNode, bsNames = self.getBlendshapeNames('ICT_Base')
        except:
            print('can not find blendshape node')
            return
        index = self.nextAvailableTargetIndex(bsNode)
        cmds.blendShape(bsNode, e=1, t=['ICT_Base', index, 'original', 1])
        cmds.setAttr(bsNode + '.' + 'original', 1)

    def clear_UVs(self):
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
            # clear history
            #cmds.delete(mesh, ch=1)

    def duplicate_blendshape_afterWrap(self):
        # 마야에서 wrap작업이 끝난후 기존 ICT에서 바뀐 토폴로지로 복사하는 기능
        # Duplicate Blendshape After Wrap
        for bs in self.ICTBlendShapeList:
            cmds.setAttr('BS_ICT.' + bs, 0)
        for bs in self.ICTBlendShapeList:
            cmds.setAttr('BS_ICT.' + bs, 1)
            dup = cmds.duplicate('CC3_Topo')
            redup = cmds.rename(dup, bs)
            cmds.setAttr('BS_ICT.' + bs, 0)

    def duplicate_blendshape_fromCC3(self):
        # Duplicate Blendshape from CC3
        for bs in self.ICTBlendShapeList:
            cmds.setAttr('BS_cc3.' + bs, 0)
        for bs in self.ICTBlendShapeList:
            cmds.setAttr('BS_cc3.' + bs, 1)
            dup = cmds.duplicate('CC3_Topo')
            redup = cmds.rename(dup, bs)
            cmds.setAttr('BS_cc3.' + bs, 0)


    def unlockTransform(self, *args):
        # unlock
        if not args:
            objects = cmds.ls(sl=1)
        else:
            objects = args

        trans = ['t','r','s']
        axis = ['x','y','z']

        for obj in objects:
            for t in trans:
                for a in axis:
                    cmds.setAttr(obj +'.'+ t + a, lock=False)
            cmds.setAttr(obj + '.t' , lock=False)
            cmds.setAttr(obj + '.r' , lock=False)
            cmds.setAttr(obj + '.s', lock=False)

    def getTranslate(self, _sel):
        if not isinstance(_sel, list):
            tx = cmds.getAttr(_sel + '.tx')
            ty = cmds.getAttr(_sel + '.ty')
            tz = cmds.getAttr(_sel + '.tz')
        else:
            tx = cmds.getAttr(_sel[0] + '.tx')
            ty = cmds.getAttr(_sel[0] + '.ty')
            tz = cmds.getAttr(_sel[0] + '.tz')
        return [tx, ty, tz]


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

    def AlignObjects(self, _sel, _startPos=(20, 0, 0), _useStartPosition=True, _maxRows=10, _disX=20, _disY=-38):

        if not _useStartPosition:
            startPostion = _startPos
        else:
            startPostion = self.getTranslate(_sel[0])

        CurrentRows = 0
        CurrentColumns = 0

        for i in _sel:
            if CurrentRows % _maxRows == 0:
                CurrentColumns += 1
                CurrentRows = 0
            self.setTranslate(i, [startPostion[0] + (_disX * CurrentRows),
                                  startPostion[1] + (_disY * CurrentColumns) - _disY, startPostion[2]])
            CurrentRows += 1

    # 안쓰임
    def copy_blendshape(self):
        baseMesh = 'ICT_Base'
        extractedBS = []

        meshHistory = cmds.listHistory(baseMesh)
        bsNodeName = cmds.ls(meshHistory, type='blendShape')[0]
        bsNameList = cmds.listAttr(bsNodeName + '.w', m=True)

        #reset
        for bs in bsNameList:
            if bs in self.ICTBlendShapeList:
                cmds.setAttr(bsNodeName + '.' + bs, 0)
            else:
                cmds.setAttr(bsNodeName + '.' + bs, 1)

        #make base
        dupList = []
        dup = cmds.duplicate(baseMesh)
        redup = cmds.rename(dup,baseMesh+'_dup')
        dupList.append(redup)
        for mesh in self.otherMeshes:
            dup = cmds.duplicate(mesh)
            redup = cmds.rename(dup,mesh+'_dup')
            dupList.append(redup)
        cmds.select(dupList)
        resultBaseMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
        resultBaseMesh = cmds.rename(resultBaseMesh,'resultBaseMesh')

        #extract BS
        for bs in self.ICTBlendShapeList:
            cmds.setAttr(bsNodeName + '.' + bs, 1)
            dupList = []
            dup = cmds.duplicate(baseMesh)
            redup = cmds.rename(dup, baseMesh + '_dup')
            dupList.append(redup)
            for mesh in self.otherMeshes:
                dup = cmds.duplicate(mesh)
                redup = cmds.rename(dup, mesh + '_dup')
                dupList.append(redup)
            cmds.select(dupList)
            resultBSMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            resultBSMesh = cmds.rename(resultBSMesh, bs)
            cmds.setAttr(bsNodeName + '.' + bs, 0)
            extractedBS.append(resultBSMesh)

        #final
        cmds.blendShape(extractedBS, resultBaseMesh)
        cmds.delete(extractedBS)

    def copy_blendshape_withEyeTeeth(self):
        # jawOpen 작업이 안되어 있다면 리턴
        if self.jawTransOpen == None:
            print 'save jawOpen Value'
            return

        baseMesh = 'ICT_Base'
        extractedBS = []

        meshHistory = cmds.listHistory(baseMesh)
        bsNodeName = cmds.ls(meshHistory, type='blendShape')[0]
        bsNameList = cmds.listAttr(bsNodeName + '.w', m=True)

        #reset 베이스리스트에 없는 특정BS라면 값을 1로 유지
        for bs in bsNameList:
            if bs in self.ICTBlendShapeList:
                cmds.setAttr(bsNodeName + '.' + bs, 0)
            else:
                cmds.setAttr(bsNodeName + '.' + bs, 1)



        ########################### 베이스 메쉬 만들기 #########################
        #######################################################################
        dupList = []
        # ICT_Base의 복사본 생성
        dup = cmds.duplicate(baseMesh)
        redup = cmds.rename(dup, baseMesh+'_dup')
        dupList.append(redup)

        # otherMeshes = ['cc_base_eye', 'cc_base_teeth', 'cc_base_tongue', 'cc_base_tearline', 'cc_base_eyeocclusion',
        #                    'combine_eyePoint', 'combine_eyelash_upper', 'combine_eyelash_lower']
        # 눈, 눈썹, 치아, 혀, 눈물, AO등도 복사본 생성
        for mesh in self.otherMeshes:
            dup = cmds.duplicate(mesh)
            redup = cmds.rename(dup,mesh+'_dup')
            dupList.append(redup)

        # 기본 표정의 복사본들을 모두 하나의 메쉬로 만듬
        cmds.select(dupList)
        resultBaseMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')

        #최종 결과물의 베이스 메쉬
        resultBaseMesh = cmds.rename(resultBaseMesh,'resultBaseMesh')

        # 바디와 한번 더 Combine, 순서가 중요하다
        if self.ui.checkBox_bodyCombine.isChecked():
            cmds.select(resultBaseMesh, 'cc_base_body1')
            resultBaseMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            resultBaseMesh = cmds.rename(resultBaseMesh, 'resultBaseMesh')
            # Vertext Merge
            vertextForMerge = [u'resultBaseMesh.vtx[0:39]', u'resultBaseMesh.vtx[51]', u'resultBaseMesh.vtx[56]',
                               u'resultBaseMesh.vtx[324]', u'resultBaseMesh.vtx[1743:1775]',
                               u'resultBaseMesh.vtx[1779:1780]', u'resultBaseMesh.vtx[1782]',
                               u'resultBaseMesh.vtx[1807:1816]', u'resultBaseMesh.vtx[1820]',
                               u'resultBaseMesh.vtx[1823:1847]', u'resultBaseMesh.vtx[1850]',
                               u'resultBaseMesh.vtx[2037]', u'resultBaseMesh.vtx[2044]', u'resultBaseMesh.vtx[2323]',
                               u'resultBaseMesh.vtx[3701]', u'resultBaseMesh.vtx[3805:3836]',
                               u'resultBaseMesh.vtx[3839:3840]', u'resultBaseMesh.vtx[3843]',
                               u'resultBaseMesh.vtx[3868:3877]', u'resultBaseMesh.vtx[3881]',
                               u'resultBaseMesh.vtx[3884:3906]', u'resultBaseMesh.vtx[3909]',
                               u'resultBaseMesh.vtx[3912]', u'resultBaseMesh.vtx[3915]', u'resultBaseMesh.vtx[4025]',
                               u'resultBaseMesh.vtx[10289]', u'resultBaseMesh.vtx[10317]',
                               u'resultBaseMesh.vtx[10351:10352]', u'resultBaseMesh.vtx[10369:10370]',
                               u'resultBaseMesh.vtx[10502]', u'resultBaseMesh.vtx[10564]', u'resultBaseMesh.vtx[10570]',
                               u'resultBaseMesh.vtx[10578]', u'resultBaseMesh.vtx[10582:10584]',
                               u'resultBaseMesh.vtx[10586:10591]', u'resultBaseMesh.vtx[10597:10619]',
                               u'resultBaseMesh.vtx[10622]', u'resultBaseMesh.vtx[10624:10625]',
                               u'resultBaseMesh.vtx[10630:10631]', u'resultBaseMesh.vtx[10635:10648]',
                               u'resultBaseMesh.vtx[10650:10653]', u'resultBaseMesh.vtx[11062:11067]',
                               u'resultBaseMesh.vtx[11098]', u'resultBaseMesh.vtx[12678:12681]',
                               u'resultBaseMesh.vtx[12700:12704]', u'resultBaseMesh.vtx[12722:12723]',
                               u'resultBaseMesh.vtx[12873:12880]', u'resultBaseMesh.vtx[12929:12930]',
                               u'resultBaseMesh.vtx[12932:12933]', u'resultBaseMesh.vtx[12938:12939]',
                               u'resultBaseMesh.vtx[12955:12956]', u'resultBaseMesh.vtx[12960:12963]',
                               u'resultBaseMesh.vtx[12976:12978]', u'resultBaseMesh.vtx[12989:12997]',
                               u'resultBaseMesh.vtx[12999:13005]', u'resultBaseMesh.vtx[13012]',
                               u'resultBaseMesh.vtx[13017:13024]', u'resultBaseMesh.vtx[13026:13029]',
                               u'resultBaseMesh.vtx[13031:13037]', u'resultBaseMesh.vtx[13040:13045]',
                               u'resultBaseMesh.vtx[13428:13429]', u'resultBaseMesh.vtx[13708]',
                               u'resultBaseMesh.vtx[13717]', u'resultBaseMesh.vtx[13721]',
                               u'resultBaseMesh.vtx[13723:13724]', u'resultBaseMesh.vtx[13730:13731]',
                               u'resultBaseMesh.vtx[13736]', u'resultBaseMesh.vtx[13738]', u'resultBaseMesh.vtx[15807]',
                               u'resultBaseMesh.vtx[15809]', u'resultBaseMesh.vtx[15811:15812]',
                               u'resultBaseMesh.vtx[16084:16085]', u'resultBaseMesh.vtx[16128:16132]',
                               u'resultBaseMesh.vtx[16134]', u'resultBaseMesh.vtx[16148]',
                               u'resultBaseMesh.vtx[16155:16156]', u'resultBaseMesh.vtx[16158:16159]',
                               u'resultBaseMesh.vtx[16164]']
            cmds.select(vertextForMerge)
            cmds.polyMergeVertex(d=0.15)



        ############################## 블렌드쉐입 추출 하기 #############################
        ################################################################################
        for bs in self.ICTBlendShapeList:
            # 특정 블렌드 쉐입일 경우 joint를 수정해 준다
            if bs == 'jawOpen':
                if self.jawRotOpen:
                    cmds.setAttr('cc_base_jawroot.rotate', self.jawRotOpen[0], self.jawRotOpen[1], self.jawRotOpen[2],
                                 type='double3')
                    cmds.setAttr('cc_base_jawroot.translate', self.jawTransOpen[0], self.jawTransOpen[1],
                                 self.jawTransOpen[2],
                                 type='double3')
            elif bs == 'jawRight':
                if self.jawRotRight:
                    cmds.setAttr('cc_base_jawroot.rotate', self.jawRotRight[0], self.jawRotRight[1],
                                 self.jawRotRight[2],
                                 type='double3')
            elif bs == 'jawLeft':
                if self.jawRotLeft:
                    cmds.setAttr('cc_base_jawroot.rotate', self.jawRotLeft[0], self.jawRotLeft[1], self.jawRotLeft[2],
                                 type='double3')
            elif bs == 'jawForward':
                if self.jawTransForward:
                    cmds.setAttr('cc_base_jawroot.translate', self.jawTransForward[0], self.jawTransForward[1],
                                 self.jawTransForward[2],
                                 type='double3')
            elif bs == 'eyeLookDownLeft':
                cmds.setAttr('cc_base_l_eye.rotate', 200, -90, 0, type='double3')
            elif bs == 'eyeLookDownRight':
                cmds.setAttr('cc_base_r_eye.rotate', 200, -90, 0, type='double3')
            elif bs == 'eyeLookInLeft':
                cmds.setAttr('cc_base_l_eye.rotate', 270, -112, -90, type='double3')
            elif bs == 'eyeLookInRight':
                cmds.setAttr('cc_base_r_eye.rotate', 90, -112, 90, type='double3')
            elif bs == 'eyeLookOutLeft':
                cmds.setAttr('cc_base_l_eye.rotate', 90, -120, 90, type='double3')
            elif bs == 'eyeLookOutRight':
                cmds.setAttr('cc_base_r_eye.rotate', 270, -120, -90, type='double3')
            elif bs == 'eyeLookUpLeft':
                cmds.setAttr('cc_base_l_eye.rotate', 160, -90, 0, type='double3')
            elif bs == 'eyeLookUpRight':
                cmds.setAttr('cc_base_r_eye.rotate', 160, -90, 0, type='double3')


            # 얼굴 복사
            cmds.setAttr(bsNodeName + '.' + bs, 1)
            dupList = []
            dup = cmds.duplicate(baseMesh)
            redup = cmds.rename(dup, baseMesh + '_dup')
            dupList.append(redup)

            # 눈, 눈썹, 치아, AO, 혀 등등 복사
            for mesh in self.otherMeshes:
                dup = cmds.duplicate(mesh)
                redup = cmds.rename(dup, mesh + '_dup')
                dupList.append(redup)


            # 얼굴과 눈, 눈썹등등을 하나로 만들기
            cmds.select(dupList)
            resultBSMesh = mel.eval('source dpSmartMeshTools; dpSmartCombine;')
            resultBSMesh = cmds.rename(resultBSMesh, bs)
            cmds.setAttr(bsNodeName + '.' + bs, 0)
            extractedBS.append(resultBSMesh)

            # 눈 Joint와 턱 Joint를 원래 위치로 복원
            cmds.setAttr('cc_base_l_eye.rotate', 180, -90, 0, type='double3')
            cmds.setAttr('cc_base_r_eye.rotate', 180, -90, 0, type='double3')
            cmds.setAttr('cc_base_jawroot.rotate', self.jawRot[0], self.jawRot[1], self.jawRot[2], type='double3')
            cmds.setAttr('cc_base_jawroot.translate', self.jawTrans[0], self.jawTrans[1], self.jawTrans[2], type='double3')


        ##################### 최종메쉬에 BlendShape 추가하기 ###############################
        # Topology Check를 하지 않음으로 얼굴Blendshape을 추가하기
        ###################################################################################
        if self.ui.checkBox_autoBS.isChecked():
            cmds.blendShape(extractedBS, resultBaseMesh, tc=False)


        # don't delete for edit blendshape
        if self.ui.checkBox_deleteBS.isChecked():
            cmds.delete(extractedBS)
        else:
            self.AlignObjects(extractedBS)
            cmds.select(extractedBS)

        self.ui.pushButton_extractBlendshape.setStyleSheet(self.buttonColor)


if __name__ == "__main__":
    try:
        ict2cc3.close()
        ict2cc3.deleteLater()
    except:
        pass

    ict2cc3 = DesignerUI()
    ict2cc3.show()