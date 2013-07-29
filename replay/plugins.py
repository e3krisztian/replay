import shutil
import os


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

    def _file_pairs(self, runner, copy_spec):
        datastore = runner.context.datastore
        working_directory = runner.context.working_directory

        for spec in copy_spec:
            for local_file, ds_file in spec.iteritems():
                yield working_directory / local_file, datastore / ds_file

    def before_execute(self, runner):
        for local, datastore in self._file_pairs(runner, runner.script.inputs):
            datastore.copy_to(local)

    def after_execute(self, runner):
        for local, datastore in self._file_pairs(runner, runner.script.outputs):
            local.copy_to(datastore)
