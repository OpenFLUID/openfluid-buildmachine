# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os

from ofbm import BuildMachine as BM


class FakeBuildMachine(BM.BuildMachine):
    def __init__(self,args, AutoTrigger=True):
        self.returnCodes = {"configure":0,
                             "build":0,
                             "test":200,
                             "package":200}
        BM.BuildMachine.__init__(self, args, AutoTrigger)

    ########################################
    
    def emulateReturnCode(self, Step, Header, ReturnCode):
        
        Command = ["sh", "generateReturnCode.sh", str(ReturnCode)]
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=os.path.dirname(os.path.abspath(__file__)))
    
    ########################################
    
    def configureOpenFLUID(self):
        
        Step = "2_Configure"
        Header = "Configuring OpenFLUID for %s build"%self.BuildType
        self.emulateReturnCode(Step, Header, self.returnCodes["configure"])

    ########################################
        
    def buildOpenFLUID(self):
        
        Step = "3_Build"
        Header = "Building OpenFLUID"
        self.emulateReturnCode(Step, Header, self.returnCodes["build"])
        
    ########################################
    
    def testOpenFLUID(self):
        
        Step = "4_Test"
        Header = "Running OpenFLUID tests"
        self.emulateReturnCode(Step, Header, self.returnCodes["test"])
        
    ########################################

    def packageOpenFLUID(self):
        
        Step = "4_Package"
        Header = "Packaging OpenFLUID"
        self.emulateReturnCode(Step, Header, self.returnCodes["package"])