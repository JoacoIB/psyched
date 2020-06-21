import unittest

from psyched.task import (ShellTask, _STATUS_FAILED, _STATUS_RUNNING,
                          _STATUS_SCHEDULED, _STATUS_SUCCEEDED,
                          _STATUS_WAITING)


class TestShellTaskMethods(unittest.TestCase):

    def test_update_success_cycle(self):
        t1 = ShellTask("test_task", "true")
        self.assertEqual(t1.status, _STATUS_WAITING)

        t1.try_to_schedule()
        self.assertEqual(t1.status, _STATUS_SCHEDULED)

        d_running = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _STATUS_SCHEDULED)
        self.assertEqual(d_running, 0)

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _STATUS_RUNNING)
        self.assertEqual(d_running, 1)

        t1.wait()
        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _STATUS_SUCCEEDED)
        self.assertEqual(d_running, -1)

    def test_update_failure_cycle(self):
        t1 = ShellTask("test_task", "false")
        self.assertEqual(t1.status, _STATUS_WAITING)

        t1.try_to_schedule()
        self.assertEqual(t1.status, _STATUS_SCHEDULED)

        d_running = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _STATUS_SCHEDULED)
        self.assertEqual(d_running, 0)

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _STATUS_RUNNING)
        self.assertEqual(d_running, 1)

        t1.wait()

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _STATUS_FAILED)
        self.assertEqual(d_running, -1)

    def test_finish_success(self):
        t1 = ShellTask("test_task", "true")
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        t1.try_to_finish()
        self.assertEqual(t1.status, _STATUS_SUCCEEDED)

    def test_finish_fail(self):
        t1 = ShellTask("test_task", "false")
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        t1.try_to_finish()
        self.assertEqual(t1.status, _STATUS_FAILED)

    def test_long_task(self):
        t1 = ShellTask("test_task", ['sleep', '5'])
        t1.try_to_schedule()

        self.assertEqual(t1.get_logs(), "")

        t1.run()
        self.assertEqual(
            t1.try_to_finish(),
            False
        )

        t1.wait()
        t1.try_to_finish()
        self.assertEqual(
            t1.status,
            _STATUS_SUCCEEDED
        )

    def test_get_logs(self):
        hw = "Hello World!"

        t1 = ShellTask("test_task", ["echo", hw])
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        self.assertEqual(
            t1.get_logs(),
            hw + '\n'
        )
