#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>, Armel Thöni <armel.thoni@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


import sys
import os
from os.path import expanduser
import subprocess
import shutil
import time
import platform

from .BuildMachineObjects import GitException, InputException, ProcedureException, LocalCodebaseRepos, GitRepos
from . import consts, utils


import logging

# Success check when can not be found through return code

StepSuccessStrings = dict()
StepSuccessStrings["4_Test"] = "100% tests passed" # necessary since sometimes 0 returned with no test done
StepSuccessStrings["6_Example"] = "**** Simulation completed ****" # TODO status code for simulation?
StepSuccessStrings["R2_Check"] = "DONE"
StepSuccessStrings["R3_Build"] = "building ‘ROpenFLUID"
StepFailStrings = dict()
StepFailStrings["R2_Check"] = "ERROR"
StepFailStrings["R3_Build"] = "No such file or directory"

DefaultRepos = dict()  # possibility to set DefaultRepos["foo"] = [urlPortion, Branch] if wanted
DefaultRepos["ropenfluid_repos"] = ["OpenFLUID/ropenfluid"]
DefaultRepos["pyopenfluid_repos"] = ["OpenFLUID/pyopenfluid"]
DefaultRepos["openfluidjs_repos"] = ["OpenFLUID/openfluidjs"]


############################################################################
############################################################################


