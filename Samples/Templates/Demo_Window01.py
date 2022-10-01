from maya import cmds
import random


def showMyWindow():
    winname = "myWindow"

    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname, window=True)

    cmds.window(winname)
    cmds.showWindow()

    column = cmds.columnLayout()
    row = cmds.rowLayout()

    cmds.frameLayout(label="Choose Object Type")

    cmds.columnLayout()
    cmds.radioCollection("objectCreationType")
    cmds.radioButton(label="Sphere")
    cmds.radioButton(label="Cube", select=True)
    cmds.radioButton(label="Cone")

    cmds.intField("numObjects", value=3)

    cmds.setParent(column)
    frame = cmds.frameLayout("Choose your max range")

    cmds.gridLayout(numberOfColumns=2, cellWidth=100)

    for axis in 'xyzab':
        cmds.text(label='%s axis' % axis)
        cmds.floatField('%sAxisField' % axis, value=random.uniform(0,10))

    cmds.setParent(column)
    cmds.rowLayout(numberOfColumns=2)

    cmds.radioCollection("randomMode")
    cmds.radioButton(label="Absolute", select=True)
    cmds.radioButton(label="Relative")

    cmds.setParent(column)
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(label="Create", command=onCreateClick)
    cmds.button(label="Randomize", command=onRandomClick)

def onCreateClick(*args):
    radio = cmds.radioCollection("objectCreationType", query=True, select=True)
    mode = cmds.radioButton(radio, query=True, label=True)

    numObjects = cmds.intField("numObjects", query=True, value=True)

    createObjects(mode, numObjects)

def createObjects(mode, numobjects):
    cmds.polyCube()

def onRandomClick(*args):
    radio = cmds.radioCollection("randomMode", query=True, select=True)
    mode = cmds.radioButton(radio, query=True, label=True)

    for axis in 'xyz':
        val = cmds.floatField("%sAxisField" % axis, query=True, value=True)
        randomize(minValue=val*-1, maxValue=val, mode=mode, axes=axis)

def randomize(objList=None, minValue=0, maxValue=10, axes='xyz', mode='Absolute'):
    if objList is None:
        objList = cmds.ls(selection=True)

    for obj in objList:
        for axis in axes:
            current = 0
            if mode == 'Relative':
                current = cmds.getAttr(obj+'.t%s'%axis)
            cmds.setAttr(obj + '.t%s'% axis, val)



showMyWindow()
