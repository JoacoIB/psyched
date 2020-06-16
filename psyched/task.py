from __future__ import annotations

import threading
from typing import Callable, List, Tuple, Union

from .image import Image

_status_waiting = 'waiting'
_status_scheduled = 'scheduled'
_status_running = 'running'
_status_succeeded = 'succeeded'
_status_failed = 'failed'


class Task(object):
    def __init__(self, name: str):
        self.name = name
        self.status = _status_waiting
        self.upstream = []
        self.downstream = []
        return

    def update_status(self, runnable: bool = False) -> Tuple[int, int]:
        if self.status == _status_scheduled:
            if runnable:
                self.run()
                return 1
            else:
                return 0
        elif self.status == _status_running:
            if self.try_to_finish():
                return -1
            else:
                return 0
        return 0

    def try_to_schedule(self) -> bool:
        assert self.status == _status_waiting
        for dep in self.upstream:
            if dep.status != _status_succeeded:
                return False
        self.status = _status_scheduled
        return True

    def run(self):
        raise NotImplementedError

    def try_to_finish(self) -> bool:
        raise NotImplementedError

    def succeed(self):
        self.status = _status_succeeded
        for t in self.downstream:
            t.try_to_schedule()
        return

    def fail(self):
        if self.status == _status_failed:
            return
        self.status = _status_failed
        for t in self.downstream:
            t.fail()
        return

    def set_upstream(self, t: Task):
        if t not in self.upstream:
            self.upstream.append(t)
            t.set_downstream(self)
        return

    def set_downstream(self, t: Task):
        if t not in self.downstream:
            self.downstream.append(t)
            t.set_upstream(self)
        return

    def get_name(self) -> str:
        return self.name

    def get_upstream(self) -> List[Task]:
        return self.upstream

    def get_downstream(self) -> List[Task]:
        return self.downstream

    def is_pending(self) -> bool:
        return self.status not in [_status_succeeded, _status_failed]

    def get_color(self) -> str:
        cmap = {
            _status_waiting: '#dbdbdb',
            _status_scheduled: '#bde4ff',
            _status_running: '#80b7ff',
            _status_succeeded: '#c1ffab',
            _status_failed: '#ffabab'
        }
        return cmap[self.status]

    def __rshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        if isinstance(other, Task):
            self.set_downstream(other)
        elif isinstance(other, list):
            for t in other:
                self >> t
        else:
            raise TypeError("Invalid type for >>")
        return other

    def __lshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        if isinstance(other, Task):
            self.set_upstream(other)
        elif isinstance(other, list):
            for t in other:
                self << t
        else:
            raise TypeError("Invalid type for >>")
        return other

    def __rrshift__(self, other: List[Task]) -> Task:
        self << other
        return self

    def __rlshift__(self, other: List[Task]) -> Task:
        self >> other
        return self

    def __str__(self):
        return f'Task<{self.name}> ({self.status})'


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
        if self.container.status != 'running':
            result = self.container.wait()
            if result['StatusCode'] == 0:
                self.succeed()
            else:
                self.fail()
            return True
        else:
            return False


class PythonTask(Task):
    def __init__(self, name: str, target: Callable, **kwargs):
        self.target = target
        self.kwargs = kwargs
        self.thread = None
        self.error = []
        super(PythonTask, self).__init__(name)

    def run(self):
        assert self.status == _status_scheduled

        def wrapped_function(__target, __error, **kwargs):
            try:
                __target(**kwargs)
            except Exception as e:
                __error.append(e)
            return

        self.thread = threading.Thread(
            target=wrapped_function,
            args=(self.target, self.error),
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
