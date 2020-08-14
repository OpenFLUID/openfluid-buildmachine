# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"

import sys
import logging

from ofbm.BuildMachine import BuildMachine
from ofbm.BuildMachineParser import BuildMachineParser
from ofbm.BuildMachineObjects import ProcedureException

"""Entry point for build machine trigger by shell using Python"""
Parser = BuildMachineParser()
Args = vars(Parser.parse_args(sys.argv[2:]))

if sys.argv[1] == "True":
    from tests.FakeBuildMachine import FakeBuildMachine
    CurrentBM = FakeBuildMachine(Args, AutoTrigger=False)
else:
    CurrentBM = BuildMachine(Args, AutoTrigger=False)

try:
    CurrentBM.triggerProcedure()
except ProcedureException:
    logging.error("Caught procedure exception")