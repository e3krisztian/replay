import os
from externals import fspath
from replay import exceptions
import external_process
from replay import plugins


class Context(object):

    datastore = None  # External
    virtualenv_parent_dir = str
    index_server_url = str
    working_directory = None  # External

    def __init__(
            self,
            datastore=None,
            virtualenv_parent_dir=None,
            index_server_url=None,
            working_directory=None):
        wd = fspath.working_directory()
        self.datastore = datastore or wd
        if virtualenv_parent_dir:
            self.virtualenv_parent_dir = virtualenv_parent_dir
        else:
            self.virtualenv_parent_dir = wd / '.virtualenvs'
        self.index_server_url = index_server_url
        self.working_directory = working_directory or (wd / 'temp')


class Runner(object):

    '''I run scripts in isolation'''

    def __init__(self, context, script):
        self.context = context
        self.script = script
        self.virtualenv_name = '_replay_venv'

    @property
    def virtualenv_dir(self):
        return self.context.virtualenv_parent_dir / self.virtualenv_name

    def run_in_virtualenv(self, cmdspec):
        venv_bin = (self.virtualenv_dir / 'bin').path
        path = venv_bin + os.pathsep + os.environ.get('PATH', '')
        env = dict(os.environ, PATH=path)
        return external_process.run(cmdspec, env=env)

    def install_package(self, package_spec, index_server_url):
        cmdspec = (
            ['pip', 'install']
            + (['--index-url=' + index_server_url] if index_server_url else [])
            + [package_spec])
        result = self.run_in_virtualenv(cmdspec)
        if result.status != 0:
            raise exceptions.MissingPythonDependency(result)

    def make_virtualenv(self):
        # potential enhancements:
        #  - clean environment from behavior changing settings
        #    (e.g. PYTHON_VIRTUALENV)
        #  - specify python interpreter to use (python 2 / 3 / pypy / ...)
        if self.virtualenv_dir.is_dir():
            return

        external_process.run(['virtualenv', self.virtualenv_dir.path])
        for package_spec in self.script.python_dependencies:
            self.install_package(package_spec, self.context.index_server_url)

    def _run_executable(self):
        if self.script.executable_name:
            self.make_virtualenv()

            executable_script = os.path.join(
                self.script.dir,
                self.script.executable_name)

            result = self.run_in_virtualenv(['python', executable_script])
            if result.status != 0:
                raise exceptions.ScriptError(result)

    def run(self):
        wdp = plugins.WorkingDirectory(self)
        wdp.before_execute()

        dsp = plugins.DataStore(self)
        dsp.before_execute()

        self._run_executable()

        dsp.after_execute()
        wdp.after_execute()
