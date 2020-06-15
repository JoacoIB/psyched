from __future__ import annotations

from typing import List, Tuple, Union

from .image import Image

_status_waiting = 'waiting'
_status_scheduled = 'scheduled'
_status_running = 'running'
_status_succeeded = 'succeeded'
_status_failed = 'failed'


class Task(object):
    def __init__(self, name: str, image: Image, command: str):
        self.name = name
        self.image = image
        self.command = command
        self.container = None
        self.status = _status_waiting
        self.upstream = []
        self.downstream = []
        return

    def update_status(self, runnable: bool = False) -> Tuple[int, int]:
        if self.status == _status_waiting:
            if self.schedule():
                if self.status == _status_failed:
                    return (0, -1)
                else:
                    return (0, 0)
            else:
                return (0, 0)
        elif self.status == _status_scheduled:
            if runnable:
                self.run()
                return (1, 0)
            else:
                return (0, 0)
        elif self.status == _status_running:
            if self.finish():
                return (-1, -1)
            else:
                return (0, 0)
        else:
            return (0, 0)

    def schedule(self) -> bool:
        assert self.status == _status_waiting
        for dep in self.upstream:
            if dep.status != _status_succeeded:
                if dep.status == _status_failed:
                    self.fail()
                    break
                else:
                    return False
        else:
            self.status = _status_scheduled
        return True

    def run(self) -> bool:
        assert self.status == _status_scheduled
        self.container = self.image.run_command(self.command)
        self.status = _status_running
        return True

    def finish(self) -> bool:
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

    def succeed(self) -> bool:
        self.status = _status_succeeded
        return True

    def fail(self) -> bool:
        self.status = _status_failed
        return True

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
