import unittest
from replay.tests import fixtures
from temp_dir import within_temp_dir
from replay import plugins


class Test_run(unittest.TestCase):

    @staticmethod
    def get_plugin(n, call_trace):
        class TPlugin(plugins.Plugin):

            def __enter__(self):
                call_trace.append((n, '__enter__'))

            def __exit__(self, *args, **kwargs):
                call_trace.append((n, '__exit__'))

        return TPlugin

    @within_temp_dir
    def test_all_plugins_are_run_in_order(self):
        call_trace = []
        setup_plugins = (
            self.get_plugin(1, call_trace),
            self.get_plugin(2, call_trace),
            self.get_plugin(3, call_trace))

        f = fixtures.Runner(
            '''\
            script: scripts/import_roman.py
            ''')
        f.context.run(setup_plugins, f.script)

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
