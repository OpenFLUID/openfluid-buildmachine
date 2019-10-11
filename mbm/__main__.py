#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__ = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"

import os
import argparse

from ofbm import utils as ofbmutils
from mbm import MultiBuildMachine as mbm

import logging

from mbm import MultiBuildMachine as MBM
from mbm import settings


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


DefaultYmlConfFile = os.path.dirname(os.path.realpath(__file__))+"/basicConf.yml"

######################################################
######################################################


def MultiBuildMachineParser():

    Parser = argparse.ArgumentParser(
              description="Tool for multiple build of the OpenFLUID modelling platform, locally or in docker images")
    Parser.add_argument("--conf-file", "-c", default=DefaultYmlConfFile, help="yaml configuration file location")
    Parser.add_argument("--out-dir", "-o", default=os.path.join(os.getcwd(), settings.OUTPUT_DIR), help="folder absolute location for mbm output files")
    Parser.add_argument("--try-image-build", "-b", default=False, action='store_true', help="try to build the docker images if not existing")
    Parser.add_argument("--shell", "-s", default=False, action='store_true', help="if true, returns mbm outputs in shell (independant from shell option of ofbm)")
    return Parser

######################################################
######################################################


def main():

    Parser = MultiBuildMachineParser()
    Args = vars(Parser.parse_args())
    
    # create out dir if needed
    ofbmutils.resetDirectory(Args["out_dir"])
     
    logging.basicConfig(filename=Args["out_dir"]+"/MBM_logs_%s.txt"%ofbmutils.currentTimestamp(noSpace=True),level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.debug("Args: %s"%str(Args))
    
    CMBM = MBM.MultiBuildMachine(OutputInShell=Args["shell"], tryImageBuild=Args["try_image_build"])
    CMBM.triggerBuilds(Args["conf_file"], Args["out_dir"])
