#-*- coding: utf-8 -*-
from maya import cmds
from maya import OpenMayaUI
from maya import OpenMaya
import os

def showMyWindow():
    global shelf_customSet1
    winname = "MyShelfBox"
    if cmds.window(winname, query=True, exists=True):
        cmds.deleteUI(winname)
    cmds.setParent('..')
    window = cmds.window(winname, title="MyShelf",widthHeight=(200,55))

    cmds.shelfTabLayout('mainShelfTab', image='smallTrash.xpm', imageVisible=True)
    shelf_customSet1 = cmds.shelfLayout('Set1')
    loadShelf()
    cmds.setParent('..')

    cmds.showWindow(window)
    return window

def saveShelf(arg=None):
    tempDir = cmds.internalVar(userTmpDir=True)
    cmds.saveShelf(shelf_customSet1, (tempDir +'shelf_custumSet1'))

def loadShelf():
    tempDir = cmds.internalVar(userTmpDir=True)
    buttonfile = (tempDir + 'shelf_custumSet1' + '.mel')
    if not os.path.isfile(buttonfile):
        saveShelf()

    line_list = []
    buttonIndex = []
    with open(buttonfile) as f:
        for line in f:
            line_list.append(line.strip())

    for i in range(len(line_list)):
        if line_list[i] == 'shelfButton':
            buttonIndex.append(i)

    for i in buttonIndex:
        annotation = ''
        image1 = "commandButton.png"
        command = ''
        imageOverlayLabel = ''
        overlayLabelColor = (0.8, 0.8, 0.8)
        overlayLabelBackColor = (0, 0, 0, 0.5)

        for j in line_list[i + 1:]:
            if j in ';':
                cmds.shelfButton(annotation=annotation,image=image1,sourceType="mel",width=35,height=35,
                                 image1=image1, command=command, imageOverlayLabel=imageOverlayLabel,
                                 overlayLabelColor=overlayLabelColor, overlayLabelBackColor=overlayLabelBackColor
                                 )
                break
            if j.split(' ')[0].replace('-', '') == 'annotation':
                annotation = j.replace(j.split(' ')[0], '').replace('\\','').replace('"','').strip()
            if j.split(' ')[0].replace('-', '') == 'image1':
                image1 = j.replace(j.split(' ')[0], '').replace('\\','').replace('"','').strip()

            if j.split(' ')[0].replace('-', '') == 'imageOverlayLabel':
                imageOverlayLabel = j.replace(j.split(' ')[0], '').replace('\\','').replace('"','').strip()

            if j.split(' ')[0].replace('-', '') == 'overlayLabelColor':
                overlayLabelColor = tuple(j.replace(j.split(' ')[0], '').split(' ')[1:])
                overlayLabelColor = (
                float(overlayLabelColor[0]), float(overlayLabelColor[1]), float(overlayLabelColor[2]))
            if j.split(' ')[0].replace('-', '') == 'overlayLabelBackColor':
                overlayLabelBackColor = tuple(j.replace(j.split(' ')[0], '').split(' ')[1:])
                overlayLabelBackColor = (float(overlayLabelBackColor[0]),float(overlayLabelBackColor[1]),float(overlayLabelBackColor[2]),float(overlayLabelBackColor[3]))
            if j.split(' ')[0].replace('-', '') == 'command':
                print j
                command = j[10:-1]
                print 'command -> {}'.format(command)



def uiDeleteCallback( *args ):
    """
    죽을때 실행되는 콜백
    """
    saveShelf()
    print 'Save MyShelf'
    # removes the callback from memory
    OpenMaya.MMessage.removeCallback( uiCallBack )

def main():
    win = showMyWindow()
    uiCallBack = OpenMayaUI.MUiMessage.addUiDeletedCallback(win, uiDeleteCallback)

if __name__ =="__main__":
    main()
