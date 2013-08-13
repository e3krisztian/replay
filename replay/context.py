import inspect

import yaml
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

    def load_plugins(self, script_file):
        try:
            for raw_spec in yaml.load_all(script_file, Loader=yaml.SafeLoader):
                yield self.load_plugin(raw_spec)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(e, 'error in script')

    def load_plugin(self, raw_spec):
        if not isinstance(raw_spec, dict):
            msg = 'script is not a mapping from plugin name to attributes'
            raise ValueError(msg)
        if len(raw_spec) != 1:
            msg = (
                'script contains a plugin spec with multiple keys: '
                + repr(raw_spec.keys()))
            raise ValueError(msg)
        plugin_name, = raw_spec.keys()
        plugin_class = self.resolve_plugin_class(plugin_name)
        return plugin_class(self, raw_spec[plugin_name])

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

    def run(self, plugins):
        '''I run scripts in isolation'''

        if plugins:
            with plugins[0]:
                self.run(plugins[1:])
