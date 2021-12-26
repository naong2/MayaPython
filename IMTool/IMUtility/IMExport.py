# -*- coding: UTF-8 -*-
import os
import maya.cmds as cmds
from IMMaya import *
from IMFile import *

def objExport(self, _path='', _filename='', _separate=True, _zero=True):
    '''
    :param path: 익스포트 경로
    :param filename: 파일 이름, 나눠서 출력하지 않을 경우만 필요
    :param separate: 나눠서 익스포트 할지
    :param zero: 익스포트 직전에 0점에 맞추고 제자리로 돌려놓음
    :return:
    '''

    # 기존 위치로 돌려주기 위해
    translate = []

    # 오브젝트 선택 되어 있는지 체크
    sel = cmds.ls(sl=1)
    if not sel:
        print u'익스포트 실패: 선택한 오브젝트가 없습니다'
        return

    # 경로가 설정 되어 있는지 체크
    if not _path:
        print u'익스포트 경로가 설정되어 있지 않습니다'
        return

    # 각각 나눠서 익스포트 시킬려면
    if _separate:
        cmds.select(clear=1)

        for i in sel:

            # 기존 위치값 저장
            if _zero:
                translate = self.imr.getTranslate(i)
                self.imr.zero(i)

            # 폴더가 없다면 만들기
            self.imf.makefolder(_path)

            # 하나씩 obj 익스포트 시키기
            path_result = os.path.join(_path, i + '.obj')
            cmds.select(i)
            cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                      op="groups=1; ptgroups=0; materials=0; smoothing=1; normals=0")

            # 원래 위치값으로 돌림
            if _zero:
                setTranslate(i, translate)

            print path_result
        print "Finish!!"

    # 하나의 파일로 익스포트 시키기, 이녀석은 0점으로 맞추면 안된다
    else:
        if not _filename:
            print u'파일이름이 없어서 익스포트 시키지 못했습니다.'
            return
        else:
            path_result = os.path.join(_path, _filename + '.obj')
            # 폴더가 없다면 만들기
            makefolder(_path)

            cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                      op="groups=1; ptgroups=0; materials=0; smoothing=1; normals=0")
            print path_result
            print "Finish!!"