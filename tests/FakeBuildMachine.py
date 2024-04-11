# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os

from ofbm import BuildMachine as BM


class FakeBuildMachine(BM.BuildMachine):
    def __init__(self,args, AutoTrigger=True):
        self.returnCodes = {"clone":0,
                            "configure":0,
                             "build":100,
                             "test":0,
                             "package":0}
        BM.BuildMachine.__init__(self, args, AutoTrigger)

    ########################################
    
    def emulateReturnCode(self, Step, Header, ReturnCode):
        
        Command = ["sh", "generateReturnCode.sh", str(ReturnCode)]
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=os.path.dirname(os.path.abspath(__file__)))
    

    def cloneProcedure(self, Step, RepoKey):
        """Execute the cloning git shell command and fetch output"""
        CodebaseRep = self.AllCodebaseRepos[RepoKey+"_repos"]

        if os.path.isdir(CodebaseRep.LocalPath):
            print("REPO EXISTS", CodebaseRep.LocalPath)
            return

        Header = "Cloning (Fake)"
        self.emulateReturnCode(Step, Header, self.returnCodes["clone"])

    ########################################
    
    def configureOpenFLUID(self):
        
        Step = "2_Configure"
        Header = "Configuring (Fake) OpenFLUID for %s build"%self.BuildType
        self.emulateReturnCode(Step, Header, self.returnCodes["configure"])

    ########################################
        
    def buildOpenFLUID(self):
        
        Step = "3_Build"
        Header = "Building (Fake) OpenFLUID"
        self.emulateReturnCode(Step, Header, self.returnCodes["build"])
        
    ########################################
    
    def testOpenFLUID(self):
        
        Step = "4_Test"
        Header = "Running (Fake) OpenFLUID tests"
        self.emulateReturnCode(Step, Header, self.returnCodes["test"])
        
    ########################################

    def packageOpenFLUID(self):
        
        Step = "4_Package"
        Header = "Packaging (Fake) OpenFLUID"
        self.emulateReturnCode(Step, Header, self.returnCodes["package"])