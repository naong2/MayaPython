import sys
import logging
from maya import cmds

logger = logging.getLogger(__name__)
logger.info('hello')

MayaPythonScripts = r'D:\Github\MayaPython'
if MayaPythonScripts not in sys.path:
    sys.path.append(MayaPythonScripts)

