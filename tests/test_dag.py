import unittest

from psyched.dag import DAG
from psyched.image import Image
from psyched.task import DockerTask, _status_failed, _status_succeeded


class TestDAGMethods(unittest.TestCase):
    def setUp(self):
        self.image = Image('amd64/ubuntu', '20.04')
        self.dag = DAG()

    def test_add_task(self):
        t1 = DockerTask("test_task", self.image, "true")
        self.dag.add_task(t1)

        self.assertEqual(
            self.dag.tasks,
            {"test_task": t1}
            )

    def test_new_task(self):
        self.dag.new_task("test_task",  task_type='docker',  image=self.image, command="true")
        self.assertEqual(
            list(self.dag.tasks.keys()),
            ["test_task"]
            )

    def test_run_success(self):
        t1 = self.dag.new_task("test_task_1",  task_type='docker',  image=self.image, command="true")
        t2 = self.dag.new_task("test_task_2",  task_type='docker',  image=self.image, command="true")
        t3 = self.dag.new_task("test_task_3",  task_type='docker',  image=self.image, command="true")
        t4 = self.dag.new_task("test_task_4",  task_type='docker',  image=self.image, command="true")

        t1 >> [t2, t3] >> t4

        self.dag.run()

        for t in [t1, t2, t3, t4]:
            self.assertEqual(t.status, _status_succeeded)

    def test_run_failure(self):
        t1 = self.dag.new_task("test_task_1",  task_type='docker',  image=self.image, command="true")
        t2 = self.dag.new_task("test_task_2",  task_type='docker',  image=self.image, command="true")
        t3 = self.dag.new_task("test_task_3",  task_type='docker',  image=self.image, command="false")
        t4 = self.dag.new_task("test_task_4",  task_type='docker',  image=self.image, command="true")

        t1 >> [t2, t3] >> t4

        self.dag.run()

        for t in [t1, t2]:
            self.assertEqual(t.status, _status_succeeded)

        for t in [t3, t4]:
            self.assertEqual(t.status, _status_failed)
