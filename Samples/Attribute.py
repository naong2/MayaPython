import maya.cmds as cmds

def add_custom_attribute(target, list):
    ''' Add Custom Attribute '''
    for attr in list:
        cmds.addAttr(target, longName=attr, attributeType='float', keyable=True)

def delete_custom_attribute(target, list):
    ''' Delete Custom Attribute '''
    for attr in list:
        cmds.deleteAttr(target + '.' + attr)

def connect_attribute(source, attr):
    '''connect some value to attribute'''
    cmds.connectAttr(source, attr)

def disconnect_attribute(source, attr):
    '''disconnect some value to attribute'''
    cmds.disconnectAttr(source, attr)

############################## Test #############################################
attributeList = ["Smile", "Angry"]
target = 'joint1'

# add_custom_attribute(target, attributeList)
# delete_custom_attribute(target, attributeList)

source = 'pCube1.tx'
attr = target + '.Smile'
connect_attribute(source, attr)
# disconnect_attribute(source='pCube1.tx', attr='joint_root.Smile')
