import maya.cmds as cmds
import maya.OpenMaya as om
import time


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

def show():
    winname = "CreateJointToVertex"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname)
    cmds.showWindow()
    cmds.columnLayout(adj=1)


    cmds.button(l='Create Joint',c=do_create_joint, h=50,bgc=[ 0.6, 0,0.6])
    cmds.button(l='Create Joint & Constraint', c=do_create_joint_constraint, h=50, bgc=[0.3, 0.1, 0.6])
    cmds.columnLayout(adj=1)


show()

