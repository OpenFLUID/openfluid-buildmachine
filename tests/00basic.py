# -*- coding: utf-8 -*-

__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__   = "jean-christophe.fabre@inra.fr"
__license__ = "see LICENSE file"


import unittest

import os.path

from ofbm.BuildMachine import BuildMachine, GitException, InputException, ProcedureException
from ofbm.BuildmachineParser import BuildmachineParser

######################################################
######################################################


class MainTest(unittest.TestCase):
    
  # TODO : correct number of jobs to 1 for release
  def setUp(self):
    self.BasicArgs = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "shell":True}
  

  def test_gitSetup(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":"OpenFLUID/openfluid:master"}
    BM = BuildMachine(Args)
    BM.setupRepos()
    BM.summaryGeneration()
    
    # TODO What is the test here? what assert?
    
  ####################################################
  
  def test_emptySetup(self):
      Args = {}
      with self.assertRaises(InputException):
        BM = BuildMachine(Args)
  
  ####################################################
  
  def test_gitBadSetup(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":"OpenFLU/openflu:mast"}
    BM = BuildMachine(Args)
    #with self.assertRaises(GitException):
    BM.setupRepos()
    BM.summaryGeneration()
    
  ####################################################
  """
  def test_localSetup(self):
    # requires test00 clone step
    # Hard to test from real local: can't define location generically since depending on system...
    
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    self.assertTrue(os.path.exists(LocalTmpPath)) #not a real test, more a config check before running the effective test. Still assert?
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":LocalTmpPath}
    BM = BuildMachine(Args)
  """
  
  ####################################################
  
  def test_config(self):
    # requires test00 clone step
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    #self.assertTrue(os.path.exists(LocalTmpPath))
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":10, "openfluid_repos":LocalTmpPath, "which":"test"}
    BM = BuildMachine(Args, AutoTrigger=False)
    
    BM.setupRepos(TriggerClone=False)
    #BM.configureOpenFLUID()
    #BM.buildOpenFLUID()
    BM.testOpenFLUID()
  
  ####################################################
 
  def test_testBuild_fromGit(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":10, "which":"test", "openfluid_repos":"OpenFLUID/openfluid"}
    BM = BuildMachine(Args)
    
  ####################################################
  
  def test_packageBuild_fromLocal(self):
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":10, "which":"package", "openfluid_repos":LocalTmpPath}
    BM = BuildMachine(Args)
    
  ####################################################
  
  def test_installCheckExamples_fromLocal(self):
    LocalTmpPath = "/tmp/openfluid-build-machine/openfluid-src"
    Args = dict(self.BasicArgs)
    Args["build_jobs"] = 10
    Args["shell"] = False
    Args["which"] = "package"
    Args["openfluid_repos"] = LocalTmpPath
    Args["examples"] = "Firespread,MHYDAS_Roujan"
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos()
    try:
      BM.installOpenFLUID()
    except ProcedureException as e:
      print(e)
      print("Repackage sources")
      BM.packageOpenFLUID()
      BM.installOpenFLUID()
      
    #BM.checkExamplesOpenFLUID()
    BM.summaryGeneration()
    
    
  def test_partial_gitRopenfluid(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":1, "openfluid_repos":"OpenFLUID/openfluid:master",
            "ropenfluid_repos":"OpenFLUID/ropenfluid:master", "shell":True}
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("ropenfluid_repos")
    BM.checkROpenFLUID()
    BM.buildROpenFLUID()
    BM.summaryGeneration(InShell=True)
    
 
  def test_partial_gitPyopenfluid(self):
    Args = {"temp_dir":"/tmp/openfluid-build-machine", "build_jobs":10, "openfluid_repos":"OpenFLUID/openfluid:master",
            "pyopenfluid_repos":"default", "shell":True}#OpenFLUID/pyopenfluid:develop
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("pyopenfluid_repos")
    BM.checkPyOpenFLUID()
    BM.buildPyOpenFLUID()
    BM.summaryGeneration(InShell=True)
    
  def test_parser(self):
    Parser = BuildmachineParser()
    #input = 'package --pyopenfluid-repos="default"'
    input = 'package --pyopenfluid-repos=default'
    Args = vars(Parser.parse_args(input.split()))
    print("Args:")
    print(Args)
    #BM = BuildMachine(Args, AutoTrigger=False)
    
  def test_fullPackage_viaParser(self):
    Parser = BuildmachineParser()
    input = '--build-jobs=9 package --pyopenfluid-repos=default --ropenfluid-repos=default'
    Args = vars(Parser.parse_args(input.split()))
    BM = BuildMachine(Args)
    
  def test_gitPyopenfluid_viaParser(self):
    Parser = BuildmachineParser()
    #input = '--shell --build-jobs=9 package --pyopenfluid-repos="default"'
    input = '--build-jobs=9 package --pyopenfluid-repos=default'
    Args = vars(Parser.parse_args(input.split()))
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("pyopenfluid_repos")
    BM.checkPyOpenFLUID()
    BM.buildPyOpenFLUID()
    BM.testPyOpenFLUID()
    BM.packagePyOpenFLUID()
    BM.summaryGeneration()
    BM.summaryGeneration(InShell=True)
    
  def test_gitRopenfluid_viaParser(self):
    Parser = BuildmachineParser()
    #input = '--shell --build-jobs=9 package --pyopenfluid-repos="default"'
    input = '--build-jobs=9 package --ropenfluid-repos=default'
    Args = vars(Parser.parse_args(input.split()))
    BM = BuildMachine(Args, AutoTrigger=False)
    BM.setupRepos(TriggerClone=False)
    BM.setupChildRepos("ropenfluid_repos")
    BM.checkROpenFLUID()
    BM.buildROpenFLUID()
    BM.summaryGeneration()
    BM.summaryGeneration(InShell=True)
    
  # need cleanup for real tests without side effects
  


######################################################
######################################################


if __name__ == '__main__':
  unittest.main()