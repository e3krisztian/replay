class MissingInput(Exception):

    '''A required input file is missing'''


class MissingOutput(Exception):

    '''A specified output file is missing'''


class MissingPythonDependency(Exception):

    '''A python dependency can not be installed'''


class ScriptError(Exception):

    '''The script terminated with an error'''
