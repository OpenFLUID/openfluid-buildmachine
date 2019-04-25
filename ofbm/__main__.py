#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


from .BuildMachine import BuildMachine
from .BuildmachineParser import BuildmachineParser

######################################################
######################################################


def main():

  Parser = BuildmachineParser()
  Args = vars(Parser.parse_args())

  BM = BuildMachine(Args)
