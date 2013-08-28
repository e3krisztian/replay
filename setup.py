#!/usr/bin/env python
# coding: utf8

from setuptools import setup

with open('requirements.txt') as f:
    requirements_txt = [line.rstrip() for line in f.readlines()]

setup(
    name='replay',
    version=':versiontools:replay:',

    description=u'Tools for replaying data transformations',
    author=u'Krisztián Fekete',
    url='https://github.com/ceumicrodata/replay',

    packages=['replay'],

    setup_requires = [
        'versiontools >= 1.8',
    ],

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
