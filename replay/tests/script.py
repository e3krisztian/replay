from StringIO import StringIO

import replay.script


def script_from(string, dir=None, name=None):
    return replay.script.Script(StringIO(string))
