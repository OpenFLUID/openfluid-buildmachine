#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


import argparse
import os
import tempfile
from os.path import expanduser

from .utils import currentTimestamp

######################################################
######################################################


def BuildMachineParser():
    """Argument parser for OpenFLUID build machine"""
    Parser = argparse.ArgumentParser(description="Tool for automatically build, test and package the OpenFLUID modelling platform")

    DefaultTempDir = os.path.join(tempfile.gettempdir(),"openfluid-build-machine", currentTimestamp(noSpace=True))
    Parser.add_argument('--temp-dir',default=DefaultTempDir, help="Temporary folder path (will be created if not present)")
    Parser.add_argument('--src-dir',default=None, help="Source folder path")
    

    Parser.add_argument('--build-jobs', '-j', default=1, help="option -j of make step")

    Parser.add_argument('--shell', '-s', default=False, action='store_true',
                        help='display output in shell instead of log file')

    Parser.add_argument('--openfluid-repos',default='OpenFLUID/openfluid', help="OpenFLUID code repository: may be a github partial url or a local path")

    SubParsers = Parser.add_subparsers(help='sub-command help')
    PackageParser = SubParsers.add_parser("package",help="Build OpenFLUID and create packages")

    PackageParser.add_argument('--run-examples',default="*",
                               help="* for all, or example names separated by commas. Ex: Firespread,MHYDAS_Roujan")
                               
                               
    PackageParser.add_argument('--ropenfluid-repos', default=argparse.SUPPRESS)
    PackageParser.add_argument('--pyopenfluid-repos', default=argparse.SUPPRESS)
    PackageParser.add_argument('--openfluidjs-repos', default=argparse.SUPPRESS)

    PackageParser.add_argument('--subrepos-only', '-o', default=False, action='store_true',
                    help='ignore OpenFLUID packaging and works only on r/py/js repositories')

    PackageParser.set_defaults(which="package")

    TestParser = SubParsers.add_parser("test", help="build OpenFLUID and run tests")

    TestParser.set_defaults(which="test")

    return Parser
