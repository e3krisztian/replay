import unittest
TODO = unittest.skip('not implemented yet')
from replay import external_process
import replay.runner as m
from replay.tests import fixtures

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


class Test_Runner_check_inputs(unittest.TestCase):

    def test_input_file_missing_is_error(self):
        f = fixtures.Runner(
            '''\
            inputs:
                - missing: missing
            ''')

        with self.assertRaises(exceptions.MissingInput):
            f.runner.check_inputs()

    def test_inputs_are_there_proceeds(self):
        f = fixtures.Runner(
            '''\
            inputs:
                - existing: somewhere/existing file
            ''')
        (f.datastore / 'somewhere' / 'existing file').content = 'some content'

        f.runner.check_inputs()


class Test_Runner_make_virtualenv(unittest.TestCase):

    @within_temp_dir
    def test_virtualenv_is_created_in_context_specified_dir(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
            ''')
        virtualenv_parent_dir = f.context.virtualenv_parent_dir

        f.runner.make_virtualenv()

        virtualenv_dir = virtualenv_parent_dir / f.runner.virtualenv_name
        self.assertTrue(virtualenv_dir.is_dir())

    @within_temp_dir
    def test_virtualenv_already_exists_no_error(self):
        f = fixtures.Runner(
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
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0
            ''')
        f.runner.make_virtualenv()

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
            f.runner.make_virtualenv()


class Test_Runner_run_in_virtualenv(unittest.TestCase):

    @within_temp_dir
    def test_module_in_virtualenv_is_available(self):
        f = fixtures.Runner(
            '''\
            python dependencies:
                - roman==2.0.0
            ''')
        f.runner.make_virtualenv()

        # verify, that we can import the required "roman" module
        cmdspec = [
            'python', '-c', 'import roman; print(roman.toRoman(23))']
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


class Test_Runner_script_options(unittest.TestCase):

    @TODO
    def test_uses_psql_adds_setup_action(self):
        pass

    @TODO
    def test_uses_psql_adds_cleanup_action(self):
        pass

    @TODO
    def test_keep_database_no_cleanup_action_is_added(self):
        pass


class Test_setup_psql(unittest.TestCase):

    # @skip_if_not_safe_to_drop_db
    # # - to prevent dropping a user's database by accident
    @TODO
    def test_env_REPLAY_DROP_DB_missing_is_an_error(self):
        pass

    # @skip_if_not_safe_to_drop_db
    # # - to prevent dropping a user's database by accident
    @TODO
    def test_env_REPLAY_DROP_DB_present_user_database_recreated(self):
        pass


class Test_cleanup_psql(unittest.TestCase):

    # @skip_if_not_safe_to_drop_db
    # # - to prevent dropping a user's database by accident
    @TODO
    def test_env_REPLAY_DROP_DB_missing_is_an_error(self):
        pass

    # @skip_if_not_safe_to_drop_db
    # # - to prevent dropping a user's database by accident
    @TODO
    def test_env_REPLAY_DROP_DB_present_user_database_dropped(self):
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


# plugins:
#   working directory:  (temporary? ramdisk? how to configure? - runner.context.script_working_directory)
#       before_execute: create & enter script working directory
#       after_execute: restore directory, remove script working directory
#   datastore:  (runner.context.datastore)
#       before_execute: copy inputs from datastore
#       after_execute: copy outputs to datastore
#   virtualenv:
#       before_execute: if not already exists create new virtualenv & install requirements
#       after_execute: NOOP
#   postgresql:  (database name {USER}_{script_name}_{datetime})
#       before_execute: create database
#       after_execute: drop database (unless debugging & explicitly requested)
#     NOTE:
#           runner should store script_name
#           should tests be configurable to run/not run database tests?
