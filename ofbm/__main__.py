#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


import argparse


######################################################
######################################################


def main():

  Parser = argparse.ArgumentParser(description="Tool for automatically build, test and package the OpenFLUID modelling platform")

  Args = vars(Parser.parse_args())
  # print(Args)
