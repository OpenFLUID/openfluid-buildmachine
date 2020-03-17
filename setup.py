#! /usr/bin/env python3
#-*-coding:utf-8-*-

import logging
logging.basicConfig(filename="OFBM_logs_setup_2.txt",level=logging.INFO)

#logger = logging.getLogger(__name__)
#logger.addHandler(logging.StreamHandler())

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = 'openfluid-buildmachine',
      version = '0.0.1',
      description = 'Tool for automatically build, test and package the OpenFLUID modelling platform',
      long_description = readme(),
      author = 'Jean-Christophe Fabre, Armel Thöni', 
      author_email = 'jean-christophe.fabre@inra.fr, armel.thoni@inra.fr',
      url = 'http://github.com/OpenFLUID/openfluid-buildmachine',
      license = 'GPLv3',
      packages = ['ofbm'],
      entry_points = {
          'console_scripts': [
              'ofbm = ofbm.__main__:main',
              'mbm = mbm.__main__:main',
              'openfluid-mbm = mbmRecast.__main__:main'
          ]
      },
      test_suite='tests',
      install_requires = [
        'argparse'
      ]
)