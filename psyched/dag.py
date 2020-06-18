import time

from .task import DockerTask, PythonTask, ShellTask, Task


class DAG (object):
    """DAG class to manage task dependencies."""

    def __init__(self, max_parallel_workers: int = 1):
        """Class constructor.

        :param max_parallel_workers: maximum number of tasks to run in parallel, defaults to 1
        :type max_parallel_workers: int, optional
        """
        self.tasks = dict()
        self.max_parallel_tasks = max_parallel_workers
        self.running = 0
        return

    def add_task(self, task: Task):
        """Add a Task to the DAG.

        :param task: Task object to add to the DAG
        :type task: Task
        """
        self.tasks[task.get_name()] = task
        return

    def new_task(self, name: str, task_type: str, **kwargs) -> Task:
        """Create a new Task and add it to this DAG.

        Passes kwargs directly to the Task constructor.

        :param name: Task name
        :type name: str
        :param task_type: string identifying the type of Task to add
        :type task_type: str
        :raises ValueError: unknown value passed as task_type
        :return: the newly created task
        :rtype: Task
        """
        if task_type == 'docker':
            image = kwargs['image']
            command = kwargs['command']
            t = DockerTask(name, image, command)
        elif task_type == 'python':
            target = kwargs['target']
            del(kwargs['target'])
            t = PythonTask(name, target, **kwargs)
        elif task_type == 'shell':
            command = kwargs['command']
            t = ShellTask(name, command)
        else:
            raise ValueError(f"Unknown task type '{task_type}'")
        self.add_task(t)
        return t

    def run(self):
        """Run the tasks in the DAG following dependencies.

        Blocks until every task has either succeeded or failed.
        """
        for k in self.tasks:
            self.tasks[k].try_to_schedule()
        pending = len(self.tasks)
        while pending > 0:
            pending = 0
            time.sleep(1)

            for k in self.tasks:
                d_run = self.tasks[k].update_status(runnable=self.running < self.max_parallel_tasks)
                self.running += d_run
                if self.tasks[k].is_pending():
                    pending += 1
        return
