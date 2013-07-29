import unittest
TODO = unittest.skip('not implemented yet')
from replay import plugins
import replay.runner as m

from replay.tests import fixtures
from replay.tests.script import script_from

import os.path
from replay import exceptions
from temp_dir import within_temp_dir


class Test_Context(unittest.TestCase):

    def test_datastore_defaults_to_current_working_directory(self):
        self.assertEqual(os.getcwd(), m.Context().datastore.path)

    def test_virtualenv_parent_dir_defaults_to_dot_virtualenvs(self):
        default = os.path.join(os.getcwd(), '.virtualenvs')
        self.assertEqual(default, m.Context().virtualenv_parent_dir.path)

    def test_working_directory_defaults_to_temp_in_current_directory(self):
        self.assertEqual(
            os.path.join(os.getcwd(), 'temp'),
            m.Context().working_directory.path)


class Test_Runner(unittest.TestCase):

    def test_minimal_construction(self):
        m.Runner(m.Context(), script_from('{}'), 'minimal')

    def test_invalid_script_name(self):
        with self.assertRaises(exceptions.InvalidScriptName):
            m.Runner(m.Context(), script_from('{}'), 'm inimal')


class Test_Runner_run_in_virtualenv(unittest.TestCase):

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
            result = f.runner.run_in_virtualenv(cmdspec)

        # if result.status: print(result)
        self.assertEqual('XXIII', result.stdout.rstrip())


class Test_Runner_run(unittest.TestCase):

    @within_temp_dir
    def test_script_is_run_in_context_specified_directory(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - working_directory : /

            script: scripts/getcwd.py
            ''')

        f.runner.run()

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
            f.runner.run()

    @within_temp_dir
    def test_script_dependencies_are_available(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0

            script: scripts/import_roman.py
            ''')

        f.runner.run()

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

        f.runner.run()

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

        f.runner.run()

        self.assertEqual('content', (f.datastore / 'data-copy').content)
        self.assertEqual('content', (f.datastore / 'another-copy').content)


class Test_Runner_virtualenv_name(unittest.TestCase):

    @TODO
    def test_virtualenv_name_of_scripts_without_required_packages(self):
        pass

    @TODO
    def test_virtualenv_name_depends_on_required_python_packages(self):
        pass


# refactor Runner - add plugin interface & move actions into plugins
#
# REQ:
# - plugins' before_execute should be run in requested order
# - after_execute actions are run in reverse order of registration
# - after_execute actions are run even if there is an exception in
#   - before_execute of another plugin
#   - while running the executable
#   - in an after_execute action
# - the executable is not run if there is an exception in a plugin's .before_execute
# - after_execute is run only for those plugins whose before_execute action was run
