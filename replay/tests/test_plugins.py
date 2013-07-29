import unittest
from temp_dir import within_temp_dir
from replay.tests import fixtures

from replay import external_process

from replay import plugins
from replay import exceptions


class TestDataStore(unittest.TestCase):

    @within_temp_dir
    def test_input_file_missing_is_error(self):
        f = fixtures.Runner(
            '''\
            inputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingInput):
            with plugins.DataStore(f.runner):
                pass

    @within_temp_dir
    def test_outputs_are_uploaded_to_datastore(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - an output file: /output/datastore/path
            ''')

        with plugins.DataStore(f.runner):
            (f.context.working_directory / 'an output file').content = 'data'

        self.assertEqual(
            'data',
            (f.datastore / 'output/datastore/path').content)

    @within_temp_dir
    def test_output_file_missing_is_error(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingOutput):
            with plugins.DataStore(f.runner):
                pass


class TestVirtualEnv(unittest.TestCase):

    @within_temp_dir
    def test_virtualenv_is_created_in_context_specified_dir(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        with plugins.VirtualEnv(f.runner):
            pass

        virtualenv_dir = virtualenv_parent_dir / f.runner.virtualenv_name
        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_virtualenv_already_exists_no_error(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        with plugins.VirtualEnv(f.runner):
            with plugins.VirtualEnv(f.runner):
                pass

        virtualenv_dir = virtualenv_parent_dir / f.runner.virtualenv_name
        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_new_virtualenv_has_all_the_required_packages(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0
            ''')
        with plugins.VirtualEnv(f.runner):
            pass

        # verify, that we can import the required "roman" module
        python = f.runner.virtualenv_dir / 'bin/python'
        program = 'import roman; print(roman.toRoman(23))'
        cmdspec = [python.path, '-c', program]
        result = external_process.run(cmdspec)

        # if result.status: print(result)
        self.assertEqual('XXIII', result.stdout.rstrip())

    @within_temp_dir
    def test_required_package_not_installed_is_an_error(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - remedy_for_all_problems==0.42.0
            ''')
        with self.assertRaises(exceptions.MissingPythonDependency):
            with plugins.VirtualEnv(f.runner):
                pass
