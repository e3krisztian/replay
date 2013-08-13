import argparse
from externals import fspath
import os.path
import sys
import replay.context
import replay.script
import replay.plugins


TEMPORARY_DIRECTORY = replay.plugins.TemporaryDirectory


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
        default=TEMPORARY_DIRECTORY,
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


def get_script_working_directory(args):
    if args.script_working_directory is TEMPORARY_DIRECTORY:
        return TEMPORARY_DIRECTORY
    return fspath.FsPath(args.script_working_directory)


def main():
    args = parse_args(sys.argv[1:])

    context = replay.context.Context(
        fspath.FsPath(args.datastore),
        fspath.FsPath(args.virtualenv_parent_directory),
        get_script_working_directory(args))

    script_path = fspath.FsPath(args.script_path)
    script_dir = script_path.parent().path
    script_name, _ = os.path.splitext(script_path.name)
    with open(args.script_path) as script_file:
        script = replay.script.Script(script_dir, script_name, script_file)

    setup_plugins = (
        (replay.plugins.TemporaryDirectory
            if args.script_working_directory is TEMPORARY_DIRECTORY
            else replay.plugins.WorkingDirectory),
        replay.plugins.CopyScript,
        replay.plugins.Inputs,
        replay.plugins.Outputs,
        replay.plugins.PythonDependencies,
        replay.plugins.Postgres,
        replay.plugins.Execute
        )

    context.run(setup_plugins, script)


if __name__ == '__main__':
    main()  # pragma: nocover
