# -*- coding: UTF-8 -*-
import maya.cmds as cmds

# 잘못 들어간 메터리얼들 다시 적용시켜주기
def selectFace(obj):
    #AO
    cmds.select([obj + '.f[10247:10351]', obj+'.f[10142:10246]'])
    cmds.hyperShade(assign='EyeAO_Mat')
    #Eye
    cmds.select([obj + '.f[8762:9561]', obj + '.f[7962:8761]'])
    cmds.hyperShade(assign='M_MyEyes')
    #Teeth
    cmds.select([obj + '.f[10352:12212]', obj + '.f[12213:13355]', obj + '.f[13356:13643]'])
    cmds.hyperShade(assign='Teeth_Mat')
    #EyeLash
    cmds.select([obj + '.f[9562:10141]'])
    cmds.hyperShade(assign='Eyelish_Mat')


def autoAssignMaterial():
    selected = cmds.ls(sl=1)
    for i in selected:
        selectFace(i)

def MoveFaces():
    #치아 위치 조절
    selected = cmds.ls(sl=1)
    for obj in selected:
        cmds.select([obj + '.f[10352:12212]', obj + '.f[12213:13355]', obj + '.f[13356:13643]'])
        cmds.move('0in', '0.2in', '0in', relative=True, objectSpace=True, worldSpaceDistance=True)

MoveFaces()

#autoAssignMaterial()
