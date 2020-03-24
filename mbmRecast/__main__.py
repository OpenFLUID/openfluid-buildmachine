#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__ = "armel.thoni@inrae.fr"


import argparse
import logging

from .MBMEnv import MBMEnv
from ofbm import utils as ofbmutils


"""#for handler in logging.root.handlers[:]:
#    logging.root.removeHa
# ndler(handler)
logging.basicConfig(filename="OFBM_logs_main.txt",level=logging.INFO)
"""


######################################################
######################################################


def MBMParser():
    """Argument parser for OpenFLUID build machine"""
    Parser = argparse.ArgumentParser(description="Tool for multiple build of the OpenFLUID modelling platform, locally or in docker images")

    SubParsers = Parser.add_subparsers(help='sub-command help')

    CreateParser = SubParsers.add_parser("create",help="Create a new MBM environment")
    CreateParser.add_argument('--env-path',default="./", help="Where the new MBM env will be created")
    CreateParser.set_defaults(which="create")


    RunParser = SubParsers.add_parser("run",help="Launch a given MBM environment")
    RunParser.add_argument('--env-path',default="./", help="The path of the target MBM environment")
    RunParser.set_defaults(which="run")
    return Parser


######################################################
######################################################


def main():
    Parser = MBMParser()
    Args = vars(Parser.parse_args())
    print("MAIN:", Args)
    m = MBMEnv(Args)
