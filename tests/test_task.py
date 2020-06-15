import unittest

from psyched.image import Image
from psyched.task import (Task, _status_failed, _status_running,
                          _status_scheduled, _status_succeeded,
                          _status_waiting)


class TestTaskMethods(unittest.TestCase):
    def setUp(self):
        self.image = Image('amd64/ubuntu', '20.04')

    def test_update_success_cycle(self):
        t1 = Task("test_task", self.image, "true")
        self.assertEqual(t1.status, _status_waiting)
        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)
        d_running, d_pending = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)
        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_running)
        self.assertEqual(d_running, 1)
        self.assertEqual(d_pending, 0)
        t1.container.wait()
        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_succeeded)
        self.assertEqual(d_running, -1)
        self.assertEqual(d_pending, -1)

    def test_update_failure_cycle(self):
        t1 = Task("test_task", self.image, "false")
        self.assertEqual(t1.status, _status_waiting)

        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)

        d_running, d_pending = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)

        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_running)
        self.assertEqual(d_running, 1)
        self.assertEqual(d_pending, 0)
        t1.container.wait()

        d_running, d_pending = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_failed)
        self.assertEqual(d_running, -1)
        self.assertEqual(d_pending, -1)

    def test_schedule_ready(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t1 >> t2

        t1.status = _status_succeeded
        d_running, d_pending = t2.update_status(runnable=True)
        self.assertEqual(t2.status, _status_scheduled)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)

    def test_schedule_not_ready(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t1 >> t2

        d_running, d_pending = t2.update_status(runnable=True)
        self.assertEqual(t2.status, _status_waiting)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, 0)

    def test_schedule_failed_dep(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t1 >> t2

        t1.status = _status_failed
        d_running, d_pending = t2.update_status(runnable=True)
        self.assertEqual(t2.status, _status_failed)
        self.assertEqual(d_running, 0)
        self.assertEqual(d_pending, -1)

    def test_finish_success(self):
        t1 = Task("test_task", self.image, "true")
        t1.schedule()
        t1.run()
        t1.container.wait()
        t1.finish()
        self.assertEqual(t1.status, _status_succeeded)

    def test_finish_fail(self):
        t1 = Task("test_task", self.image, "false")
        t1.schedule()
        t1.run()
        t1.container.wait()
        t1.finish()
        self.assertEqual(t1.status, _status_failed)

    def test_rshift(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")

        t1 >> t2

        self.assertEqual(t1.downstream, [t2])
        self.assertEqual(t2.upstream, [t1])

    def test_rshift_list(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t3 = Task("test_task_3", self.image, "true")

        t1 >> [t2, t3]

        self.assertEqual(t1.downstream, [t2, t3])
        self.assertEqual(t2.upstream, [t1])
        self.assertEqual(t3.upstream, [t1])

    def test_lshift(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")

        t1 << t2

        self.assertEqual(t1.upstream, [t2])
        self.assertEqual(t2.downstream, [t1])

    def test_lshift_list(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t3 = Task("test_task_3", self.image, "true")

        t1 << [t2, t3]

        self.assertEqual(t1.upstream, [t2, t3])
        self.assertEqual(t2.downstream, [t1])
        self.assertEqual(t3.downstream, [t1])

    def test_rrshift(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t3 = Task("test_task_3", self.image, "true")

        [t1, t2] >> t3

        self.assertEqual(t3.upstream, [t1, t2])
        self.assertEqual(t1.downstream, [t3])
        self.assertEqual(t2.downstream, [t3])

    def test_rlshift(self):
        t1 = Task("test_task_1", self.image, "true")
        t2 = Task("test_task_2", self.image, "true")
        t3 = Task("test_task_3", self.image, "true")

        [t1, t2] << t3

        self.assertEqual(t3.downstream, [t1, t2])
        self.assertEqual(t1.upstream, [t3])
        self.assertEqual(t2.upstream, [t3])
