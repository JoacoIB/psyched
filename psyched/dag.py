import time

import networkx as nx
from matplotlib import pyplot as plt

from .image import Image
from .task import Task


class DAG (object):
    def __init__(self, max_parallel_workers: int = 1):
        self.tasks = dict()
        self.max_parallel_tasks = max_parallel_workers
        return

    def add_task(self, task: Task):
        self.tasks[task.get_name()] = task
        return

    def new_task(self, name: str, image: Image, command: str) -> Task:
        t = Task(name, image, command)
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
        running = 0
        pending = len(self.tasks)
        while pending != 0:
            time.sleep(1)
            print('='*30)
            for k in self.tasks:
                d_running, d_pending = self.tasks[k].update_status(runnable=running < self.max_parallel_tasks)
                running += d_running
                pending += d_pending
                print(self.tasks[k])
        self.draw()
        return
