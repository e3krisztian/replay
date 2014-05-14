import argparse
import externals
import os.path
import sys
import replay.context
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
        default=externals.working_directory().path,
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
    args.script_path = externals.File(args.script_path).path

    return args


def get_script_working_directory(args):
    if args.script_working_directory is TEMPORARY_DIRECTORY:
        return TEMPORARY_DIRECTORY
    return externals.File(args.script_working_directory)


def main():
    args = parse_args(sys.argv[1:])

    context = replay.context.Context(
        externals.File(args.datastore),
        externals.File(args.virtualenv_parent_directory),
        get_script_working_directory(args))

    script_path = externals.File(args.script_path)
    script_dir = script_path.parent().path

    with open(args.script_path) as script_file:
        plugins = (
            [replay.plugins.TemporaryDirectory(context)
                if args.script_working_directory is TEMPORARY_DIRECTORY
                else replay.plugins.WorkingDirectory(context)]
            + [replay.plugins.CopyScript(script_dir)]
            + list(context.load_plugins(script_file)))

    context.run(plugins)


if __name__ == '__main__':
    main()  # pragma: nocover
