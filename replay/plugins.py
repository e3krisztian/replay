import abc
import external_process
import shutil
import os
from replay import exceptions
import getpass
import datetime
import tempfile
from externals import fspath
import hashlib
import logging


log = logging.getLogger(__name__)


class Plugin(object):

    '''I am a context manager, I can perform setup tasks \
    and also provide cleanup.

    My operation is usually driven by one of context & script
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, context, script):
        self.context = context
        self.script = script

    @abc.abstractmethod
    def __enter__(self):  # pragma: nocover
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        log.debug('%s: __exit__', self.__class__.__name__)


class _WorkingDirectoryPlugin(Plugin):

    '''I am a base class helping to implement real Plugins \
    that ensure that the scripts run in a clean directory, \
    and also clean up after them.
    '''

    def __init__(self, context):
        super(_WorkingDirectoryPlugin, self).__init__(context, script=None)
        self.original_working_directory = os.getcwd()
        self.working_directory = None

    def __exit__(self, exc_type, exc_value, traceback):
        log.debug('%s: __exit__', self.__class__.__name__)
        try:
            self._change_to_directory(self.original_working_directory)
        finally:
            log.debug(
                '%s: rmtree %s',
                self.__class__.__name__,
                self.working_directory)
            shutil.rmtree(self.working_directory)

    def _change_to_directory(self, directory):
        log.debug('%s: chdir %s', self.__class__.__name__, directory)
        os.chdir(directory)


class WorkingDirectory(_WorkingDirectoryPlugin):

    '''I ensure that the scripts run in a clean directory, \
    and also clean up after them.

    The directory to run in is taken from the context.
    '''

    def __enter__(self):
        log.debug('WorkingDirectory: __enter__')
        self.working_directory = self.context.working_directory.path
        os.makedirs(self.working_directory)
        self._change_to_directory(self.working_directory)


class TemporaryDirectory(_WorkingDirectoryPlugin):

    '''I ensure that the scripts run in a clean directory, \
    and also clean up after them.

    The directory to run in is a new temporary directory.
    '''

    def __enter__(self):
        log.debug('TemporaryDirectory: __enter__')
        self.working_directory = tempfile.mkdtemp()
        self._change_to_directory(self.working_directory)


class CopyScript(Plugin):

    '''I copy the scripts to the working directory for execution there

    I am pretty special, in a way, that I must immediately follow either of
    WorkingDirectory or TemporaryDirectory in the plugin list.
    '''

    def __init__(self, script_dir):
        super(CopyScript, self).__init__(context=None, script=None)
        self.script_dir = script_dir

    def __enter__(self):
        source = self.script_dir
        destination = os.getcwd()
        log.debug('CopyScript: %s -> %s', source, destination)
        self._copy_tree(source, destination)

    def _copy_tree(self, source, destination):
        for child in os.listdir(source):
            s = os.path.join(source, child)
            d = os.path.join(destination, child)
            if os.path.isdir(s):
                log.debug('CopyScript: mkdir %s', d)
                os.mkdir(d)
                self._copy_tree(s, d)
            else:
                log.debug('CopyScript: cp %s %s', s, d)
                shutil.copy2(s, d)


class _DataStorePlugin(Plugin):

    def _file_pairs(self, copy_spec):
        datastore = self.context.datastore
        working_directory = fspath.working_directory()

        for spec in copy_spec:
            for local_file, ds_file in spec.iteritems():
                yield (working_directory / local_file), (datastore / ds_file)


class Inputs(_DataStorePlugin):

    '''I ensure that inputs are available from DataStore and outputs are saved.
    '''

    def __enter__(self):
        self._check_inputs()
        self._download_inputs()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _input_file_pairs(self):
        return self._file_pairs(self.script)

    def _check_inputs(self):
        for local, datastore in self._input_file_pairs():
            if not datastore.exists():
                raise exceptions.MissingInput(datastore)

    def _download_inputs(self):
        for local, datastore in self._input_file_pairs():
            datastore.copy_to(local)


class Outputs(_DataStorePlugin):

    '''I ensure outputs are saved to DataStore.
    '''

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self._check_outputs()
        self._upload_outputs()

    def _output_file_pairs(self):
        return self._file_pairs(self.script)

    def _check_outputs(self):
        for local, datastore in self._output_file_pairs():
            if not local.exists():
                raise exceptions.MissingOutput(local)

    def _upload_outputs(self):
        for local, datastore in self._output_file_pairs():
            local.copy_to(datastore)


class _EnvironKeyState(object):

    def __init__(self, environ, key):
        self.key = key
        self.missing = key not in environ
        self.value = environ.get(key)

    def restore(self, environ):
        key = self.key
        if self.missing:
            if key in environ:
                del environ[key]
        else:
            environ[key] = self.value


class PythonDependencies(Plugin):

    def __init__(self, context, script):
        super(PythonDependencies, self).__init__(context, script)
        self.python_dependencies = self.script or []
        self.virtualenv_name = '_replay_' + self._package_hash()
        self.virtualenv_dir = (
            self.context.virtualenv_parent_dir / self.virtualenv_name)
        self.PATH = _EnvironKeyState(os.environ, 'PATH')

    def __enter__(self):
        venv_bin = (self.virtualenv_dir / 'bin').path
        path = venv_bin + os.pathsep + os.environ.get('PATH', '')
        os.environ['PATH'] = path
        if not self.virtualenv_dir.exists():
            self._make_virtualenv()

    def __exit__(self, exc_type, exc_value, traceback):
        self.PATH.restore(os.environ)

    def _package_hash(self):
        dependencies = '\n'.join(sorted(self.python_dependencies))
        return hashlib.md5(dependencies).hexdigest()

    @property
    def index_server_url(self):
        return self.context.index_server_url

    def _install_package(self, package_spec, index_server_url):
        cmdspec = (
            ['pip', 'install']
            + (['--index-url=' + index_server_url] if index_server_url else [])
            + [package_spec])

        result = external_process.run(cmdspec)
        if result.status != 0:
            raise exceptions.MissingPythonDependency(result)

    def _make_virtualenv(self):
        # potential enhancements:
        #  - clean environment from behavior changing settings
        #    (e.g. PYTHON_VIRTUALENV)
        #  - specify python interpreter to use (python 2 / 3 / pypy / ...)
        external_process.run(['virtualenv', self.virtualenv_dir.path])
        python_dependencies = self.python_dependencies
        for package_spec in python_dependencies:
            self._install_package(package_spec, self.index_server_url)


class Postgres(Plugin):

    def __init__(self, context, script):
        super(Postgres, self).__init__(context, script)
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.keep_database = script.get('keep database', False)
        self.script_name = script.get('script name', 'SCRIPT_NAME')
        self.PGDATABASE = None

    @property
    def database(self):
        return '{user}_{script_name}_{timestamp}'.format(
            user=getpass.getuser(),
            script_name=self.script_name,
            timestamp=self.timestamp)

    def __enter__(self):
        self.PGDATABASE = _EnvironKeyState(os.environ, 'PGDATABASE')
        os.environ['PGDATABASE'] = self.database
        external_process.run(['createdb', self.database])

    def __exit__(self, exc_type, exc_value, traceback):
        self.PGDATABASE.restore(os.environ)
        if not self.keep_database:
            external_process.run(['dropdb', self.database])


class Execute(Plugin):

    def __enter__(self):
        command = ['python', self.script]
        result = external_process.run(command)
        if result.status != 0:
            raise exceptions.ScriptError(result)
