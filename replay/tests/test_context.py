import unittest
from replay.tests import fixtures
from replay import plugins


class Test_run(unittest.TestCase):

    @staticmethod
    def get_plugin_class(n, call_trace):
        class TPlugin(plugins.Plugin):

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
        plugins = f.context.load_plugins(plugin_classes, f.script)
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


class Test_resolve_plugin_class(unittest.TestCase):

    @property
    def context(self):
        return fixtures.PluginContext().context

    def test_resolve_by_dotted_name(self):
        plugin_name = 'replay.tests.test_context.XPlugin'

        plugin_class = self.context.resolve_plugin_class(plugin_name)
        self.assertIs(XPlugin, plugin_class)

    def test_nonexistent_plugin_raises_ImportError(self):
        plugin_name = 'replay.tests.test_context.NONEXISTENTPlugin'

        with self.assertRaises(ImportError):
            self.context.resolve_plugin_class(plugin_name)

    def test_non_class_raises_ValueError(self):
        plugin_name = 'replay.tests.test_context.plugins'

        with self.assertRaises(ValueError):
            self.context.resolve_plugin_class(plugin_name)

    def test_non_plugin_raises_ValueError(self):
        plugin_name = '{}.{}'.format(
            self.__module__,
            self.__class__.__name__)

        with self.assertRaises(ValueError):
            self.context.resolve_plugin_class(plugin_name)

    def test_unqualified_plugin_resolved(self):
        plugin_class = self.context.resolve_plugin_class('Execute')
        self.assertIs(plugins.Execute, plugin_class)
