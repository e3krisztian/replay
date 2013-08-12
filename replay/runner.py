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


class Runner(object):

    '''I run scripts in isolation'''

    def __init__(self, context, script):
        self.context = context
        self.script = script
        self.script_name = script.name

    def run_with(self, setup_plugins):
        if setup_plugins:
            plugin = setup_plugins[0](self)
            with plugin:
                self.run_with(setup_plugins[1:])
