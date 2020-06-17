import time

import networkx as nx
from matplotlib import pyplot as plt

from .task import DockerTask, PythonTask, Task


class DAG (object):
    def __init__(self, max_parallel_workers: int = 1):
        self.tasks = dict()
        self.max_parallel_tasks = max_parallel_workers
        self.running = 0
        return

    def add_task(self, task: Task):
        self.tasks[task.get_name()] = task
        return

    def new_task(self, name: str, task_type: str, **kwargs) -> Task:
        if task_type == 'docker':
            image = kwargs['image']
            command = kwargs['command']
            t = DockerTask(name, image, command)
        elif task_type == 'python':
            target = kwargs['target']
            del(kwargs['target'])
            t = PythonTask(name, target, **kwargs)
        else:
            raise ValueError(f"Unknown task type '{task_type}'")
        self.add_task(t)
        return t

    def draw(self, path: str = 'dag.png'):
        G = nx.DiGraph()
        colors = []
        for k in self.tasks:
            G.add_node(k)
            colors.append(self.tasks[k].get_color())
        for k in self.tasks:
            for tp in self.tasks[k].get_downstream():
                G.add_edge(k, tp.get_name())
        plt.close()
        nx.draw(G, with_labels=True, node_color=colors)
        plt.savefig(path)
        return

    def run(self):
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
