# http://stackoverflow.com/a/14298190
import urlparse
import urllib


def path2url(path):
    return urlparse.urljoin('file:', urllib.pathname2url(path))
