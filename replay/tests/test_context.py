import unittest
from replay.tests import fixtures
from replay import plugins
from StringIO import StringIO


class Test_run(unittest.TestCase):

    @staticmethod
    def get_plugin_class(n, call_trace):
        class TPlugin(plugins.Plugin):

            def __init__(self):
                super(TPlugin, self).__init__(context=None, script=None)

            def __enter__(self):
                call_trace.append((n, '__enter__'))

            def __exit__(self, *args, **kwargs):
                call_trace.append((n, '__exit__'))

        return TPlugin

    def test_all_plugins_are_run_in_order(self):
        call_trace = []
        plugin_classes = (
            self.get_plugin_class(1, call_trace),
            self.get_plugin_class(2, call_trace),
            self.get_plugin_class(3, call_trace))

        f = fixtures.PluginContext()
        plugins = [plugin_class() for plugin_class in plugin_classes]
        f.context.run(plugins)

        self.assertEqual(
            [
                (1, '__enter__'),
                (2, '__enter__'),
                (3, '__enter__'),
                (3, '__exit__'),
                (2, '__exit__'),
                (1, '__exit__')
            ],
            call_trace)


XPlugin = plugins.Plugin


def context():
    return fixtures.PluginContext().context


class Test_resolve_plugin_class(unittest.TestCase):

    def test_resolve_by_dotted_name(self):
        plugin_name = 'replay.tests.test_context.XPlugin'

        plugin_class = context().resolve_plugin_class(plugin_name)
        self.assertIs(XPlugin, plugin_class)

    def test_nonexistent_plugin_raises_ImportError(self):
        plugin_name = 'replay.tests.test_context.NONEXISTENTPlugin'

        with self.assertRaises(ImportError):
            context().resolve_plugin_class(plugin_name)

    def test_non_class_raises_ValueError(self):
        plugin_name = 'replay.tests.test_context.plugins'

        with self.assertRaises(ValueError):
            context().resolve_plugin_class(plugin_name)

    def test_non_plugin_raises_ValueError(self):
        plugin_name = '{}.{}'.format(
            self.__module__,
            self.__class__.__name__)

        with self.assertRaises(ValueError):
            context().resolve_plugin_class(plugin_name)

    def test_unqualified_plugin_resolved(self):
        plugin_class = context().resolve_plugin_class('Execute')
        self.assertIs(plugins.Execute, plugin_class)


class Test_load_plugin(unittest.TestCase):

    def test_non_map_yaml_raises_ValueError(self):
        with self.assertRaises(ValueError):
            context().load_plugin(['1', '2'])

    def test_non_one_key_map_raises_ValueError(self):
        with self.assertRaises(ValueError):
            context().load_plugin(dict(a='1', b='2'))


class Test_load_plugins(unittest.TestCase):

    def test_executable_content_raises_ValueError(self):
        f = StringIO(
            '''\
            Execute: !!python/object/new:tuple
                [[3, 4]]
            ''')
        with self.assertRaises(ValueError):
            list(context().load_plugins(f))
