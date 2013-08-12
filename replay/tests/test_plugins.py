import unittest
TODO = unittest.skip('not implemented yet')

from temp_dir import within_temp_dir
import getpass
import os
from externals import fspath

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
            plugins.DataStore(f.runner).__enter__()

    @within_temp_dir
    def test_outputs_are_uploaded_to_datastore(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - an output file: /output/datastore/path
            ''')

        with plugins.DataStore(f.runner):
            (fspath.working_directory() / 'an output file').content = 'data'

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


class TestWorkingDirectory(unittest.TestCase):

    orig_working_directory = str
    script_working_directory = str

    @within_temp_dir
    def test_working_directory_changed(self):
        self.run_plugin()
        self.assertNotEqual(
            self.orig_working_directory,
            self.script_working_directory)

    @within_temp_dir
    def test_script_dir_is_deleted(self):
        self.run_plugin()
        self.assertFalse(os.path.isdir(self.script_working_directory))

    @within_temp_dir
    def test_orig_directory_restored(self):
        self.run_plugin()
        self.assertEqual(self.orig_working_directory, os.getcwd())

    @within_temp_dir
    def test_copy_of_scripts_directory_is_in_working_directory(self):
        DEFAULT_FIXTURE_KNOWN_FILE = 'scripts/import_roman.py'

        def run_in_directory():
            print os.getcwd(), os.listdir('.')
            self.assertTrue(os.path.exists(DEFAULT_FIXTURE_KNOWN_FILE))
        self.run_plugin(run_in_directory)

    def run_plugin(self, run_in_directory=(lambda: False)):
        f = fixtures.Runner('{}')
        self.orig_working_directory = os.getcwd()

        with plugins.WorkingDirectory(f.runner):
            self.script_working_directory = os.getcwd()
            run_in_directory()


class TestTemporaryDirectory(TestWorkingDirectory):

    def run_plugin(self, run_in_directory=(lambda: False)):
        f = fixtures.Runner('{}')
        f.context.working_directory = (
            plugins.TemporaryDirectory)
        self.orig_working_directory = os.getcwd()

        with plugins.TemporaryDirectory(f.runner):
            self.script_working_directory = os.getcwd()
            run_in_directory()


class TestVirtualEnv(unittest.TestCase):

    @within_temp_dir
    def test_virtualenv_is_created_in_context_specified_dir(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        plugin = plugins.VirtualEnv(f.runner)
        with plugin:
            virtualenv_dir = virtualenv_parent_dir / plugin.virtualenv_name

        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_virtualenv_already_exists_no_error(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        with plugins.VirtualEnv(f.runner):
            plugin = plugins.VirtualEnv(f.runner)
            with plugin:
                virtualenv_dir = virtualenv_parent_dir / plugin.virtualenv_name

        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_new_virtualenv_has_all_the_required_packages(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0
            ''')
        plugin = plugins.VirtualEnv(f.runner)
        with plugin:
            python = plugin.virtualenv_dir / 'bin/python'

        # verify, that we can import the required "roman" module
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
            plugins.VirtualEnv(f.runner).__enter__()

    @within_temp_dir
    def test_module_in_virtualenv_is_available(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0
            ''')

        # verify, that we can import the required "roman" module
        cmdspec = [
            'python', '-c', 'import roman; print(roman.toRoman(23))']

        with plugins.VirtualEnv(f.runner):
            result = external_process.run(cmdspec)

        # if result.status: print(result)
        self.assertEqual('XXIII', result.stdout.rstrip())


class Test_VirtualEnv_virtualenv_name(unittest.TestCase):

    def test_empty_virtualenv_name(self):
        f = fixtures.Runner('{}')
        self.assertEqual(
            '_replay_d41d8cd98f00b204e9800998ecf8427e',
            plugins.VirtualEnv(f.runner).virtualenv_name)

    def test_virtualenv_name_depends_on_required_python_packages(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - a
                - roman==2.0.0
                - pi>=3.14
            ''')
        self.assertEqual(
            '_replay_e8a8bbe2f9fd4e9286aeedab2a5009e2',
            plugins.VirtualEnv(f.runner).virtualenv_name)

    def test_python_package_order_does_not_matter(self):
        f1 = fixtures.Runner(
            '''\
            python dependencies:
                - a
                - roman==2.0.0
                - pi>=3.14
            ''')
        f2 = fixtures.Runner(
            '''\
            python dependencies:
                - pi>=3.14
                - roman==2.0.0
                - a
            ''')

        ve_name1 = plugins.VirtualEnv(f1.runner).virtualenv_name
        ve_name2 = plugins.VirtualEnv(f2.runner).virtualenv_name
        self.assertEqual(ve_name1, ve_name2)
        self.assertEqual('_replay_e8a8bbe2f9fd4e9286aeedab2a5009e2', ve_name1)


