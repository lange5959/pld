# -*- coding: utf-8 -*-

import os
import sys
import socket
from functools import wraps


def log_exception(func):
    @wraps(func)
    def wrappe(*args, **kwargs):
        import traceback
        try:
            return func(*args, **kwargs)
        except Exception:
            variables = sys.exc_info()[2].tb_next.tb_frame.f_locals
            record_data_dict = {
                'func_name': func.__name__,
                'lineno_': sys.exc_info()[2].tb_next.tb_lineno,
                'msg': traceback.format_exc(),
                'pathname': func.__globals__['__file__'],
                'host': socket.gethostname(),
                'variables': variables,
            }

            # todo: record record_data_dict to db

    return wrappe


