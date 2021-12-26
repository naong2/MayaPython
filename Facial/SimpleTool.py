import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import time

##########################################################################
# Copy Blendshapes
##########################################################################
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
def blendshape_copy(*args):
    _sel = cmds.ls(sl=1)[0]
    meshHistory = cmds.listHistory(_sel)
    bsNodeName = cmds.ls(meshHistory, type='blendShape')[0]
    bsNameList = cmds.listAttr(bsNodeName + '.w', m=True)
    targetIndex = len(bsNodeName)+1
    copyBlendshapes = []

    # reset
    for bs in bsNameList:
        if bs in ICTBlendShapeList:
            cmds.setAttr(bsNodeName + '.' + bs, 0)
            copyBlendshapes.append(bs)
        else:
            cmds.setAttr(bsNodeName + '.' + bs, 1)
    # copy
    for bs in copyBlendshapes:
        cmds.setAttr(bsNodeName + '.' + bs, 1)
        dup = cmds.duplicate(_sel)
        redup = cmds.rename(dup,bs)
        cmds.setAttr(bsNodeName + '.' + bs, 0)


##########################################################################
# Delta
##########################################################################
def assignMFnMesh(arg):
    """
    assign object to MFnMesh class
    """
    mSel = om.MSelectionList()
    mSel.clear()
    mSel.add(arg)
    dag = om.MDagPath()
    mSel.getDagPath(0, dag)
    meshFn = om.MFnMesh(dag)
    return meshFn


def getPTArray(obj, worldspace=False):
    """
    get point vector array from MFnMesh
    """
    PointSpace = om.MSpace.kObject
    if worldspace == True:
        PointSpace = om.MSpace.kWorld


    meshFn = assignMFnMesh(obj)
    points = om.MPointArray()
    points.clear()
    meshFn.getPoints(points, PointSpace)
    pointsArray = om.MVectorArray()
    pointsArray.clear()
    for i in range(points.length()):
        ptVector = om.MVector(points[i])
        pointsArray.append(ptVector)
    return pointsArray


def getDelta(*args, **kwargs):
    startTime = time.time()
    TargetMesh = args[0]
    SourceMesh = args[1]
    tmpSpace = kwargs.get('worldspace', False)
    PointSpace = om.MSpace.kObject
    if tmpSpace == True:
        PointSpace = om.MSpace.kWorld


    PointDelta = om.MVectorArray()
    PointDelta.clear()
    TargetMeshPoints = getPTArray(TargetMesh, worldspace=PointSpace)
    SourceMeshPoints = getPTArray(SourceMesh, worldspace=PointSpace)
    for i in range(TargetMeshPoints.length()):
        PointDelta.append(TargetMeshPoints[i] - (SourceMeshPoints[i]))
    print ('DeltaVector Execution time in second : {:010.4f}s'.format(time.time() - startTime))
    return PointDelta


def mergeOffset(*args, **kwargs):
    startTime = time.time()
    BaseMesh = args[0]
    PointsDelta = args[1]
    if not isinstance(PointsDelta, om.MVectorArray):
        return False


    tmpSpace = kwargs.get('worldspace', False)
    PointSpace = om.MSpace.kObject
    if tmpSpace == True:
        PointSpace = om.MSpace.kWorld


    BaseMeshPoints = getPTArray(BaseMesh)
    offsetPoints = om.MPointArray()
    offsetPoints.clear()
    for i in range(BaseMeshPoints.length()):
        tmpPoint = om.MPoint(BaseMeshPoints[i] + (PointsDelta[i]))
        offsetPoints.append(tmpPoint)
    print ('PointArray MergeFunction Execution time in second : {:010.4f}s'.format(time.time() - startTime))
    return offsetPoints

def delta_set_point(*args):
    tmp_sel = cmds.ls(sl=1)
    tmpArray = getDelta(tmp_sel[0], tmp_sel[1])
    resultArray = mergeOffset(tmp_sel[2], tmpArray)
    deltaMesh = assignMFnMesh(tmp_sel[2])
    deltaMesh.setPoints(resultArray, om.MSpace.kObject)

##########################################################################
# Create Joint to vertex
##########################################################################
def create_joint_to_vertex(constraint=True):
    vtx = cmds.ls(sl=1, fl=1)
    step = 1
    jnt = []
    n = 0
    newVtxList = []
    for i in range(0, len(vtx), step):
        newVtxList.append(vtx[i])

    for v in vtx:
        cmds.select(cl=1)
        jnt.append(cmds.joint(n='joint_Vertex'))
        pos = cmds.pointPosition(v, w=1)
        cmds.xform(jnt[n], worldSpace=True, t=pos)
        cmds.select(v)
        cmds.select(jnt[n], add=True)
        if constraint:
            mel.eval('pointOnPolyConstraint -offset 0 0 0  -weight 1;')
        n = n + 1

def do_create_joint(*args):
    create_joint_to_vertex(False)

def do_create_joint_constraint(*args):
    create_joint_to_vertex(True)


##########################################################################
# Align
##########################################################################
def getTranslate(_sel):
    if not isinstance(_sel, list):
        tx = cmds.getAttr(_sel + '.tx')
        ty = cmds.getAttr(_sel + '.ty')
        tz = cmds.getAttr(_sel + '.tz')
    else:
        tx = cmds.getAttr(_sel[0] + '.tx')
        ty = cmds.getAttr(_sel[0] + '.ty')
        tz = cmds.getAttr(_sel[0] + '.tz')
    return [tx, ty, tz]


def setTranslate(_sel, _trans):
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

def AlignObjects(_sel, _startPos=(20, 0, 0), _useStartPosition=True, _maxRows=10, _disX=20, _disY=-38):

    if not _useStartPosition:
        startPostion = _startPos
    else:
        startPostion = getTranslate(_sel[0])

    CurrentRows = 0
    CurrentColumns = 0

    for i in _sel:
        if CurrentRows % _maxRows == 0:
            CurrentColumns += 1
            CurrentRows = 0
        setTranslate(i, [startPostion[0] + (_disX * CurrentRows),
                              startPostion[1] + (_disY * CurrentColumns) - _disY, startPostion[2]])
        CurrentRows += 1

def do_align(*args):
    AlignObjects(_sel=cmds.ls(sl=1))

##########################################################################
# Windows
##########################################################################

def show():
    winname = "SimpleTool"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname)
    cmds.showWindow()
    cmds.columnLayout(adj=1)
    # bgc=[ 0.6, 0,0.6]
    cmds.button(l='Create Joint',c=do_create_joint, h=40)
    cmds.button(l='Create Joint & Constraint', c=do_create_joint_constraint, h=40)
    cmds.button(l='Copy Blendshapes', c=blendshape_copy, h=50, bgc=[ 0.0, 0.6 ,0.6])
    cmds.button(l='Align', c=do_align, h=40)
    cmds.button(l='Delta Set Point', c=delta_set_point, h=50, bgc=[ 0.6, 0,0.6])
    cmds.columnLayout(adj=1)


show()