#   postgresql:  (database name {USER}_{script_name}_{datetime})
#       before_execute: create database
#       after_execute: drop database (unless debugging & explicitly requested)
#     NOTE:
#           runner should store script_name
#           should tests be configurable to run/not run database tests?


# within Postgres() block psql connects to the database of the Postgres plugin

class TestPostgres(unittest.TestCase):

    @property
    def fixture(self):
        return fixtures.Runner(
            '''\
            options:
                - uses psql
            ''')

    def test_database_name(self):
        f = self.fixture
        plugin = plugins.Postgres(f.runner)
        timestamp = plugin.timestamp

        self.assertIn(f.runner.script_name, plugin.database)
        self.assertIn(getpass.getuser(), plugin.database)
        self.assertIn(timestamp, plugin.database)
        self.assertEqual(timestamp, plugin.timestamp)

    def test_database_name_is_unique(self):
        f = self.fixture

        plugin1 = plugins.Postgres(f.runner)
        plugin2 = plugins.Postgres(f.runner)

        self.assertLess(plugin1.timestamp, plugin2.timestamp)
        self.assertLess(plugin1.database, plugin2.database)

    def check_psql_default_database(self, database):
        result = external_process.run(['psql', '-c', r'\conninfo'])

        self.assertEqual(0, result.status)
        self.assertIn(database, result.stdout)
        self.assertNotIn(database, result.stderr)

    def check_database_exists(self, database):
        result = external_process.run(['psql', '-c', r'\list'])

        self.assertEqual(0, result.status)
        self.assertIn(database, result.stdout)
        self.assertNotIn(database, result.stderr)

    def check_database_does_not_exist(self, database):
        result = external_process.run(['psql', 'postgres', '-c', r'\list'])

        self.assertEqual(0, result.status)
        self.assertNotIn(database, result.stdout)

    def test_psql_connects_to_database(self):
        plugin = plugins.Postgres(self.fixture.runner)

        with plugin:
            self.check_psql_default_database(plugin.database)

    def test_database_dropped_after_block(self):
        plugin = plugins.Postgres(self.fixture.runner)

        with plugin:
            pass

        self.check_database_does_not_exist(plugin.database)

    def test_environment_variable_restored(self):
        orig_environ = os.environ.copy()

        with plugins.Postgres(self.fixture.runner):
            pass

        self.assertDictEqual(orig_environ, os.environ.copy())

    def test_without_uses_psql_database_is_not_available(self):
        f = fixtures.Runner(
            '''\
            options:
                - uses text files!
            ''')

        plugin = plugins.Postgres(f.runner)

        with plugin:
            self.assertFalse(plugin.enabled)
            self.check_database_does_not_exist(plugin.database)

    def test_option_keep_database_database_remains_available(self):
        f = fixtures.Runner(
            '''\
            options:
                - uses psql
                - keep database
                - debug
            ''')

        plugin = plugins.Postgres(f.runner)

        try:
            with plugin:
                self.check_psql_default_database(plugin.database)

            self.check_database_exists(plugin.database)
        finally:
            external_process.run(['dropdb', plugin.database])


class Test_EnvironKeyState(unittest.TestCase):

    def test_nonexistent_key(self):
        env = {'a': 1}
        state = plugins._EnvironKeyState(env, 'key')
        env['key'] = 'create'

        state.restore(env)

        self.assertEqual({'a': 1}, env)

    def test_nonexistent_key_not_changed(self):
        env = {'a': 1}
        state = plugins._EnvironKeyState(env, 'key')

        state.restore(env)

        self.assertEqual({'a': 1}, env)

    def test_overwritten_key(self):
        env = {'a': 1, 'key': 'value'}
        state = plugins._EnvironKeyState(env, 'key')
        env['key'] = 'another value'

        state.restore(env)

        self.assertEqual({'a': 1, 'key': 'value'}, env)

    def test_deleted_key_restored(self):
        env = {'a': 1, 'key': 'value'}
        state = plugins._EnvironKeyState(env, 'key')
        del env['key']

        state.restore(env)

        self.assertEqual({'a': 1, 'key': 'value'}, env)
