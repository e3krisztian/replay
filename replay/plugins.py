import external_process
import shutil
import os
from replay import exceptions


class Plugin(object):

    '''I am a context manager, I can perform setup tasks \
    and also provide cleanup for Runner

    My operation is usually driven by runner.context & runner.script
    '''

    def __init__(self, runner):
        self.runner = runner

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class WorkingDirectory(Plugin):

    '''I ensure that the scripts run in a clean directory, \
    and also clean up after them.
    '''

    def __init__(self, runner):
        super(WorkingDirectory, self).__init__(runner)
        self.context = runner.context
        self.original_working_directory = '.'

    def __enter__(self):
        working_directory = self.context.working_directory.path
        os.mkdir(working_directory)
        self.original_working_directory = os.getcwd()
        os.chdir(working_directory)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            os.chdir(self.original_working_directory)
        finally:
            shutil.rmtree(self.context.working_directory.path)


class DataStore(Plugin):

    '''I ensure that inputs are available from DataStore and outputs are saved.
    '''

    def __enter__(self):
        self._check_inputs()
        self._download_inputs()

    def __exit__(self, exc_type, exc_value, traceback):
        self._check_outputs()
        self._upload_outputs()

    # helpers
    def _file_pairs(self, copy_spec):
        datastore = self.runner.context.datastore
        working_directory = self.runner.context.working_directory

        for spec in copy_spec:
            for local_file, ds_file in spec.iteritems():
                yield (working_directory / local_file), (datastore / ds_file)

    def _input_file_pairs(self):
        return self._file_pairs(self.runner.script.inputs)

    def _output_file_pairs(self):
        return self._file_pairs(self.runner.script.outputs)

    def _check_inputs(self):
        for local, datastore in self._input_file_pairs():
            if not datastore.exists():
                raise exceptions.MissingInput(datastore)

    def _check_outputs(self):
        for local, datastore in self._output_file_pairs():
            if not local.exists():
                raise exceptions.MissingOutput(local)

    def _download_inputs(self):
        for local, datastore in self._input_file_pairs():
            datastore.copy_to(local)

    def _upload_outputs(self):
        for local, datastore in self._output_file_pairs():
            local.copy_to(datastore)


class VirtualEnv(Plugin):

    def __enter__(self):
        if not self.virtualenv_dir.exists():
            self._make_virtualenv()

    @property
    def virtualenv_dir(self):
        return self.runner.virtualenv_dir

    def run_in_virtualenv(self, cmdspec):
        return self.runner.run_in_virtualenv(cmdspec)

    @property
    def index_server_url(self):
        return self.runner.context.index_server_url

    def _install_package(self, package_spec, index_server_url):
        cmdspec = (
            ['pip', 'install']
            + (['--index-url=' + index_server_url] if index_server_url else [])
            + [package_spec])
        result = self.run_in_virtualenv(cmdspec)
        if result.status != 0:
            raise exceptions.MissingPythonDependency(result)

    def _make_virtualenv(self):
        # potential enhancements:
        #  - clean environment from behavior changing settings
        #    (e.g. PYTHON_VIRTUALENV)
        #  - specify python interpreter to use (python 2 / 3 / pypy / ...)
        if self.virtualenv_dir.is_dir():
            return

        external_process.run(['virtualenv', self.virtualenv_dir.path])
        python_dependencies = self.runner.script.python_dependencies
        for package_spec in python_dependencies:
            self._install_package(package_spec, self.index_server_url)
