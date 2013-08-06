import argparse
from externals import fspath
import os.path
import sys
import replay.runner
import replay.script
from temp_dir import in_temp_dir


MAKE_TEMPORARY_DIRECTORY = object()


def get_virtualenv_parent_dir():
    if 'WORKON_HOME' in os.environ:
        return os.environ['WORKON_HOME']

    user_home = os.path.expanduser('~')
    return os.path.join(user_home, '.virtualenvs')


def parse_args(args):
    parser = argparse.ArgumentParser()

    # optional parameters, with defaults
    parser.add_argument(
        '--datastore',
        '--ds',
        default=fspath.working_directory().path,
        help='Persistent place for data (default: %(default)s)')

    parser.add_argument(
        '--script-working-directory',
        '--dir',
        default=MAKE_TEMPORARY_DIRECTORY,
        help='Run script[s] under this directory - somewhere'
        ' (default: NEW TEMPORARY DIRECTORY)')

    parser.add_argument(
        '--virtualenv-parent-directory',
        '--venvs',
        default=get_virtualenv_parent_dir(),
        help='Use this directory to cache python virtual environments'
        ' (default: %(default)s)')

    # mandatory parameter
    parser.add_argument(
        'script_path',
        help='Script to run')

    args = parser.parse_args(args)

    # fix script_path
    args.script_path = fspath.FsPath(args.script_path).path

    return args


def run(working_directory, args):
    context = replay.runner.Context(
        fspath.FsPath(args.datastore),
        fspath.FsPath(args.virtualenv_parent_directory),
        fspath.FsPath(working_directory))

    script_path = fspath.FsPath(args.script_path)
    script_dir = script_path.parent().path
    with open(args.script_path) as script_file:
        script = replay.script.Script(script_dir, script_file)
    script_name, _ = os.path.splitext(script_path.name)

    runner = replay.runner.Runner(context, script, script_name)
    runner.run()


def main():
    args = parse_args(sys.argv[1:])
    if args.script_working_directory is MAKE_TEMPORARY_DIRECTORY:
        with in_temp_dir():
            run((fspath.working_directory() / 'temp').path, args)
    else:
        run(args.script_working_directory, args)


if __name__ == '__main__':
    main()  # pragma: nocover
