from __future__ import annotations

import subprocess
from io import StringIO
from typing import List

from .task import Task, _status_running, _status_scheduled


class ShellTask(Task):
    def __init__(self, name: str, command: List[str]):
        self.command = command
        self.process = None
        self.outfile = StringIO("")
        super(ShellTask, self).__init__(name)

    def run(self):
        assert self.status == _status_scheduled
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        self.status = _status_running
        return

    def try_to_finish(self) -> bool:
        assert self.status == _status_running
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
        self.process.wait()
        return

    def get_logs(self) -> str:
        if self.process is None:
            return ""
        return self.process.stdout.peek(-1).decode('utf-8')

    def __del__(self):
        if self.process is not None:
            self.process.stdout.close()
