import unittest
from temp_dir import within_temp_dir
from replay.tests import fixtures

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

        plugin = plugins.DataStore(f.runner)

        with self.assertRaises(exceptions.MissingInput):
            plugin.before_execute()

    @within_temp_dir
    def test_outputs_are_uploaded_to_datastore(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - an output file: /output/datastore/path
            ''')
        (f.context.working_directory / 'an output file').content = 'data'

        plugin = plugins.DataStore(f.runner)
        plugin.after_execute()

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

        plugin = plugins.DataStore(f.runner)

        with self.assertRaises(exceptions.MissingOutput):
            plugin.after_execute()
