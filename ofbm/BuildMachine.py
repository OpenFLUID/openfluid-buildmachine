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
import datetime
import time
import platform
import json


# Success check when can not be found through return code

StepSuccessStrings = dict()
StepSuccessStrings["4_Test"] = "100% tests passed" # necessary since sometimes 0 returned with no test done
StepSuccessStrings["6_Example"] = "**** Simulation completed ****" # TODO status code for simulation?

DefaultRepos = dict()  # possibility to set DefaultRepos["foo"] = [urlPortion, Branch] if wanted
DefaultRepos["ropenfluid_repos"] = ["OpenFLUID/ropenfluid"]
DefaultRepos["pyopenfluid_repos"] = ["OpenFLUID/pyopenfluid"]

############################################################################
############################################################################

class InputException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

############################################################################

class GitException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

############################################################################

class ProcedureException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

############################################################################
############################################################################


class LocalCodebaseRepos :
    
  def __init__(self, path, origin="Local"):
        
    self.Origin = origin  # "GitHub" or "Local"
    self.LocalPath = path
  
  def __str__(self):
    info = "Origin: %s\nLocal path: %s"%(self.Origin, self.LocalPath)
    return info
      

############################################################################


class GitRepos(LocalCodebaseRepos) :
    
  def __init__(self, urlPortion, path, branch=None):
    
    LocalCodebaseRepos.__init__(self, path, origin="GitHub")
    self.GitRepos = urlPortion
    self.Branch = branch
  
  def __str__(self):
    info = "Github Repo: %s"%self.GitRepos
    if self.Branch is not None:
      info += "\nGithub Branch: %s"%self.Branch
    return LocalCodebaseRepos.__str__(self)+"\n"+info
    

############################################################################
############################################################################

def currentTimestamp():

  return str(datetime.datetime.now()).split(".")[0]

##############################################################

def envInfos():
    
  EnvInfos = dict()
  
  f = open("/etc/os-release", "r")
  fl = f.readlines()
  f.close()
  for l in fl:
    lst = l.rstrip()
    if "ID" == l.split("=")[0]:
      EnvInfos["distrib"] = lst.split("=")[1]
    elif "VERSION_ID" == l.split("=")[0]:
      EnvInfos["version"] = lst.split("=")[1]
      if '"' in EnvInfos["version"]:
          EnvInfos["version"] = EnvInfos["version"][1:-1]
          
  #EnvInfos["proc"] = platform.machine() #not even necessary
  
  return EnvInfos

##############################################################

def resetDirectory(Path, Purge=False):
  
  NeedCreation = True
  
  if os.path.isdir(Path):
    if Purge:
      shutil.rmtree(Path)
    else:
      NeedCreation = False
  
  if NeedCreation:
    os.makedirs(Path)
    print("Made PATH %s"%Path)
  

###################################


def addToLogFile(StepFile, Content, TS=0):
  
  try:
    f = open(StepFile, "a+")
  except:
    print("Can't open log file %s"%StepFile)
    return 1
  if TS == 0:
    TS = currentTimestamp()
  f.write("%s\t%s\n"%(TS, Content))
  f.close()

############################################################################

