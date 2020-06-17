import unittest
from time import sleep

from psyched.task import (PythonTask, _status_failed, _status_running,
                          _status_scheduled, _status_succeeded,
                          _status_waiting)


class TestPythonTaskMethods(unittest.TestCase):
    def setUp(self):
        def count(n):
            cnt = 0
            for i in range(n):
                cnt += 1
            return
        self.func = count

    def test_update_success_cycle(self):
        t1 = PythonTask("test_task", target=self.func, n=10000)
        self.assertEqual(t1.status, _status_waiting)

        t1.try_to_schedule()
        self.assertEqual(t1.status, _status_scheduled)

        d_running = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_running)
        self.assertEqual(d_running, 1)

        t1.wait()
        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_succeeded)
        self.assertEqual(d_running, -1)

    def test_update_failure_cycle(self):
        t1 = PythonTask("test_task", target=self.func, n="bad_value")
        self.assertEqual(t1.status, _status_waiting)

        t1.try_to_schedule()
        self.assertEqual(t1.status, _status_scheduled)

        d_running = t1.update_status(runnable=False)
        self.assertEqual(t1.status, _status_scheduled)
        self.assertEqual(d_running, 0)

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_running)
        self.assertEqual(d_running, 1)

        t1.wait()

        d_running = t1.update_status(runnable=True)
        self.assertEqual(t1.status, _status_failed)
        self.assertEqual(d_running, -1)

    def test_finish_success(self):
        t1 = PythonTask("test_task", target=self.func, n=10000)
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        t1.try_to_finish()
        self.assertEqual(t1.status, _status_succeeded)

    def test_finish_fail(self):
        t1 = PythonTask("test_task", target=self.func, n="bad_value")
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        t1.try_to_finish()
        self.assertEqual(t1.status, _status_failed)

    def test_long_task(self):
        def long_task():
            sleep(5)

        t1 = PythonTask("test_task", target=long_task)
        t1.try_to_schedule()
        t1.run()
        self.assertEqual(
            t1.update_status(),
            0
        )
        t1.wait()
        t1.try_to_finish()
        self.assertEqual(
            t1.status,
            _status_succeeded
        )

    def test_get_logs(self):
        hw = "Hello World!"

        def log_something():
            print(hw)

        t1 = PythonTask("test_task", target=log_something)
        t1.try_to_schedule()
        t1.run()
        t1.wait()
        self.assertEqual(
            t1.get_logs(),
            hw + '\n'
        )
