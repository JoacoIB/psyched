from __future__ import annotations

import sys
import threading
from io import StringIO
from typing import Callable

from ..utils import SysRedirect
from .task import Task, _status_running, _status_scheduled


class PythonTask(Task):
    def __init__(self, name: str, target: Callable, **kwargs):
        self.target = target
        self.kwargs = kwargs
        self.thread = None
        self.error = []
        self.outfile = StringIO("")
        super(PythonTask, self).__init__(name)

    def run(self):
        assert self.status == _status_scheduled

        def wrapped_function(__target, __error, __outfile, **kwargs):
            sys.stdout.register(self.outfile)
            try:
                __target(**kwargs)
            except Exception as e:
                __error.append(e)
            return

        SysRedirect.install()

        self.thread = threading.Thread(
            target=wrapped_function,
            args=(self.target, self.error, self.outfile),
            kwargs=self.kwargs)
        self.thread.start()
        self.status = _status_running
        return

    def try_to_finish(self) -> bool:
        assert self.status == _status_running
        if not self.thread.is_alive():
            self.thread.join()
            if self.error == []:
                self.succeed()
            else:
                self.fail()
            return True
        else:
            return False

    def wait(self):
        self.thread.join()
        return

    def get_logs(self) -> str:
        return self.outfile.getvalue()
