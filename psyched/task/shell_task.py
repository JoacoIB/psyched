"""This module exports the ShellTask class to represent a task consisting of the execution of a command in a shell."""
from __future__ import annotations

import subprocess
from io import StringIO
from typing import List

from .task import Task, _STATUS_RUNNING, _STATUS_SCHEDULED


class ShellTask(Task):
    """Task representing a shell command."""

    def __init__(self, name: str, command: List[str]):
        """Class contructor.

        :param name: task name
        :type name: str
        :param command: command to run on shell
        :type command: List[str]
        """
        self.command = command
        self.process = None
        self.outfile = StringIO("")
        super(ShellTask, self).__init__(name)

    def run(self):
        """Run command on a subprocess."""
        assert self.status == _STATUS_SCHEDULED
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        self.status = _STATUS_RUNNING

    def try_to_finish(self) -> bool:
        """Check if the subprocess exited and update the status accordingly.

        :return: whether the task finished
        :rtype: bool
        """
        assert self.status == _STATUS_RUNNING
        exit_code = self.process.poll()
        if exit_code is not None:
            self.wait()
            if exit_code == 0:
                self.succeed()
            else:
                self.fail()
            return True
        else:
            return False

    def wait(self):
        """Block until the task is finished."""
        self.process.wait()

    def get_logs(self) -> str:
        """Get task logs.

        :return: contents of the subprocess stdout and stderr
        :rtype: str
        """
        if self.process is None:
            return ""
        return self.process.stdout.peek(-1).decode('utf-8')

    def __del__(self):
        if self.process is not None:
            self.process.stdout.close()
