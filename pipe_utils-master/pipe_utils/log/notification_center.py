import threading, Queue

from pipe_utils.log import getCoreLogger


class EventSignalLoop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.reqs = Queue.Queue()
        
    def run(self):
        while True:
            req, args, kwargs = self.reqs.get()
            getCoreLogger().debug("processing Signal: %s", req)
            if req == 'exit': 
                break
            try:
                req(*args, **kwargs)
            except Exception, e:
                getCoreLogger().exception("Error in Signal handling; executed method: %s; Error: %s", str(req), str(e))
            except:
                getCoreLogger().exception("Error in Signal handling; executed method:  %s; no additional info", str(req))
    
    def append(self, func, *args, **kwargs):
        self.reqs.put((func, args, kwargs))
    
    def finish(self):
        self.reqs.put(("exit", None, None))


def _connectFunc(func):
    signal = func.__name__[7:]
    def newFunc(self, callback):
        func(self, callback)
        self._addCallback(signal, callback)
    return newFunc
        
# def _disconnectFunc(func):
#     signal = func.__name__[10:]
#     def newFunc(self, callback):
#         func(self, callback)
#         self._removeCallback(signal, callback)
#     return newFunc


def _emitFunc(func):
    signal = func.__name__[4:]
    def newFunc(self, *args, **kwargs):
        #func(self, *args, **kwargs) TODO why would we do this?
        self._emit(signal, *args, **kwargs)
    return newFunc


class NotificationCenter(object):
    """Central class for notification passing within Lunchinator."""
    _instance = None
    
    @classmethod
    def getSingletonInstance(cls):
        """Returns the singleton NotificationCenter instance.
        
        Don't call this method directly. Use
        lunchinator.get_notification_center() instead.
        """
        if cls._instance == None:
            # fallback if it was not set from outside, no event loop in this case
            cls._instance = NotificationCenter(loop=False)
        return cls._instance
    
    @classmethod
    def setSingletonInstance(cls, instance):
        """Set the singleton instance.
        
        This is being taken care of in the lunch server controller.
        """
        cls._instance = instance
        
    def __init__(self, loop=True):
        self._callbacks = {}
        if loop:
            self.eventloop = EventSignalLoop()
            self.eventloop.start()
        else:
            self.eventloop = None
        
    def finish(self):
        self.eventloop.finish()
        
    def _addCallback(self, signal, callback):
        if signal in self._callbacks:
            callbacks = self._callbacks[signal]
        else:
            callbacks = []
        callbacks.append(callback)
        self._callbacks[signal] = callbacks
        
    def _removeCallback(self, signal, callback):
        if not signal in self._callbacks:
            return
        callbacks = self._callbacks[signal]
        if callback in callbacks:
            callbacks.remove(callback)
    
    def _emit(self, signal, *args, **kwargs):
        if not signal in self._callbacks:
            return
        if self.eventloop != None:
            for callback in self._callbacks[signal]:
                self.eventloop.append(callback, *args, **kwargs)
        else:
            # no event loop, call directly
            for callback in self._callbacks[signal]:
                callback(*args, **kwargs)

    @_connectFunc
    def connectLogMessage(self, callback):
        pass

    @_emitFunc
    def emitLoggerAdded(self, loggerName):
        pass

    @_emitFunc
    def emitLoggingLevelChanged(self, loggerName, newLevel):
        pass

    @_emitFunc
    def emitLogMessage(self, logRecord):
        pass

    # @_emitFunc
    # def emitLoggingLevelChanged(self, loggerName, newLevel):
    #     pass
    
if __name__ == '__main__':
    def _testCallback(a, b, c):
        print a, b, c
    
    print "foo"
    nc = NotificationCenter()
    nc.connectMessagePrepended(_testCallback)
    nc.emitMessagePrepended("a", "b", [{"foo":4}])
