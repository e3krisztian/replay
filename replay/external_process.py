import subprocess


PIPE = subprocess.PIPE


class Result(object):

    def __init__(self, cmdspec, status, stdout, stderr):
        self.cmdspec = cmdspec
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        def indent(text):
            indent = u' ' * 2
            return indent + (u'\n' + indent).join(text.splitlines())

        def fragments():
            yield u'Command execution result'
            if self.cmdspec:
                yield u'COMMAND:'
                yield indent(str(self.cmdspec))
            yield u'STATUS:'
            yield indent(str(self.status))
            if self.stdout:
                yield u'STDOUT:'
                yield indent(self.stdout.decode('utf8'))
            if self.stderr:
                yield u'STDERR:'
                yield indent(self.stderr.decode('utf8'))
        return u'\n'.join(fragments())


def run(args_list, env=None, cwd=None):
    process = subprocess.Popen(
        args_list, env=env, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    process.stdin.close()
    process.wait()
    result = Result(
        cmdspec=tuple(args_list),
        status=process.returncode,
        stdout=process.stdout.read(),
        stderr=process.stderr.read(),
        )

    return result
