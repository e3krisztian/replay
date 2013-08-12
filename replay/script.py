import yaml


class Script(object):

    dir = str
    name = str
    inputs = [{str: str}]
    outputs = [{str: str}]
    executable_name = str
    python_dependencies = [str]

    def __init__(self, dir, name, script_file):
        self._raw_spec = raw_spec = yaml.safe_load(script_file)
        self.dir = dir
        self.name = name
        self.inputs = raw_spec.get('inputs', [])
        self.outputs = raw_spec.get('outputs', [])
        self.executable_name = raw_spec.get('script', '')
        self.python_dependencies = raw_spec.get('python dependencies') or []
        self._options = set(raw_spec.get('options') or {})

    def has_option(self, option):
        return option in self._options
