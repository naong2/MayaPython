from maya import cmds
import maya.api.OpenMaya as om
import os

def get_mfn_mesh(mesh):
    list = om.MSelectionList()
    list.add(mesh)
    dag_path = list.getDagPath(0)
    return om.MFnMesh(dag_path)

def create_joints_with_new_position():
    ## setup
    original_mesh = 'head_lod0_mesh'
    new_mesh = "newhead"


    # get list all joint
    cmds.select(clear=True)
    cmds.duplicate('DHIhead:spine_04')
    cmds.select('spine_05', hierarchy=True)
    joint_list = cmds.ls(selection=True)

    # OG_Mesh #############################
    cmds.select(clear=True)

    # mfn_mesh1 = <OpenMaya.MFnMesh object at 0x000001FE8C5ACD90>
    mfn_mesh1 = get_mfn_mesh(original_mesh)
    # New_Mesh ###################################
    mfn_mesh2 = get_mfn_mesh(new_mesh)

    # get all vertex
    all_vertex = mfn_mesh1.getPoints()

    for joint in joint_list:
        # Save Join Position
        joint_pos = cmds.xform(joint, q=1, ws=1, t=1)
        joint_X = joint_pos[0]
        joint_Y = joint_pos[1]
        joint_Z = joint_pos[2]
        joint_point = om.MPoint(joint_pos)

        # Save all vertext distance
        dist_list = []
        for index in range(len(all_vertex)):
            distance = joint_point.distanceTo(mfn_mesh1.getPoint(index, space=om.MSpace.kWorld))
            dist_list.append(distance)

        # Search min vertex position
        min_vertex_index = dist_list.index(min(dist_list))
        min_vertex_pos = mfn_mesh1.getPoint(min_vertex_index, space=om.MSpace.kWorld)
        M1X = min_vertex_pos.x
        M1Y = min_vertex_pos.y
        M1Z = min_vertex_pos.z

        # Get new position
        point2 = mfn_mesh2.getPoint(min_vertex_index, space=om.MSpace.kWorld)
        M2X = point2.x
        M2Y = point2.y
        M2Z = point2.z

        # Calc offset
        offsetX = M2X - (M1X - joint_X)
        offsetY = M2Y - (M1Y - joint_Y)
        offsetZ = M2Z - (M1Z - joint_Z)

        # Move joint to new position
        cmds.move(offsetX, offsetY, offsetZ, joint, absolute=True, worldSpace=True, preserveChildPosition=True)




def move_joints_with_new_position():
    move_joint_list = ['neck_01', 'FACIAL_C_Neck1Root', 'neck_02', 'FACIAL_C_Neck2Root', 'head', 'FACIAL_C_FacialRoot','FACIAL_C_MouthUpper']
    for joint in move_joint_list:
        # # move to new position
        old = 'DHIhead:' + joint
        new = joint
        xform = cmds.xform(new, q=1, ws=1, t=1)
        cmds.move(xform[0], xform[1], xform[2], old, absolute=True, worldSpace=True)



def rl4_node_op():
    riglogic = 'rl4Embedded_SJ02_rl'
    rigBoneLists = []
    rigBones = []
    rigBoneStrippedList = []

    # Get connection info
    for index in range(0,2563):
        '''
        jto_ID:              rl4Embedded_SJ02_rl.jntTranslationOutputs[0]
        rigBoneLists:        DHIhead:FACIAL_C_NeckB.translateX
        rigBones:            DHIhead:FACIAL_C_NeckB.translateX
        rigBoneStrippedList: DHIhead:FACIAL_C_NeckB
        '''
        jto_ID = '%s.jntTranslationOutputs[%s]' % (riglogic, index)
        rigBoneLists.append(cmds.connectionInfo(jto_ID, destinationFromSource=1))
        rigBones.append(rigBoneLists[index][0])
        rigBoneStrippedList.append(rigBones[index][:-11])

    # remove same joint
    # result: 2563 -> 856(joints)
    ndBoneList = []
    for nd in rigBoneStrippedList:
        if nd not in ndBoneList:
            ndBoneList.append(nd)

    offsetLIST = []
    preffix = "DHIhead:"
    for bone in ndBoneList: # DHIhead:FACIAL_C_NeckB
        # getting translate value of Original Bone List with each ID
        TranslateX_OBLI = cmds.getAttr("%s.translateX" % bone)
        TranslateY_OBLI = cmds.getAttr("%s.translateY" % bone)
        TranslateZ_OBLI = cmds.getAttr("%s.translateZ" % bone)

        # getting translate value of Duplicated Bone List with each ID
        TranslateX_DBLI = cmds.getAttr("%s.translateX" % bone[len(preffix):])
        TranslateY_DBLI = cmds.getAttr("%s.translateY" % bone[len(preffix):])
        TranslateZ_DBLI = cmds.getAttr("%s.translateZ" % bone[len(preffix):])

        # calculating different between Duplicated bones and DHI
        ADL_X = TranslateX_DBLI - TranslateX_OBLI
        ADL_Y = TranslateY_DBLI - TranslateY_OBLI
        ADL_Z = TranslateZ_DBLI - TranslateZ_OBLI

        offsetLIST.append(ADL_X)
        offsetLIST.append(ADL_Y)
        offsetLIST.append(ADL_Z)

    del offsetLIST[987]
    del offsetLIST[987]
    del offsetLIST[1951]
    del offsetLIST[1952]
    del offsetLIST[2390]

    for index, trans in enumerate(rigBones): # DHIhead:FACIAL_C_NeckB.translateX
        # Create Add Double Linear Node and connect them
        adlName = 'ADL_%s' % trans
        adlName1 = adlName.replace(":", "")
        adlName2 = adlName1.replace(".", "_")

        # create ADL node
        cmds.createNode('addDoubleLinear', n=adlName2)
        rlno = riglogic + '.jntTranslationOutputs[%s]' % index
        adlNNI = '%s.input1' % adlName2

        # Connect ADL to RL4
        cmds.connectAttr(rlno, adlNNI)
        adlNNO = '%s.output' % adlName2

        # Connect ADL to Joint
        cmds.connectAttr(adlNNO, trans, force=1)

        # Give ADL I2 Values
        adlNNI2 = '%s.input2' % adlName2
        cmds.setAttr(adlNNI2, offsetLIST[index])
    cmds.select(rigBones)


# create_joints_with_new_position()
# move_joints_with_new_position()
rl4_node_op()
cmds.delete('spine_04')
#confirm box
# cmds.confirmDialog( title='Reset Done', message='Proceed now', button=['Yes'], defaultButton='Yes', dismissString='No' )

