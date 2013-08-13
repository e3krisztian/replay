from externals.fake import Fake as MemoryStore
from replay import context
import pkg_resources
from replay.tests.path2url import path2url
from externals.fspath import working_directory
import os.path


class PluginContext(object):

    '''I hold a context and a datastore. The context is set up in a way,
    that by removing the current working directory no residue remains.
    '''

    def __init__(self, script=None):
        venv_parent_dir = working_directory() / 'replay_virtualenvs'

        self.datastore = MemoryStore()
        self.context = context.Context(
            self.datastore,
            venv_parent_dir,
            working_directory() / 'temp',
            self._local_pypi_url)
        if script:
            self.plugin = list(self.context.load_plugins(script))[0]

    @property
    def _local_pypi_url(self):
        index_server_dir = pkg_resources.resource_filename(
            'replay', 'tests/fixtures/pypi/simple')
        assert os.path.isdir(index_server_dir), index_server_dir
        index_server_url = path2url(index_server_dir)

        return index_server_url
