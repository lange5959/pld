# coding=utf8
from pipe_utils.log.logger import initializeLogger, getCoreLogger, newLogger,\
    removeLogger, getLoggingLevel, getLogLineTime, getCachedLogRecords,\
    setLogCacheSize, getLoggerNames, setLoggingLevel


def convert_string(string):
    if string is None:
        return None
    if type(string) == unicode:
        return string
    elif type(string) == str:
        return string.decode('utf-8')
    return unicode(string.toUtf8(), 'utf-8')


from pipe_utils.log.notification_center import NotificationCenter
def get_notification_center():
    return NotificationCenter.getSingletonInstance()
"""
import sys
sys.path.append(r'D:\code')
sys.path.append(r'C:\Python27\Lib\site-packages')
sys.path.append(r'D:\mw\code_test')
# D:\code\pipe_utils\log\__init__.py
import pipe_utils
from pipe_utils.log import error_dialog

tool = error_dialog.ErrorLogDialog(None)
tool.show()

from pipe_utils.log import test_func
reload(test_func)
test_func.func()
"""