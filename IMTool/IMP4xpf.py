#-*- coding: utf-8 -*-

from P4 import P4, P4Exception
import xpf
import IMTool.IMP4 as imp4
import IMTool.IMUtil as imu

'''

[사용 예시]
* 파일 추가 - 디폴트
add_changelist_default(testFiles)
* 파일 추가 - Description
add_changelist_descript(testFiles,'설명문구')
* 파일 추가 - Changelist No.
add_changelist_changeId(testFiles,3801)

* 리버트
revert_files(files)

* 서밋하기 (무조건 같은 체인지리스트안에 있어야 올라감)
submit_files(files,'설명문구')

'''

#--------------------xpf 초기화 ------------------------------
p4 = imp4.get_p4()

xpf.variables.set_host(p4.host)
xpf.variables.set_port(p4.port)
xpf.variables.set_user(p4.user)
xpf.variables.set_client(p4.client)

try:
    p4.connect()
    p4.cwd = p4.run('info')[0]['clientRoot']
    # 전역으로 쓸녀석
    _cwd = p4.run('info')[0]['clientRoot']
    p4.disconnect()
except:
    print u'cwd 설정 Error'
#--------------------xpf 초기화 ------------------------------

def get_host():
    return xpf.variables.get_host()
def get_port():
    return xpf.variables.get_port()
def get_user():
    return xpf.variables.get_user()
def get_client():
    return xpf.variables.get_client()
def get_clientRoot():
    return p4.cwd

def get_sync(_filePath):
    xpf.direct.sync(
        [
            _filePath
        ]
    )

def run_login():
    try:
        p4.run_login()
    except:
        print"what!!"

#쌩으로 값 읽기
def read_Info(value=''):
    '''

    :param value:
    :return:
    '''
    if not p4.connected():
        p4.connect()
        try:
            info = p4.run_info()
            return info[0][value]
        except:
            print 'Error'


# 설명을 이쁘게 달기위해 / 한글지원 / 아뒤를 작업명으로 변경해줌
def make_Description(_description=''):
    return _description.encode('cp949')

# 파일 넣으면 체크리스트번호 알려줌 (새로 생성 안함)
def get_changeId_file(_filePath):
    return xpf.assist.changelist(_filePath)

# 파일 체크아웃하면서 리스트를 바꿔준다
def add_changelist_descript(_files, _description='default'):
    u'''
    파일, 설명
    설명을 찾아서 등록함
    '''
    print u'설명문구를 매칭해서 파일등록'
    return xpf.assist.add_to_changelist(_files, _description.encode('cp949'))

def add_changelist_changeId(_files, change_id=None):
    u'''
    파일, 체인지리스트id
    체인지리스트 번호를 찾아서 등록함
    '''
    print u'체인지ID로 파일등록'
    return xpf.assist.add_to_changelist(_files, change_id=change_id)

def add_changelist_default(_files):
    u'''
    파일
    디폴트 체인지리스트에 등록함
    '''
    print u'디폴트 체인지리스트에 파일등록'
    return xpf.assist.add_to_changelist(_files, change_id='default')

# 파일 리버트/ 당분간 forceAll은 안쓰는걸로
def revert_files(_files, _forceAll=False):
    '''
    파일이 여러개일경우 forceAll이 false면 맨 첫번째 파일의 changelist와 같은 녀석들만 리버트 됩니다.
    :param _files:
    :param _forceAll: True일 경우 하나씩 changelist를 얻어와서 리버트 시킵니다.
    :return:
    '''
    if not isinstance(_files, (list, tuple)):
        try:
            _changeId = xpf.direct.fstat(_files)[0]['change']
        except:
            print u''
    else:
        if not _forceAll:
            _changeId = xpf.direct.fstat(_files[0])[0]['change']
            current_changes = xpf.direct.revert(
                '-c',
                _changeId,
                xpf.variables.get_client(),
                _files
                )
            return current_changes
        else:
            #다중 파일 개별로 리버트 시키기
            for file in _files:
                _changeId = xpf.direct.fstat(file)[0]['change']
                current_changes = xpf.direct.revert(
                    '-c',
                    _changeId,
                    xpf.variables.get_client(),
                    _files
                )
    print u'리버트 완료'

