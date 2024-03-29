from logging import Handler
from collections import deque


class NotificationLogHandler(Handler):
    def __init__(self):
        # handler is old-style class in older Python versions
        Handler.__init__(self)
        self._maxLen = 100
        self._buf = deque(maxlen=self._maxLen)
    
    def emit(self, record):
        from pipe_utils.log import get_notification_center
        with self.lock:
            self._buf.append(record)
            get_notification_center().emitLogMessage(record)

    def getCachedRecords(self):
        with self.lock:
            return list(self._buf)
        
    def setCacheSize(self, size):
        if self._maxLen != size:
            with self.lock:
                self._buf = deque(self._buf, maxlen=size)
                self._maxLen = size
