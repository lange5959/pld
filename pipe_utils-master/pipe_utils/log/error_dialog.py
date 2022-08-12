# coding=utf8

import logging, traceback
from StringIO import StringIO
from time import localtime, strftime

from Qt.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QLabel, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QFrame, QPushButton
from Qt.QtGui import QColor
from Qt.QtCore import Qt, QSize

from pipe_utils.log import get_notification_center, convert_string
from pipe_utils.log.utilities import formatException, getPlatform, PLATFORM_MAC
from pipe_utils.log.logger import getCachedLogRecords
from pipe_utils.log.logger import getLoggingLevel


class ErrorLogDialog(QDialog):
    def __init__(self, parent):
        super(ErrorLogDialog, self).__init__(parent, Qt.WindowStaysOnTopHint)
        self._empty = True
        
        self._initUI()
        self.setWindowTitle("Error")
        self.resize(500, 500)

        get_notification_center().connectLogMessage(self._checkLogMessage)
        
        for record in getCachedLogRecords():
            self._checkLogMessage(record)
        
    def sizeHint(self):
        return QSize(400, 200)
        
    def _initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(0)
        
        labelLayout = QHBoxLayout()
        labelLayout.addWidget(QLabel(u"Sorry, something went wrong:", self))
        labelLayout.setContentsMargins(10, 0, 0, 0)
        layout.addLayout(labelLayout)
        layout.addSpacing(5)
        self._errorLog = QTextEdit(self)
        self._errorLog.setReadOnly(True)
        # self._errorLog.setWordWrapMode(QTextOption.NoWrap)
        self._errorLog.setTextColor(QColor(200, 200, 200))
        self._errorLog.setObjectName(u"__ERROR_LOG_")
        
        self._errorLog.setFrameShape(QFrame.StyledPanel)
        if getPlatform() == PLATFORM_MAC:
            self._errorLog.setStyleSheet(
                "QFrame#__ERROR_LOG_{"
                "border-width: 1px; "
                "border-top-style: solid; "
                "border-right-style: none; "
                "border-bottom-style: solid; "
                "border-left-style: none; "
                "border-color:palette(mid)}");
            
        layout.addWidget(self._errorLog)
        
        bottomWidget = QWidget(self)
        bottomLayout = QHBoxLayout(bottomWidget)
        
        self._notAgain = QCheckBox(u"Please, no more error messages!", self)
        bottomLayout.addWidget(self._notAgain, 1, Qt.AlignTop)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        buttonBox.rejected.connect(self.reject)
        mybtn = QPushButton('Test')
        mybtn.clicked.connect(self.test)

        bottomLayout.addWidget(buttonBox)
        bottomLayout.addWidget(mybtn)

        layout.addWidget(bottomWidget)
        
    # @loggingSlot()
    def reject(self):
        self._errorLog.clear()
        self._empty = True
        return QDialog.reject(self)
    
    # @loggingSlot(object)
    def _checkLogMessage(self, record):
        try:
            if self._notAgain.checkState() == Qt.Checked:
                return
            if record.levelno == logging.ERROR:
                # red
                self._errorLog.setTextColor(QColor(200, 0, 0))
            elif record.levelno == logging.WARNING:
                # yellow
                self._errorLog.setTextColor(QColor(200, 200, 0))
            elif record.levelno == logging.INFO:
                # info
                self._errorLog.setTextColor(QColor(200, 200, 200))
            elif record.levelno == logging.CRITICAL:
                # critical
                self._errorLog.setTextColor(QColor(200, 50, 210))

            elif record.levelno == logging.DEBUG:
                # critical

                self._errorLog.setTextColor(QColor(200, 190, 200))

            level_dict = {logging.DEBUG: 'DEBUG',
                          logging.INFO: 'INFO'}
            if record.levelno >= logging.INFO:
                recMsg = record.msg
                if not isinstance(recMsg, basestring):
                    recMsg = unicode(recMsg)
                err = convert_string(recMsg) % record.args
                component = record.name
                if component.startswith("lunchinator."):
                    component = component[12:]

                msg = u"%s - %s - In component %s (%s:%d):\n%s" % (
                    strftime("%H:%M:%S", localtime(record.created)),
                    record.levelname,
                    component,
                    record.pathname,
                    record.lineno,
                    err)
                if record.exc_info:
                    out = StringIO()
                    traceback.print_tb(record.exc_info[2], file=out)
                    msg += u"\nStack trace:\n" + out.getvalue() + formatException(record.exc_info) + u"\n"

                self._errorLog.append(msg)
                self._empty = False
                # if not self.isVisible():
                #     self.showNormal()
                #     self.raise_()
                #     self.activateWindow()
        except:
            from log import getCoreLogger
            getCoreLogger().info(formatException())

    def test(self):
        from test_func import func

        func()


if __name__ == '__main__':
    from Qt.QtWidgets import QApplication
    import sys
    from log import initializeLogger, getCoreLogger

    initializeLogger()
    print('initializeLogger-------------------')
    app = QApplication(sys.argv)
    window = ErrorLogDialog(None)
    window.show()

    # getCoreLogger().error(u"Foo error")
    # getCoreLogger().info(u"Foo info")
    # getCoreLogger().info(u"阿里斯顿加")
    # getCoreLogger().warning(u"Foo info")
    # try:
    #     raise ValueError("foo")
    # except:
    #     getCoreLogger().exception("An exception occurred")
    
    app.exec_()

