import sys


PLATFORM_OTHER = -1
PLATFORM_LINUX = 0
PLATFORM_MAC = 1
PLATFORM_WINDOWS = 2


def formatException(exc_info=None):
    if exc_info is None:
        exc_info = sys.exc_info()
    typeName = u"Unknown Exception"
    if exc_info[0] != None:
        typeName = unicode(exc_info[0].__name__)
    return u"%s: %s" % (typeName, unicode(exc_info[1]))


def getPlatform():
    if "linux" in sys.platform:
        return PLATFORM_LINUX
    elif "darwin" in sys.platform:
        return PLATFORM_MAC
    elif "win32" in sys.platform:
        return PLATFORM_WINDOWS
    else:
        return PLATFORM_OTHER


def convert_string(string):
    if string is None:
        return None
    if type(string) == unicode:
        return string
    elif type(string) == str:
        return string.decode('utf-8')
    return unicode(string.toUtf8(), 'utf-8')



# def get_notification_center():
#     return NotificationCenter.getSingletonInstance()