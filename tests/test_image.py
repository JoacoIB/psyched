import unittest

from psyched.image import Image


class TestImageMethods(unittest.TestCase):
    def setUp(self):
        self.image = Image('amd64/ubuntu', '20.04')

    def test_add_volume(self):
        cases = [
            ('/a1', '/b1', 'rw'),
            ('/a2', '/b2', 'ro')
        ]
        for case in cases:
            self.image.add_volume(*case)
        self.assertEqual(
            self.image.volumes[case[0]],
            {'bind': case[1], 'mode': case[2]}
            )

    def test_run_command_success(self):
        container = self.image.run_command("echo hello")
        result = container.wait()
        self.assertEqual(
            result,
            {'Error': None,
             'StatusCode': 0}
            )
        output = container.logs()
        self.assertEqual(output, b'hello\n')

    def test_run_command_fail(self):
        container = self.image.run_command("false")
        result = container.wait()
        self.assertEqual(
            result,
            {'Error': None,
             'StatusCode': 1}
            )
        output = container.logs()
        self.assertEqual(output, b'')
