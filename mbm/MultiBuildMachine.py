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
                #logging.info("--     Launching build machine in image: %s" % Image)
                IsImage = True
                
            elif self.tryImageBuild:
                logging.info("--     Building docker image: %s" % Image)
                CreationReturnCode = DM.generateImage(Image)
                logging.debug("--     Creation return code: %d" % CreationReturnCode)
                # trigger launch if image successfully created
                if Image in DM.getImages(NameOnly=True):
                    logging.info("--     Launching build machine in image: %s" % Image)
                    IsImage = True
                else:
                    logging.error("--     Docker image %s missing after building" % (Image))
            else:
                ErrorTxt = "--     Image %s is not created. Please generate this docker image before performing any operation."%Image
                logging.error(ErrorTxt)
                return EmptySummary
            
            if IsImage:
                LaunchLogs = DM.launchInDocker(Image, Cmd, ScriptDir, LogDir, SrcDir)

        LogPath = os.path.join(ConvertedLogDir, consts.LOGS_SUBDIR)
        ReportPath = os.path.join(LogPath, "report.json")
        if os.path.isfile(ReportPath):
            BuildSummary = utils.loadJsonSummary(ReportPath)
            BuildSummary["metadata"]["log-path"] = LogPath
            return BuildSummary
        else:
            logging.error(ReportPath+" not found. Build may have failed.")
            return EmptySummary


    ######################################################
    ######################################################


    def triggerBuilds(self, ConfFile, ExecDir=".", ScriptDir="."):
        """Fetch instructions from yaml configuration file, triggers builds and generates summaries"""
        if not os.path.exists(ExecDir):
            os.mkdir(ExecDir)
        GlobalOutDir = os.path.join(ExecDir, "global")
        LogOutDir = os.path.join(ExecDir, "logs")
        SrcDir = os.path.join(ExecDir, "src")
        os.mkdir(GlobalOutDir)
        os.mkdir(LogOutDir)
        os.mkdir(SrcDir)

        logging.basicConfig(filename=LogOutDir+"/mbm_run_logs.txt",level=logging.INFO,#"/MBM_logs_%s.txt"%ofbmutils.currentTimestamp(noSpace=True)
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger("mbm").addHandler(logging.StreamHandler())

        Setups = utils.importYaml(ConfFile)

        ProceduresSummary = []
        logging.info("-- Triggering builds")

        for Setup in Setups["active-setups"]:

            # SET PARAMETERS
            logging.info("--   "+"*"*20)
            for Key in Setup:
                logging.info("--   "+f"{Key}: {Setup[Key]}")
            

            for MandatoryGenericParam in ["contexts", "build-type"]:
                if MandatoryGenericParam not in Setup:
                    logging.error("'%s' missing for active setup"%MandatoryGenericParam)

            SeveralContexts = len(Setup["contexts"]) > 1
            NContext = 0
            for Context in Setup["contexts"]:
                if ":" in Context:
                    SplittedContext = Context.split(":")
                    System, Image = SplittedContext[0], ":".join(SplittedContext[1:])
                else:
                    System, Image = Context, ""

                TempDir = ""
                if "temp-dir" in Setup:
                    TempDir = Setup["temp-dir"]
                else:
                    TempDir = ExecDir  # os.path.join(tempfile.gettempdir(),"openfluid-build-machine")
                    Setup["temp-dir"] = TempDir
                if System == "local":
                    TempDir += "/Local-%d"%NContext
                    NContext += 1
                elif System == "docker":
                    """if TempDir[:8] != "/shared/":
                        logging.error("Temp dir %s must be located in /shared/ folder for image/host communication reasons"%TempDir)
                        exit(0)"""
                    TempDir += "/%s/"%Image.replace(":","_").replace(".","-")
                else:
                    logging.error("Launch for %s not implemented"%Context)


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
                if System == "local" and not HasRepo:
                    BuildMachineParams += [("openfluid-repos",Image)]

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

        logging.info("--")
        ReportName = 'fullreport.json'
        JsonFile = os.path.join(GlobalOutDir, ReportName)
        with open(JsonFile, 'w') as Outfile:
          Outfile.write(json.dumps(ProceduresSummary, indent=4))

        logging.info("-- %s generated."%ReportName)
        LogFile = GlobalOutDir+'/mbm_%s.txt'%ofbmutils.currentTimestamp(True)
        utils.constructMultiBuildHTMLSummary(ProceduresSummary, OutDir=GlobalOutDir, LogFile=LogFile)


if __name__ == "__main__":
    CMBM = MultiBuildMachine()
    CMBM.triggerBuilds("theoricalconf.yml")
