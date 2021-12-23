import maya.cmds as cmds

infoNode = []
slider = []
JointCount = 4
columRoot = None

def selectSurface(*args):
    global infoNode

    if infoNode != []:
        deleteSlder()
    else:
        pass

    selected = cmds.ls(sl=1)
    # check select
    if selected ==[]:
        print 'Nothing'
        return
    # get shape
    shapes = cmds.listRelatives(selected[0], shapes=True)

    # check nurbsSurface
    if cmds.nodeType(shapes) == 'nurbsSurface':
        UValue=0.0
        count = 0
        count = cmds.intSliderGrp('jointSlider',q=1,v=1)
        for i in range(count):
            cmds.select(d=True)
            getJoint = cmds.joint()
            infoNode.append(cmds.pointOnSurface(selected[0], ch=True, u=UValue, v=0.5))
            cmds.attrFieldSliderGrp('POS_slider'+str(i), h=30,parent=columRoot, min=0, max=1,step=0.1, at='%s.parameterU' % infoNode[i])
            cmds.connectAttr(infoNode[i] + '.px', getJoint + '.tx')
            cmds.connectAttr(infoNode[i] + '.py', getJoint + '.ty')
            cmds.connectAttr(infoNode[i] + '.pz', getJoint + '.tz')
            UValue += (1/float(count-1))


        print infoNode
    else:
        print 'Select a Surface!'


def deleteSlder(*args):
    global infoNode
    for i in range(len(infoNode)):
        cmds.deleteUI('POS_slider'+str(i),control=1)
    infoNode =[]

def setJointCount(slider):
    print cmds.intSliderGrp(slider,q=1,v=1)
    #global JointCount
    #JointCount = cmds.intSliderGrp(slider,q=1,v=1)

def loft(*args):
    cmds.loft('curve1', 'curve2', ch=True, rn=True, ar=True)

def connectJoint(*args):
    print 'connect joint'

def showMyWindow():
    winname = "IMPointOnSurface"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname)
    cmds.showWindow()
    cmds.columnLayout(adj=1)

    global JointCount, columRoot
    # Set Joint Count
    cmds.intSliderGrp('jointSlider',field=True,
                      label='Add Joint Count',
                      minValue=1,
                      maxValue=20,
                      value=JointCount,
                      h=50)


    cmds.button(l='Create PointOnSurface',c=selectSurface, h=50,bgc=[ 0.6, 0,0.6])
    #cmds.button(l='DEL PointOnSurfaceInfo')
    #cmds.button(l='Delete UI',c=deleteButton)
    columRoot = cmds.columnLayout(adj=1)


showMyWindow()