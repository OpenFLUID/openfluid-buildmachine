#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


import os
import argparse
import tempfile
from .BuildMachine import BuildMachine


######################################################
######################################################


def main():

  Parser = argparse.ArgumentParser(description="Tool for automatically build, test and package the OpenFLUID modelling platform")
  
  Parser.add_argument('--temp-dir',default=os.path.join(tempfile.gettempdir(),"openfluid-build-machine"))
  
  Parser.add_argument('--openfluid-repos',default='https://github.com/OpenFLUID/openfluid')
  Parser.add_argument('--openfluid-branch',default='develop')
  
  SubParsers = Parser.add_subparsers(help='sub-command help')
  PackageParser = SubParsers.add_parser("package",help="Build OpenFLUID and create packages")

  PackageParser.add_argument('--with-ropenfluid',action='store_true')
  PackageParser.add_argument('--ropenfluid-repos',default='https://github.com/OpenFLUID/ropenfluid')
  PackageParser.add_argument('--ropenfluid-branch',default='develop')

  PackageParser.add_argument('--with-pyopenfluid',action='store_true')
  PackageParser.add_argument('--pyopenfluid-repos',default='https://github.com/OpenFLUID/pyopenfluid')
  PackageParser.add_argument('--pyopenfluid-branch',default='develop')

  PackageParser.add_argument('--with-openfluidjs',action='store_true')
  PackageParser.add_argument('--openfluidjs-repos',default='https://github.com/OpenFLUID/openfluidjs')
  PackageParser.add_argument('--openfluidjs-branch',default='develop')

  TestParser = SubParsers.add_parser("test",help="build OpenFLUID and run tests")

  Args = vars(Parser.parse_args())
  print(Args)

  BM = BuildMachine(Args)
