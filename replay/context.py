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
