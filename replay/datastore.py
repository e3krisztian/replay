from abc import ABCMeta, abstractmethod


class PathDoesNotExist(Exception):
    '''I am raised, if a path is referenced which does not exists'''


class IDataStore(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def download(self, datastore_path, destination):
        raise PathDoesNotExist

    @abstractmethod
    def upload(self, source, datastore_path):
        pass


class WorkingDirectoryDataStore(object):

    def __init__(self):
        pass