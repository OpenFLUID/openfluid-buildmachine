# -*- coding: utf-8 -*-

__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__   = "jean-christophe.fabre@inra.fr"
__license__ = "see LICENSE file"


import unittest

import os.path

from ofbm.BuildMachine import BuildMachine, GitException, InputException, ProcedureException
from ofbm.BuildMachineParser import BuildMachineParser

from tests import FakeBuildMachine as FBM

######################################################
######################################################


import logging


class MainTest(unittest.TestCase):
    

  def test_gitSetup(self):
      
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":"OpenFLUID/openfluid#master"}
    BM = BuildMachine(Args)
    BM.setupRepos()
    BM.summaryGeneration()
    
    
  ####################################################
  
  
  def test_emptySetup(self):
    
      Args = {}
      with self.assertRaises(InputException):
        BM = BuildMachine(Args)
  
  
  ####################################################
  
  
  def test_gitBadSetup(self):
    
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":"OpenFLU/openflu:mast"}
    BM = BuildMachine(Args)
    BM.setupRepos()
    BM.summaryGeneration()

  
  ####################################################
  

  def test_parser(self):

    Parser = BuildMachineParser()
    ParserInput = 'package --pyopenfluid-repos=default'
    Args = vars(Parser.parse_args(ParserInput.split()))
    print("Args:")
    print(Args)
  
  
  ####################################################
  
  
  def test_machineSequence(self):
      
      Parser = BuildMachineParser()
      Args = vars(Parser.parse_args(['package', "--localinstall"]))
      FBM.FakeBuildMachine(Args)


######################################################
######################################################


if __name__ == '__main__':
  unittest.main()