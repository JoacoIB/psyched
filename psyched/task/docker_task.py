from __future__ import annotations

from ..image import Image
from .task import Task, _status_running, _status_scheduled, _status_waiting


class DockerTask(Task):
    def __init__(self, name: str, image: Image, command: str):
        self.image = image
        self.container = None
        self.command = command
        super(DockerTask, self).__init__(name)

    def run(self):
        assert self.status == _status_scheduled
        self.container = self.image.run_command(self.command)
        self.status = _status_running
        return

    def try_to_finish(self) -> bool:
        assert self.status == _status_running
        self.container.reload()
        if self.container.status != 'running':
            result = self.container.wait()
            if result['StatusCode'] == 0:
                self.succeed()
            else:
                self.fail()
            return True
        else:
            return False

    def wait(self):
        self.container.wait()
        return

    def get_logs(self) -> str:
        if self.status in [_status_scheduled, _status_waiting]:
            return ""
        return self.container.logs().decode("utf-8")
