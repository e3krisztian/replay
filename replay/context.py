import inspect

import zope.dottedname.resolve as dottedname

from replay import plugins


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

    def load_plugins(self, plugin_classes, script):
        return [plugin_class(self, script) for plugin_class in plugin_classes]

    def run(self, plugins):
        '''I run scripts in isolation'''

        if plugins:
            with plugins[0]:
                self.run(plugins[1:])

    def resolve_plugin_class(self, plugin_name):
        try:
            plugin_class = dottedname.resolve(plugin_name)
        except ImportError as e:
            full_plugin_name = 'replay.plugins.' + plugin_name
            try:
                plugin_class = dottedname.resolve(full_plugin_name)
            except ImportError:
                raise e

        if not (inspect.isclass(plugin_class)
                and issubclass(plugin_class, plugins.Plugin)):
            raise ValueError('{} is not a Plugin'.format(plugin_name))

        return plugin_class
