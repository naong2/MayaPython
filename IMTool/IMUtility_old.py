# -*- coding: UTF-8 -*-
import maya.cmds as cmds
import os

class IMFile():
    def makefolder(self, path):
        '''
        :param path: 파일이름까지 포함시켜도 되고, 폴더경로만 있어도 되고
        :return:
        '''
        # 맨 마지막 단락을 가져와서 .이 있으면 파일
        if '.' in path.split('//')[-1]:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
                print u'폴더를 만들었습니다', os.path.dirname(path)
                return True
            else:
                return False
        # .점 없으면 full 경로라 생각
        else:
            if not os.path.exists(path):
                os.makedirs(path)
                print u'폴더를 만들었습니다', path
                return True
            else:
                return False

class IMViewport():

    def saveScreenshot(self, name, directory=''):
        imagesize = 500
        closeup = 250

        path = os.path.join(directory, '%s.jpg' % name)

        cmds.viewFit()
        cmds.select(clear=1)
        cmds.setAttr('persp1' + '.tz', cmds.getAttr('persp1' + '.tz') - closeup)


        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg

        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=imagesize, height=imagesize,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)

class IMReplace():

    def Align(self, sel, startPos =[20,0,0], useStartPosition=True, maxRows=10, disX=20, disY=-38):
        '''
        블렌드쉐입 정렬하는 용으로 제작
        :param sel:  정렬하려는 오브젝트들
        :param useStartPosition: 사용안함으로 하면  [20,0,0]에서 시작한다
        :param maxRows: 한줄 최대 개수
        :return:
        '''

        if useStartPosition:
            startPostion = startPos
        else:
            startPostion = self.getTranslate(sel[0])

        distanceX = disX
        distanceY = disY
        oneLineMax = maxRows

        CurrentRows = 0
        CurrentColumns = 0

        for i in sel:
            if CurrentRows%oneLineMax == 0:
                CurrentColumns += 1
                CurrentRows = 0
            self.setTranslate(i,[startPostion[0] + (distanceX*CurrentRows), startPostion[1] + (distanceY*CurrentColumns)-distanceY, 0])
            CurrentRows += 1



    def getTranslate(self, sel):
        '''
        리스트를 집어 넣어도 맨 처음녀석의 값만 반환함
        :param sel: 단일객체 or 리스트
        :return:
        '''
        # sel 값이 리스트인지 체크
        if not isinstance(sel, list):
            tx = cmds.getAttr(sel + '.tx')
            ty = cmds.getAttr(sel + '.ty')
            tz = cmds.getAttr(sel + '.tz')
        else:
            # 리스트라면 젤 처음녀석만 반환
            tx = cmds.getAttr(sel[0] + '.tx')
            ty = cmds.getAttr(sel[0] + '.ty')
            tz = cmds.getAttr(sel[0] + '.tz')
        return [tx, ty, tz]

    def setTranslate(self, sel, trans):
        '''

        :param sel: 단일객체 or 리스트
        :param trans: [x, y, z] 이동시킬 값
        :return: 리스트일 경우 이동시킨 총 갯수를 반환
        '''
        count = 0

        if len(trans) != 3:
            print trans, u'총 3개값을 가진 리스트여야 합니다'
            return

        if not isinstance(sel, list):
            cmds.setAttr(sel + '.tx', trans[0])
            cmds.setAttr(sel + '.ty', trans[1])
            cmds.setAttr(sel + '.tz', trans[2])
            return 'Moved: 1'
        else:
            for i in sel:
                cmds.setAttr(i + '.tx', trans[0])
                cmds.setAttr(i + '.ty', trans[1])
                cmds.setAttr(i + '.tz', trans[2])
                count += 1
            return 'Moved: ' + str(count)

    def zero(self, sel):
        if not isinstance(sel, list):
            cmds.setAttr(sel + '.tx', 0)
            cmds.setAttr(sel + '.ty', 0)
            cmds.setAttr(sel + '.tz', 0)
        else:
            for i in sel:
                cmds.setAttr(i + '.tx', 0)
                cmds.setAttr(i + '.ty', 0)
                cmds.setAttr(i + '.tz', 0)

# fbx, obj 익스포트 모음
class IMExport():

    def __init__(self):
        self.imf = IMFile()
        self.imr = IMReplace()

    def objExport(self, path='', filename='', separate=True, zero=True):
        '''
        :param path: 익스포트 경로
        :param filename: 파일 이름, 나눠서 출력하지 않을 경우만 필요
        :param separate: 나눠서 익스포트 할지
        :param zero: 익스포트 직전에 0점에 맞추고 제자리로 돌려놓음
        :return:
        '''

        #기존 위치로 돌려주기 위해
        translate = []


        # 오브젝트 선택 되어 있는지 체크
        sel = cmds.ls(sl=1)
        if not sel:
            print u'익스포트 실패: 선택한 오브젝트가 없습니다'
            return

        # 경로가 설정 되어 있는지 체크
        if not path:
            print u'익스포트 경로가 설정되어 있지 않습니다'
            return

        # 각각 나눠서 익스포트 시킬려면
        if separate:
            cmds.select(clear=1)

            for i in sel:

                # 기존 위치값 저장
                if zero:
                    translate = self.imr.getTranslate(i)
                    self.imr.zero(i)

                #폴더가 없다면 만들기
                self.imf.makefolder(path)

                # 하나씩 obj 익스포트 시키기
                path_result = os.path.join(path, i + '.obj')
                cmds.select(i)
                cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                          op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")

                # 원래 위치값으로 돌림
                if zero:
                    self.imr.setTranslate(i, translate)

                print path_result
            print "Finish!!"

        # 하나의 파일로 익스포트 시키기, 이녀석은 0점으로 맞추면 안된다
        else:
            if not filename:
                print u'파일이름이 없어서 익스포트 시키지 못했습니다.'
                return
            else:
                path_result = os.path.join(path, filename + '.obj')
                # 폴더가 없다면 만들기
                self.imf.makefolder(path)

                cmds.file(path_result, force=1, pr=1, typ="OBJexport", es=1,
                          op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
                print path_result
                print "Finish!!"

