# -*- coding: UTF-8 -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class BlendshapeDialog(QtWidgets.QDialog):
    targetMeshes = []

    def __init__(self, parent=maya_main_window()):
        super(BlendshapeDialog, self).__init__(parent)

        self.setWindowTitle('BlendShape Tools')
        self.setMinimumSize(180, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connection()
        self.setProperty("saveWindowPref", True)

    def create_widgets(self):
        self.reset_btn = QtWidgets.QPushButton("Reset BlendshapeWeight")
        self.ok_btn = QtWidgets.QPushButton("Extract Blendshape")
        self.del_btn = QtWidgets.QPushButton("Delete BlendshapeTarget")
        self.select_btn = QtWidgets.QPushButton("Select BlendshapeTarget")
        self.bindpose_btn = QtWidgets.QPushButton("Reset BindPose to Current")
        self.unlock_btn = QtWidgets.QPushButton("Unlock Transform")
        self.lock_btn = QtWidgets.QPushButton("Lock Transform")
        self.bind_btn = QtWidgets.QPushButton("Bind")
        self.unbind_btn = QtWidgets.QPushButton("UnBind")
        self.match_btn = QtWidgets.QPushButton("Match Transform All")


    def create_layout(self):
        buttonLayout = QtWidgets.QVBoxLayout(self)
        buttonLayout.addWidget(self.reset_btn)
        buttonLayout.addWidget(self.ok_btn)
        buttonLayout.addWidget(self.del_btn)
        buttonLayout.addWidget(self.select_btn)
        buttonLayout.addWidget(self.bindpose_btn)
        buttonLayout.addWidget(self.unlock_btn)
        buttonLayout.addWidget(self.lock_btn)
        buttonLayout.addWidget(self.bind_btn)
        buttonLayout.addWidget(self.unbind_btn)
        buttonLayout.addWidget(self.match_btn)

    ###
    # Connect
    ###
    def create_connection(self):
        self.ok_btn.clicked.connect(self.set_blendshapeWeight)
        self.del_btn.clicked.connect(self.del_target)
        self.reset_btn.clicked.connect(self.reset_blendshape)
        self.select_btn.clicked.connect(self.select_blendshapes)
        self.bindpose_btn.clicked.connect(self.getSelectedObjectSkinnedJoints)
        self.unlock_btn.clicked.connect(self.unlock)
        self.lock_btn.clicked.connect(self.lock)
        self.bind_btn.clicked.connect(self.bind)
        self.unbind_btn.clicked.connect(self.unBind)
        self.match_btn.clicked.connect(self.matchTransform)

    def matchTransform(self):
        select = cmds.ls(sl=1)
        cmds.matchTransform(select[0],select[1])

    def bind(self):
        select = cmds.ls(sl=1)
        cmds.skinCluster(select,  bm=0, sm=0, nw=1, tsb=True)

    def unBind(self):
        selects = cmds.ls(sl=1)
        for select in selects:
            cmds.skinCluster(select, edit=True, unbind=True)

    def unlock(self):
        # unlock
        objects = cmds.ls(sl=1)
        trans = ['t','r','s']
        axis = ['x','y','z']

        for obj in objects:
            for t in trans:
                for a in axis:
                    cmds.setAttr(obj +'.'+ t + a, lock=False)
            # t, r, s 한번 더 unlock
            cmds.setAttr(obj + '.t' , lock=False)
            cmds.setAttr(obj + '.r' , lock=False)
            cmds.setAttr(obj + '.s', lock=False)

    def lock(self):
        # unlock
        objects = cmds.ls(sl=1)
        trans = ['t','r','s']
        axis = ['x','y','z']

        for obj in objects:
            for t in trans:
                for a in axis:
                    cmds.setAttr(obj +'.'+ t + a, lock=True)
            # t, r, s 한번 더 unlock
            cmds.setAttr(obj + '.t' , lock=True)
            cmds.setAttr(obj + '.r' , lock=True)
            cmds.setAttr(obj + '.s', lock=True)

    def getSelectedObjectSkinnedJoints(self):
        #
        # 현재 잡고 있는 오브젝트 BindPose 업데이트
        #
        objects = cmds.ls(sl=True)
        cmds.select(cl=True)
        for obj in objects:
            skinClusterStr = 'findRelatedSkinCluster("' + obj + '")'
            skinCluster = mel.eval(skinClusterStr)
            if (skinCluster is not None):
                jnt = cmds.skinCluster(skinCluster, query=True, inf=True)[0]
                cmds.select(jnt, add=True)
                bindpose = cmds.listConnections(skinCluster, d=False, type='dagPose')[0]
                print "===================================="
                print "SkinCluster: " + skinCluster
                print "Joint: " + jnt
                print "BindPose: " + bindpose
                print "===================================="
                cmds.dagPose(jnt, reset=True, n=bindpose)
                #cmds.delete(bindpose)
                #cmds.dagPose(jnt, reset=True, n=bindpose, save=True)

            else:
                print("-----> no skin on " + obj + "!")



    # 블랜드쉐입 리스트 가져오기
    def get_blendshapeNames(self):
        mesh = cmds.ls(sl=True)
        if not mesh:
            print('Select Blendshape Mesh')
            return

        meshHistory = cmds.listHistory(mesh)
        meshBlendshapeNode = cmds.ls(meshHistory,type='blendShape')
        meshBlendshapeName = cmds.listAttr(meshBlendshapeNode[0]+'.w',m=True)
        return mesh, meshBlendshapeNode, meshBlendshapeName

    def reset_blendshape(self):
        bsMesh, bsNode, bsName = self.get_blendshapeNames()
        print bsNode[0]
        # all set to 0
        for bs in bsName:
            cmds.setAttr(bsNode[0] +'.'+ bs, 0)
            print (bsNode[0] +'.'+ bs)

    def del_target(self):
        cmds.delete(self.targetMeshes)
        print 'Delete Target OK!'

    def set_blendshapeWeight(self):
        # 헤드메쉬, 노드 List, 이름 List
        bsMesh, bsNode, bsName = self.get_blendshapeNames()
        distanceX = 30
        distanceY = 140
        count = 0
        # set to 1
        for bs in bsName:
            #cnt = cmds.listConnections(bsNode[0] +'.'+ bs, p=1)[0]
            #print cnt
            #if cnt != None:
            #    cmds.disconnectAttr(cnt, bsNode[0] +'.'+ bs)
            cmds.setAttr(bsNode[0] +'.'+ bs, 1)
            # 복사
            dup = cmds.duplicate(bsMesh)
            cmds.setAttr(bsNode[0] +'.'+ bs, 0)
            # unlock
            trans = ['t','r','s']
            axis = ['x','y','z']
            for t in trans:
                for a in axis:
                    cmds.setAttr(dup[0] +'.'+ t + a, lock=False)
                # t, r, s 한번 더 unlock
                cmds.setAttr(dup[0] + '.' + t , lock=False)
            # rename to blendshapeName

            renameDup = cmds.rename(dup, bs)
            self.targetMeshes.append(renameDup)

        # all set to 0
        for bs in bsName:
            cmds.setAttr(bsNode[0] +'.'+ bs, 0)

        # Align Mesh

        for result in self.targetMeshes:
            distanceX += 30
            count += 1
            if count > 10:
                distanceY -= 40
                distanceX = 30
                count = 0
            cmds.setAttr(result+'.tx', distanceX)
            cmds.setAttr(result+'.ty', distanceY)




def main():

    try:
        template_dialog2.close()
        template_dialog2.deleteLater()
    except:
        pass

    template_dialog2 = BlendshapeDialog()
    template_dialog2.show()

if __name__ =="__main__":
    main()