from __future__ import annotations

from typing import List, Union

_status_waiting = 'waiting'
_status_scheduled = 'scheduled'
_status_running = 'running'
_status_succeeded = 'succeeded'
_status_failed = 'failed'


class Task(object):
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
        self.status = _status_waiting
        self.upstream = []
        self.downstream = []
        return

    def update_status(self, runnable: bool = False) -> int:
        """Update query status.

        Runs the task (and updates the status) if it's scheduled and runnable is True.
        If the status is ``running`` tries to finish it.

        :param runnable: indicates whether the task should be run if possible, defaults to False
        :type runnable: bool, optional
        :return: 1 if started running task, -1 if finished running task, 0 if no changes made
        :rtype: int
        """
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
        """Check if all dependencies finished and if so schedule this task.

        :return: whether the task was scheduled or not
        :rtype: bool
        """
        assert self.status == _status_waiting
        for dep in self.upstream:
            if dep.status != _status_succeeded:
                return False
        self.status = _status_scheduled
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
        self.status = _status_succeeded
        for t in self.downstream:
            t.try_to_schedule()
        return

    def fail(self):
        """Set task status as failed and does the same recursively downstream."""
        if self.status == _status_failed:
            return
        self.status = _status_failed
        for t in self.downstream:
            t.fail()
        return

    def set_upstream(self, t: Task):
        """Set another task as downstream from this one.

        :param t: Task downstream to this one
        :type t: Task
        """
        if t not in self.upstream:
            self.upstream.append(t)
            t.set_downstream(self)
        return

    def set_downstream(self, t: Task):
        """Set another task as upstream from this one.

        :param t: Task upstream to this one
        :type t: Task
        """
        if t not in self.downstream:
            self.downstream.append(t)
            t.set_upstream(self)
        return

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
        return self.status not in [_status_succeeded, _status_failed]

    def __rshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        """Operator >>.

        Sets right task(s) downstream from left task.
        """
        if isinstance(other, Task):
            self.set_downstream(other)
        elif isinstance(other, list):
            for t in other:
                self >> t
        else:
            raise TypeError("Invalid type for >>")
        return other

    def __lshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        """Operator <<.

        Sets right task(s) upstream from left task.
        """
        if isinstance(other, Task):
            self.set_upstream(other)
        elif isinstance(other, list):
            for t in other:
                self << t
        else:
            raise TypeError("Invalid type for >>")
        return other

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
