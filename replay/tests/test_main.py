import unittest
TODO = unittest.skip('not implemented yet')
import replay.main as m
import os.path

import mock
from temp_dir import within_temp_dir
import pkg_resources
from externals.fspath import working_directory

from replay import plugins
from replay import exceptions
from replay.tests import fixtures


class Test_parse_args(unittest.TestCase):

    def test_defaults(self):
        args = m.parse_args(['dir/scriptname.py'])

        self.assertEqual(working_directory().path, args.datastore)

        self.assertEqual(
            m.TEMPORARY_DIRECTORY,
            args.script_working_directory)

        self.assertEqual(
            m.get_virtualenv_parent_dir(),
            args.virtualenv_parent_directory)

    def test_absolute_script_path(self):
        args = m.parse_args(['/absolute/script/path/scriptname.py'])

        self.assertEqual(
            '/absolute/script/path/scriptname.py',
            args.script_path)

    def test_relative_script_path(self):
        args = m.parse_args(['relative/script/path/scriptname.py'])

        self.assertEqual(
            (working_directory() / 'relative/script/path/scriptname.py').path,
            args.script_path)


class Test_get_virtualenv_parent_dir(unittest.TestCase):

    def test_value_of_WORKON_HOME_is_returned(self):
        environ = {'WORKON_HOME': '/virtualenvs'}
        with mock.patch('os.environ', environ):
            self.assertEqual('/virtualenvs', m.get_virtualenv_parent_dir())

    def test_WORKON_HOME_is_unset_user_home_dot_virtualenvs_is_returned(self):
        def expanduser(arg):
            self.assertEqual('~', arg)
            return '/test/user/home'
        patch_expanduser = mock.patch('os.path.expanduser', expanduser)
        patch_environ = mock.patch('os.environ', {})
        with patch_expanduser, patch_environ:
            self.assertEqual(
                '/test/user/home/.virtualenvs',
                m.get_virtualenv_parent_dir())


class Test_run_with(unittest.TestCase):

    PLUGINS = (
        plugins.WorkingDirectory,
        plugins.CopyScript,
        plugins.Inputs,
        plugins.Outputs,
        plugins.PythonDependencies,
        plugins.Execute
        )

    @staticmethod
    def get_plugin(n, call_trace):
        class TPlugin(plugins.Plugin):

            def __enter__(self):
                call_trace.append((n, '__enter__'))

            def __exit__(self, *args, **kwargs):
                call_trace.append((n, '__exit__'))

        return TPlugin

    @within_temp_dir
    def test_all_plugins_are_run_in_order(self):
        call_trace = []
        setup_plugins = (
            self.get_plugin(1, call_trace),
            self.get_plugin(2, call_trace),
            self.get_plugin(3, call_trace))

        f = fixtures.Runner(
            '''\
            script: scripts/import_roman.py
            ''')
        f.run_with(setup_plugins)

        self.assertEqual(
            [
                (1, '__enter__'),
                (2, '__enter__'),
                (3, '__enter__'),
                (3, '__exit__'),
                (2, '__exit__'),
                (1, '__exit__')
            ],
            call_trace)

    @within_temp_dir
    def test_script_is_run_in_context_specified_directory(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - working_directory : /

            script: scripts/getcwd.py
            ''')

        f.run_with(self.PLUGINS)

        self.assertEqual(
            os.path.normpath(f.context.working_directory.path),
            os.path.normpath(f.datastore.content))

    @within_temp_dir
    def test_nonzero_exit_status_is_an_error(self):
        f = fixtures.Runner(
            '''\
            script: scripts/this_script_does_not_exist_should_cause_an_error.py
            ''')

        with self.assertRaises(exceptions.ScriptError):
            f.run_with(self.PLUGINS)

    @within_temp_dir
    def test_script_dependencies_are_available(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0

            script: scripts/import_roman.py
            ''')

        f.run_with(self.PLUGINS)

    @within_temp_dir
    def test_input_files_are_available_to_script(self):
        f = fixtures.Runner(
            '''\
            inputs:
                - file1: data1
                - file2: deeper/data2

            script: scripts/check_inputs.py
            ''')

        (f.datastore / 'data1').content = 'OK'
        (f.datastore / 'deeper/data2').content = 'exists, too'

        f.run_with(self.PLUGINS)

    @within_temp_dir
    def test_generated_output_files_are_uploaded_to_datastore(self):
        f = fixtures.Runner(
            '''\
            inputs:
                - file: data

            outputs:
                - file: data-copy
                - file: another-copy
            ''')

        (f.datastore / 'data').content = 'content'

        f.run_with(self.PLUGINS)

        self.assertEqual('content', (f.datastore / 'data-copy').content)
        self.assertEqual('content', (f.datastore / 'another-copy').content)


class Test_main(unittest.TestCase):

    @within_temp_dir
    def test_run_with_defaults(self):
        to_roman_script = pkg_resources.resource_filename(
            'replay',
            'tests/fixtures/scripts/to_roman.script')
        ds = working_directory()

        (ds / 'arab').content = '23'

        with mock.patch('sys.argv', ['replay', to_roman_script]):
            m.main()

        self.assertEqual('XXIII', (ds / 'roman').content)

    @within_temp_dir
    def test_run_with_explicit_working_directory(self):
        getcwd_script = pkg_resources.resource_filename(
            'replay',
            'tests/fixtures/scripts/getcwd.script')
        ds = working_directory() / 'datastore'
        wd = working_directory() / 'script_working_directory'

        command = [
            'replay',
            '--script-working-directory=' + wd.path,
            '--datastore=' + ds.path,
            getcwd_script]
        with mock.patch('sys.argv', command):
            m.main()

        self.assertEqual(wd.path, (ds / 'working_directory').content)
