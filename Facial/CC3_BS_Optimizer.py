# -*- coding: UTF-8 -*-

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from inspect import getsourcefile
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
import os


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    winptr = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return winptr


class DesignerUI(QtWidgets.QDialog):

    # CC3 ExPlus로 추가된 블렌드쉐입 리스트
    _BS_CC3ExPlusList = ['A01_Brow_Inner_Up', 'A02_Brow_Down_Left', 'A03_Brow_Down_Right',
                              'A04_Brow_Outer_Up_Left',
                              'A05_Brow_Outer_Up_Right', 'A06_Eye_Look_Up_Left', 'A07_Eye_Look_Up_Right',
                              'A08_Eye_Look_Down_Left', 'A09_Eye_Look_Down_Right', 'A10_Eye_Look_Out_Left',
                              'A11_Eye_Look_In_Left', 'A12_Eye_Look_In_Right', 'A13_Eye_Look_Out_Right',
                              'A14_Eye_Blink_Left', 'A15_Eye_Blink_Right', 'A16_Eye_Squint_Left',
                              'A17_Eye_Squint_Right',
                              'A18_Eye_Wide_Left', 'A19_Eye_Wide_Right', 'A20_Cheek_Puff', 'A21_Cheek_Squint_Left',
                              'A22_Cheek_Squint_Right', 'A23_Nose_Sneer_Left', 'A24_Nose_Sneer_Right',
                              'A25_Jaw_Open',
                              'A26_Jaw_Forward', 'A27_Jaw_Left', 'A28_Jaw_Right', 'A29_Mouth_Funnel',
                              'A30_Mouth_Pucker',
                              'A31_Mouth_Left', 'A32_Mouth_Right', 'A33_Mouth_Roll_Upper', 'A34_Mouth_Roll_Lower',
                              'A35_Mouth_Shrug_Upper', 'A36_Mouth_Shrug_Lower', 'A37_Mouth_Close',
                              'A38_Mouth_Smile_Left',
                              'A39_Mouth_Smile_Right', 'A40_Mouth_Frown_Left', 'A41_Mouth_Frown_Right',
                              'A42_Mouth_Dimple_Left', 'A43_Mouth_Dimple_Right', 'A44_Mouth_Upper_Up_Left',
                              'A45_Mouth_Upper_Up_Right', 'A46_Mouth_Lower_Down_Left', 'A47_Mouth_Lower_Down_Right',
                              'A48_Mouth_Press_Left', 'A49_Mouth_Press_Right', 'A50_Mouth_Stretch_Left',
                              'A51_Mouth_Stretch_Right', 'A52_Tongue_Out']
    # Arkit 기본 블렌드쉐입
    _BS_ARKitList = ['browInnerUp', 'browDownLeft', 'browDownRight', 'browOuterUpLeft',
                          'browOuterUpRight', 'eyeLookUpLeft', 'eyeLookUpRight', 'eyeLookDownLeft',
                          'eyeLookDownRight', 'eyeLookOutLeft', 'eyeLookInLeft', 'eyeLookInRight',
                          'eyeLookOutRight', 'eyeBlinkLeft', 'eyeBlinkRight', 'eyeSquintLeft',
                          'eyeSquintRight', 'eyeWideLeft', 'eyeWideRight', 'cheekPuff', 'cheekSquintLeft',
                          'cheekSquintRight', 'noseSneerLeft', 'noseSneerRight', 'jawOpen', 'jawForward',
                          'jawLeft', 'jawRight', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight',
                          'mouthRollUpper', 'mouthRollLower', 'mouthShrugUpper', 'mouthShrugLower', 'mouthClose',
                          'mouthSmileLeft', 'mouthSmileRight', 'mouthFrownLeft', 'mouthFrownRight',
                          'mouthDimpleLeft', 'mouthDimpleRight', 'mouthUpperUpLeft', 'mouthUpperUpRight',
                          'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight',
                          'mouthStretchLeft', 'mouthStretchRight', 'tongueOut']
    # JB 확장된 블렌드쉐입 리스트
    _BS_ICTList = ['eyeBlinkLeft', 'eyeBlinkRight', 'eyeLookDownLeft', 'eyeLookDownRight', 'eyeLookInLeft',
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

    _Meshes=[]

    def __init__(self, ui_path=None, title_name='CC3Opimizer', parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        print 'Start CC3 Blendshape Opimizer'

        # 윈도우 설정
        self.setWindowTitle(title_name)
        self.setMinimumSize(200, 250)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # 순차적 실행
        self.init_ui(ui_path)
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
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)


    # ------------------------------------------------------------------------------------------
    # 버튼 연결
    # ------------------------------------------------------------------------------------------
    def create_connection(self):
        self.ui.pb_addmeshes.clicked.connect(self.add_meshes_for_cleanup)
        self.ui.pb_clearlist.clicked.connect(self.clear_list)
        self.ui.pb3.clicked.connect(self.cleanup_cc3)






    # ------------------------------------------------------------------------------------------
    # 메소드들
    # ------------------------------------------------------------------------------------------
    def test1(self):
        sel = self.current_select()
        bsNode = self.get_bs_node(sel)
        index = self.get_bs_list(bsNode)
        print self.get_bs_index(bsNode, 'A52_Tongue_Out')





    def test2(self):
        print('test2')
    def test3(self):
        print('test3')

    def current_select(self, onlyOne=True):
        sel = cmds.ls(sl=1)
        if onlyOne:
            return sel[0]
        else:
            return sel

    def get_bs_all(self, meshName):
        if not meshName:
            print('Select Blendshape Mesh')
            return
        _meshHistory = cmds.listHistory(meshName)
        _meshBlendshapeNode = cmds.ls(_meshHistory, type='blendShape')[0]
        _meshBlendshapeName = cmds.listAttr(_meshBlendshapeNode + '.w', m=True)
        return meshName, _meshBlendshapeNode, _meshBlendshapeName

    def get_bs_node(self, meshName):
        if not meshName:
            print('Select Blendshape Mesh')
            return
        _meshHistory = cmds.listHistory(meshName)
        try:
            _meshBlendshapeNode = cmds.ls(_meshHistory, type='blendShape')[0]
            return _meshBlendshapeNode
        except:
            return False

    def get_bs_list(self, bsNode):
        # Get attribute alias
        _targetList = cmds.listAttr(bsNode+'.w',m=True)
        if not _targetList: _targetList = []

        # Return result
        return _targetList

    def get_bs_index(self, bsNode, bsName):

        # Check target
        if not cmds.objExists(bsNode + '.' + bsName):
            raise Exception('Blendshape "' + bsNode + '" has no target "' + bsName + '"!')

        # Get attribute alias
        aliasList = cmds.aliasAttr(bsNode, q=True)
        aliasIndex = aliasList.index(bsName)
        aliasAttr = aliasList[aliasIndex+1]

        # Get index
        targetIndex = int(aliasAttr.split('[')[-1].split(']')[0])

        # Return result
        return targetIndex

    def next_available_bs_index(self, bsNode):

        # Get blendShape target list
        targetList = self.get_bs_list(bsNode)
        if not targetList: return 0

        # Get last index
        lastIndex = self.get_bs_index(bsNode, targetList[-1])
        nextIndex = lastIndex + 1

        # Return result
        return nextIndex



    def rename_blendshape(self,bsNode='', bsNames='', original_bsName='', rename_bsName=''):
        for bs in bsNames:
            if original_bsName == bs:
                try:

                    ## rename
                    cmds.aliasAttr(rename_bsName, bsNode + '.weight[%s]' % self.get_bs_index(bsNode, bs))

                    om.MGlobal.displayInfo(u'{}을 {}로 변경하였습니다.'.format(original_bsName, rename_bsName))
                except:
                    om.MGlobal.displayError(u'변경하지 못했습니다.')

    def remove_blendshape(self, bsMesh='', bsNode='', originalName='',removeName=''):
        # 선택한 녀석
        if originalName == removeName:

            ## remove
            cmds.blendShape(bsNode, e=1, rm=1, t=[bsMesh, self.getTargetIndex(bsNode, originalName), originalName, 1])

            om.MGlobal.displayInfo(u'{0}에서 {1}를 삭제했습니다.'.format(bsNode, originalName))
            cmds.select(bsNode)

    def add_meshes_for_cleanup(self):
        sel = cmds.ls(sl=1)
        for mesh in sel:
            if self.get_bs_node(mesh):
                self._Meshes.append(mesh)
                self.ui.listWidget.addItem(mesh)

    def clear_list(self):
        self.ui.listWidget.clear()
        self._Meshes = []

    def cleanup_cc3(self):
        if self._Meshes:
            for mesh in self._Meshes:
                # init
                remove_bsNames=[]
                bsNode = self.get_bs_node(mesh)

                # ARKit용으로 이름바꾸기
                for index, bs in enumerate(self._BS_CC3ExPlusList):
                    if cmds.objExists(bsNode + '.' + bs):
                        cmds.aliasAttr(self._BS_ARKitList[index], bsNode + '.weight[%s]' % self.get_bs_index(bsNode, bs))

                # 변경된 리스트
                remove_bsNames = self.get_bs_list(bsNode)

                # ARKit용을 제외한 리스트
                for bs in self._BS_ARKitList:
                    if bs in remove_bsNames:
                        remove_bsNames.remove(bs)

                # 지우기
                for bs in remove_bsNames:
                    if cmds.objExists(bsNode + '.' + bs):
                        targetIndex = self.get_bs_index(bsNode, bs)
                        cmds.blendShape(bsNode, e=1, rm=1, t=[mesh, targetIndex, bs, 1])
                        cmds.removeMultiInstance(bsNode + '.weight[%s]' % targetIndex, b=True)
                        cmds.removeMultiInstance(bsNode +'.inputTarget[0].inputTargetGroup[%s]' % targetIndex, b=True)










if __name__ == "__main__":
    try:
        cc3Opti.close()
        cc3Opti.deleteLater()
    except:
        pass

    cc3Opti = DesignerUI()
    cc3Opti.show()