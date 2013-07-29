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
