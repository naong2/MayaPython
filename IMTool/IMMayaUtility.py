# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import maya.OpenMaya as om
import pymel as pm
import maya.mel as mel

def CreateJointToVertex(center='', fromCenter=False, step=1):
    """ creates joints based on vertices positions or curve.cvs """
    vtx = cmds.ls(sl=1, fl=1)
    # is selection curve?
    jnt = []
    n = 0
    newVtxList = []
    # loop rebuilds vtx list, encase of high topo
    for i in range(0, len(vtx), step):
        newVtxList.append(vtx[i])

    # get vtx pos, set jnt to pos
    for v in newVtxList:
        cmds.select(cl=1)
        jnt.append(cmds.joint())
        # 버텍스의 위치를 가져와서
        pos = cmds.xform(v, q=1, ws=1, t=1)
        # 조인트의 위치를 변경한다
        cmds.xform(jnt[n], ws=1, t=pos)

        cmds.select(v)
        cmds.select(jnt[n], add=True)
        mel.eval('pointOnPolyConstraint -offset 0 0 0  -weight 1;')
        # currently has to use PYMEL implentation as python cmds does not work 'because maya'
        #pm.runtime.PointOnPolyConstraint(v, jnt[n])

        if fromCenter:
            posC = cmds.xform(center, q=1, ws=1, t=1)
            cmds.select(cl=1)
            jntC = cmds.joint()
            cmds.xform(jntC, ws=1, t=posC)
            cmds.parent(jnt[n], jntC)
            cmds.joint(jntC, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
        n = n + 1
    return jnt

def get_selected_comp_ids():
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(sel)
    li = 0
    path = om.MDagPath()
    comp = om.MObject()
    stat = sel.getDagPath(li, path, comp)
    compFn = om.MFnSingleIndexedComponent(comp)
    ids = om.MIntArray()
    compFn.getElements(ids)
    message =  "  selected VertexID: \n\n           {}".format(ids)
    cmds.confirmDialog(title='VertexID', message=message, defaultButton='Yes',
                       cancelButton='No', button=['OK'], dismissString='No')
    return ids

def count_selected(hierachy=False):
    sel = cmds.ls(sl=True)
    if hierachy:
        mel.eval('SelectHierarchy')
    count = 0
    for i in sel:
        count += 1
    message =  "  selected Count: \n\n           {}".format(count)
    cmds.confirmDialog(title='Selct Object Count', message=message, defaultButton='Yes',
                       cancelButton='No', button=['OK'], dismissString='No')
