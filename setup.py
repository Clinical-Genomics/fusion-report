#!/usr/bin/env python
import sys
import os
from setuptools import setup

VERSION = '1.0'
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)
EXCLUDE_FROM_PACKAGES = []

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of fusion-report requires Python {}.{}, but you're trying to
install it on Python {}.{}.""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
sys.exit(1)

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as in_file:
        return in_file.read()

setup(
    name='fusion-report',
    version=VERSION,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    description='''
        Tool for parsing outputs from fusion detection tools.
        Part of a nf-core/rnafusion pipeline.
    ''',
    long_description=read('README.md'),
    license='MIT',
    author='Martin Proks',
    author_email='mproksik@gmail.com',
    url='https://github.com/matq007/fusion-report',
    py_modules=['fusion_report'],
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    scripts=['bin/fusion-report'],

)
