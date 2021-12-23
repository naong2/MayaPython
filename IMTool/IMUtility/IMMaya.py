# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import maya.mel as mel


def BreakConnection(attrName=''):
    mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\""%attrName)

def AlignObjects(_sel, _startPos=(20, 0, 0), _useStartPosition=True, _maxRows=10, _disX=20, _disY=-38):
    '''
    블렌드쉐입 정렬하는 용으로 제작
    :rtype: object
    :param sel:  정렬하려는 오브젝트들
    :param useStartPosition: 사용안함으로 하면  [20,0,0]에서 시작한다
    :param maxRows: 한줄 최대 개수
    :return:
    '''

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


def getTranslate(_sel):
    '''
    리스트를 집어 넣어도 맨 처음녀석의 값만 반환함
    :param _sel: 단일객체 or 리스트
    :return:
    '''
    # sel 값이 리스트인지 체크
    if not isinstance(_sel, list):
        tx = cmds.getAttr(_sel + '.tx')
        ty = cmds.getAttr(_sel + '.ty')
        tz = cmds.getAttr(_sel + '.tz')
    else:
        # 리스트라면 젤 처음녀석만 반환
        tx = cmds.getAttr(_sel[0] + '.tx')
        ty = cmds.getAttr(_sel[0] + '.ty')
        tz = cmds.getAttr(_sel[0] + '.tz')
    return [tx, ty, tz]


def setTranslate(_sel, _trans):
    '''

    :param _sel: 단일객체 or 리스트
    :param _trans: [x, y, z] 이동시킬 값
    :return: 리스트일 경우 이동시킨 총 갯수를 반환
    '''
    count = 0

    if len(_trans) != 3:
        print _trans, u'총 3개값을 가진 리스트여야 합니다'
        return
    
    # 리스트가 아니면 그냥
    if not isinstance(_sel, list):
        cmds.setAttr(_sel + '.tx', _trans[0])
        cmds.setAttr(_sel + '.ty', _trans[1])
        cmds.setAttr(_sel + '.tz', _trans[2])
        return 'Moved: 1'
    # 리스트일 경우 막 돌려
    else:
        for i in _sel:
            cmds.setAttr(i + '.tx', _trans[0])
            cmds.setAttr(i + '.ty', _trans[1])
            cmds.setAttr(i + '.tz', _trans[2])
            count += 1
        return 'Moved: ' + str(count)


def zeroPosition(_sel):
    if not isinstance(_sel, list):
        cmds.setAttr(_sel + '.tx', 0)
        cmds.setAttr(_sel + '.ty', 0)
        cmds.setAttr(_sel + '.tz', 0)
    else:
        for i in _sel:
            cmds.setAttr(i + '.tx', 0)
            cmds.setAttr(i + '.ty', 0)
            cmds.setAttr(i + '.tz', 0)


def matchTransform():
    select = cmds.ls(sl=1)
    cmds.matchTransform(select[0],select[1])

def bindSkin():
    select = cmds.ls(sl=1)
    cmds.skinCluster(select,  bm=0, sm=0, nw=1, tsb=True)

def unBindSkin():
    selects = cmds.ls(sl=1)
    for select in selects:
        cmds.skinCluster(select, edit=True, unbind=True)

def unlockTransform(*args):
    # unlock
    if not args:
        objects = cmds.ls(sl=1)
    else:
        objects = args

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

def lockTransform():
    # lock
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

def getSelectedObjectSkinnedJoints():
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
def get_blendshapeNames():

    mesh = cmds.ls(sl=True)

    if not mesh:
        print('Select Blendshape Mesh')
        return

    meshHistory = cmds.listHistory(mesh)
    meshBlendshapeNode = cmds.ls(meshHistory,type='blendShape')
    if len(meshBlendshapeNode) == []:
        return
    meshBlendshapeName = cmds.listAttr(meshBlendshapeNode[0]+'.w',m=True)
    return mesh, meshBlendshapeNode, meshBlendshapeName

def reset_blendshape():
    bsMesh, bsNode, bsName = get_blendshapeNames()
    print bsNode[0]
    # all set to 0
    for bs in bsName:
        cmds.setAttr(bsNode[0] +'.'+ bs, 0)
        print (bsNode[0] +'.'+ bs)




def extractBlendshapes():

    targetMeshes = []

    # 헤드메쉬, 노드 List, 이름 List
    bsMesh, bsNode, bsName = get_blendshapeNames()
    distanceX = 30
    distanceY = 140
    count = 0
    # set to 1
    for index, bs in enumerate(bsName):
        print index
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
        targetMeshes.append(renameDup)

    # all set to 0
    for bs in bsName:
        cmds.setAttr(bsNode[0] +'.'+ bs, 0)

    # Align Mesh

    for result in targetMeshes:
        distanceX += 30
        count += 1
        if count > 10:
            distanceY -= 40
            distanceX = 30
            count = 0
        cmds.setAttr(result+'.tx', distanceX)
        cmds.setAttr(result+'.ty', distanceY)

    return targetMeshes