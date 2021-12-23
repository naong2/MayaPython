#-*- coding:utf-8 -*-
import os
import tempfile
import maya.cmds as cmds
import maya.mel as mel
from inspect import getsourcefile
from os.path import abspath
import maya.app.general.resourceBrowser as resourceBrowser

def makefolder(path):
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

def path_Cleanup(path):
    """
    :type path: str
    :rtype: unicode
    """
    # 처음에 시작하는게 혹시 // 이런거라면 True
    unc = path.startswith("//") or path.startswith("\\\\")
    path = path.replace("//", "/")
    path = path.replace("\\", "/")

    # 경로 끝이 /로 끝나는애라면
    if path.endswith("/") and not path.endswith(":/"):
        #끝에 / 지워준다
        path = path.rstrip("/")

    # //로 시작하는 경로가 있고, 시작이 //가 아니고, /로 시작하는 애라면
    if unc and not path.startswith("//") and path.startswith("/"):
        # /를 //로 만들어준다
        path = "/" + path

    return path


def paths_Cleanup(paths):
    """
    리스트로 여려개 들어있는 주소들을 깔끔히 정리해준다
    """
    return [path_Cleanup(path) for path in paths]

def path_Split(path):
    """
    경로, 파일이름, 확장자
    """
    path = path_Cleanup(path)
    filename, extension = os.path.splitext(path)
    return os.path.dirname(filename), os.path.basename(filename), extension

def getPath_scriptRoot():
    '''
    IMUtility 폴더가 들어있는 상위 폴더 경로를 알려준다
    :return:
    '''
    return path_Cleanup(os.path.dirname(os.path.dirname(__file__)))

def getPath_Appdata():
    '''
    C:\Users\naong\AppData\Roaming
    :return:
    '''
    return path_Cleanup(os.getenv('APPDATA'))

def getPath_HOME():
    '''
    C:/Users/naong/Documents
    :return:
    '''
    return path_Cleanup(os.getenv('HOME'))

def getPath_temp():
    '''
    c:\users\naong\appdata\local\temp
    :return:
    '''
    return path_Cleanup(tempfile.gettempdir())


def getPath_MayaFile():
    u'''
    Maya파일의 절대경로
    '''
    # 파일이름 포함 풀경로 얻어오기
    return cmds.file(q=True, sn=True)


def getName_MayaFile():
    u'''
    Maya파일의 이름
    '''
    # 파일이름 얻어오기 /로 나눠서 맨끝에서 한칸 읽어오기(unicode)
    return cmds.file(q=True, sn=True).split('/')[-1]


def getPath_FindFile(_filename):
    u'''
    MAYA_SCRIPT_PATH안에 파일이 있으면 경로값을, 없으면 None을 반환
    Script안 서브폴더까지는 검색하지 않음
    '''
    # scriptPath = os.environ['MAYA_SCRIPT_PATH'] 환경변수값 가져오는 다른 방식
    scriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH"').split(";")
    if not scriptPaths:
        return None
    for path in scriptPaths:
        testPath = path + '/' + _filename
        if os.path.exists(testPath):
            return testPath
    return None


def get_maya_AppDir():
    '''
    C:/Users/rationalcat/Documents/maya/
    :return:
    '''
    return cmds.internalVar(userAppDir=True)


def getPath_DocumentMaya():
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


def getPath_DocumentMaya_Add(path):
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
            return os.path.join(os.path.realpath(os.path.join(home, 'Documents/maya')), path)
        else:
            return os.path.realpath(os.path.join(home, 'Documents/maya'))


def getPath_Maya2018Script():
    u'''
    maya/2018/Script 경로 반환
    '''
    scriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH"').split(";")
    for path in scriptPaths:
        if path.find('markingMenus') != -1:
            return path.replace('prefs/markingMenus', 'scripts')


def getPath_IMTool():
    u'''
    C:/Users/rationalcat/Documents/maya/scripts/IMTool/utility.py
    abspath(getsourcefile(lambda:0)).replace("\\","/")
    '''
    # scriptPath = scriptPath.replace('/IMUtility/common.py','')
    return abspath(getsourcefile(lambda: 0)).replace("\\", "/").replace('/IMUtil.py', '')


def getPath_module_dir_path():
    '''
    IMTool 폴더
    :return:
    '''
    return (os.path.dirname(__file__).replace("\\", "/"))


# 정보
#############################################################################
def getMayaVersion():
    u'''
    마야의 버전을 반환합니다.
    2018 이런식으로 int 값임
    '''
    return int(cmds.about(v=True).split("-")[0].split(" ")[0])

def getPath_resource():
    resource_browser = resourceBrowser.resourceBrowser()
    resource_path = resource_browser.run()

    return resource_path