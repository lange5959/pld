# -*- coding: utf-8 -*-
# Time    : 2021/10/18 15:18
# Author  : MengWei

from Qt.QtWidgets import QApplication
import logging
import sys
from pipe_utils.log import initializeLogger, getCoreLogger, setLoggingLevel
initializeLogger()
# setLoggingLevel('NAME', 'logging.INFO')
# setLoggingLevel('NAME', 'logging.DEBUG')

def func():
    # getCoreLogger().debug(u"func debug")
    getCoreLogger().info(u"------func info--------")
    # getCoreLogger().info(u"阿里斯顿加")
    # getCoreLogger().warning(u"Foo warning")
    # getCoreLogger().error(u"Foo error")
    # print 123
    # try:
    #     print 1/0
    #     # raise ValueError(":::::foo")
    # except:
    #     getCoreLogger().exception("::::::::文件不规范！！")