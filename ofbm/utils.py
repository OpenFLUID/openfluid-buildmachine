#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__ = "armel.thoni@inra.fr"


import datetime
import os
import json
import shutil


def currentTimestamp(noSpace=False):
  TS = str(datetime.datetime.now()).split(".")[0]
  if noSpace:
    return TS.replace(" ","_").replace(":","-")
  else:
    return TS


############################################################################


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


############################################################################


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

  
############################################################################


def printStage(Text):

  print("################################################################")
  print(" "+Text)
  print("################################################################")
  
  return "# "+Text


############################################################################


def addToLogFile(StepFile, Content, TS=0):
  
  try:
    f = open(StepFile, "a+")
  except:
    raise Exception("Can't open log file %s"%StepFile)
  
  if TS == 0:
    TS = currentTimestamp()
  
  f.write("%s\t%s\n"%(TS, Content))
  f.close()


############################################################################


def findSubdirs(path):
  return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]
  
  
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
    f = open(HtmlPath, "w")
    f.write(HtmlContent)
    f.close()
    
    print("file://%s written."%HtmlPath)