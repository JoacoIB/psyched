"""This module exports the PythonTask class to represent a task consisting of the execution of a Python function."""
from __future__ import annotations

import sys
import threading
from io import StringIO
from typing import Callable

from ..utils import SysRedirect
from .task import Task, _STATUS_RUNNING, _STATUS_SCHEDULED


class PythonTask(Task):
    """Task representing a python function."""

    def __init__(self, name: str, target: Callable, **kwargs):
        """Class constructor.

        kwargs are passed directly to the target.

        :param name: task name
        :type name: str
        :param target: callable object to call on task run
        :type target: Callable
        """
        self.target = target
        self.kwargs = kwargs
        self.thread = None
        self.error = []
        self.outfile = StringIO("")
        super(PythonTask, self).__init__(name)

    def run(self):
        """Run the target in a new thread."""
        assert self.status == _STATUS_SCHEDULED

        def wrapped_function(__target, __error, __outfile, **kwargs):
            sys.stdout.register(self.outfile)
            try:
                __target(**kwargs)
            except Exception as ex:
                __error.append(ex)

        SysRedirect.install()

        self.thread = threading.Thread(
            target=wrapped_function,
            args=(self.target, self.error, self.outfile),
            kwargs=self.kwargs)
        self.thread.start()
        self.status = _STATUS_RUNNING

    def try_to_finish(self) -> bool:
        """Check if the associated thread is still alive and update the status accordingly.

        :return: whether the task finished
        :rtype: bool
        """
        assert self.status == _STATUS_RUNNING
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
        """Block until the task is finished."""
        self.thread.join()

    def get_logs(self) -> str:
        """Get task logs.

        :return: contents of the thread stdout
        :rtype: str
        """
        return self.outfile.getvalue()
