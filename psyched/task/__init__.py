"""This module exports all the Task classes."""
from .docker_task import DockerTask
from .python_task import PythonTask
from .shell_task import ShellTask
from .task import (_STATUS_FAILED, _STATUS_RUNNING, _STATUS_SCHEDULED,
                   _STATUS_SUCCEEDED, _STATUS_WAITING, Task)

__all__ = [
    'DockerTask',
    'PythonTask',
    'ShellTask',
    'Task',
    '_STATUS_FAILED',
    '_STATUS_RUNNING',
    '_STATUS_SCHEDULED',
    '_STATUS_SUCCEEDED',
    '_STATUS_WAITING'
]
