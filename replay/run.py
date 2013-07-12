from externals import fspath
from replay import exceptions


class Context(object):

    datastore = None  # External
    virtualenv_parent_dir = str

    def __init__(self, datastore=None, virtualenv_parent_dir=None):
        wd = fspath.working_directory()
        self.datastore = datastore or wd
        self.virtualenv_parent_dir = virtualenv_parent_dir or (wd / '.virtualenvs')


class Runner(object):

    '''I run scripts in isolation'''

    def __init__(self, context, script):
        self.context = context
        self.script = script

    def check_inputs(self):
        datastore = self.context.datastore
        for input_spec in self.script.inputs:
            ds_file, = input_spec.values()
            if not (datastore / ds_file).is_file():
                raise exceptions.MissingInput(ds_file)
