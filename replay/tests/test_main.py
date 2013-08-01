import unittest
import replay.main as m
from externals.fspath import working_directory
import mock


class Test_parse_args(unittest.TestCase):

    def test_defaults(self):
        args = m.parse_args(['dir/scriptname.py'])

        self.assertEqual(working_directory().path, args.datastore)

        self.assertEqual(
            m.MAKE_TEMPORARY_DIRECTORY,
            args.script_working_directory)

        self.assertEqual(
            m.get_virtualenv_parent_dir(),
            args.virtualenv_parent_directory)

    def test_absolute_script_path(self):
        args = m.parse_args(['/absolute/script/path/scriptname.py'])

        self.assertEqual(
            '/absolute/script/path/scriptname.py',
            args.script_path)

    def test_relative_script_path(self):
        args = m.parse_args(['relative/script/path/scriptname.py'])

        self.assertEqual(
            (working_directory() / 'relative/script/path/scriptname.py').path,
            args.script_path)


class Test_get_virtualenv_parent_dir(unittest.TestCase):

    def test_value_of_WORKON_HOME_is_returned(self):
        environ = {'WORKON_HOME': '/virtualenvs'}
        with mock.patch('os.environ', environ):
            self.assertEqual('/virtualenvs', m.get_virtualenv_parent_dir())

    def test_WORKON_HOME_is_unset_user_home_dot_virtualenvs_is_returned(self):
        def expanduser(arg):
            self.assertEqual('~', arg)
            return '/test/user/home'
        patch_expanduser = mock.patch('os.path.expanduser', expanduser)
        patch_environ = mock.patch('os.environ', {})
        with patch_expanduser, patch_environ:
            self.assertEqual(
                '/test/user/home/.virtualenvs',
                m.get_virtualenv_parent_dir())
