import unittest

from psyched.task import Task, _status_failed


class TestDockerTaskMethods(unittest.TestCase):
    def test_double_fail(self):
        t1 = Task('test_task')
        t1.fail()
        t1.fail()
        self.assertEqual(t1.status, _status_failed)
#     def setUp(self):
#         self.image = Image('amd64/ubuntu', '20.04')

#     def test_update_success_cycle(self):
#         t1 = DockerTask("test_task", self.image, "true")
#         self.assertEqual(t1.status, _status_waiting)

#         t1.try_to_schedule()
#         self.assertEqual(t1.status, _status_scheduled)

#         d_running = t1.update_status(runnable=False)
#         self.assertEqual(t1.status, _status_scheduled)
#         self.assertEqual(d_running, 0)

#         d_running = t1.update_status(runnable=True)
#         self.assertEqual(t1.status, _status_running)
#         self.assertEqual(d_running, 1)

#         t1.container.wait()
#         d_running = t1.update_status(runnable=True)
#         self.assertEqual(t1.status, _status_succeeded)
#         self.assertEqual(d_running, -1)

#     def test_update_failure_cycle(self):
#         t1 = DockerTask("test_task", self.image, "false")
#         self.assertEqual(t1.status, _status_waiting)

#         t1.try_to_schedule()
#         self.assertEqual(t1.status, _status_scheduled)

#         d_running = t1.update_status(runnable=False)
#         self.assertEqual(t1.status, _status_scheduled)
#         self.assertEqual(d_running, 0)

#         d_running = t1.update_status(runnable=True)
#         self.assertEqual(t1.status, _status_running)
#         self.assertEqual(d_running, 1)

#         t1.container.wait()

#         d_running = t1.update_status(runnable=True)
#         self.assertEqual(t1.status, _status_failed)
#         self.assertEqual(d_running, -1)

#     def test_schedule_ready(self):
#         t1 = DockerTask("test_task_1", self.image, "true")
#         t2 = DockerTask("test_task_2", self.image, "true")
#         t1 >> t2

#         t1.succeed()
#         self.assertEqual(t2.status, _status_scheduled)

#     def test_schedule_not_ready(self):
#         t1 = DockerTask("test_task_1", self.image, "true")
#         t2 = DockerTask("test_task_2", self.image, "true")
#         t1 >> t2

#         t2.try_to_schedule()
#         self.assertEqual(t2.status, _status_waiting)

#     def test_failed_dep(self):
#         t1 = DockerTask("test_task_1", self.image, "true")
#         t2 = DockerTask("test_task_2", self.image, "true")
#         t1 >> t2

#         t1.fail()
#         self.assertEqual(t2.status, _status_failed)

#     def test_finish_success(self):
#         t1 = DockerTask("test_task", self.image, "true")
#         t1.try_to_schedule()
#         t1.run()
#         t1.container.wait()
#         t1.try_to_finish()
#         self.assertEqual(t1.status, _status_succeeded)

#     def test_finish_fail(self):
#         t1 = DockerTask("test_task", self.image, "false")
#         t1.try_to_schedule()
#         t1.run()
#         t1.container.wait()
#         t1.try_to_finish()
#         self.assertEqual(t1.status, _status_failed)

    def test_rshift(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")

        t1 >> t2

        self.assertEqual(t1.get_downstream(), [t2])
        self.assertEqual(t2.get_upstream(), [t1])

    def test_rshift_list(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")
        t3 = Task("test_task_3")

        t1 >> [t2, t3]

        self.assertEqual(t1.get_downstream(), [t2, t3])
        self.assertEqual(t2.get_upstream(), [t1])
        self.assertEqual(t3.get_upstream(), [t1])

    def test_lshift(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")

        t1 << t2

        self.assertEqual(t1.get_upstream(), [t2])
        self.assertEqual(t2.get_downstream(), [t1])

    def test_lshift_list(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")
        t3 = Task("test_task_3")

        t1 << [t2, t3]

        self.assertEqual(t1.get_upstream(), [t2, t3])
        self.assertEqual(t2.get_downstream(), [t1])
        self.assertEqual(t3.get_downstream(), [t1])

    def test_rrshift(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")
        t3 = Task("test_task_3")

        [t1, t2] >> t3

        self.assertEqual(t3.get_upstream(), [t1, t2])
        self.assertEqual(t1.get_downstream(), [t3])
        self.assertEqual(t2.get_downstream(), [t3])

    def test_rlshift(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")
        t3 = Task("test_task_3")

        [t1, t2] << t3

        self.assertEqual(t3.get_downstream(), [t1, t2])
        self.assertEqual(t1.get_upstream(), [t3])
        self.assertEqual(t2.get_upstream(), [t3])
