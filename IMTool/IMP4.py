#-*- coding:utf-8 -*-

import os, sys
# initialize 
###################################################
# Perforce
if not os.getenv('P4CONFIG'):
    os.environ['P4CONFIG'] = '.p4config'
try:
    from P4 import P4, P4Exception
except ImportError as e:
    raise ImportError('%s, ensure P4API is installed into your DCC script paths' % e)

# Evil global
p4 = P4()

def get_p4():
    return p4


def read_Info(value=''):
    if not p4.connected():
        p4.connect()
        try:
            info = p4.run_info()
            return info[0][value]
        except:
            print 'Error'

def connect():
    if not p4.connected():
        p4.connect()

    try:
        if read_Info('clientName')=='*unknown*':
            e = u'Error: 클라이언트 이름을 알수 없습니다.'
            raise e
        # p4 cwd 설정 : D:\Perforce
        p4.cwd = read_Info('clientRoot')

    except:
        print u'무언가 접속시 에러가... 뭐지?'

# 접속해서 cwd 설정

print u'IMTool init 스타트!'


# SetupConnection
########################################################
def connect():
    if not p4.connected():
        #p4.cwd = os.environ['MAYA_APP_DIR']
        print p4.cwd
        p4.connect()


# Func 
###################################################
def p4run(_key):
    try:
        p4.connect()
        info = p4.run("info")
        for key in info[0]:
            if key == _key:
                return info[0][key].replace('\\','/')
        p4.disconnect()
    except P4Exception:
        for e in p4.errors:
            print e

def get_serverAddress():
    return p4run('serverAddress')

def get_userName():
    return p4run('userName')

def get_clientRoot():
    return p4run('clientRoot')

def get_clientName():
    return p4run('clientName')

def get_checkoutFiles():
    return p4.run_fstat(file)

def get_fetch_change():
    try:
        connect()
        files = p4.run_opened("-u", p4.user, "-C", p4.client, "...")
        entries = []
        for file in files:
            filePath = file['clientFile']
            entry = {'File': filePath,
                         'Folder': os.path.split(filePath)[0],
                         'Type': file['type'],
                         'Pending_Action': file['action'],
                         }
            entries.append(entry)

            return entries
        p4.disconnect()
    except:
        pass

def read_fetchClient(value=''):
    try:
        p4.connect()
        root = p4.fetch_client()
        #pp.pprint(root)
        return root[value]
    except :
        print 'Error'
    p4.disconnect()

def read_Info(value=''):
    if not p4.connected():
        p4.connect()
        try:
            info = p4.run_info()
            #pp.pprint(info)
            return info[0][value]
        except:
            print 'Error'


# 폴더 열기
def open_file(_folderName):
    if sys.platform == "win32":
        os.startfile(_folderName)

# 테스트 실행
##########################################

#_file = 'D:\Perforce\depot\master\Art\Source'.replace('\\','/')
#open_file(_file)


