# -*- coding: UTF-8 -*-
import maya.cmds as cmds
from IMTool.IMUtility import BlendShapeList

def pprint(sel):
    for i in sel:
        print i
print '-------------start-----------------'


curves = BlendShapeList.JBControlRigList
item = []


#블랜드쉐입노드 알아내기
# mesh = cmds.ls(sl=1)
# meshHistory = cmds.listHistory(mesh)
# meshBlendshapeNode = cmds.ls(meshHistory, type='blendShape')
# print meshBlendshapeNode
#cmds.disconnectAttr(meshBlendshapeNode[0]+'.eyeBlinkLeft',f=1)

# ok !!!!!! 연결전에 breakconnection
#cmds.connectAttr('Lip_ctrl_M_UP.translateY','BS_node.mouthShrugUpper')

#for c in curves:
# 중요! 연결정보만 알아내면 됨
# [u'R_squeeze_Ctrl.translateY', u'BS_node_cheekSquintRight']
# 3 [u'Lip_ctrl_M_UP.translateY', u'BS_node_mouthShrugUpper']
# driving_source = cmds.listConnections(curves[3], c=1)
#print driving_source

# [u'BS_node_cheekSquintRight']
#driving_target = cmds.listConnections(curves[0], d=1)

# [u'R_squeeze_CtrlShape']
#futureNodes = [node for node in cmds.listHistory(curves[0], future=1, ac=1)]

# nurbsCurve
#cmds.nodeType(futureNodes[0])

# [u'BS_node_cheekSquintRight.input']
#drivenAttr = cmds.listConnections(curves[0], p=1)


#인텍스 정보알아오기
# for idx, rig in enumerate(BlendShapeList.JBControlRigList):
#     if rig =='M_Roll_Ctrl':
#         print '{} : index {}'.format(rig,idx)

#########################################################
# 1차 연결 정보
#########################################################
# print 'ControlRig List'+'-'*40
# all = cmds.listConnections('M_Roll_Ctrl',c=1,d=1, s=1)
#
# sour = 'sour'
# nextList = []
# for index, node in enumerate(all):
#     if index % 2 == 0:
#         sour = node
#     else:
#         print (sour, node)
#         # 여기서 연결하면 될듯!!
#         # Blendshape이 아니면 다음 검색을 위해 추가한다
#         if cmds.nodeType(node) != 'blendShape':
#             nextList.append(node)
# print '2nd List'+'-'*40
# all = cmds.listConnections(nextList[0],c=1,d=1, s=1)
#
# print nextList[0]
# for index, node in enumerate(all):
#     if index % 2 == 0:
#         sour = node
#     else:
#         print (sour, node)
#         # 여기서 연결하면 될듯!!
#         # Blendshape이 아니면 다음 검색을 위해 추가한다
#         if cmds.nodeType(node) != 'blendShape':
#             nextList.append(node)


######################################################### 추출
# last = cmds.listConnections('BS_node',c=1,d=1, s=1)
#
# nextList = []
# count = 0
# for index, node in enumerate(last):
#     if index % 2 == 0:
#         sour = node
#     else:
#         if cmds.nodeType(node) == 'blendWeighted' or cmds.nodeType(node) == 'animCurveUU':
#             nextList.append([sour, node])
#             count +=1
#
# print 'count: {}'.format(count)
# print nextList

# for info in nextList:
#     sour = 'sour'
#     for index, node in enumerate(info):
#         if index % 2 == 0:
#             sour = node
#         else:
#             #cmds.connectAttr(sour, node)
#             print 'sour: {} -> {}'.format(sour, node)


######################################################### 추출

# nextList = BlendShapeList.JBControlConnectionInfo
#
# for info in nextList:
#     sour = ''
#     for index, node in enumerate(info):
#         if index % 2 == 0:
#             sour = node
#         else:
#             cmds.connectAttr(sour+'.output', node+'.input')
#             print 'Connect: {} -> {}'.format(sour+'.output', node+'.input')



#[u'BS_node_mouthDimpleLeft.output', u'BS_node', u'BS_node_mouthDimpleLeft.input', u'Lip_ctrl_L_End']
# select = cmds.ls(sl=1)[0]
# print cmds.listConnections(select, c=1, d=1,s=1)



# JBControlInfo 미리보기
# for info in BlendShapeList.JBControlConnectionInfo:
#     sour = ''
#     for index, node in enumerate(info):
#         if index % 2 == 0:
#             sour = node
#         else:
#             print 'Connect: {} -> {}'.format(node+'.output', sour)

#안보이는 Controlrig  선택하기
# hiddenList = []
# for info in BlendShapeList.JBControlConnectionInfo:
#     sour = ''
#     for index, node in enumerate(info):
#         if index % 2 == 0:
#             sour = node
#         else:
#             hiddenList.append(node)
#
# print hiddenList

# 익스포트하기위해서 히든오브젝트 선택하기
# cmds.select(BlendShapeList.hiddenControlRig)



#JBControlInfo 연결
# for info in BlendShapeList.JBControlConnectionInfo:
#     sour = ''
#     for index, node in enumerate(info):
#         if index % 2 == 0:
#             sour = node
#         else:
#             print 'Connect: {} -> {}'.format(node+'.output', sour)
#             cmds.connectAttr(node+'.output', sour)
#
#
# print len(BlendShapeList.JBControlConnectionInfo)
print cmds.ls(type='blendShape')