def procedureSummary(StatusTable, OutputDir=".", LogDir="", Metadata={}):
  
  """Generates a synthesis of steps and write it in json in a file"""
  
  Steps = list(StatusTable.keys())
  Steps.sort()
  
  if OutputDir is None or OutputDir == "":
    
    print("\n** Build-machine summary **")  
    for Step in Steps:
      Tag, StepName = Step.split("_")
      Prefix = ""
      if len(Tag) > 1:
        Prefix = Tag[0]+"-"
      else:
        Prefix = "OF-"
      print("%s%s\t%r"%(Prefix, StepName, StatusTable[Step]))
    print("-"*10)
  
  else:
    ### Json generation
    print("\nGenerates Build-machine summary...")
    Procedure = {}
    if Metadata != {}:
      Procedure["metadata"] = Metadata
    Procedure["steps"] = []
    for Step in Steps:
      Number, Name = Step.split("_")
      Procedure["steps"].append({
        "number":Number,
        "name":Name,
        "success":StatusTable[Step]["ReturnCode"],
        "duration":StatusTable[Step]["Duration"]
      })
  
    ReportName = 'report.json'
    JsonFile = os.path.join(OutputDir, ReportName)
    with open(JsonFile, 'w') as Outfile:  
      json.dump(Procedure, Outfile)
    
    print("%s generated."%ReportName)
    
    ### Generates html
    HtmlContent = "<table>\n"
    HtmlContent += "  <tr><td>Step</td><td>Duration (s)</td><td>Success</td><td>Log file</td></tr>\n"
    for Step in Steps:
      LogPath = os.path.join(LogDir, "%s.txt"%Step)
      HtmlContent += "  <tr>\n"
      Tag, StepName = Step.split("_")
      Prefix = ""
      if len(Tag) > 1:
        Prefix = Tag[0]+"-"
      else:
        Prefix = "OF-"
       
      if StatusTable[Step]["ReturnCode"]:  # when success
        SuccessHtml = "OK"
        Color = "blue"
      else:
        SuccessHtml = "KO"
        Color = "Red"
      
      HtmlContent += "\t<td>%s%s</td>\n\t<td>%.3f</td>\n\t<td style='color:%s;'>%s</td>\n\t<td><a href='%s'>log</a></td>\n"%(Prefix, StepName, StatusTable[Step]["Duration"], Color, SuccessHtml, LogPath)
      HtmlContent += "  </tr>\n"
    HtmlContent += "</table>\n"
    HtmlPath = os.path.join(OutputDir, "report.html")
    f = open(HtmlPath, "w") #TODO change location (or duplicate)
    f.write(HtmlContent)
    f.close()
    print("file://%s written."%HtmlPath)

############################################################################
############################################################################


