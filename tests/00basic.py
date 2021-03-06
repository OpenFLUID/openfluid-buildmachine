# -*- coding: utf-8 -*-

__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__   = "jean-christophe.fabre@inra.fr"
__license__ = "see LICENSE file"


import unittest

import os.path

from ofbm.BuildMachine import BuildMachine, GitException, InputException, ProcedureException
from ofbm.BuildMachineParser import BuildMachineParser

######################################################
######################################################


class MainTest(unittest.TestCase):
    
  def setUp(self):
    self.BasicArgs = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "shell":True}
  

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
  
  
  def _test_config(self):
    
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    #self.assertTrue(os.path.exists(LocalTmpPath))
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":2, "openfluid_repos":LocalTmpPath, "which":"test"}
    BM = BuildMachine(Args, AutoTrigger=False)
    
    BM.setupRepos(TriggerClone=False)
    #BM.configureOpenFLUID()
    #BM.buildOpenFLUID()
    BM.testOpenFLUID()
  
  
  ####################################################
 
 
  def test_testBuild_fromGit(self):
 
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":2, "which":"test", "openfluid_repos":"OpenFLUID/openfluid"}
    BM = BuildMachine(Args)
 
    
  ####################################################
 
  
  def _test_packageBuild_fromLocal(self):
 
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":2, "which":"package", "openfluid_repos":LocalTmpPath}
    BM = BuildMachine(Args)
 
 
  ####################################################   
  
    
  def _test_partial_gitRopenfluid(self):

    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":2, "openfluid_repos":"OpenFLUID/openfluid#master",
            "ropenfluid_repos":"OpenFLUID/ropenfluid#master", "shell":True}
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("ropenfluid_repos")
    BM.checkROpenFLUID()
    BM.buildROpenFLUID()
    BM.summaryGeneration(InShell=True)


  ####################################################    
 
 
  def _test_partial_gitPyopenfluid(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":2, "openfluid_repos":"OpenFLUID/openfluid#master",
            "pyopenfluid_repos":"default", "shell":True}
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("pyopenfluid_repos")
    BM.checkPyOpenFLUID()
    BM.buildPyOpenFLUID()
    BM.summaryGeneration(InShell=True)
 
 
  ####################################################   


  def test_parser(self):

    Parser = BuildMachineParser()
    ParserInput = 'package --pyopenfluid-repos=default'
    Args = vars(Parser.parse_args(ParserInput.split()))
    print("Args:")
    print(Args)
  
  
  ####################################################    
  
  
  def test_fullPackage_viaParser(self):

    Parser = BuildMachineParser()
    ParserInput = '--build-jobs=9 package --pyopenfluid-repos=default --ropenfluid-repos=default'
    Args = vars(Parser.parse_args(ParserInput.split()))
    BM = BuildMachine(Args)
    
  
  ####################################################
  
  
  def _test_gitPyopenfluid_viaParser(self):

    Parser = BuildMachineParser()
    ParserInput = '--build-jobs=9 package --pyopenfluid-repos=default'
    Args = vars(Parser.parse_args(ParserInput.split()))
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("pyopenfluid_repos")
    BM.checkPyOpenFLUID()
    BM.buildPyOpenFLUID()
    BM.testPyOpenFLUID()
    BM.packagePyOpenFLUID()
    BM.summaryGeneration()
    BM.summaryGeneration(InShell=True)
    
  
  ####################################################
  
  
  def _test_gitRopenfluid_viaParser(self):
    
    Parser = BuildMachineParser()
    ParserInput = '--build-jobs=9 package --ropenfluid-repos=default'
    Args = vars(Parser.parse_args(ParserInput.split()))
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("ropenfluid_repos")
    BM.checkROpenFLUID()
    BM.buildROpenFLUID()
    BM.summaryGeneration()
    BM.summaryGeneration(InShell=True)
  
  ####################################################
  
  
  def _test_examples_viaParser(self):

    Parser = BuildMachineParser()
    ParserInput = '--build-jobs=9 package --examples=Firespread'
    Args = vars(Parser.parse_args(ParserInput.split()))
    BM = BuildMachine(Args)


######################################################
######################################################


if __name__ == '__main__':
  unittest.main()