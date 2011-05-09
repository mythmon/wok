#!/usr/bin/env python2

from distutils.core import setup

from wok import version

setup(name='wok',
      version=version.encode("utf8"),
      description='Static site generator',
      install_requires=['pyyaml', 'markdown', 'docutils', 'jinja2'],
      author='Mike Cooper',
      author_email='mythmon@gmail.com',
      url='https://www.github.com/mythmon/wok',
      packages=['wok'],
      scripts=['scripts/wok'],
      )
