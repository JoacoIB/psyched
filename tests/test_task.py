import unittest

from psyched.task import Task, _STATUS_FAILED


class TestTaskMethods(unittest.TestCase):
    def test_double_fail(self):
        t1 = Task('test_task')
        t1.fail()
        t1.fail()
        self.assertEqual(t1.status, _STATUS_FAILED)

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

    def test_cycle(self):
        t1 = Task("test_task_1")
        t2 = Task("test_task_2")

        t1 >> t2
        with self.assertRaises(RuntimeError):
            t2 >> t1
