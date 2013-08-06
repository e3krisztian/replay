import os
import re
from replay import exceptions
import external_process
from replay import plugins
import hashlib


class Context(object):

    datastore = None  # External
    virtualenv_parent_dir = str
    index_server_url = str
    working_directory = None  # External

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
        self.virtualenv_name = '_replay_' + self._package_hash()
        self.virtualenv_dir = (
            self.context.virtualenv_parent_dir / self.virtualenv_name)

    def _package_hash(self):
        dependencies = '\n'.join(sorted(self.script.python_dependencies))
        return hashlib.md5(dependencies).hexdigest()

    def run_in_virtualenv(self, cmdspec):
        venv_bin = (self.virtualenv_dir / 'bin').path
        path = venv_bin + os.pathsep + os.environ.get('PATH', '')
        env = dict(os.environ, PATH=path)
        return external_process.run(cmdspec, env=env)

    def _run_executable(self):
        if self.script.executable_name:
            executable_script = os.path.join(
                self.script.dir,
                self.script.executable_name)

            result = self.run_in_virtualenv(['python', executable_script])
            if result.status != 0:
                raise exceptions.ScriptError(result)

    def run(self):
        with plugins.WorkingDirectory(self):
            with plugins.DataStore(self):
                with plugins.VirtualEnv(self):
                    self._run_executable()
