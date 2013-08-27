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


class TestInputs(unittest.TestCase):

    @within_temp_dir
    def test_input_file_missing_is_error(self):
        f = fixtures.PluginContext(
            '''\
            Inputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingInput):
            f.plugin.__enter__()

    @within_temp_dir
    def test_inputs_are_downloaded_from_datastore(self):
        f = fixtures.PluginContext(
            '''\
            Inputs:
                - an input file: input/datastore/path
            ''')

        (f.datastore / 'input/datastore/path').content = 'hello'

        with f.plugin:
            self.assertEqual(
                'hello',
                (fspath.working_directory() / 'an input file').content)


class TestOutputs(unittest.TestCase):

    @within_temp_dir
    def test_outputs_are_uploaded_to_datastore(self):
        f = fixtures.PluginContext(
            '''\
            Outputs:
                - an output file: /output/datastore/path
            ''')

        with f.plugin:
            (fspath.working_directory() / 'an output file').content = 'data'

        self.assertEqual(
            'data',
            (f.datastore / 'output/datastore/path').content)

    @within_temp_dir
    def test_output_file_missing_is_error(self):
        f = fixtures.PluginContext(
            '''\
            Outputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingOutput):
            with f.plugin:
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

    def run_plugin(self):
        f = fixtures.PluginContext()
        self.orig_working_directory = os.getcwd()

        with plugins.WorkingDirectory(f.context):
            self.script_working_directory = os.getcwd()


class TestTemporaryDirectory(TestWorkingDirectory):

    def run_plugin(self):
        f = fixtures.PluginContext()
        f.context.working_directory = (
            plugins.TemporaryDirectory)
        self.orig_working_directory = os.getcwd()

        with plugins.TemporaryDirectory(f.context):
            self.script_working_directory = os.getcwd()


class TestCopyScript(unittest.TestCase):

    @within_temp_dir
    def test_copy_of_scripts_directory_is_in_working_directory(self):
        DEFAULT_FIXTURE_KNOWN_FILE = 'scripts/import_roman.py'

        with plugins.CopyScript(fixtures.FIXTURES_DIR):
            self.assertTrue(os.path.exists(DEFAULT_FIXTURE_KNOWN_FILE))


class TestPythonDependencies(unittest.TestCase):

    @within_temp_dir
    def test_virtualenv_is_created_in_context_specified_dir(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        with f.plugin:
            virtualenv_dir = virtualenv_parent_dir / f.plugin.virtualenv_name

        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_virtualenv_already_exists_no_error(self):
        empty_spec = '''\
            PythonDependencies:
            '''

        f1 = fixtures.PluginContext(empty_spec)
        f2 = fixtures.PluginContext(empty_spec)
        virtualenv_parent_dir = f1.context.virtualenv_parent_dir

        with f1.plugin:
            with f2.plugin:
                virtualenv_dir = (
                    virtualenv_parent_dir / f2.plugin.virtualenv_name)

        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_new_virtualenv_has_all_the_required_packages(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - roman==2.0.0
            ''')
        with f.plugin:
            python = f.plugin.virtualenv_dir / 'bin/python'

        # verify, that we can import the required "roman" module
        program = 'import roman; print(roman.toRoman(23))'
        cmdspec = [python.path, '-c', program]
        result = external_process.run(cmdspec)

        # if result.status: print(result)
        self.assertEqual('XXIII', result.stdout.rstrip())

    @within_temp_dir
    def test_required_package_not_installed_is_an_error(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - remedy_for_all_problems==0.42.0
            ''')
        with self.assertRaises(exceptions.MissingPythonDependency):
            f.plugin.__enter__()

    @within_temp_dir
    def test_module_in_virtualenv_is_available(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - roman==2.0.0
            ''')

        # verify, that we can import the required "roman" module
        cmdspec = [
            'python', '-c', 'import roman; print(roman.toRoman(23))']

        with f.plugin:
            result = external_process.run(cmdspec)

        # if result.status: print(result)
        self.assertEqual('XXIII', result.stdout.rstrip())


class Test_PythonDependencies_virtualenv_name(unittest.TestCase):

    def test_empty_virtualenv_name(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
            ''')
        self.assertEqual(
            '_replay_d41d8cd98f00b204e9800998ecf8427e',
            f.plugin.virtualenv_name)

    def test_virtualenv_name_depends_on_required_python_packages(self):
        f = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - a
                - roman==2.0.0
                - pi>=3.14
            ''')
        self.assertEqual(
            '_replay_e8a8bbe2f9fd4e9286aeedab2a5009e2',
            f.plugin.virtualenv_name)

    def test_python_package_order_does_not_matter(self):
        f1 = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - a
                - roman==2.0.0
                - pi>=3.14
            ''')
        f2 = fixtures.PluginContext(
            '''\
            PythonDependencies:
                - pi>=3.14
                - roman==2.0.0
                - a
            ''')

        ve_name1 = f1.plugin.virtualenv_name
        ve_name2 = f2.plugin.virtualenv_name
        self.assertEqual(ve_name1, ve_name2)
        self.assertEqual('_replay_e8a8bbe2f9fd4e9286aeedab2a5009e2', ve_name1)


