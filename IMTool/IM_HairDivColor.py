import maya.cmds as cmds
import random as random
import math as math

ColorSet =[
    [0, 0, 2.0],
    [0.413, 0.930, 0.930],
    [1, 1, 0],
    [0, 2.0, 0.0],
    [2, 0.5, 2.0],
    [0.191, 0.062, 0.255],
    [2, 0.0, 0.0]
]

GraySet =[
    [1, 1, 1],
    [0.8, 0.8, 0.8],
    [0.6, 0.6, 0.6],
    [0.3, 0.3, 0.3],
    [0, 0, 0]
]


getSelectedObjects = []
getSelectedShaders = []
SG_LIST = []
colorList = GraySet

def create_materialG(*args):
    colorList = GraySet
    for color in colorList:
        MaterialName = 'M_HairColor_Vari1'
        shader = cmds.shadingNode('lambert', asShader=True, n=MaterialName)
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=MaterialName + 'SG')
        getSelectedShaders.append(shading_group)
        cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
        cmds.setAttr(shader + '.color', color[0], color[1], color[2])

def create_materialC(*args):
    colorList = ColorSet
    for color in colorList:
        MaterialName = 'M_HairColor_Vari1'
        shader = cmds.shadingNode('lambert', asShader=True, n=MaterialName)
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=MaterialName + 'SG')
        getSelectedShaders.append(shading_group)
        cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
        cmds.setAttr(shader + '.color', color[0], color[1], color[2])

def delete_material(*args):
    cmds.select("M_HairColor_Vari*", allDagObjects=False, noExpand=True)
    sel_shader = cmds.ls(sl=1)
    cmds.delete(sel_shader)

def bake_objects(*args):
    objects = cmds.ls(sl=True)
    del getSelectedObjects[:]
    for item in objects:
        getSelectedObjects.append(item)
    print getSelectedObjects


def bake_shaders(*args):
    shaders = cmds.ls(sl=True)
    del getSelectedShaders[:]
    for item in shaders:
        getSelectedShaders.append(item)
    print getSelectedShaders


def randomize_assign(*args):
    shaderCount = len(getSelectedShaders)
    for item in getSelectedObjects:
        randNumber = random.random()
        roundNumber = math.floor(randNumber * (shaderCount))
        intNumber = int(roundNumber)
        cmds.select(item)
        shaderName = getSelectedShaders[intNumber]
        cmds.hyperShade(assign=shaderName)
    cmds.select(clear=True)


# UI setup

def UI():
    winname = "IMHairRandomColor"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname, mxb=False, sizeable=False)
    cmds.windowPref(winname, exists=True )
    cmds.frameLayout('Create Material', w=200)
    cmds.columnLayout(w=200)
    cmds.button("Gray Materials", w=200, h=25, align='center', c=create_materialG)
    cmds.button("Color Materials", w=200, h=25, align='center', c=create_materialC)
    cmds.button("Delete Materials", w=200, h=25, align='center', c=delete_material)
    cmds.frameLayout('Assign Material', w=200)
    cmds.columnLayout(w=200)
    cmds.button("Select Materials", w=200, h=35, align='center', backgroundColor=[0.647, 0.288, 0.356], c=bake_shaders)
    cmds.button("Select Hairs", w=200, h=35, align='center', backgroundColor=[0.447, 0.588, 0.356], c=bake_objects)
    cmds.button('Random Assign', w=200, h=35, align='center', backgroundColor=[0.992, 0.776, 0.517], c=randomize_assign)
    cmds.setParent('..')
    cmds.showWindow()


UI()