def submit_files_desc(files, description=None):
    """
    이것은 주어진 파일을 주어진 설명과 함께 변경 목록 아래에 제출합니다.
    모든 파일이 올바른 설명과 함께 동일한 변경 목록에 이미있는 경우 직접 제출이 수행됩니다.

    주어진 설명과 함께 변경 목록이 없으면 새로운 변경 목록이 생성됩니다.
    지정된 파일이 현재 여러 변경 목록에 분산되어 있거나 예상 변경과
    다른 변경 목록에있는 경우 제출을 수행하기 전에 제출 변경 목록으로 이동됩니다.

    :param files: Optional list of files to sync to, or a single filepath
    :type files: list(str, str, ...) or str

    :param description: 존재하지 않는 경우 변경 목록에 지정하기위한 설명입니다.
    :type description: str

    :return: submission changelist number
    """
    if not isinstance(files, (list, tuple)):
        files = [files]

    # -- 모든 파일이 동일한 변경 목록에있는 경우 제출하십시오.
    # 첫번째 파일의 ChangeList 숫자를 가져온다
    cl_number = xpf.assist.changelist(files[0])

    # -- 변경 목록에서 전체 파일 목록 가져 오기
    cl_description = xpf.direct.describe(cl_number)[-1]

    local_files = []
    for df in cl_description:
        if "depotFile" in df:
            tempPath = xpf.direct.where(cl_description[df])[0]['path']
            local_files.append(tempPath)

    all_files_in_cl = True

    for local_file in local_files:
        if local_file not in files:
            all_files_in_cl = False
            break
    # 파일안에 파일들이
    if not all_files_in_cl:
        xpf.assist.add_to_changelist(
            files,
            description=make_Description(description),
        )

    return xpf.direct.submit(
        '-c',
        cl_number,
    )

def submit_files_autoCL(files):
    """
    이것은 주어진 파일을 주어진 설명과 함께 변경 목록 아래에 제출합니다.
    모든 파일이 올바른 설명과 함께 동일한 변경 목록에 이미있는 경우 직접 제출이 수행됩니다.

    주어진 설명과 함께 변경 목록이 없으면 새로운 변경 목록이 생성됩니다.
    지정된 파일이 현재 여러 변경 목록에 분산되어 있거나 예상 변경과
    다른 변경 목록에있는 경우 제출을 수행하기 전에 제출 변경 목록으로 이동됩니다.

    :param files: Optional list of files to sync to, or a single filepath
    :type files: list(str, str, ...) or str

    :param description: 존재하지 않는 경우 변경 목록에 지정하기위한 설명입니다.
    :type description: str

    :return: submission changelist number
    """
    if not isinstance(files, (list, tuple)):
        files = [files]

    # -- 모든 파일이 동일한 변경 목록에있는 경우 제출하십시오.
    # 첫번째 파일의 ChangeList 숫자를 가져온다
    cl_number = xpf.assist.changelist(files[0])

    # -- 변경 목록에서 전체 파일 목록 가져 오기
    cl_description = xpf.direct.describe(cl_number)[-1]

    local_files = []
    for df in cl_description:
        if "depotFile" in df:
            tempPath = xpf.direct.where(cl_description[df])[0]['path']
            local_files.append(tempPath)

    all_files_in_cl = True

    for local_file in local_files:
        if local_file not in files:
            all_files_in_cl = False
            break
    # 파일안에 파일들이

    return xpf.direct.submit(
        '-c',
        cl_number,
    )

#------------------------------------------------------------
import pprint
pp = pprint.PrettyPrinter()

# / 로 바꿔줘야 먹히넹?
myfile = r'D:\Perforce\depot\master\Art\Source\Character\skeletalMesh2.txt'.replace('\\','/')
myfiles =[
    'D:/Perforce/depot/master/Art/Source/Animation.fbx',
    'D:/Perforce/depot/master/Art/Source/Character/skeletalMesh.txt',
    'D:/Perforce/depot/master/Art/Source/Character/skeletalMesh3.txt',
    'D:/Perforce/depot/master/IM/Content/Developers/rationalcat/Blutility/renameTest.uasset'
]
#add_changelist_changeId(myfile, 3801)
#add_changelist_descript(myfiles, '[TA] 테스트01')
#revert_files(myfiles)
#xpf.direct.fstat('D:/Perforce/depot/master/Art/Source/한글폴더/Animation.fbx')
#pp.pprint(xpf.direct.fstat(myfiles))

# 이건 되넹
#submit_files_autoCL(myfiles)
