import shutil
import os
from replay import exceptions


class Plugin(object):

    '''I can perform setup tasks and also provide cleanup for Runner

    My operation is usually driven by runner.context & runner.script
    '''

    def before_execute(self, runner):
        pass

    def after_execute(self, runner):
        pass


class WorkingDirectory(Plugin):

    '''I ensure that the scripts run in a clean directory, \
    and also clean up after them.
    '''

    def __init__(self):
        self.original_working_directory = '.'

    def before_execute(self, runner):
        working_directory = runner.context.working_directory.path
        os.mkdir(working_directory)
        self.original_working_directory = os.getcwd()
        os.chdir(working_directory)

    def after_execute(self, runner):
        try:
            os.chdir(self.original_working_directory)
        finally:
            shutil.rmtree(runner.context.working_directory.path)


class DataStore(Plugin):

    '''I ensure that inputs are available from DataStore and outputs are saved.
    '''

    def before_execute(self, runner):
        self._check_inputs(runner)
        self._download_inputs(runner)

    def after_execute(self, runner):
        self._check_outputs(runner)
        self._upload_outputs(runner)

    def _file_pairs(self, runner, copy_spec):
        datastore = runner.context.datastore
        working_directory = runner.context.working_directory

        for spec in copy_spec:
            for local_file, ds_file in spec.iteritems():
                yield working_directory / local_file, datastore / ds_file

    def _input_file_pairs(self, runner):
        return self._file_pairs(runner, runner.script.inputs)

    def _output_file_pairs(self, runner):
        return self._file_pairs(runner, runner.script.outputs)

    def _check_inputs(self, runner):
        for local, datastore in self._input_file_pairs(runner):
            if not datastore.exists():
                raise exceptions.MissingInput(datastore)

    def _check_outputs(self, runner):
        for local, datastore in self._output_file_pairs(runner):
            if not local.exists():
                raise exceptions.MissingOutput(local)

    def _download_inputs(self, runner):
        for local, datastore in self._input_file_pairs(runner):
            datastore.copy_to(local)

    def _upload_outputs(self, runner):
        for local, datastore in self._output_file_pairs(runner):
            local.copy_to(datastore)
