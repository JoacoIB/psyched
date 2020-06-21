"""This module exports the DockerTask class to represent a task consisting of the execution of a command\
in a docker container."""
from __future__ import annotations

from ..image import Image
from .task import Task, _STATUS_RUNNING, _STATUS_SCHEDULED, _STATUS_WAITING


class DockerTask(Task):
    """Task representing a command to be run on a Docker container."""

    def __init__(self, name: str, image: Image, command: str):
        """Class constructor.

        :param name: task name
        :type name: str
        :param image: docker image to run the command
        :type image: Image
        :param command: command to exec on the container.
        :type command: str
        """
        self.image = image
        self.container = None
        self.command = command
        super(DockerTask, self).__init__(name)

    def run(self):
        """Run the command in a new docker container from the given image."""
        assert self.status == _STATUS_SCHEDULED
        self.container = self.image.run_command(self.command)
        self.status = _STATUS_RUNNING

    def try_to_finish(self) -> bool:
        """Check if the container exited and update the status accordingly.

        :return: whether the task finished.
        :rtype: bool
        """
        assert self.status == _STATUS_RUNNING
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
        """Block until the task is finished."""
        self.container.wait()

    def get_logs(self) -> str:
        """Get task logs.

        :return: contents of the container logs
        :rtype: str
        """
        if self.status in [_STATUS_SCHEDULED, _STATUS_WAITING]:
            return ""
        return self.container.logs().decode("utf-8")
