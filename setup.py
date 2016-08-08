#!/usr/bin/env python

from setuptools import setup

setup(
    name='scripta',
    version='0.0.1',

    description='Scripting & Tooling for AWS',

    url='https://github.com/purposefly/scripta',

    author='Tomas Bouda',
    author_email='tomas.bouda@purposefly.com',

    license='MIT',

    install_requires=[
        'PyYAML>=3.11',
        'boto3>=1.3.1'
    ],

    packages=[
        'scripta.aws',
        'scripta.template'
    ],
    package_dir={'': 'src'},

    entry_points={
        'console_scripts': [
            'scripta=scripta.main:main',
        ],
    }
)
