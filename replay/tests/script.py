import os.path
from StringIO import StringIO

import replay.script


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def script_from(string, dir=FIXTURES_DIR):
    return replay.script.Script(dir, StringIO(string))