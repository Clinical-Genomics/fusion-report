import os
import sys
from setuptools import find_packages, setup

VERSION = '1.0'
PACKAGE_DATA = {
    '': ['LICENSE', '*.md'],
    'fusion_report': [
        'templates/*',
        'templates/assets/*'
        'templates/partials/*'
    ]
}

with open('README.md') as f:
    README = f.read()

with open('requirements.txt') as f:
    INSTALL_REQUIREMENTS = f.read().splitlines()

setup(
    name='fusion_report',
    version=VERSION,
    python_requires='>=3.6.*',
    description='Tool for parsing outputs from fusion detection tools.',
    long_description=README,
    author='Martin Proks',
    author_email='mproksik@gmail.com',
    url='https://github.com/matq007/fusion-report',
    license='GPL_v3',
    packages=find_packages(exclude=('tests')),
    install_requires=INSTALL_REQUIREMENTS,
    zip_safe=False,
    scripts=['bin/fusion_report'],
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    # package_data=PACKAGE_DATA,
    include_package_data=True
)