class TestPostgres(unittest.TestCase):

    def fixture(self):
        return fixtures.PluginContext(
            '''\
            Postgres:
                script name: xsfw
            ''')

    def test_database_name(self):
        plugin = self.fixture().plugin
        timestamp = plugin.timestamp

        self.assertIn('xsfw', plugin.database)
        self.assertIn(getpass.getuser(), plugin.database)
        self.assertIn(timestamp, plugin.database)
        self.assertEqual(timestamp, plugin.timestamp)

    def test_database_name_is_unique(self):
        plugin1 = self.fixture().plugin
        plugin2 = self.fixture().plugin

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
        plugin = self.fixture().plugin

        with plugin:
            self.check_psql_default_database(plugin.database)

    def test_database_dropped_after_block(self):
        plugin = self.fixture().plugin

        with plugin:
            pass

        self.check_database_does_not_exist(plugin.database)

    def test_environment_variable_restored(self):
        orig_environ = os.environ.copy()

        with self.fixture().plugin:
            pass

        self.assertDictEqual(orig_environ, os.environ.copy())

    def test_option_keep_database_database_remains_available(self):
        f = fixtures.PluginContext(
            '''\
            Postgres:
                keep database: True
            ''')

        try:
            with f.plugin:
                self.check_psql_default_database(f.plugin.database)

            self.check_database_exists(f.plugin.database)
        finally:
            external_process.run(['dropdb', f.plugin.database])


class Test_EnvironKeyState(unittest.TestCase):

    def test_nonexistent_key(self):
        env = {'a': 1}
        state = plugins._EnvironKeyState(env, 'key')
        env['key'] = 'create'

        state.restore()

        self.assertEqual({'a': 1}, env)

    def test_nonexistent_key_not_changed(self):
        env = {'a': 1}
        state = plugins._EnvironKeyState(env, 'key')

        state.restore()

        self.assertEqual({'a': 1}, env)

    def test_overwritten_key(self):
        env = {'a': 1, 'key': 'value'}
        state = plugins._EnvironKeyState(env, 'key')
        env['key'] = 'another value'

        state.restore()

        self.assertEqual({'a': 1, 'key': 'value'}, env)

    def test_deleted_key_restored(self):
        env = {'a': 1, 'key': 'value'}
        state = plugins._EnvironKeyState(env, 'key')
        del env['key']

        state.restore()

        self.assertEqual({'a': 1, 'key': 'value'}, env)


class TestExecute(unittest.TestCase):

    @within_temp_dir
    def test_python_script_executed(self):
        wd = fspath.working_directory()
        (wd / 'script.py').content = (
            '''open('output', 'w').write('hello from python')''')

        f = fixtures.PluginContext(
            '''\
            Execute:
                python script.py
            ''')

        with f.plugin:
            pass

        self.assertEqual(
            'hello from python',
            (wd / 'output').content.rstrip())

    @within_temp_dir
    def test_nonzero_exit_status_is_an_error(self):
        f = fixtures.PluginContext(
            '''\
            Execute:
                exit 1
            ''')

        with self.assertRaises(exceptions.ScriptError):
            f.plugin.__enter__()

    @within_temp_dir
    def test_python_script_not_found_is_an_error(self):
        f = fixtures.PluginContext(
            '''\
            Execute:
                python this_script_does_not_exist.py
            ''')

        with self.assertRaises(exceptions.ScriptError):
            f.plugin.__enter__()

    @within_temp_dir
    def test_short_inline_shell_script_executed(self):
        wd = fspath.working_directory()
        (wd / 'script').content = 'echo hello from /bin/sh > output'

        f = fixtures.PluginContext(
            '''\
            Execute:
                chmod +x script; ./script
            ''')

        with f.plugin:
            pass

        self.assertEqual(
            'hello from /bin/sh',
            (wd / 'output').content.rstrip())