class BuildMachine :

  def __init__(self,args, AutoTrigger=True):
    
    self.InitBuildTimestamp = currentTimestamp()
    # CONSTANTS
    self.BaseRepos = ['openfluid_repos'] # Related to parser fields
    self.ChildrenRepos = ['ropenfluid_repos', 'pyopenfluid_repos'] # Related to parser fields
    self.AllRepos = self.BaseRepos + self.ChildrenRepos
    ## OF
    self.SrcSubDirs = dict()
    self.SrcSubDirs["openfluid"] = 'openfluid-src'
    self.OpenFLUIDBuildSubdir = 'openfluid-build'
    ## ROF
    self.SrcSubDirs["ropenfluid"] = 'ropenfluid-src'
    self.SrcSubDirs["pyopenfluid"] = 'pyopenfluid-src'
    ## MACHINE LOGS
    self.LogSubdir = '_log_%s'%str(time.time()).split(".")[0]
    
    # PARAMETERS
    self.BuildType = None
    self.AllCodebaseRepos = dict()
    self.BuildJobs = 1
    
    self.OutputInShell = False
    
    self.HostInfos = {}
    self.OpenFLUIDCMakeCommands = dict()
    self.ExamplesCheck = []
    
    # STATUS Check
    self.StatusTable = {}
    
    # run prebuild actions
    
    #del args["which"]
    self.ROpenFLUIDCMakeCommands = dict()
    self.ROpenFLUIDCMakeCommands["check"] = ["cmake","-P","check.cmake"]
    self.ROpenFLUIDCMakeCommands["build"] = ["cmake","-P","build.cmake"]
    self.processCommonOptions(args)
    self.findEnvOptions()
    
    
    if self.BuildType is not None and AutoTrigger:
        self.triggerProcedure()
  
  ########################################
  
  def triggerProcedure(self):
    
    self.setupRepos()
    
    # Openfluid management
    
    self.configureOpenFLUID()
    self.buildOpenFLUID()
    
    if self.BuildType == "package":
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
          
          else:
            print(Repo, "not handled yet")
      
    if self.BuildType == "test":
      self.testOpenFLUID()
    
    self.summaryGeneration()
    self.summaryGeneration(InShell=True)
      
  ########################################
  
  def printStage(self, Text):

    print("################################################################")
    print(" "+Text)
    print("################################################################")
    
    return "# "+Text
  
  ########################################
  
  def getLogFileName(self, Step):
      return os.path.join(self.LogPath, "%s.txt"%Step)
  
  ########################################
  
  def logCommand(self, Step, Command, Title="", CommandCwd=''):
    
    InitTime = time.time()
    if CommandCwd=='':
      CommandCwd=self.OpenFLUIDBuildPath
    
    FilePath = self.getLogFileName(Step)
    
    if Title != "":
      LogHeader = self.printStage(Title)
      addToLogFile(FilePath, LogHeader)

    # check if CommandCwd exists
    if not os.path.exists(CommandCwd):
      addToLogFile(FilePath, "Directory '%s' does not exist. Command canceled."%CommandCwd)  
      print("Returncode %s %d\n"%(Step, -1))
      return -1, round(time.time() - InitTime, 3)
  
    if self.OutputInShell:
      P = subprocess.Popen(Command,cwd=CommandCwd)
      P.wait()
    
    else:
      P = subprocess.Popen(Command,cwd=CommandCwd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
      out, err = P.communicate()
      Outputs = {"ERR":err, "OUT":out}
      for Output in ["OUT", "ERR"]:
        if type(Outputs[Output]) != str:
          Outputs[Output] = Outputs[Output].decode("utf-8")
        if len(Outputs[Output]) > 0:
          addToLogFile(FilePath, Output+":\n"+Outputs[Output])
      
      if P.returncode == -11: #SIGSEGV
        addToLogFile(FilePath, "FATAL: "+str(P.returncode)+". Probably segmentation fault.")
      addToLogFile(FilePath, "End of command.") # to have the timestamp of command's end
      
    print("Returncode %s %d\n"%(Step, P.returncode))
    return P.returncode, round(time.time() - InitTime, 3)
  
  ########################################
    
  def logCommandAndCheck(self, Step, Command, Header, CommandCwd=''):
    
    ReturnCode, Seconds = self.logCommand(Step, Command, Header, CommandCwd=CommandCwd)
    self.checkStepSuccess(Step, ReturnCode, Seconds)
    return ReturnCode
  
  ########################################
  
  def processCommonOptions(self, Options):
    
    if 'which' in Options and not Options['which'] is None:
      self.BuildType = Options["which"]

    if 'build_jobs' in Options and not Options['build_jobs'] is None:
      self.BuildJobs = Options['build_jobs']
    
    if 'shell' in Options and not Options['shell'] is None:
      self.OutputInShell = Options['shell']

    if 'temp_dir' in Options and not Options['temp_dir'] is None:
      self.BaseTempPath = Options['temp_dir']
      self.OpenFLUIDBuildPath = os.path.join(self.BaseTempPath, self.OpenFLUIDBuildSubdir)
      self.LogPath = os.path.join(self.BaseTempPath, self.LogSubdir)
    else:
      raise InputException("ERROR: Can't work without temp_dir information")

    if 'home_dir' in Options and not Options['home_dir'] is None:
      self.HomePath = Options['home_dir']
    else:
      self.HomePath = os.path.join(expanduser("~"),".openfluid")

    for Repo in self.AllRepos: #openfluid_repos, ropenfluid_repos, pyopenfluid_repos
      RepoName = Repo.split("_")[0]
      
      if Repo in Options and not Options[Repo] is None:
        if Options[Repo][0] == "/": # IF LOCAL
          self.AllCodebaseRepos[Repo] = LocalCodebaseRepos(path=Options[Repo])
        else:
          FuturePath = os.path.join(self.BaseTempPath, self.SrcSubDirs[RepoName])
          
          if Options[Repo] == "default":
            RepoInfos = DefaultRepos[Repo]
          else:
            RepoInfos = Options[Repo].split(":")
          if len(RepoInfos) in [1,2]:
            Branch = None
            if len(RepoInfos) == 2:
              Branch = RepoInfos[1]
            self.AllCodebaseRepos[Repo] = GitRepos(urlPortion=RepoInfos[0], branch=Branch, path=FuturePath)
          else:
            raise InputException("Can't parse %s parameter since several ':' symbols in path"%Repo)
        #print("Codebase repo set:", self.AllCodebaseRepos[Repo])
      elif Repo == "openfluid_repos":
        raise InputException("Need a value for %s"%Repo)
      else:
        if Repo in Options and Options[Repo] is None:
          print(Repo, "none")
        self.AllCodebaseRepos[Repo] = None
      
      
    if 'examples' in Options and not Options['examples'] is None:
      self.ExamplesCheck = Options['examples'].split(",")
      
    if self.BuildType is not None:
      print(self.BuildType)
      self.processBuildOptions()    
  
  
  #####################################
  
  def processBuildOptions(self):
    
    self.OpenFLUIDCMakeCommands["build"] = ["cmake","--build",self.OpenFLUIDBuildPath]
    self.OpenFLUIDCMakeCommands["test"] = ["ctest"]
    self.OpenFLUIDCMakeCommands["package"] = ["cpack"]
    
    if self.BuildType == "package":
      self.OpenFLUIDCMakeCommands["configure"] = ["cmake",self.AllCodebaseRepos["openfluid_repos"].LocalPath,"-DCMAKE_BUILD_TYPE=Release"]
    elif self.BuildType == "test":
      self.OpenFLUIDCMakeCommands["configure"] = ["cmake",self.AllCodebaseRepos["openfluid_repos"].LocalPath]
      
    self.HostInfos['built-packages-dir'] = os.path.join(self.BaseTempPath, "packages-releases")
    # TODO set packages dir to "/shared/..." if in container: "/shared/packages-releases" (check if /shared/ exists)

  
  ######################################
  
  def findEnvOptions(self):
    """check what linux is run to set several specific parameters"""
    #Can't use platform lib since some values will be wrong in docker case (parent os will be returned)
    self.EnvInfos = envInfos()
    
    print(self.EnvInfos)
    
    if self.EnvInfos["distrib"] == "ubuntu":
      self.HostInfos["PackagesExt"] = "deb"
      self.HostInfos["OpenFLUIDInstallCommand"] = ["/usr/bin/sudo","/usr/bin/dpkg","--install","@PACKAGING_FILE@"]
      self.OpenFLUIDCMakeCommands["package"] = ["cpack","-G","DEB"]
      
    elif self.EnvInfos["distrib"] == "fedora":
      self.HostInfos["PackagesExt"] = "rpm"
      self.HostInfos["OpenFLUIDInstallCommand"] = ["/usr/bin/sudo","/usr/bin/rpm","--install","@PACKAGING_FILE@"]
      self.OpenFLUIDCMakeCommands["package"] = ["cpack","-G","RPM"]
      
    else:
      raise Exception("OS not recognized")

    if self.EnvInfos["distrib"] in ["ubuntu", "fedora"]:
      if self.BuildType == "package":
        self.OpenFLUIDCMakeCommands["configure"].append("-DCMAKE_INSTALL_PREFIX=/usr")
  
  ########################################
  
  def setupRepos(self, TriggerClone=True):
      
    # set up log folder
    resetDirectory(self.BaseTempPath) #TODO be less violent for folder cleaning (to avoid data delete)
    resetDirectory(self.LogPath, Purge=True)
    
    # if git, set up source folder
    if self.AllCodebaseRepos["openfluid_repos"].Origin == "GitHub" and TriggerClone:
      self.cloneOpenFLUID()
  
  #######################################
    
  def setupChildRepos(self, Repo):
    
    self.ReposIndex = dict()
    self.ReposIndex["ropenfluid_repos"] = ("R", "ropenfluid")
    self.ReposIndex["pyopenfluid_repos"] = ("P", "pyopenfluid")
    
    if self.AllCodebaseRepos[Repo].Origin == "GitHub":
      Step = self.ReposIndex[Repo][0]+"1_Fetch"
      self.cloneProcedure(Step, RepoKey=self.ReposIndex[Repo][1])
    
    # TODO check that folder really exists (especially when not in clone case)
    
  #######################################
  
  def cloneProcedure(self, Step, RepoKey):
    
    CodebaseRep = self.AllCodebaseRepos[RepoKey+"_repos"]
    
    FullGithubURL = "https://github.com/%s" % CodebaseRep.GitRepos
    
    Command = ["git","clone", FullGithubURL, "--progress",self.SrcSubDirs[RepoKey]]
    Header = "Cloning from %s" % (FullGithubURL)
    ReturnCode = self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.BaseTempPath)
    
    if ReturnCode == 0:
      if not os.path.exists(CodebaseRep.LocalPath): # verify if folder correctly created when clone successful
        raise GitException("Local path %s non-existent after clone procedure. Abort."%CodebaseRep.LocalPath)
    
    if CodebaseRep.Branch is not None:
      Command = ["git","checkout", CodebaseRep.Branch, "--progress"]
      Header = "Checking out '%s'" % (CodebaseRep.Branch)
      self.logCommandAndCheck(Step, Command, Header, CommandCwd=CodebaseRep.LocalPath)
    
    
  #######################################
  
  def cloneOpenFLUID(self):
    
    Step = "1_Fetch"
    self.cloneProcedure(Step, RepoKey="openfluid")
  
  ########################################
  
  def cloneROpenFLUID(self):

    Step = "R1_Fetch"
    self.cloneProcedure(Step, RepoKey="ropenfluid")
  
  ########################################
  
  def configureOpenFLUID(self):
    
    Step = "2_Configure"
    resetDirectory(self.OpenFLUIDBuildPath, Purge=True)
    Command = self.OpenFLUIDCMakeCommands["configure"]
    Header = "Configuring OpenFLUID for %s build"%self.BuildType
    self.logCommandAndCheck(Step, Command, Header)
  
  ########################################
  
  def buildOpenFLUID(self):
    
    Step = "3_Build"
    Command = self.OpenFLUIDCMakeCommands["build"] + ["--","-j",str(self.BuildJobs)]
    Header = "Building OpenFLUID"
    self.logCommandAndCheck(Step, Command, Header)
  
  ########################################
  
  def packageOpenFLUID(self):
    
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
      raise ProcedureException("ERROR: No package found for installation")
    
  
  ########################################
  
  def checkExamplesOpenFLUID(self):
    
    for Example in  self.ExamplesCheck:
      self.triggerExamplesOpenFLUID(Example)
  
  ########################################
  
  def triggerExamplesOpenFLUID(self, Example):
    
    Step = "6_Example"
    Header = "Launching OpenFLUID example *%s*"%Example
    Command = ["openfluid", "run", os.path.join(self.HomePath, "examples", "projects", Example, "IN")]
    self.logCommandAndCheck(Step, Command, Header)
    
  ########################################
  
  def testOpenFLUID(self):
    
    Step = "4_Test"
    Command = self.OpenFLUIDCMakeCommands["test"]
    Header = "Running OpenFLUID tests"
    self.logCommandAndCheck(Step, Command, Header)
    
  ########################################
  
  def checkROpenFLUID(self):
    
    Step = "R2_Check"
    Command = self.ROpenFLUIDCMakeCommands["check"]
    Header = "Checking ROpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["ropenfluid_repos"].LocalPath)
    
  ########################################
    
  def buildROpenFLUID(self):
    
    Step = "R3_Build"
    Command = self.ROpenFLUIDCMakeCommands["build"]
    Header = "Building ROpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["ropenfluid_repos"].LocalPath)
     
  ########################################
  
  def checkPyOpenFLUID(self):
    
    Step = "P2_Check"
    Command = ["python3", "setup.py", "check"]
    Header = "Checking PyOpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath)
  
  ########################################
  
  def buildPyOpenFLUID(self):
    
    Step = "P3_Build"
    Command = ["python3", "setup.py", "build"]  # TODO Clean build dir every time?
    Header = "Building PyOpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath)
  
  ########################################
  
  def testPyOpenFLUID(self):
      
    Step = "P4_Test"
    Command = ["python3", "setup.py", "build", "test"]
    Header = "Testing PyOpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath)
  
  ########################################
  
  def packagePyOpenFLUID(self):
    
    Step = "P5_Package"
    Command = ["python3", "setup.py", "sdist", "bdist"]
    Header = "Packaging PyOpenFLUID"
    self.logCommandAndCheck(Step, Command, Header, CommandCwd=self.AllCodebaseRepos["pyopenfluid_repos"].LocalPath)
  
  ########################################
  
  def checkStepSuccess(self, Step, ReturnCode, Seconds):  # TODO need test on this part to check if bad steps are detected

    IsSuccess = False
    if Step in StepSuccessStrings:
      FilePath = self.getLogFileName(Step)
      IsSuccess = StepSuccessStrings[Step] in open(FilePath).read()
    elif ReturnCode == 0:
      IsSuccess = True
    
    if Step in self.StatusTable:
      Seconds += self.StatusTable[Step]["Duration"]
      IsSuccess = IsSuccess and self.StatusTable[Step]["ReturnCode"]
    self.StatusTable[Step] = {"ReturnCode":IsSuccess, "Duration":Seconds}
    return IsSuccess
  
  ########################################
  
  def summaryGeneration(self, InShell=False):
    Metadata = dict()
    Metadata["execution_timestamps"] = {'begin':self.InitBuildTimestamp, 'end':currentTimestamp()}
    
    Dir = self.LogPath
    if InShell:
      Dir = ""
    procedureSummary(self.StatusTable, OutputDir=Dir, LogDir=self.LogPath, Metadata=Metadata)