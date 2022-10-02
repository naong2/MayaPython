from maya import cmds
import subprocess

def showMyWindow():
    winname = "MayaDefaultIconViewer"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.window(winname, w=750, h=400)
    cmds.windowPref(winname, exists=True )
    cmds.showWindow()

    cmds.scrollLayout()
    cmds.columnLayout()
    cmds.gridLayout(numberOfColumns=25, cellWidthHeight=(30, 30))
    #count = 0
    for item in cmds.resourceManager(nameFilter="*png"):
        cmds.iconTextButton(style='iconOnly', image1=item, annotation=item, c='clipboard("%s")' % item)
        #count += 1
        #if count >10:
        #    break


def clipboard(item):
    cmd = 'echo ' + item.strip() + '|clip'
    print (item)
    return subprocess.check_call(cmd, shell=True)


showMyWindow()