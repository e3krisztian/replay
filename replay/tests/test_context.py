import unittest
from replay.tests import fixtures
from temp_dir import within_temp_dir
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

    @within_temp_dir
    def test_all_plugins_are_run_in_order(self):
        call_trace = []
        plugin_classes = (
            self.get_plugin_class(1, call_trace),
            self.get_plugin_class(2, call_trace),
            self.get_plugin_class(3, call_trace))

        f = fixtures.PluginContext(
            '''\
            script: scripts/import_roman.py
            ''')
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
