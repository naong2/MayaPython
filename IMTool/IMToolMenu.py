#-*- coding:utf-8 -*-
import os
import maya.cmds as cmds
import maya.mel as mel

#import IMTool.IMP4xpf as IMP4xpf
import IMTool.IMUtil as imu

# Tool list
#import IMTool.IMWin_Export_v1 as IMWin_Export_v1
import IMTool.IMMayaUtility as IMMayaUtility
#reload(IMMayaUtility)
#import IMTool.IMWin_AddJoint as IMWin_AddJoint
#import IMTool.IMMyShelf as IMMyShelf

#import IMTool.IMWin_FaceControl as IMWin_FaceControl
#import IMTool.IMWin_Renamer as IMWin_Renamer

exporter_dialog = None
multi_exporter_dialog = None

# Initialize
########################################################################################
_MenuName = 'IMTools'
_ArtResourceFolder =r'D:\Work2020'


#
########################################################################################

def CreateMenu():
    global _MenuName
    _MenuName = 'IMTools'

    #부모를 현재 윈도우로 설정한다
    cmds.setParent(mel.eval("$temp1=$gMainWindow"))

    # 기존메뉴 삭제
    DeleteMenu()

    # 상단 메뉴
    menu = cmds.menu( _MenuName,  label='IMTools', tearOff=True)

    # 메뉴
    cmds.menuItem(divider=True)
    cmds.menuItem(label='IM Exporter', image='executeDebug.png',command=lambda x:open_IMWin_Export())
    cmds.menuItem(label='IM Batch Exporter', image='executeAll.png',command=lambda x:open_IMWin_MultiExport())
    cmds.menuItem(divider=True)
    cmds.menuItem(label='IM Blend Copy', image='executeDebug.png', command=lambda x: open_IMWin_BlendCopy())
    cmds.menuItem(label='IM point On Surface', image="ptPosCrvConstraint.png", command=lambda x: Open_PointOnSurface())
    cmds.menuItem(label='IM Add Joint Constrain', image="out_joint.png", command=lambda x: open_add_Joint_Contrain())
    cmds.menuItem(label='Face Control', image='sphere.png',command=lambda x: open_FaceControl())
    cmds.menuItem(label=u'IM BlendShape Extractor', image='cmdWndIcon.png',command=lambda x: Open_BlendShapeEx())
    cmds.menuItem(divider=True)
    cmds.menuItem(label='Hair Color Divider', image='paintEffectsTool.png',command=lambda x: Open_HairPaint())
    cmds.menuItem(label="Align Normal", image='stitchSrf.png',command=lambda x: Open_AlignNormal())
    cmds.menuItem(label="IM Grid", image='GridDown.png',command=lambda x: open_Grid())
    cmds.menuItem(label=u'IM 리네임툴', image='sphere.png',command=lambda x: open_renumbering())

    cmds.menuItem(divider=True)
    #cmds.menuItem(label='Snappers Tools', command=lambda x:open_SnappersTool())
    #cmds.menuItem(divider=True)
    cmds.menuItem(label=u'폴더열기: Art ReSource', command=lambda x:openSourcefolder())
    #cmds.menuItem(label=u'폴더열기: 마지막작업소스폴더', command=lambda x:openSourcefolder())
    cmds.menuItem(divider=True)
    # 서브메뉴 시작
    sub_menu1 = cmds.menuItem(label="Sub Tools", subMenu=True)
    cmds.menuItem(label="Selected Counter", command=lambda x:tool_selectd_counter())
    cmds.menuItem(label='IM My Shelf', image='connect24_NEX.png',command=lambda x:open_MyShelf())


    cmds.setParent(menu, menu=True)
    # 서브메뉴 끝
    cmds.menuItem(label="About", command=lambda x:open_about())
    cmds.setParent(menu, menu=True)

def DeleteMenu():
    global _MenuName
    if cmds.control(_MenuName, exists=True):
        cmds.deleteUI(_MenuName, menu=True)


# --------------------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------------------

def Open_AlignNormal():
    import AlignNormal
    AlignNormal.main()

def Open_HairPaint():
    import IM_HairDivColor

def Open_PointOnSurface():
    import IM_JointToJoint as IMJJ

def Open_BlendShapeEx():
    import IMWin_BlendShape as IMBSE
    IMBSE.main()

def open_renumbering():
    import IMTool.IMWin_Renamer as IMWin_Renamer
    #reload(IMWin_Renamer)
    IMWin_Renamer.main()

def open_Grid():
    melfile = os.path.join(imu.getPathIMTool(),'IMGrid.mel').replace("\\","/")
    mel.eval('source "{}";'.format(melfile))
    mel.eval('IMGrid;')

def open_FaceControl():
    import IMTool.IMWin_FaceControl as IMWin_FaceControl
    IMWin_FaceControl.main()

def open_IMWin_Export():
    import IMTool.IMWin_Export_v1 as IMWin_Export_v1
    #reload(IMWin_Export_v1)
    global exporter_dialog
    print 'Start Exporter UI'
    try:
        exporter_dialog.close()
        exporter_dialog.deleteLater()
    except:
        pass
    exporter_dialog = IMWin_Export_v1.DesignerUI()
    exporter_dialog.show()

def open_IMWin_BlendCopy():
    import IMTool.IMWin_BlendCopy as IMWin_BlendCopy
    #reload(IMWin_BlendCopy)
    global blendcopy_dialog
    print 'Start Exporter UI'
    try:
        blendcopy_dialog.close()
        blendcopy_dialog.deleteLater()
    except:
        pass
    blendcopy_dialog = IMWin_BlendCopy.DesignerUI()
    blendcopy_dialog.show()

def open_IMWin_MultiExport():
    import IMWin_MultiExporter as IMWin_MultiExporter
    global multi_exporter_dialog
    print 'Start Exporter UI'
    try:
        multi_exporter_dialog.close()
        multi_exporter_dialog.deleteLater()
    except:
        pass
    multi_exporter_dialog = IMWin_MultiExporter.IMMulti_Exporter()
    multi_exporter_dialog.show()


def open_MyShelf():
    import IMTool.IMMyShelf as IMMyShelf
    IMMyShelf.main()

# def open_SnappersTool():
#     try:
#         from Snappers.rig_manager import snappers_rig_manager
#         snappers_rig_manager.showRigManagerWindow()
#     except:
#         print "Can't find Snappers module"

def open_add_Joint_Contrain():
    import IMTool.IMWin_AddJoint as IMWin_AddJoint
    reload(IMWin_AddJoint)
    try:
        AddJoint_dialog.close()
        AddJoint_dialog.deleteLater()
    except:
        pass

    AddJoint_dialog = IMWin_AddJoint.AddJointDialog()
    AddJoint_dialog.show()

def open_about():
    print 'naong2@gmail.com'


def tool_selectd_counter():
    IMMayaUtility.count_selected()



def openSourcefolder():
    os.startfile(_ArtResourceFolder)
