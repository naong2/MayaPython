# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import subprocess

def copy2clip(text):
    #txt = '"' + str(text) + '"'
    cmd = 'echo ' + str(text) + '|clip'
    return subprocess.check_call(cmd, shell=True)



sel = cmds.ls(sl=1)
xyz = cmds.getAttr(sel[0] + '.translate')[0]
offset = (0,0,25.567459)
x = str(-(xyz[0])+offset[0])
y = str(-(xyz[1])+offset[2])
z = str(-(xyz[2])+offset[1])

final_text = '(X=' + x + ', Y=' + z + ', Z=' + y +')'
copy2clip(final_text)

#(X=15.606098,Y=92.485023,Z=54.368851)