import unittest
from temp_dir import in_temp_dir
import replay.external_process as m
import os
import textwrap


class Test_run(unittest.TestCase):

    def test_stdout(self):
        result = m.run(['/bin/sh', '-c', 'echo test output'])
        self.assertEqual('test output', result.stdout.rstrip())

    def test_stderr(self):
        result = m.run(['/bin/sh', '-c', 'echo test output >&2'])
        self.assertEqual('test output', result.stderr.rstrip())

    def test_status(self):
        result = m.run(['/bin/sh', '-c', 'exit 31'])
        self.assertEqual(31, result.status)

    def test_cwd(self):
        wd = os.getcwd()
        with in_temp_dir():
            result = m.run(['/bin/sh', '-c', 'pwd'], cwd=wd)
        self.assertEqual(wd, result.stdout.rstrip())

    def test_env(self):
        env = {'V1': 'V1SET'}
        result = m.run(['/bin/sh', '-c', 'echo $V1'], env=env)
        self.assertIn('V1SET', result.stdout)

        os.environ['V2'] = 'V2SET'
        result = m.run(['/bin/sh', '-c', 'echo $V2'], env=env)
        self.assertNotIn('V2SET', result.stdout)

    def test_str(self):
        result = m.run(['/bin/sh', '-c', 'echo test output'])
        expected = textwrap.dedent(
            '''\
            Command execution result
            COMMAND:
              ('/bin/sh', '-c', 'echo test output')
            STATUS:
              0
            STDOUT:
              test output
            ''').splitlines()
        actual = str(result).splitlines()
        self.assertListEqual(expected, actual)
