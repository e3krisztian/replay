import unittest
from replay.tests.script import script_from
import replay.run as m

import os
from replay import exceptions
from externals.fake import Fake as MemoryStore


class Test_Context(unittest.TestCase):

    @property
    def wd(self):
        return os.getcwd()

    def test_datastore_defaults_to_current_working_directory(self):
        self.assertEqual(self.wd, m.Context().datastore.path)

    def test_virtualenv_parent_dir_defaults_to_dot_virtualenvs(self):
        default = os.path.join(self.wd, '.virtualenvs')
        self.assertEqual(default, m.Context().virtualenv_parent_dir.path)


class Test_Runner_check_inputs(unittest.TestCase):

    def test_input_file_missing_is_error(self):
        script = script_from(
            '''\
            inputs:
                - missing: missing
            ''')
        runner = m.Runner(m.Context(MemoryStore()), script)
        with self.assertRaises(exceptions.MissingInput):
            runner.check_inputs()

    def test_inputs_are_there_proceeds(self):
        script = script_from(
            '''\
            inputs:
                - existing: somewhere/existing file
            ''')
        store = MemoryStore()
        (store / 'somewhere' / 'existing file').content = 'some content'
        runner = m.Runner(m.Context(store), script)

        runner.check_inputs()


class Test_Runner(unittest.TestCase):

    @unittest.skip('unimplemented')
    def test_script_is_run_in_a_different_directory(self):
        pass

    @unittest.skip('unimplemented')
    def test_script_dependencies_are_available(self):
        pass

    @unittest.skip('unimplemented')
    def test_input_files_are_available_to_script(self):
        pass

    @unittest.skip('unimplemented')
    def test_generated_output_files_are_uploaded_to_datastore(self):
        pass


# testing goal: program is exercised
