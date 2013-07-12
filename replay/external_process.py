import subprocess

PIPE = subprocess.PIPE


class Result(object):

    def __init__(self, status, stdout, stderr):
        self.status = status
        self.stdout = stdout
        self.stderr = stderr


def run(args_list, env=None, cwd=None):
    process = subprocess.Popen(
        args_list, env=env, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    process.stdin.close()
    process.wait()
    result = Result(
        status=process.returncode,
        stdout=process.stdout.read(),
        stderr=process.stderr.read(),
        )

    return result
