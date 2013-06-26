import unittest
import os.path
import replay.script as m
from StringIO import StringIO


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def script_from(string, dir=FIXTURES_DIR):
    return m.Script(dir, StringIO(string))


class Test_Script(unittest.TestCase):

    def check_sample_script(self, script):
        self.assertEqual(FIXTURES_DIR, script.dir)
        self.assertEqual([{'input': 'dsinput'}], script.inputs)
        self.assertEqual([{'output': 'dsoutput'}], script.outputs)
        self.assertEqual('run.py', script.executable_name)
        self.assertEqual([], script.python_dependencies)
        self.assertTrue(script.has_option('some option'))

    def test_create(self):
        script_filename = os.path.join(FIXTURES_DIR, 'sample_script.yaml')

        with open(script_filename) as script_file:
            script = m.Script(FIXTURES_DIR, script_file)

        self.check_sample_script(script)

    def test_attribute_inputs(self):
        script = script_from('''\
            inputs:
                - i1: di1
                - i2: di2
            ''')

        self.assertEqual([{'i1': 'di1'}, {'i2': 'di2'}], script.inputs)

    def test_attribute_outputs(self):
        script = script_from('''\
            outputs:
                - o1: do1
                - o2: do2
            ''')

        self.assertEqual([{'o1': 'do1'}, {'o2': 'do2'}], script.outputs)

    def test_attribute_executable_name(self):
        script = script_from('''\
            script: exec.py
            ''')

        self.assertEqual('exec.py', script.executable_name)

    def test_attribute_python_dependencies(self):
        script = script_from('''\
            python dependencies:
                - PyYAML==3.10
                - lxml=3.2.1
            ''')

        self.assertEqual(['PyYAML==3.10', 'lxml=3.2.1'], script.python_dependencies)

    def test_has_option(self):
        script = script_from('''\
            options:
                - option1
                - option 2
            ''')

        self.assertTrue(script.has_option('option1'))
        self.assertTrue(script.has_option('option 2'))
        self.assertFalse(script.has_option('option3'))
