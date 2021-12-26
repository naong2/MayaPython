import maya.cmds as cmds



def Wraped_Blendshape_Copy():
    # Init
    bsMesh = 'IMBase_Default'
    cpMesh = 'IMBase_Default'
    BlendshapeList = []


    # GET blendshape
    bsHistory = cmds.listHistory(bsMesh)
    bsNode = cmds.ls(bsHistory, type='blendShape')[0]
    bsNames = cmds.listAttr(bsNode + '.w', m=True)

    # RESET blendshape
    for bs in bsNames:
        if bs == 'Head_Mesh':
            cmds.setAttr(bsNode + '.' + bs, 1)
        else:
            cmds.setAttr(bsNode + '.' + bs, 0)


    # COPY blendshape
    for bs in bsNames:
        if bs == 'Head_Mesh':
            pass
        else:
            cmds.setAttr(bsNode + '.' + bs, 1)
            dup = cmds.duplicate(cpMesh)
            redup = cmds.rename(dup,bs)
            BlendshapeList.append(redup)

            cmds.setAttr(bsNode + '.' + bs, 0)


    cmds.select(BlendshapeList)

def Count_Blendshape():
    bsMesh = 'IMBase_Default'
    # GET blendshape
    bsHistory = cmds.listHistory(bsMesh)
    bsNode = cmds.ls(bsHistory, type='blendShape')[0]
    bsNames = cmds.listAttr(bsNode + '.w', m=True)
    print len(bsNames)


Wraped_Blendshape_Copy()
#Count_Blendshape()