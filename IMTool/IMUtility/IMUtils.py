#-*- coding:utf-8 -*-
import os
import sys
import getpass


def getUser():
    return getpass.getuser().lower()


def reload():
    """
    Python 캐시에서 해당폴더에 있는 모든 모듈을 제거합니다.
    이 기능은 DCC 애플리케이션 내에서 개발하는 데 사용할 수 있지만 프로덕션에서는 사용해서는 안됩니다.

    Example:
        import studiolibrary
        studiolibrary.reload()

        import studiolibrary
        studiolibrary.main()
    """
    '''
    # https://www.daleseo.com/python-os-environ/
    os.environ["IMUTILITY_RELOADED"] = "1"
    from studiolibrary import librarywindow
    librarywindow.LibraryWindow.destroyInstances()
    '''
    # IMUtility안에 있는 모든 파일 목록
    names = modules()
    # 마야 안에서 사용중인 모듈이름들
    for mod in sys.modules.keys():
        for name in names:
            # 사용중인 모듈안에 있고, 시작 이름이 같다면
            if mod in sys.modules and mod.startswith(name):
                # 해당 모듈을 지워라
                del sys.modules[mod]


def modules():
    """
    Get all the module names for the package.

    :rtype: list[str]
    """
    names = []

    dirname = os.path.dirname(os.path.dirname(__file__))
    for filename in os.listdir(dirname):
        names.append(filename)
    return names