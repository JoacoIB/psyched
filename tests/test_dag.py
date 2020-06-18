import unittest

from psyched.dag import DAG
from psyched.image import Image
from psyched.task import (DockerTask, PythonTask, _status_failed,
                          _status_succeeded)


class TestDAGMethods(unittest.TestCase):
    def setUp(self):
        self.image = Image('amd64/ubuntu', '20.04')
        self.dag = DAG()
        self.pytarget = lambda: print(0)

    def test_add_task(self):
        t1 = DockerTask("test_docker", self.image, "true")
        t2 = PythonTask("test_python", self.pytarget)
        self.dag.add_task(t1)
        self.dag.add_task(t2)

        self.assertEqual(self.dag.tasks["test_docker"], t1)
        self.assertEqual(self.dag.tasks["test_python"], t2)

    def test_new_docker_task(self):
        self.dag.new_task("test_task",  task_type='docker',  image=self.image, command="true")
        self.assertEqual(
            list(self.dag.tasks.keys()),
            ["test_task"]
            )

    def test_new_python_task(self):
        self.dag.new_task("test_task",  task_type='python',  target=self.pytarget)
        self.assertEqual(
            list(self.dag.tasks.keys()),
            ["test_task"]
            )

    def test_new_shell_task(self):
        self.dag.new_task("test_task",  task_type='shell', command="true")
        self.assertEqual(
            list(self.dag.tasks.keys()),
            ["test_task"]
            )

    def test_new_wrong_task(self):
        with self.assertRaises(ValueError):
            self.dag.new_task("test_task",  task_type='aSdF',  target=self.pytarget)

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
