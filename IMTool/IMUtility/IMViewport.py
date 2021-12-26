# -*- coding: UTF-8 -*-
import os
import maya.cmds as cmds


def saveScreenshot(self, _directory='', _name='', _imagesize = 500, _closeup = 250):

    path = os.path.join(_directory, '%s.jpg' % _name)

    cmds.viewFit()
    cmds.select(clear=1)
    cmds.setAttr('persp1' + '.tz', cmds.getAttr('persp1' + '.tz') - _closeup)

    cmds.setAttr("defaultRenderGlobals.imageFormat", 10)  # This is the value for jpeg

    cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=_imagesize, height=_imagesize,
                   showOrnaments=False, startTime=1, endTime=1, viewer=False)