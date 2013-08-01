import argparse
from externals import fspath
import os.path


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
        default=fspath.working_directory().path)

    parser.add_argument(
        '--script_working_directory',
        default=MAKE_TEMPORARY_DIRECTORY)

    parser.add_argument(
        '--virtualenv_parent_directory',
        default=get_virtualenv_parent_dir())

    # mandatory parameter
    parser.add_argument(
        'script_path')

    args = parser.parse_args(args)

    # fix script_path
    args.script_path = fspath.FsPath(args.script_path).path

    return args
