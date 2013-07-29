import unittest
from temp_dir import within_temp_dir
from replay.tests import fixtures

from replay import plugins


class TestDataStore(unittest.TestCase):

    @within_temp_dir
    def test_outputs_are_uploaded_to_datastore(self):
        f = fixtures.Runner(
            '''\
            outputs:
                - an output file: /output/datastore/path
            ''')
        (f.context.working_directory / 'an output file').content = 'data'

        plugin = plugins.DataStore()
        plugin.after_execute(f.runner)

        self.assertEqual(
            'data',
            (f.datastore / 'output/datastore/path').content)
