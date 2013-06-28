import unittest
import replay.datastore as m
from temp_dir import within_temp_dir, in_temp_dir


class Test_WorkingDirectoryFileDataStore(unittest.TestCase):

    @within_temp_dir
    def test_file_upload(self):
        ds = m.WorkingDirectoryFileDataStore()
        with in_temp_dir():
            # create a file and upload it
            xf1 = externals.working_directory() / 'f1'
            xf1.set_content('tempfile1')
            ds.upload('./tempfile1', 'a/b')
            ds.upload('./tempfile1', 'another_ds_path')
