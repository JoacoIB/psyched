"""This module exports the class Task used as a base class from which specific tasks inherit."""
from __future__ import annotations

from typing import List, Union

_STATUS_WAITING = 'waiting'
_STATUS_SCHEDULED = 'scheduled'
_STATUS_RUNNING = 'running'
_STATUS_SUCCEEDED = 'succeeded'
_STATUS_FAILED = 'failed'


class Task():
    """Generic Task class from which specific Task classes inherit.

    There are two fundamental concepts that need to be understood about tasks:
    * upstream/downstream
    * status

    **Upstream and downstream**

    The key concept that psyched is based on is task interdependency. Some\
        task B can't start before another task A finishes. When this is\
        the case we say A is upstream from B, or conversely, that B is\
        downstream from B. With these relationship we can define complex\
        dependency structures called DAGs (Directed Acyclic Graphs).

    **Status**
    During their lifetime tasks go through a variety of status.

    ``waiting``: tasks start in this status. It means the task is waiting for\
        some condition before it is ready to be run. Can be due to either \
        some upstream tasks not being finished yet or the DAG not having started.

    ``scheduled``: task is ready to be run. All its upstream tasks already\
        finished successfully.

    ``running``: task is running.

    ``succeeded``: task completed successfully.

    ``failed``: either this task or an upstream task completed unsuccessfully.
    """

    def __init__(self, name: str):
        """Class constructor.

        :param name: task name
        :type name: str
        """
        self.name = name
        self.status = _STATUS_WAITING
        self.upstream = []
        self.downstream = []

    def update_status(self, runnable: bool = False) -> int:
        """Update query status.

        Runs the task (and updates the status) if it's scheduled and runnable is True.
        If the status is ``running`` tries to finish it.

        :param runnable: indicates whether the task should be run if possible, defaults to False
        :type runnable: bool, optional
        :return: 1 if started running task, -1 if finished running task, 0 if no changes made
        :rtype: int
        """
        if self.status == _STATUS_SCHEDULED:
            if runnable:
                self.run()
                return 1
            return 0
        if self.status == _STATUS_RUNNING:
            if self.try_to_finish():
                return -1
            return 0
        return 0

    def try_to_schedule(self) -> bool:
        """Check if all dependencies finished and if so schedule this task.

        :return: whether the task was scheduled or not
        :rtype: bool
        """
        assert self.status == _STATUS_WAITING
        for dep in self.upstream:
            if dep.status != _STATUS_SUCCEEDED:
                return False
        self.status = _STATUS_SCHEDULED
        return True

    def run(self):
        """Run the task.

        :raises NotImplementedError: this function is a shell. It should be\
        overriden by classes inheriting from Task
        """
        raise NotImplementedError

    def try_to_finish(self) -> bool:
        """Check if the task is finished and update the status accordingly.

        :raises NotImplementedError: this function is a shell. It should be\
        overriden by classes inheriting from Task
        """
        raise NotImplementedError

    def succeed(self):
        """Set task status as succeeded and try to schedule downstream tasks."""
        self.status = _STATUS_SUCCEEDED
        for task in self.downstream:
            task.try_to_schedule()

    def fail(self):
        """Set task status as failed and does the same recursively downstream."""
        if self.status == _STATUS_FAILED:
            return
        self.status = _STATUS_FAILED
        for task in self.downstream:
            task.fail()

    def set_upstream(self, task: Task):
        """Set another task as downstream from this one.

        :param task: Task downstream to this one
        :type task: Task
        """
        if task not in self.upstream:
            self.upstream.append(task)
            task.set_downstream(self)

    def set_downstream(self, task: Task):
        """Set another task as upstream from this one.

        :param task: Task upstream to this one
        :type task: Task
        """
        if task not in self.downstream:
            self.downstream.append(task)
            task.set_upstream(self)

    def get_name(self) -> str:
        """Get this task name.

        :return: Task assigned name.
        :rtype: str
        """
        return self.name

    def get_logs(self) -> str:
        """Get this task log.

        :raises NotImplementedError: this function is a shell. It should be\
        overriden by classes inheriting from Task.
        :return: task logs
        :rtype: str
        """
        raise NotImplementedError

    def get_upstream(self) -> List[Task]:
        """Get the list of upstream tasks.

        :return: list of upstream tasks
        :rtype: List[Task]
        """
        return self.upstream

    def get_downstream(self) -> List[Task]:
        """Get the list of downstream tasks.

        :return: list of downstream tasks
        :rtype: List[Task]
        """
        return self.downstream

    def is_pending(self) -> bool:
        """Check if this task has not finished yet.

        :return: whether the Task is pending
        :rtype: bool
        """
        return self.status not in [_STATUS_SUCCEEDED, _STATUS_FAILED]

    def check_cycles(self):
        """Cheks if the task is part of a cycle.

        :raises RuntimeError: if it finds a cycle
        """
        visited = []
        pending = self.get_downstream()
        while pending != []:
            task = pending[0]
            if self == task:
                raise RuntimeError(f"Task {self} is part of a cycle.")
            visited.append(task)
            downstream_tasks = [
                dtask
                for dtask in task.get_downstream()
                if dtask not in visited and dtask not in pending
                ]
            pending = pending[1:] + downstream_tasks

    def __rshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        """Operator >>.

        Sets right task(s) downstream from left task.
        """
        if isinstance(other, Task):
            self.set_downstream(other)
        elif isinstance(other, list):
            for task in other:
                self >> task
        else:
            raise TypeError("Invalid type for >>")
        return other
        self.check_cycles()

    def __lshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        """Operator <<.

        Sets right task(s) upstream from left task.
        """
        if isinstance(other, Task):
            self.set_upstream(other)
        elif isinstance(other, list):
            for task in other:
                self << task
        else:
            raise TypeError("Invalid type for >>")
        return other
        self.check_cycles()

    def __rrshift__(self, other: List[Task]) -> Task:
        """Reverse operator >>.

        Sets right task downstream from left tasks.
        """
        self << other
        return self

    def __rlshift__(self, other: List[Task]) -> Task:
        """Reverse operator >>.

        Sets right task upstream from left tasks.
        """
        self >> other
        return self

    def __str__(self):
        return f'Task<{self.name}> ({self.status})'
