import unittest
TODO = unittest.skip('not implemented yet')
from replay.tests.script import script_from
from replay.tests.path2url import path2url
from replay import external_process
import replay.run as m
import contextlib

import os
from replay import exceptions
from externals.fake import Fake as MemoryStore
from externals.fspath import working_directory
from temp_dir import within_temp_dir

import pkg_resources


class Test_Context(unittest.TestCase):

    def test_datastore_defaults_to_current_working_directory(self):
        self.assertEqual(os.getcwd(), m.Context().datastore.path)

    def test_virtualenv_parent_dir_defaults_to_dot_virtualenvs(self):
        default = os.path.join(os.getcwd(), '.virtualenvs')
        self.assertEqual(default, m.Context().virtualenv_parent_dir.path)


class RunnerFixture(object):

    def __init__(self, script, virtualenv_parent_dir=None):
        if virtualenv_parent_dir:
            venv_parent_dir = virtualenv_parent_dir
        else:
            venv_parent_dir = working_directory() / 'replay_virtualenvs'

        self.datastore = MemoryStore()
        self.context = m.Context(self.datastore, venv_parent_dir)
        self.script = script_from(script)
        self.runner = m.Runner(self.context, self.script)


class Test_Runner_check_inputs(unittest.TestCase):

    def test_input_file_missing_is_error(self):
        f = RunnerFixture(
            '''\
            inputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingInput):
            f.runner.check_inputs()

    def test_inputs_are_there_proceeds(self):
        f = RunnerFixture(
            '''\
            inputs:
                - existing: somewhere/existing file
            ''')
        (f.datastore / 'somewhere' / 'existing file').content = 'some content'

        f.runner.check_inputs()


@contextlib.contextmanager
def local_pypi_url():
    try:
        index_server_dir = pkg_resources.resource_filename(
            'replay', 'tests/fixtures/pypi/simple')
        assert os.path.isdir(index_server_dir), index_server_dir
        index_server_url = path2url(index_server_dir)

        yield index_server_url
    finally:
        pkg_resources.cleanup_resources(force=True)


class Test_Runner_make_virtualenv(unittest.TestCase):

    @within_temp_dir
    def test_virtualenv_is_created_in_context_specified_dir(self):
        f = RunnerFixture(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        f.runner.make_virtualenv()

        virtualenv_dir = virtualenv_parent_dir / f.runner.virtualenv_name
        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_virtualenv_already_exists_no_error(self):
        f = RunnerFixture(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        f.runner.make_virtualenv()
        f.runner.make_virtualenv()

        virtualenv_dir = virtualenv_parent_dir / f.runner.virtualenv_name
        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_new_virtualenv_has_all_the_required_packages(self):
        with local_pypi_url() as index_server_url:
            f = RunnerFixture(
                '''\
                python dependencies:
                    - roman==2.0.0
                ''')
            f.runner.make_virtualenv(index_server_url)

            # verify, that we can import the required "roman" module
            python = f.runner.virtualenv_dir / 'bin/python'
            program = 'import roman; print(roman.toRoman(23))'
            cmdspec = [python.path, '-c', program]
            result = external_process.run(cmdspec)

            if result.status:
                print(result)
            self.assertEqual('XXIII', result.stdout.rstrip())

    @within_temp_dir
    def test_required_package_not_installed_is_an_error(self):
        with local_pypi_url() as index_server_url:
            f = RunnerFixture(
                '''\
                python dependencies:
                    - remedy_for_all_problems==0.42.0
                ''')
            with self.assertRaises(exceptions.MissingPythonDependency):
                f.runner.make_virtualenv(index_server_url)


class Test_Runner_run_in_virtualenv(unittest.TestCase):

    @within_temp_dir
    def test_module_in_virtualenv_is_available(self):
        with local_pypi_url() as index_server_url:
            f = RunnerFixture(
                '''\
                python dependencies:
                    - roman==2.0.0
                ''')
            f.runner.make_virtualenv(index_server_url)

            # verify, that we can import the required "roman" module
            cmdspec = [
                'python', '-c', 'import roman; print(roman.toRoman(23))']
            result = f.runner.run_in_virtualenv(cmdspec)

            if result.status:
                print(result)
            self.assertEqual('XXIII', result.stdout.rstrip())


class Test_Runner(unittest.TestCase):

    @TODO
    def test_script_is_run_in_a_different_directory(self):
        pass

    @TODO
    def test_script_dependencies_are_available(self):
        pass

    @TODO
    def test_input_files_are_available_to_script(self):
        pass

    @TODO
    def test_generated_output_files_are_uploaded_to_datastore(self):
        pass
