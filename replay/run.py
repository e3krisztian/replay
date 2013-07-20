import os
from externals import fspath
from replay import exceptions
import external_process
from temp_dir import in_temp_dir


class Context(object):

    datastore = None  # External
    virtualenv_parent_dir = str
    index_server_url = str

    def __init__(
            self,
            datastore=None,
            virtualenv_parent_dir=None,
            index_server_url=None):
        wd = fspath.working_directory()
        self.datastore = datastore or wd
        if virtualenv_parent_dir:
            self.virtualenv_parent_dir = virtualenv_parent_dir
        else:
            self.virtualenv_parent_dir = wd / '.virtualenvs'
        self.index_server_url = index_server_url


class Runner(object):

    '''I run scripts in isolation'''

    def __init__(self, context, script):
        self.context = context
        self.script = script
        self.virtualenv_name = '_replay_venv'

    @property
    def virtualenv_dir(self):
        return self.context.virtualenv_parent_dir / self.virtualenv_name

    def check_inputs(self):
        datastore = self.context.datastore
        for input_spec in self.script.inputs:
            ds_file, = input_spec.values()
            if not (datastore / ds_file).is_file():
                raise exceptions.MissingInput(ds_file)

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

    def upload_outputs(self):
        datastore = self.context.datastore
        working_directory = fspath.working_directory()
        for output_spec in self.script.outputs:
            for local_file, ds_file in output_spec.iteritems():
                (working_directory / local_file).copy_to(datastore / ds_file)

    def run(self):
        executable_script = os.path.join(
            self.script.dir,
            self.script.executable_name)

        with in_temp_dir():
            self.make_virtualenv()
            result = self.run_in_virtualenv(['python', executable_script])
            if result.status != 0:
                raise exceptions.ScriptError(result)
            self.upload_outputs()
