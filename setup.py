#!/usr/bin/env python
# coding: utf8
from __future__ import unicode_literals, print_function

from setuptools import setup, find_packages

import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2


with open('requirements.txt') as f:
    requirements_txt = [line.rstrip() for line in f.readlines()]

setup(
    name='replay',
    version=':versiontools:replay:',

    description='Tools for replaying data transformations',
    author='Krisztián Fekete',
    url='https://github.com/ceumicrodata/replay',

    packages=find_packages('.'),
    include_package_data=True,

    setup_requires=['versiontools >= 1.8'],

    use_2to3=PY3,
    install_requires=requirements_txt,
    dependency_links=[
        'https://github.com/krisztianfekete/externals/tarball/master#egg=externals-0.1'],

    tests_require=['mock'],

    entry_points={
        'console_scripts': [
            'replay=replay.main:main'
        ],
    }
)
