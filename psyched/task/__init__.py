"""This module exports all the Task classes."""
from .docker_task import DockerTask  # noqa
from .python_task import PythonTask  # noqa
from .shell_task import ShellTask  # noqa
from .task import (Task, _STATUS_FAILED, _STATUS_RUNNING, _STATUS_SCHEDULED,  # noqa
                   _STATUS_SUCCEEDED, _STATUS_WAITING)  # noqa
