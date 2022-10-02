import os
from inspect import getsourcefile

# Version 1.0
class ControlRig_V1:
    # Setup
    VERSION = 'JBControlRig V1'
    ControlRigMayaFileName = 'JBControlRig_Controller_v1.mb'
    JB_CONTROLRIG_MAYA_FILE = os.path.abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace(getsourcefile(lambda: 0).split('/')[-1], ControlRigMayaFileName)

    def __init__(self,ControlRigBlendshapeName='BS_node'):
        self.ControlRigBS = ControlRigBlendshapeName
        self.BSList = ['eyeBlinkLeft', 'eyeBlinkRight', 'eyeLookDownLeft', 'eyeLookDownRight', 'eyeLookInLeft',
                             'eyeLookInRight', 'eyeLookOutLeft', 'eyeLookOutRight', 'eyeLookUpLeft', 'eyeLookUpRight',
                             'eyeSquintLeft', 'eyeSquintRight', 'eyeWideLeft', 'eyeWideRight', 'browDownLeft',
                             'browDownRight', 'browInnerUp', 'browInnerUpLeft', 'browInnerUpRight', 'browOuterUpLeft',
                             'browOuterUpRight', 'jawOpen', 'jawRight', 'jawForward', 'jawLeft', 'mouthClose',
                             'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthFunnel',
                             'mouthLeft', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft',
                             'mouthPressRight',
                             'mouthPucker', 'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
                             'mouthShrugUpper', 'mouthSmileLeft', 'mouthSmileRight', 'mouthStretchLeft',
                             'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'cheekPuff', 'cheekPuffLeft',
                             'cheekPuffRight', 'cheekRaiserLeft', 'cheekRaiserRight', 'cheekSquintLeft',
                             'cheekSquintRight',
                             'noseSneerLeft', 'noseSneerRight', 'tongueOut']
        self.ConnectInfo_BS = [self.ControlRigBS + '.mouthFrownLeft', self.ControlRigBS + '.mouthDimpleRight',
                      self.ControlRigBS + '.mouthDimpleLeft',
                      self.ControlRigBS + '.mouthClose', self.ControlRigBS + '.jawRight', self.ControlRigBS + '.jawOpen',
                      self.ControlRigBS + '.jawLeft',
                      self.ControlRigBS + '.jawForward', self.ControlRigBS + '.mouthFunnel', self.ControlRigBS + '.mouthFrownRight',
                      self.ControlRigBS + '.eyeWideRight',
                      self.ControlRigBS + '.cheekRaiserLeft', self.ControlRigBS + '.cheekPuffRight',
                      self.ControlRigBS + '.cheekPuffLeft',
                      self.ControlRigBS + '.browOuterUpRight', self.ControlRigBS + '.browOuterUpLeft',
                      self.ControlRigBS + '.browInnerUpRight',
                      self.ControlRigBS + '.browInnerUpLeft', self.ControlRigBS + '.browDownRight',
                      self.ControlRigBS + '.browDownLeft',
                      self.ControlRigBS + '.noseSneerRight', self.ControlRigBS + '.noseSneerLeft',
                      self.ControlRigBS + '.mouthUpperUpRight',
                      self.ControlRigBS + '.mouthUpperUpLeft', self.ControlRigBS + '.mouthStretchRight',
                      self.ControlRigBS + '.mouthStretchLeft',
                      self.ControlRigBS + '.eyeLookInLeft', self.ControlRigBS + '.eyeLookDownRight',
                      self.ControlRigBS + '.eyeLookDownLeft',
                      self.ControlRigBS + '.eyeBlinkRight', self.ControlRigBS + '.eyeBlinkLeft',
                      self.ControlRigBS + '.cheekSquintRight',
                      self.ControlRigBS + '.cheekSquintLeft', self.ControlRigBS + '.cheekRaiserRight',
                      self.ControlRigBS + '.eyeWideLeft',
                      self.ControlRigBS + '.eyeSquintRight', self.ControlRigBS + '.eyeSquintLeft',
                      self.ControlRigBS + '.eyeLookUpRight',
                      self.ControlRigBS + '.eyeLookUpLeft', self.ControlRigBS + '.eyeLookOutRight',
                      self.ControlRigBS + '.eyeLookOutLeft',
                      self.ControlRigBS + '.eyeLookInRight', self.ControlRigBS + '.mouthPucker',
                      self.ControlRigBS + '.mouthLowerDownRight',
                      self.ControlRigBS + '.mouthPressRight', self.ControlRigBS + '.mouthPressLeft',
                      self.ControlRigBS + '.mouthRollLower',
                      self.ControlRigBS + '.mouthRight', self.ControlRigBS + '.mouthRollUpper', self.ControlRigBS + '.mouthSmileLeft',
                      self.ControlRigBS + '.mouthShrugUpper', self.ControlRigBS + '.mouthShrugLower',
                      self.ControlRigBS + '.mouthSmileRight',
                      self.ControlRigBS + '.mouthLowerDownLeft', self.ControlRigBS + '.mouthLeft']
        self.ConnectInfo_Ctrl = [u'blendShape1_mouthFrown_L_Mesh.output', u'mouthDimple_R_ctl.translateY',
                        u'mouthDimple_L_ctl.translateY', u'mouthClose_ctl.translateY',
                        u'blendShape1_jawRight_Mesh.output',
                        u'jaw_ctl.translateY', u'blendShape1_jawLeft_Mesh.output', u'Jaw_F_ctl.translateY',
                        u'mouthFunnel_ctl.translateY', u'blendShape1_mouthFrown_R_Mesh1.output',
                        u'blendShape1_eyeWide_R_Mesh.output', u'cheekRaiser_L_ctl.translateY',
                        u'cheekPuff_R_ctl.translateY', u'cheekPuff_L_ctl.translateY',
                        u'blendShape1_browOuterUp_R_Mesh.output', u'blendShape1_browOuterUp_L_Mesh.output',
                        u'browInnerUp_R_ctl.translateY', u'browInnerUp_L_ctl.translateY',
                        u'blendShape1_browDown_R_Mesh.output', u'blendShape1_browDown_L_Mesh.output',
                        u'noseSneer_R_ctl.translateY', u'noseSneer_L_ctl.translateY', u'mouthUpperUp_R_ctl.translateY',
                        u'mouthUpperUp_L_ctl.translateY', u'mouth_end_R_ctrl.translateY',
                        u'mouth_end_L_ctrl.translateY',
                        u'blendShape1_eyeLookIn_L_Mesh.output', u'blendShape1_eyeLookDown_R_Mesh.output',
                        u'blendShape1_eyeLookDown_L_Mesh.output', u'blendShape1_eyeBlink_R_Mesh.output',
                        u'blendShape1_eyeBlink_L_Mesh.output', u'cheekSquint_R_ctl.translateY',
                        u'cheekSquint_L_ctl.translateY', u'cheekRaiser_R_ctl.translateY',
                        u'blendShape1_eyeWide_L_Mesh.output', u'eyeSquint_R_ctl.translateY',
                        u'eyeSquint_L_ctl.translateY',
                        u'blendShape1_eyeLookUp_R_Mesh.output', u'blendShape1_eyeLookUp_L_Mesh.output',
                        u'blendShape1_eyeLookOut_R_Mesh.output', u'blendShape1_eyeLookOut_L_Mesh.output',
                        u'blendShape1_eyeLookIn_R_Mesh.output', u'mouthPucker_ctl.translateY',
                        u'mouthLowerDown_R_ctl.translateY', u'mouth_press_R_ctl.translateY',
                        u'mouth_press_L_ctl.translateY', u'mouthRollLower_ctl.translateY',
                        u'blendShape1_mouthRight_Mesh.output', u'mouthRollUpper_ctl.translateY',
                        u'blendShape1_mouthSmile_L_Mesh.output', u'mouthShrugUpper_ctl.translateY',
                        u'mouthShrugLower_ctl.translateY', u'blendShape1_mouthSmile_R_Mesh1.output',
                        u'mouthLowerDown_L_ctl.translateY', u'blendShape1_mouthLeft_Mesh.output']
        self.JBController = [u'mouth_press_R_ctl', u'mouth_press_L_ctl', u'cheekRaiser_R_ctl', u'eyelid_Up_L_ctl',
                               u'eyeSquint_R_ctl', u'eyeSquint_L_ctl', u'mouthPucker_ctl', u'mouthDimple_L_ctl',
                               u'cheekRaiser_L_ctl', u'cheekSquint_L_ctl', u'cheekSquint_R_ctl', u'browOuterUp_L_ctl',
                               u'browOuterUp_R_ctl', u'browInnerUp_L_ctl', u'browInnerUp_R_ctl', u'eyelid_Up_R_ctl',
                               u'eye_control', u'mouthClose_ctl', u'mouth_end_R_ctrl', u'mouth_end_L_ctrl',
                               u'mouthLowerDown_R_ctl', u'cheekPuff_R_ctl', u'cheekPuff_L_ctl', u'noseSneer_R_ctl',
                               u'noseSneer_L_ctl', u'jaw_ctl', u'mouthDimple_R_ctl', u'mouth_L_R_ctl',
                               u'mouthLowerDown_L_ctl', u'mouthShrugLower_ctl', u'mouthShrugUpper_ctl',
                               u'mouthUpperUp_R_ctl', u'mouthUpperUp_L_ctl', u'mouthRollUpper_ctl', u'mouthFunnel_ctl',
                               u'mouthRollLower_ctl', u'Jaw_F_ctl']

class ControlRig_V2:
    pass

#
def print_connect_info():
    pass
