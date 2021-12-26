#-*- coding: utf-8 -*-
import sys, os
import maya.cmds as cmds
import maya.mel as mel
from inspect import getsourcefile
from os.path import abspath
import maya.app.general.resourceBrowser as resourceBrowser

# 기능
#############################################################################
def convertSlash(_path):
    u'''
    파일 경로를 윈도우에서 바로 복사할 경우 \를 /로 이쁘게 바꿔준다
    아니면 경로 앞에 r을 붙여줘라
    '''
    return _path.replace("\\","/")

def clearOutput():
    u'''
    Clear History for Script Editor
    '''
    cmds.scriptEditorInfo(clearHistory=True)

def forPrint(_list):
    u'''
    그냥 리스트를 나열해줍니다
    '''
    for item in _list:
        print item
# 파일 리스트 얻기
def get_dirfiles(_path):
    file_list = []
    for r, d, f in os.walk(_path):
        for file in f:
            #패스가 같을 경우 만( 고로 같은 폴더 녀석들만 골라쥼)
            if r == _path:
                file_list.append(os.path.join(r,file).replace('\\','/'))
    return file_list

def get_dirfiles_sub(_path):
    '''
    sub 폴더 포함
    '''
    file_list = []
    for r, d, f in os.walk(_path):
        for file in f:
            file_list.append(os.path.join(r,file).replace('\\','/'))
    return file_list

# 경로
#############################################################################

def getPathMayaFile():
    u'''
    Maya파일의 절대경로
    '''
    #파일이름 포함 풀경로 얻어오기
    return cmds.file(q=True, sn=True)

def getNameMayaFile():
    u'''
    Maya파일의 이름
    '''
    #파일이름 얻어오기 /로 나눠서 맨끝에서 한칸 읽어오기(unicode)
    return cmds.file(q=True, sn=True).split('/')[-1]

def getPathFindFile(_filename):
    u'''
    MAYA_SCRIPT_PATH안에 파일이 있으면 경로값을, 없으면 None을 반환
    Script안 서브폴더까지는 검색하지 않음
    '''
    # scriptPath = os.environ['MAYA_SCRIPT_PATH'] 환경변수값 가져오는 다른 방식
    scriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH"').split(";")
    if not scriptPaths:
        return None
    for path in scriptPaths:
        testPath = path +'/' + _filename
        if os.path.exists(testPath):
            return testPath
    return None

def get_maya_AppDir():
    '''
    C:/Users/rationalcat/Documents/maya/
    :return:
    '''
    return cmds.internalVar(userAppDir=True)

def getPathDocumentMaya():
    u'''
    * Dos에서도 잘 먹힘
    C:/Users/rationalcat/Documents/maya/
    '''
    if os.environ.get('MAYA_APP_DIR'):
        maya_app_dir = os.environ['MAYA_APP_DIR']
        return maya_app_dir

    if os.environ.get('HOME'):
        home = os.environ['HOME']
    else:
        home = os.environ['USERPROFILE']
        return os.path.realpath(os.path.join(home, 'Documents/maya'))

def getPathDocumentMaya_Add(path):
    u'''
    * Dos에서도 잘 먹힘
    User/Documents/Maya 폴더의 경로를 반환
    '''
    if os.environ.get('MAYA_APP_DIR'):
        maya_app_dir = os.environ['MAYA_APP_DIR']
        if path != '':
            return os.path.join(maya_app_dir, path)
        else:
            return maya_app_dir

    if os.environ.get('HOME'):
        home = os.environ['HOME']
    else:
        home = os.environ['USERPROFILE']
        if path != '':
            return os.path.join(os.path.realpath(os.path.join(home, 'Documents/maya')),path)
        else:
            return os.path.realpath(os.path.join(home, 'Documents/maya'))
        
def getPathMaya2018Script():
    u'''
    maya/2018/Script 경로 반환
    '''
    scriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH"').split(";")
    for path in scriptPaths:
        if path.find('markingMenus') != -1:
            return path.replace('prefs/markingMenus','scripts')

def getPathIMTool():
    u'''
    C:/Users/rationalcat/Documents/maya/scripts/IMTool/utility.py
    abspath(getsourcefile(lambda:0)).replace("\\","/")
    '''
    #scriptPath = scriptPath.replace('/IMUtility/common.py','')
    return abspath(getsourcefile(lambda:0)).replace("\\","/").replace('/IMUtil.py','')

def get_module_dir_path():
    '''
    IMTool 폴더
    :return:
    '''
    return (os.path.dirname(__file__).replace("\\","/"))

# 정보
#############################################################################
def getMayaVersion():
    u'''
    마야의 버전을 반환합니다.
    2018 이런식으로 int 값임
    '''
    return int(cmds.about(v = True).split("-")[0].split(" ")[0])

def get_resource_path():
    resource_browser = resourceBrowser.resourceBrowser()
    resource_path = resource_browser.run()

    return resource_path

