from psyched.utils import SysRedirect
import unittest
import sys


class TestSysRedirect(unittest.TestCase):
    def setUp(self):
        SysRedirect.install()

    def test_regular_print(self):
        print("", end='')
        sys.stdout.flush()
        self.assertEqual(
            type(sys.stdout),
            SysRedirect
        )
