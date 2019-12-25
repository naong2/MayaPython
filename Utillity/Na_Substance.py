# -*- coding: UTF-8 -*-
from maya import cmds

def showMyWindow():
    winname = "IMSubstance"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname, w=525, h=200)
    cmds.windowPref(winname, exists=True )
    #cmds.windowPref(winname, remove=True)
    cmds.showWindow()

    cmds.columnLayout()
    #cmds.button('applyMaterial', c=applyMaterial)
    cmds.iconTextButton(style='iconAndTextVertical', image1='render_adskMaterial.png', label='Add_IDMat', c=applyMaterial)
    cmds.iconTextButton(style='iconAndTextVertical', image1='SP_MessageBoxCritical.png', label='Del Unused',
                        c=deleteUnuseNode)


def applyMaterial(*args):
    select = cmds.ls(sl=1)
    if not select:
        print 'select!'
        return
    shd = cmds.shadingNode('lambert', name="ID_Mat", asShader=True)
    shdSG = cmds.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
    cmds.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
    cmds.sets(select, e=True, forceElement=shdSG)

def deleteUnuseNode(*args):
    import maya.mel as mel
    mel.eval('MLdeleteUnused;')


def get_materials_in_scene(*args):
    for shading_engine in cmds.ls(type='shadingEngine'):
        if cmds.sets(shading_engine, q=True):
            for material in cmds.ls(cmds.listConnections(shading_engine), materials=True):
                print material

showMyWindow()