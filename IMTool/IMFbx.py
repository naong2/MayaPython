#-*- coding:utf-8 -*-
import sys
import maya.mel as mel
import maya.cmds as cmds




def setFbxExportOptions_SkeletalMesh():
    """
    This method sets the appropriate FBX options for export
    :return:
    """

    # 현재 FBX 설정을 저장해놓는다
    mel.eval('FBXPushSettings;')

    # 아래와 같이 설정을 바꾸고
    mel.eval('FBXResetExport;'
             'FBXExportSplitAnimationIntoTakes -c;'
             'FBXExportInputConnections -v false;'
             'FBXExportIncludeChildren -v false;'
             'FBXExportLights -v false;'
             'FBXExportShapes -v false;'
             'FBXExportCameras -v false; '
             'FBXExportInAscii -v true; '
             'FBXExportFileVersion FBX201800; '
             'FBXExportConstraints -v false;'
             'FBXExportInstances -v false;'
             'FBXExportUpAxis y;'
             'FBXExportBakeComplexAnimation -v true; '
             'FBXExportSmoothingGroups -v false; '
             'FBXExportSmoothMesh -v false; '
             'FBXExportApplyConstantKeyReducer -v false; '
             'FBXExportBakeComplexStep -v 1; '
             'FBXExportCacheFile -v false;'
             'FBXExportEmbeddedTextures -v false;'
             'FBXExportSkins -v false;')

    def setFbxExportOptions_Animation():
        """
        This method sets the appropriate FBX options for export
        :return:
        """

        # 현재 FBX 설정을 저장해놓는다
        mel.eval('FBXPushSettings;')

        # 아래와 같이 설정을 바꾸고
        mel.eval('FBXResetExport;'
                 'FBXExportSplitAnimationIntoTakes -c;'
                 'FBXExportLights -v false;'
                 'FBXExportShapes -v false;'
                 'FBXExportCameras -v false; '
                 'FBXExportConstraints -v false;'
                 'FBXExportInstances -v false;'
                 'FBXExportUpAxis y;'              
                 'FBXExportSmoothMesh -v false; '
                 'FBXExportApplyConstantKeyReducer -v false;'
                 'FBXExportBakeComplexStep -v 1; '
                 'FBXExportCacheFile -v false;'
                 )
'''
'FBXExportInputConnections -v false;'
'FBXExportIncludeChildren -v false;'
'FBXExportInAscii -v true; '
'FBXExportFileVersion FBX201800; '
'FBXExportBakeComplexAnimation -v true; '
'FBXExportSmoothingGroups -v false; '
'FBXExportEmbeddedTextures -v false;'
'FBXExportSkins -v false;
'''

def setFbxOption_Smooth(_bool='true'):
    mel.eval('FBXExportSmoothingGroups -v {}'.format(_bool))

def setFbxOption_Tangent(_bool='true'):
    mel.eval('FBXExportSmoothingGroups -v {}'.format(_bool))




def setFbxOption_Ascii(_bool='true'):
    mel.eval('FBXExportInAscii -v {}'.format(_bool))

def setFbxOption_IncludeChildren(_bool='true'):
    mel.eval( 'FBXExportIncludeChildren -v {};'.format(_bool))

def setFbxOption_InputConnection(_bool='true'):
    mel.eval( 'FBXExportIncludeChildren -v {};'.format(_bool))

def setFbxOption_EmbeddedTextures(_bool='false'):
    mel.eval('FBXExportEmbeddedTextures -v {};'.format(_bool))

def setFbxOption_BakeComplexAnimatio(_bool='true'):
    mel.eval('FBXExportBakeComplexAnimation -v {};'.format(_bool))

def setFbxOption_FbxVersion(ver='FBX201800'):
    mel.eval('FBXExportFileVersion {};'.format(ver))



# -------------------------------------------------------------------------------
# Export
# -------------------------------------------------------------------------------
# Selection 셋을 이용한 익스포트
def exportFbx(_selection, _exportPath):

    # 미리 설정된 FBX 옵션을 적용

    setFbxExportOptions_Animation()

    # 선택 해제
    cmds.select(cl=True)

    # 익스포트할 녀석들 다시 잡기
    cmds.select(_selection, r=True)
    #mel.eval('SelectHierarchy')

    # export to FBX
    mel.eval('FBXExport -f "{0}" -s'.format(_exportPath))
    print('File was exported to: \n')
    print _exportPath

    # 아까 저장해놓은 FBX 옵션을 되돌려 놓는다
    mel.eval('FBXPopSettings;')

    # 마야 맨 밑줄에 표시돼
    sys.stdout.write(u'FBX 익스포트 완료 \n')



# Root를 자동으로 찾아서 Joint만 익스포트
def Export_Animation_Auto(_exportPath,ascii=True,children=False,Bake=True,Texture=False,version='FBX201800'):
    setFbxExportOptions_Animation()
    setFbxOption_Ascii(ascii)
    setFbxOption_IncludeChildren(children)
    setFbxOption_BakeComplexAnimatio(Bake)
    setFbxOption_EmbeddedTextures(Texture)
    setFbxOption_FbxVersion(version)
    # 자동 Root를 찾아서 조인트만 선택한다
    cmds.select("Root")
    jointHierarchy = cmds.select(cmds.ls(dag=1,sl=1,type='joint'))
    mel.eval('FBXExport -f "{0}" -s'.format(_exportPath))
    # 아까 저장해놓은 FBX 옵션을 되돌려 놓는다
    mel.eval('FBXPopSettings;')



# 선택은 내가 직접
def Export_Animation_Direct(_exportPath,ascii=True,children=False,Bake=True,Texture=False,version='FBX201800'):
    setFbxExportOptions_Animation()
    setFbxOption_Ascii(ascii)
    setFbxOption_IncludeChildren(children)
    setFbxOption_BakeComplexAnimatio(Bake)
    setFbxOption_EmbeddedTextures(Texture)
    setFbxOption_FbxVersion(version)
    mel.eval('FBXExport -f "{0}" -s'.format(_exportPath))
    # 아까 저장해놓은 FBX 옵션을 되돌려 놓는다
    mel.eval('FBXPopSettings;')

