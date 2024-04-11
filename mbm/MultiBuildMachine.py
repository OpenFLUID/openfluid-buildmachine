# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"

import os
import tempfile
import json
import logging


from mbm import dockerManagement as DM
from mbm import utils, settings

from ofbm import consts
from ofbm import utils as ofbmutils
from ofbm import BuildMachine as BM


######################################################
######################################################

class MultiBuildMachine:
    
    
    def __init__(self, OutputInShell=False, tryImageBuild=False, isFake=False):
        self.OutputInShell = OutputInShell
        self.tryImageBuild = tryImageBuild
        self.isFake = isFake
        self.logger = None
    
    
    ######################################################
    ######################################################
    

    def genericBuild(self, Params, Image="", LogDir="/", ScriptDir="", SrcDir=""):
        """Activate the OpenFLUID build on given context (local if Image parameter is empty) and generates summary"""
        # TODO SET INSIDE SUBPROCESS OR THREAD FOR PARALLEL CALL?

        EmptySummary = {"steps":[], "metadata":{"log-path":""}}
        LaunchLogs = {"OUT":"", "ERR":""}

        if Image == "" or Image.startswith("/"): # For local launch
            Cmd = "python3 %s/../OFBMInjector.py %s" % (os.path.dirname(os.path.realpath(__file__)), str(self.isFake) + " " +Params)
            ConvertedLogDir = LogDir
            LogPath = os.path.join(ConvertedLogDir, consts.LOGS_SUBDIR)
            LaunchLogs = ofbmutils.subprocessCall(Cmd.split(), LogPath+"/tmpLOFS.txt",  # TODO log path was commented?
                                                  OutputInShell=self.OutputInShell, OutputAsReturn=True)
        
        else:
            Cmd = "python3 /shared/scripts/OFBMInjector.py %s" % (str(self.isFake) + " " +Params)
            HostPath = LogDir
            ConvertedLogDir = LogDir.replace("/shared", HostPath)
            
            # check if docker image exists, deploy it otherwise
            IsImage = False
            ImageID = Image.split(":")[0]
            if ImageID in DM.getImages(NameOnly=True): #TODO renforcer pour vérifier existence tag
                #self.logger.log(logging.INFO, "--     Launching build machine in image: %s" % Image)
                IsImage = True
                
            elif self.tryImageBuild:
                self.logger.log(logging.INFO, "--     Building docker image: %s" % Image)
                CreationReturnCode = DM.generateImage(Image)
                self.logger.log(logging.DEBUG, "--     Creation return code: %d" % CreationReturnCode)
                # trigger launch if image successfully created
                if Image in DM.getImages(NameOnly=True):
                    self.logger.log(logging.INFO, "--     Launching build machine in image: %s" % Image)
                    IsImage = True
                else:
                    self.logger.log(logging.ERROR, "--     Docker image %s missing after building" % (Image))
            else:
                ErrorTxt = "--     Image %s is not created. Please generate this docker image before performing any operation."%Image
                self.logger.log(logging.ERROR, ErrorTxt)
                return EmptySummary
            
            if IsImage:
                LaunchLogs = DM.launchInDocker(Image, Cmd, ScriptDir, LogDir, SrcDir, Logger=self.logger)

        LogPath = os.path.join(ConvertedLogDir, consts.LOGS_SUBDIR)
        ReportPath = os.path.join(LogPath, "report.json")
        if os.path.isfile(ReportPath):
            BuildSummary = utils.loadJsonSummary(ReportPath)
            BuildSummary["metadata"]["log-path"] = LogPath
            return BuildSummary
        else:
            self.logger.log(logging.ERROR, ReportPath+" not found. Build may have failed.")
            return EmptySummary


    ######################################################
    ######################################################


    def triggerBuilds(self, ConfFile, ExecDir="_out", ScriptDir="."):
        """Fetch instructions from yaml configuration file, triggers builds and generates summaries"""
        if not os.path.exists(ExecDir):
            os.mkdir(ExecDir)
        GlobalOutDir = os.path.join(ExecDir, "global")
        LogOutDir = os.path.join(ExecDir, "logs")
        SrcDir = os.path.join(ExecDir, "src")
        os.mkdir(GlobalOutDir)
        try:
            os.mkdir(LogOutDir)
        except FileExistsError:
            pass
        os.mkdir(SrcDir)

        if not self.logger:
            print("NEED MBM LOGGER")
            self.logger = logging.getLogger(__name__)

        Setups = utils.importYaml(ConfFile)

        ProceduresSummary = []
        self.logger.log(logging.INFO, "--")
        self.logger.log(logging.INFO, "-- Triggering builds")

        for Setup in Setups["active-setups"]:

            # SET PARAMETERS
            self.logger.log(logging.INFO, "--   "+"*"*20)
            for Key in Setup:
                self.logger.log(logging.INFO, "--   "+f"{Key}: {Setup[Key]}")
            

            for MandatoryGenericParam in ["contexts", "build-type"]:
                if MandatoryGenericParam not in Setup:
                    self.logger.log(logging.ERROR, "'%s' missing for active setup"%MandatoryGenericParam)

            SeveralContexts = len(Setup["contexts"]) > 1
            NContext = 0
            for Context in set(Setup["contexts"]): # CAUTION: ignores if context present several times in list
                if ":" in Context:
                    SplittedContext = Context.split(":")
                    System, Image = SplittedContext[0], ":".join(SplittedContext[1:])
                else:
                    System, Image = Context, ""

                TempDir = ""
                if "temp-dir" in Setup:
                    TempDir = Setup["temp-dir"]
                else:
                    TempDir = os.path.join(ExecDir, "content", Setup["build-type"]+"_setup")  # os.path.join(tempfile.gettempdir(),"openfluid-build-machine")
                    Setup["temp-dir"] = TempDir
                if System == "local":
                    TempDir += "/Local-%d"%NContext
                    NContext += 1
                elif System == "docker":
                    """if TempDir[:8] != "/shared/":
                        self.logger.log(logging.ERROR, "Temp dir %s must be located in /shared/ folder for image/host communication reasons"%TempDir)
                        exit(0)"""
                    TempDir += "/%s/"%Image.replace(":","_").replace(".","-")
                else:
                    self.logger.log(logging.ERROR, "Launch for %s not implemented"%Context)


                BuildMachineParams = []
                if System == "local":
                    BuildMachineParams+= [("temp-dir", TempDir), ("src-dir", SrcDir)]
                else:
                    BuildMachineParams+= [("temp-dir", "/shared/build/"), ("src-dir", "/shared/src/")]
                GlobalParams = ["shell", "temp-dir", "build-jobs", "openfluid-repos"]
                SubParserParams = []

                HasRepo = False
                for Param in Setup:
                    if Param == "openfluid-repos":
                        HasRepo = True
                    if Param not in ["contexts", "build-type", "temp-dir"]:
                        if Param in GlobalParams:
                            BuildMachineParams += [(Param, Setup[Param])]
                        else:
                            SubParserParams += [(Param, Setup[Param])]
                if System == "local":
                    if not HasRepo:
                        BuildMachineParams += [("openfluid-repos",Image)]
                    if Setup["build-type"]=="package":
                        SubParserParams += [("localinstall", "")]

                ParamsTxt = utils.BMArgsFromParams(BuildMachineParams, Setup["build-type"], SubParserParams)
                print("--     "+"*"*20)
                #print("--     Launching OFBM with params: ",ParamsTxt)
                # LAUNCH BUILD
                BuildSummary = self.genericBuild(ParamsTxt, Image, TempDir, ScriptDir=ScriptDir, SrcDir=SrcDir)

                # INJECT OUTPUTS
                if "metadata" not in BuildSummary:
                    BuildSummary["metadata"] = {}
                BuildSummary["metadata"]["setup"] = Setup
                BuildSummary["metadata"]["context"] = Context
                ProceduresSummary.append(BuildSummary)

        self.logger.log(logging.INFO, "-- Builds done")
        ReportName = 'fullreport.json'
        JsonFile = os.path.join(GlobalOutDir, ReportName)
        with open(JsonFile, 'w') as Outfile:
          Outfile.write(json.dumps(ProceduresSummary, indent=4))

        self.logger.log(logging.INFO, "--   %s generated."%ReportName)
        #LogFile = GlobalOutDir+'/mbm_%s.txt'%ofbmutils.currentTimestamp(True)
        LogFile = LogOutDir+'/mbm_run_logs.txt'
        HtmlFilename = "summary.html"
        HtmlPath = utils.constructMultiBuildHTMLSummary(ProceduresSummary, OutDir=GlobalOutDir, LogFile=LogFile, HtmlFilename=HtmlFilename)
        self.logger.log(logging.INFO, "--   file://%s written."%HtmlPath)


if __name__ == "__main__":
    CMBM = MultiBuildMachine()
    CMBM.triggerBuilds("theoricalconf.yml")
