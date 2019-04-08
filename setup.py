#! /usr/bin/env python3

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = 'openfluid-buildmachine',
      version = '0.0.1',
      description = 'Tool for automatically build, test and package the OpenFLUID modelling platform',
      long_description = readme(),
      author = 'Jean-Christophe Fabre',
      author_email = 'jean-christophe.fabre@inra.fr',
      url = 'http://github.com/OpenFLUID/openfluid-buildmachine',
      license = 'GPLv3',
      packages = ['ofbm'],
      entry_points = {
          'console_scripts': [
              'ofbm = ofbm.__main__:main'
          ]
      },
      install_requires = [
        'argparse'
      ]
)