class BuildMachine :
    """OpenFLUID building operations system"""

    def __init__(self,args, AutoTrigger=True):
        self.InitBuildTimestamp = utils.currentTimestamp()
        # CONSTANTS
        self.BaseRepos = ['openfluid_repos'] # Related to parser fields
        self.ChildrenRepos = ['ropenfluid_repos', 'pyopenfluid_repos', 'openfluidjs_repos'] # Related to parser fields
        self.AllRepos = self.BaseRepos + self.ChildrenRepos
        ## OF
        self.SrcSubDirs = dict()
        self.SrcSubDirs["openfluid"] = "openfluid"
        self.OpenFLUIDBuildSubdir = os.path.join('build', "openfluid")
        ## ROF
        self.SrcSubDirs["ropenfluid"] = "ropenfluid"
        self.SrcSubDirs["pyopenfluid"] = "pyopenfluid"
        self.SrcSubDirs["openfluidjs"] = "openfluidjs"
        ## MACHINE LOGS

        self.LogSubdir = consts.LOGS_SUBDIR

        # PARAMETERS
        self.BuildType = None
        self.AllCodebaseRepos = dict()
        self.BuildJobs = 1

        self.OutputInShell = False
        self.SubreposOnly = False

        self.HostInfos = {}
        self.OpenFLUIDCMakeCommands = dict()
        self.ExamplesCheck = []

        # STATUS Check
        self.StatusTable = {}

        # Constant commands
        self.ROpenFLUIDCMakeCommands = dict()
        self.ROpenFLUIDCMakeCommands["check"] = ["cmake","-P","check.cmake"]
        self.ROpenFLUIDCMakeCommands["build"] = ["cmake","-P","build.cmake"]
        
        self.ExamplesPath = "/usr/share/doc/openfluid/examples/projects/"#Primitives/

        self.processCommonOptions(args)
        self.findEnvOptions()


        logging.info("BuildMachine steps logs are located in specific files in %s "%self.LogPath)

        if self.BuildType is not None and AutoTrigger:
            self.triggerProcedure()

    ########################################

    def triggerProcedure(self):
        """Comprehensive sequence of building operations from fetching to reporting"""
        logging.info("Beginning of BuildMachine procedure, env: %s"%str(self.EnvInfos))
        self.setupRepos()

        # Openfluid management
        if not self.SubreposOnly:
            self.configureOpenFLUID()
            self.buildOpenFLUID()

        if self.BuildType == "package":
            if not self.SubreposOnly:
                self.packageOpenFLUID()
                self.installOpenFLUID()
                self.checkExamplesOpenFLUID()
                
            # Check children projects
            for Repo in self.ChildrenRepos:
                if self.AllCodebaseRepos[Repo] is not None:

                    self.setupChildRepos(Repo)

                    if Repo == "ropenfluid_repos":
                        self.checkROpenFLUID()
                        self.buildROpenFLUID()

                    elif Repo == "pyopenfluid_repos":
                        self.checkPyOpenFLUID()
                        self.buildPyOpenFLUID()
                        self.testPyOpenFLUID()
                        self.packagePyOpenFLUID()

                    elif Repo == "openfluidjs_repos":
                        self.buildOpenFLUIDJS()
                        self.testOpenFLUIDJS()
                        self.packageOpenFLUIDJS()

                    else:
                        logging.warning("%s not handled yet"%Repo)

        if self.BuildType == "test":
            self.testOpenFLUID()
            

        self.summaryGeneration()
        logging.info("End of BuildMachine procedure, env: %s"%str(self.EnvInfos))

    ########################################

    def getLogFileName(self, Step):
        """Generate the full log file corresponding to the given step"""
        return os.path.join(self.LogPath, "%s.txt"%Step)

    ########################################

    def logCommand(self, Step, Command, Title="", CommandCwd='', NeedEnv=False):
        """Run a shell command in the "CommandCwd" directory and log the output"""
        InitTime = time.time()
        if CommandCwd=='':
            CommandCwd=self.OpenFLUIDBuildPath

        FilePath = self.getLogFileName(Step)

        if Title != "":
            LogHeader = utils.printStage(Title)
            utils.addToLogFile(FilePath, LogHeader)

        # check if CommandCwd exists
        if not os.path.exists(CommandCwd):
            utils.addToLogFile(FilePath, "Directory '%s' does not exist. Command canceled."%CommandCwd)
            logging.debug("Returncode %s %d\n"%(Step, -1))
            return -1, round(time.time() - InitTime, 3)

        CustomEnv = os.environ.copy()
        if NeedEnv:
            PreviousPath = ""
            if "LD_LIBRARY_PATH" in CustomEnv:
                PreviousPath = CustomEnv["LD_LIBRARY_PATH"]
            CustomEnv["LD_LIBRARY_PATH"] = os.path.join(self.LocalInstallPath,"lib") + ":" + PreviousPath
            PreviousPath = ""
            if "PATH" in CustomEnv:
                PreviousPath = CustomEnv["PATH"]
            CustomEnv["PATH"] = os.path.join(self.LocalInstallPath,"bin") + ":" + PreviousPath
            CustomEnv["OPENFLUID_INSTALL_PREFIX"] = self.LocalInstallPath

        ReturnCode = utils.subprocessCall(Command, FilePath, CommandCwd, self.OutputInShell, CustomEnv=CustomEnv)
            
        if not self.OutputInShell:
            if ReturnCode == -11: #SIGSEGV
                utils.addToLogFile(FilePath, "FATAL: "+str(ReturnCode)+". Probably segmentation fault.")
            utils.addToLogFile(FilePath, "End of command.") # to have the timestamp of command's end

        logging.debug("Returncode %s %d\n"%(Step, ReturnCode))
        return ReturnCode, round(time.time() - InitTime, 3)

    ########################################

    def logCommandAndCheck(self, Step, Command, Header, CommandCwd='', NeedEnv=False):
        """Wrapper for "logCommand" adding returncode to reporting system"""
        ReturnCode, Seconds = self.logCommand(Step, Command, Header, CommandCwd=CommandCwd, NeedEnv=NeedEnv)
        self.checkStepSuccess(Step, ReturnCode, Seconds)
        return ReturnCode

    ########################################

    def manualLog(self, Step, Title, ReturnCode, MessageOut="", MessageErr=""):
        """Replacement of "logCommandAndCheck" for manual outputs"""
        InitTime = time.time()
        FilePath = self.getLogFileName(Step)

        if Title != "":
            LogHeader = utils.printStage(Title)
            utils.addToLogFile(FilePath, LogHeader)

        if self.OutputInShell:
            print(Message)
        else:
            Outputs = {"ERR":MessageErr, "OUT":MessageOut}
            for Output in ["OUT", "ERR"]:
                if Outputs[Output] != "":
                    utils.addToLogFile(FilePath, Output+":\n"+Outputs[Output])
        utils.addToLogFile(FilePath, "End of command.") # to have the timestamp of command's end

        Seconds = 0
        print("Returncode %s %d\n"%(Step, ReturnCode))
        self.checkStepSuccess(Step, ReturnCode, Seconds)
        return ReturnCode

    ########################################

    def processCommonOptions(self, Options):
        """Convert generic input options into BuildMachine parameters"""
        print("COMMON OPTIONS:")
        print(Options)
        if 'which' in Options and not Options['which'] is None:
            self.BuildType = Options["which"]

        if 'build_jobs' in Options and not Options['build_jobs'] is None:
            self.BuildJobs = Options['build_jobs']

        if 'shell' in Options:
            if Options['shell'] is not None:
                self.OutputInShell = Options['shell']
            
        if 'subrepos_only' in Options and not Options['subrepos_only'] is None:
            self.SubreposOnly = Options['subrepos_only']

        if 'temp_dir' in Options and not Options['temp_dir'] is None:
            self.BaseTempPath = Options['temp_dir']
            self.OpenFLUIDBuildPath = os.path.join(self.BaseTempPath, self.OpenFLUIDBuildSubdir)
            self.LogPath = os.path.join(self.BaseTempPath, self.LogSubdir)
        else:
            raise InputException("ERROR: Can't work without temp_dir information")

        if 'src_dir' in Options and not Options['src_dir'] is None:
            self.SrcPath = Options['src_dir']
        else:
            self.SrcPath = self.BaseTempPath+"/src/"

        for Repo in self.AllRepos:  # openfluid_repos, ropenfluid_repos, pyopenfluid_repos
            RepoName = Repo.split("_")[0]

            if Repo in Options and not Options[Repo] is None:
                if Options[Repo][0] == "/": # IF LOCAL
                    self.AllCodebaseRepos[Repo] = LocalCodebaseRepos(path=Options[Repo])
                else:
                    FuturePath = os.path.join(self.SrcPath, self.SrcSubDirs[RepoName])

                    if Options[Repo] == "default":
                        RepoInfos = DefaultRepos[Repo]
                    else:
                        RepoInfos = Options[Repo].split("#")
                    if len(RepoInfos) in [1,2]:
                        Branch = None
                        if len(RepoInfos) == 2:
                            Branch = RepoInfos[1]
                        self.AllCodebaseRepos[Repo] = GitRepos(urlPortion=RepoInfos[0], branch=Branch, path=FuturePath)
                    else:
                        raise InputException("Can't parse %s parameter since several ':' symbols in path" % Repo)
                #print("Codebase repo set:", self.AllCodebaseRepos[Repo])
            elif Repo == "openfluid_repos":
                raise InputException("Need a value for %s" % Repo)
            else:
                if Repo in Options and Options[Repo] is None:
                    logging.warning("Repo %s is none"%Repo)
                self.AllCodebaseRepos[Repo] = None

        if 'run_examples' in Options and not Options['run_examples'] is None:
            self.ExamplesCheck = Options['run_examples'].split(",")

        if self.BuildType is not None:
            logging.debug(self.BuildType)
            self.processBuildOptions()

    #####################################

    def processBuildOptions(self):
        """Convert build-related input options into BuildMachine parameters"""

        self.OpenFLUIDCMakeCommands["build"] = ["cmake","--build",self.OpenFLUIDBuildPath]
        self.OpenFLUIDCMakeCommands["test"] = ["ctest"]
        self.OpenFLUIDCMakeCommands["package"] = ["cpack"]

        if self.BuildType == "package":
            self.LocalInstallPath = os.path.join(self.BaseTempPath, "LocalInstall")
            PackageCommand = ["cmake",self.AllCodebaseRepos["openfluid_repos"].LocalPath,"-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_INSTALL_PREFIX="+self.LocalInstallPath]
            self.OpenFLUIDCMakeCommands["configure"] = PackageCommand
        elif self.BuildType == "test":
            self.OpenFLUIDCMakeCommands["configure"] = ["cmake",self.AllCodebaseRepos["openfluid_repos"].LocalPath]

        self.HostInfos['built-packages-dir'] = os.path.join(self.BaseTempPath, "release")
        # TODO
        # set packages dir to "/shared/..." if in container: "/shared/packages-releases" (check if /shared/ exists)

    ######################################

    def findEnvOptions(self):
        """Check what linux is run to set several specific parameters"""
        #Can't use platform lib since some values will be wrong in docker case (parent os will be returned)
        self.EnvInfos = utils.envInfos()

        self.HostInfos["OpenFLUIDInstallCommand"] = ["make", "install"]#self.LocalInstallPath

        if self.EnvInfos["distrib"] == "ubuntu":
            self.HostInfos["PackagesExt"] = "deb"
            #self.HostInfos["OpenFLUIDInstallCommand"] = ["/usr/bin/sudo","/usr/bin/dpkg","--install","@PACKAGING_FILE@"]
            self.OpenFLUIDCMakeCommands["package"] = ["cpack","-G","DEB"]

        elif self.EnvInfos["distrib"] == "fedora":
            self.HostInfos["PackagesExt"] = "rpm"
            #self.HostInfos["OpenFLUIDInstallCommand"] = ["/usr/bin/sudo","/usr/bin/rpm","--install","@PACKAGING_FILE@"]
            self.OpenFLUIDCMakeCommands["package"] = ["cpack","-G","RPM"]

        else:
            raise Exception("OS not recognized")

        """if self.EnvInfos["distrib"] in ["ubuntu", "fedora"]:
            if self.BuildType == "package":
                self.OpenFLUIDCMakeCommands["configure"].append("-DCMAKE_INSTALL_PREFIX=/usr")"""

    ########################################

    def setupRepos(self, TriggerClone=True):
        """Generate directories and clone OpenFLUID when needed"""
        # set up log folder
        utils.resetDirectory(self.BaseTempPath, Purge=False)  # No purge to avoid data erasing on the temp directory
        logging.info("LOGPATH:||%s||"%self.LogPath)
        utils.resetDirectory(self.LogPath, Purge=False)  # Purge of the log directory (disabled)

        # if git, set up source folder
        if not self.SubreposOnly:
            if self.AllCodebaseRepos["openfluid_repos"].Origin == "GitHub" and TriggerClone:
                self.cloneOpenFLUID()

    #######################################

    def setupChildRepos(self, Repo):
        """Clone OpenFLUID-related repositories (ropenfluid, pyopenfluid)"""

        self.ReposIndex = dict()
        self.ReposIndex["ropenfluid_repos"] = ("R", "ropenfluid")
        self.ReposIndex["pyopenfluid_repos"] = ("P", "pyopenfluid")
        self.ReposIndex["openfluidjs_repos"] = ("J", "openfluidjs")

        if self.AllCodebaseRepos[Repo].Origin == "GitHub":
            Step = self.ReposIndex[Repo][0]+"1_Fetch"
            self.cloneProcedure(Step, RepoKey=self.ReposIndex[Repo][1])

        # TODO check that folder really exists (especially when not in clone case)

    #######################################

    def cloneProcedure(self, Step, RepoKey):
        """Execute the cloning git shell command and fetch output"""
        CodebaseRep = self.AllCodebaseRepos[RepoKey+"_repos"]

        FullGithubURL = "https://github.com/%s" % CodebaseRep.GitRepos

        if os.path.isdir(CodebaseRep.LocalPath):
            print("REPO EXISTS", CodebaseRep.LocalPath)
            # remove previous repo dir if existing
            #shutil.rmtree(CodebaseRep.LocalPath)


        Command = ["git","clone", FullGithubURL, "--progress",self.SrcSubDirs[RepoKey]]
        Header = "Cloning from %s" % (FullGithubURL)
        ReturnCode = self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.SrcPath)

        if ReturnCode == 0:
            if not os.path.exists(CodebaseRep.LocalPath): # verify if folder correctly created when clone successful
                raise GitException("Local path %s non-existent after clone procedure. Abort."%CodebaseRep.LocalPath)

        if CodebaseRep.Branch is not None:
            Command = ["git","checkout", CodebaseRep.Branch, "--progress"]
            Header = "Checking out '%s'" % (CodebaseRep.Branch)
            self.logCommandAndCheck(Step, Command, Header, CommandCwd=CodebaseRep.LocalPath)

    #######################################

    def cloneOpenFLUID(self):
        """Trigger the OpenFLUID cloning step"""
        Step = "1_Fetch"
        self.cloneProcedure(Step, RepoKey="openfluid")

    ########################################

    def cloneROpenFLUID(self):
        """Trigger the ROpenFLUID cloning step"""
        Step = "R1_Fetch"
        self.cloneProcedure(Step, RepoKey="ropenfluid")

    ########################################

    def configureOpenFLUID(self):
        """Trigger the OpenFLUID configuration step"""
        Step = "2_Configure"
        utils.resetDirectory(self.OpenFLUIDBuildPath, Purge=True)
        Command = self.OpenFLUIDCMakeCommands["configure"]
        Header = "Configuring OpenFLUID for %s build from %s via command %s"%(self.BuildType,self.BaseTempPath,Command)
        self.logCommandAndCheck(Step, Command, Header)

    ########################################

    def buildOpenFLUID(self):
        """Trigger the OpenFLUID building step"""
        Step = "3_Build"
        Command = self.OpenFLUIDCMakeCommands["build"] + ["--","-j",str(self.BuildJobs)]
        Header = "Building OpenFLUID"
        self.logCommandAndCheck(Step, Command, Header)

    ########################################

    def packageOpenFLUID(self):
        """Trigger the OpenFLUID packaging step"""
        Step = "4_Package"
        Command = self.OpenFLUIDCMakeCommands["package"]
        Header = "Packaging OpenFLUID"
        self.logCommandAndCheck(Step, Command, Header)

        if not os.path.isdir(self.HostInfos['built-packages-dir']):
            os.makedirs(self.HostInfos['built-packages-dir'])

        for f in os.listdir(self.OpenFLUIDBuildPath):
            if f.endswith(".%s" % self.HostInfos["PackagesExt"]):
                shutil.copy(self.OpenFLUIDBuildPath+"/"+f,self.HostInfos['built-packages-dir']+"/"+f)

    ########################################

    def installOpenFLUID(self):
        """Trigger the OpenFLUID installing step"""
        # TODO make this step optional
        Step = "5_Install"
        Header = "Installing OpenFLUID"

        PackageFound = False

        for f in os.listdir(self.OpenFLUIDBuildPath):
            if f.endswith(".%s" % self.HostInfos["PackagesExt"]):
                PackageFound = True
                Command = self.HostInfos["OpenFLUIDInstallCommand"][:]
                for Part in range(len(Command)):
                    Command[Part] = Command[Part].replace("@PACKAGING_FILE@",f)

                self.logCommandAndCheck(Step, Command, Header)

        if not PackageFound:
            #raise ProcedureException("ERROR: No package found for installation")
            self.manualLog(Step, Header, 1, MessageErr="[BuildMachine] No package found for installation")

    ########################################

    def checkExamplesOpenFLUID(self):
        """Trigger the OpenFLUID checking step via example(s) running"""
        #self.ExamplesPath = os.path.join(self.AllCodebaseRepos["openfluid_repos"].LocalPath, "examples", "projects")
        
        WantedExamples = self.ExamplesCheck
        Step = "6_Example"
        logging.info("Check examples in folder %s"%self.ExamplesPath)
        if WantedExamples == ["*"]:
            WantedExamples = utils.findSubdirs(self.ExamplesPath)    # takes all examples subdirs
            if not WantedExamples:
                self.manualLog(Step, "", 1, MessageErr="[BuildMachine] No example found.")
        for Example in WantedExamples:
            self.triggerExamplesOpenFLUID(Step, Example)

    ########################################

    def triggerExamplesOpenFLUID(self, Step, Example):
        """Run OpenFLUID with a given example"""
        Header = "Launching OpenFLUID example *%s*"%Example
        Command = ["openfluid", "run", os.path.join(self.ExamplesPath, Example, "IN"), os.path.join(self.BaseTempPath, "Examples","%s.OUT"%Example)]
        try:
            self.logCommandAndCheck(Step, Command, Header)
        except FileNotFoundError as Inst:
            self.manualLog(Step, "", 1, MessageErr="[BuildMachine] FileNotFoundError : %s"%Inst)

    ########################################

    def testOpenFLUID(self):
        """Trigger the OpenFLUID cmake test step"""
        Step = "4_Test"
        Command = self.OpenFLUIDCMakeCommands["test"]
        Header = "Running OpenFLUID tests"
        self.logCommandAndCheck(Step, Command, Header)

    ########################################

    def checkROpenFLUID(self):
        """Trigger the ROpenFLUID check step"""
        Step = "R2_Check"
        Command = self.ROpenFLUIDCMakeCommands["check"]
        Header = "Checking ROpenFLUID"
        RRepos = self.AllCodebaseRepos["ropenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=RRepos, NeedEnv=True)

    ########################################

    def buildROpenFLUID(self):
        """Trigger the ROpenFLUID build step"""
        Step = "R3_Build"
        Command = self.ROpenFLUIDCMakeCommands["build"]
        Header = "Building ROpenFLUID"
        RRepos = self.AllCodebaseRepos["ropenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=RRepos, NeedEnv=True)

    ########################################

    def checkPyOpenFLUID(self):
        """Trigger the PyOpenFLUID check step"""
        Step = "P2_Check"
        Command = ["python3", "setup.py", "check"]
        Header = "Checking PyOpenFLUID"
        PyRepos = self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=PyRepos, NeedEnv=True)

    ########################################

    def buildPyOpenFLUID(self):
        """Trigger the PyOpenFLUID build step"""
        Step = "P3_Build"
        Command = ["python3", "setup.py", "build"]    # TODO Clean build dir every time?
        Header = "Building PyOpenFLUID"
        PyRepos = self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=PyRepos, NeedEnv=True)

    ########################################

    def testPyOpenFLUID(self):
        """Trigger the PyOpenFLUID test step"""
        Step = "P4_Test"
        Command = ["python3", "setup.py", "build", "test"]
        Header = "Testing PyOpenFLUID"
        PyRepos = self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=PyRepos, NeedEnv=True)

    ########################################

    def packagePyOpenFLUID(self):
        """Trigger the PyOpenFLUID package step"""
        Step = "P5_Package"
        Command = ["python3", "setup.py", "sdist", "bdist"]
        Header = "Packaging PyOpenFLUID"
        PyRepos = self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=PyRepos, NeedEnv=True)

    ########################################

    def buildOpenFLUIDJS(self):
        """Trigger the OpenFLUIDJS build step"""
        Step = "J3_Build"
        # TODO GERER CAS ABSENCE NPM AVEC EXCEPTION
        Command = ["npm", "install"]
        Header = "Building OpenFLUIDJS"
        JSRepos = self.AllCodebaseRepos["openfluidjs_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=JSRepos, NeedEnv=True)
        

    ########################################

    def testOpenFLUIDJS(self):
        """Trigger the OpenFLUIDJS test step"""
        Step = "J4_Test"
        Command = ["npm", "test"]
        Header = "Testing OpenFLUIDJS"
        JSRepos = self.AllCodebaseRepos["openfluidjs_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=JSRepos, NeedEnv=True)

    ########################################

    def packageOpenFLUIDJS(self):
        """Trigger the OpenFLUIDJS package step"""
        Step = "J5_Package"
        Command = ["npm", "pack"]
        Header = "Packaging OpenFLUIDJS"
        JSRepos = self.AllCodebaseRepos["openfluidjs_repos"].LocalPath
        self.logCommandAndCheck(Step, Command, Header, CommandCwd=JSRepos, NeedEnv=True)

    ########################################

    def checkStepSuccess(self, Step, ReturnCode, Seconds):
        """Deduce a step success depending on the return code or target string"""
        IsSuccess = False
        if Step in StepSuccessStrings or Step in StepFailStrings:
            FilePath = self.getLogFileName(Step)
            FileFound = True
            try:
                FileObject = open(FilePath)
                FileContent = FileObject.read()
            except OSError:
                logging.warning("Can't find file %s" % FilePath)
                FileFound = False

        if Step in StepSuccessStrings:
            if FileFound:
                IsSuccess = StepSuccessStrings[Step] in FileContent
        elif ReturnCode == 0:
            IsSuccess = True
        
        if Step in StepFailStrings:
            if FileFound:
                IsSuccess = IsSuccess and not(StepFailStrings[Step] in FileContent)
                
        if Step in StepSuccessStrings or Step in StepFailStrings:
            FileObject.close()

        if Step in self.StatusTable:
            Seconds += self.StatusTable[Step]["Duration"]
            IsSuccess = IsSuccess and self.StatusTable[Step]["ReturnCode"]
        self.StatusTable[Step] = {"ReturnCode": IsSuccess, "Duration": Seconds}
        return IsSuccess

    ########################################

    def summaryGeneration(self, InShell=False, asReturn=False):
        """Create a summary of every steps, output as HTML and JSON files or returns direct dictionnary"""
        Metadata = dict()
        Metadata["execution_timestamps"] = {'begin': self.InitBuildTimestamp, 'end': utils.currentTimestamp()}

        Dir = self.LogPath
        if asReturn:
            return utils.procedureDict(self.StatusTable, Metadata=Metadata)
        elif InShell:
            Dir = ""
        utils.procedureSummary(self.StatusTable, OutputDir=Dir, LogDir=self.LogPath, Metadata=Metadata)
