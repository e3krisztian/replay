from externals.fake import Fake as MemoryStore
from replay import runner
from replay import main
import pkg_resources
from replay.tests.script import script_from
from replay.tests.path2url import path2url
from externals.fspath import working_directory
import os.path


class Runner(object):

    '''I hold a runner and its parts in a way,
    that by removing the current working directory no residue remains.
    '''

    def __init__(self, script):
        venv_parent_dir = working_directory() / 'replay_virtualenvs'

        self.datastore = MemoryStore()
        self.context = runner.Context(
            self.datastore,
            venv_parent_dir,
            working_directory() / 'temp',
            self._local_pypi_url)
        self.script = script_from(script)
        # self.runner = runner.Runner(self.context, self.script)

    def plugin(self, class_):
        return class_(self.context, self.script)

    def run_with(self, setup_plugins):
        main.run_with(setup_plugins, self.context, self.script)

    @property
    def _local_pypi_url(self):
        index_server_dir = pkg_resources.resource_filename(
            'replay', 'tests/fixtures/pypi/simple')
        assert os.path.isdir(index_server_dir), index_server_dir
        index_server_url = path2url(index_server_dir)

        return index_server_url
