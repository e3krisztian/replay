def read_or_die(fname, content):
    with open(fname) as f:
        if content != f.read():
            raise ValueError(fname, content)


read_or_die('file1', 'OK')
read_or_die('file2', 'exists, too')
