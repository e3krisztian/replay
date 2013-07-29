#!/usr/bin/env python
# coding: utf8

from setuptools import setup

VERSION = '0.20130626.0'
VERSION_SUFFIX = '-dev'

with open('requirements.txt') as f:
    requirements_txt = [line.rstrip() for line in f.readlines()]

setup(
    name='replay',
    version='{version}{version_suffix}'.format(
        version=VERSION, version_suffix=VERSION_SUFFIX),

    description=u'Tools for replaying data transformations',
    author=u'Krisztián Fekete',
    url='https://github.com/ceumicrodata/replay',

    packages=['replay'],

    install_requires=requirements_txt,
    dependency_links=[
        'https://github.com/krisztianfekete/externals/tarball/master#egg=externals-0.1'],

    provides=['replay ({version})'.format(version=VERSION)],

    entry_points={
        'console_scripts': [
            'run=replay.run:main'
            ],
        }
    )
