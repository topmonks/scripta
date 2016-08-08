#!/usr/bin/env python

from distutils.core import setup

setup(name='scripta',
      version='0.0.1',
      description='Scripting & Tooling',
      author='Tomas Bouda',
      author_email='tomas.bouda@purposefly.com',
      url='https://github.com/purposefly/scripta',
      packages=['scripta'],
      package_dir={'scripta': 'src/scripta'},
      )
