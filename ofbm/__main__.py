#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


from ofbm.BuildMachine import BuildMachine
from ofbm.BuildMachineParser import BuildMachineParser

import logging
#print("remove handlers")
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename="OFBM_logs_main.txt",level=logging.INFO)


######################################################
######################################################


def main():
    Parser = BuildMachineParser()
    Args = vars(Parser.parse_args())

    BM = BuildMachine(Args)
