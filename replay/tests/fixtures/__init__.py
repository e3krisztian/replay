from replay.tests.fixtures.plugin_context import PluginContext

import os.path


FIXTURES_DIR = os.path.join(os.path.dirname(__file__))

__all__ = ['PluginContext', 'FIXTURES_DIR']
