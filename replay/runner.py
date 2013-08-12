import os
import re
from replay import exceptions
import external_process


class Context(object):

    datastore = None  # External
    virtualenv_parent_dir = str
    index_server_url = str
    working_directory = None  # External | TEMPORARY_DIRECTORY

    def __init__(
            self,
            datastore,
            virtualenv_parent_dir,
            working_directory,
            index_server_url=None):
        self.datastore = datastore
        self.virtualenv_parent_dir = virtualenv_parent_dir
        self.working_directory = working_directory
        self.index_server_url = index_server_url


RE_SCRIPT_NAME = re.compile('^[a-z][a-z0-9_]*$', re.IGNORECASE)


class Runner(object):

    '''I run scripts in isolation'''

    def __init__(self, context, script, script_name):
        self.context = context
        self.script = script
        if not RE_SCRIPT_NAME.match(script_name):
            raise exceptions.InvalidScriptName(script_name)
        self.script_name = script_name

    def _run_executable(self):
        if self.script.executable_name:
            executable_script = os.path.join(
                self.script.dir,
                self.script.executable_name)

            result = external_process.run(['python', executable_script])
            if result.status != 0:
                raise exceptions.ScriptError(result)

    def run_with(self, setup_plugins):
        if setup_plugins:
            plugin = setup_plugins[0](self)
            with plugin:
                self.run_with(setup_plugins[1:])
        else:
            self._run_executable()
