# -*- coding: UTF-8 -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import pymel.core as pm
import os
import IMTool.IMUtil as imu

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class AddJointDialog(QtWidgets.QDialog):

    ICON = QtGui.QIcon()

    def __init__(self, parent=maya_main_window()):
        super(AddJointDialog,self).__init__(parent)

        self.setWindowTitle('Add Joint Constrain')
        self.setMinimumSize(120, 100)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connection()
        self.setProperty("saveWindowPref", True)

    def create_widgets(self):
        self.ok_btn = QtWidgets.QPushButton("Add Joint to Vertex")
        self.ok_btn.setFixedHeight(50)
        self.addIcon(self.ok_btn,'File0441.png')

        self.AddJoint_btn = QtWidgets.QPushButton("Add Joint To Joint")
        self.AddJoint_btn.setFixedHeight(50)
        self.addIcon(self.AddJoint_btn, 'File0441.png')
        self.AddJoint_btn.setStyleSheet("background-color:rgb(255,0,0)")

        self.AddJointGroup_btn = QtWidgets.QPushButton("Add Group Joint To Joint")
        self.AddJointGroup_btn.setFixedHeight(50)
        self.addIcon(self.AddJointGroup_btn, 'File0441.png')
        self.AddJointGroup_btn.setStyleSheet("background-color:rgb(0,0,255)")

        self.counter_btn = QtWidgets.QPushButton("Counter")
        self.counter_btn.setFixedHeight(25)
        self.addIcon(self.counter_btn, 'File0432.png')

        self.ViewVertex_btn = QtWidgets.QPushButton("Vertex ID")
        self.ViewVertex_btn.setFixedHeight(25)
        self.addIcon(self.ViewVertex_btn, 'File0415.png')

        self.counter_label = QtWidgets.QLabel("result")
        self.counter_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.hammer_btn = QtWidgets.QPushButton("Hammer")
        self.hammer_btn.setFixedHeight(20)

        self.attachToSurface_btn = QtWidgets.QPushButton("AttachToSurface")
        self.attachToSurface_btn.setFixedHeight(30)

    def addIcon(self, _object, _icon):
        iconpath = os.path.join(imu.getPathIMTool(),'images',_icon)
        self.ICON.addPixmap(QtGui.QPixmap(iconpath))
        _object.setIcon(self.ICON)


    def create_layout(self):
        buttonLayout = QtWidgets.QVBoxLayout(self)
        buttonLayout.addWidget(self.ok_btn)
        buttonLayout.addWidget(self.AddJoint_btn)
        buttonLayout.addWidget(self.AddJointGroup_btn)
        buttonLayout.addWidget(self.counter_btn)
        buttonLayout.addWidget(self.ViewVertex_btn)
        buttonLayout.addWidget(self.counter_label)
        AnimLayout = QtWidgets.QHBoxLayout(self)
        buttonLayout.addWidget(self.hammer_btn)
        buttonLayout.addWidget(self.attachToSurface_btn)


    def create_connection(self):
        self.ok_btn.clicked.connect(self.CreateJointToVertex)
        self.AddJoint_btn.clicked.connect(self.CreateJointToJoint)
        self.AddJointGroup_btn.clicked.connect(self.CreateGroupJointToJoint)

        self.counter_btn.clicked.connect(self.count_selected)
        self.ViewVertex_btn.clicked.connect(self.get_selected_comp_ids)
        self.hammer_btn.clicked.connect(self.weight_hammer)

    def weight_hammer(self):
        mel.eval('weightHammerVerts;')


    def CreateJointToVertex(self, center='', fromCenter=False, step=1):
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

        for v in vtx:
            cmds.select(cl=1)
            # Joint 생성
            jnt.append(cmds.joint(n='joint_Vertex'))

            # 버텍스의 위치를 가져와서
            # pos = cmds.xform(v, query=True, translation=True, worldSpace=True)
            pos = cmds.pointPosition(v, w=1)
            # 조인트의 위치를 변경한다
            cmds.xform(jnt[n], worldSpace=True, t=pos)

            cmds.select(v)
            cmds.select(jnt[n], add=True)
            # mel.eval('pointOnPolyConstraint -offset 0 0 0  -weight 1;')

            # self.follicle_mesh(jnt[n],v.split('.')[0])
            # currently has to use PYMEL implentation as python cmds does not work 'because maya'
            # pm.runtime.PointOnPolyConstraint(v, jnt[n])

            if fromCenter:
                posC = cmds.xform(center, q=1, ws=1, t=1)
                cmds.select(cl=1)
                jntC = cmds.joint()
                cmds.xform(jntC, ws=1, t=posC)
                cmds.parent(jnt[n], jntC)
                cmds.joint(jntC, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
            n = n + 1
        return jnt



    def CreateJointToJoint(self, center='', fromCenter=False, step=1):
        """ creates joints based on vertices positions or curve.cvs """
        joints = cmds.ls(sl=1, type='joint')
        jnt = []
        n = 0
        for item in joints:
            cmds.select(cl=1)
            jnt.append(cmds.joint(n='joint_Joint'))
            pos = cmds.xform(item, q=1, ws=0, t=1)
            cmds.xform(jnt[n], ws=0, t=pos)
            cmds.select(item)
            cmds.select(jnt[n], add=True)
            mel.eval('doCreateParentConstraintArgList 1 {"1", "0", "0", "0", "0", "0", "0", "0", "1", "", "1"};')
            mel.eval('parentConstraint - mo - weight 1;')
            n += 1

    def CreateGroupJointToJoint(self, center='', fromCenter=False, step=1):
        """ creates joints based on vertices positions or curve.cvs """
        joints = cmds.ls(sl=1, type='joint')
        jnt = []
        grp = []
        n = 0
        for item in joints:
            cmds.select(cl=1)
            jnt.append(cmds.joint())
            grp.append(cmds.group(jnt[n],n='Joint_Grp'))

            pos = cmds.xform(item, q=1, ws=0, t=1)
            cmds.xform(grp[n], ws=0, t=pos)

            cmds.select(item)
            cmds.select(grp[n], add=True)
            mel.eval('doCreateParentConstraintArgList 1 {"1", "0", "0", "0", "0", "0", "0", "0", "1", "", "1"};')
            mel.eval('parentConstraint - mo - weight 1;')
            n += 1


    # 버텍스 ID 알아내기
    def get_selected_comp_ids(self):
        sel = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(sel)
        li = 0
        path = om.MDagPath()
        comp = om.MObject()
        stat = sel.getDagPath(li, path, comp)
        compFn = om.MFnSingleIndexedComponent(comp)
        ids = om.MIntArray()
        compFn.getElements(ids)
        result = "VertexID: {}".format(ids)
        self.counter_label.setText(result)

    # 선택 숫자세기
    def count_selected(self, hierachy=False):
        sel = cmds.ls(sl=True)
        if hierachy:
            mel.eval('SelectHierarchy')
        count = 0
        for i in sel:
            count += 1
        result = "selected: {}".format(count)
        self.counter_label.setText(result)




    def follicle_mesh(obj, mesh):
        import pymel.core as pm


        ''' connect via follicle '''
        ''' first select joint/locator to attatch to surface, then select the surface to attatch to '''
        # list=pm.ls(sl=True)





        closest=cmds.createNode('closestPointOnMesh')
        pm.connectAttr(mesh+'.outMesh',closest+'.inMesh')



        x = getWorldPos(obj)



        pm.setAttr(closest+'.inPositionX', x[0])
        pm.setAttr(closest+'.inPositionY', x[1])
        pm.setAttr(closest+'.inPositionZ', x[2])




        folicle=pm.createNode("follicle")
        folicleTrans=pm.listRelatives(folicle,type='transform',p=True)




        pm.connectAttr(folicle + ".outRotate", folicleTrans[0] + ".rotate")
        pm.connectAttr(folicle + ".outTranslate", folicleTrans[0] + ".translate")



        # 이걸해주면 옷의 매트릭스를 따라가는데 난 무조건
        # 월드에서 계산 되어 주길 원해서 삭제한다.
        # pm.connectAttr(mesh+'.worldMatrix',folicle+'.inputWorldMatrix')




        pm.connectAttr(mesh+'.outMesh',folicle+'.inputMesh')
        pm.setAttr(folicle + ".simulationMethod", 0)
        u=pm.getAttr(closest+'.result.parameterU')
        v=pm.getAttr(closest+'.result.parameterV')
        pm.setAttr(folicle+'.parameterU',u)
        pm.setAttr(folicle+'.parameterV',v)




        pm.rename(folicleTrans[0], obj + '_Fol')

        pm.delete(closest)




        # pymel에서 벗어나기 위해 스트링으로 바꾸고
        folicleTrans = str(folicleTrans[0])
        setElement(getShape(folicleTrans))






        return folicleTrans



if __name__ =="__main__":
    try:
        AddJoint_dialog.close()
        AddJoint_dialog.deleteLater()
    except:
        pass

    AddJoint_dialog = AddJointDialog()
    AddJoint_dialog.show()

