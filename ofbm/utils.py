#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__ = "armel.thoni@inra.fr"


import datetime
import os
import json
import shutil
import subprocess

import logging

def currentTimestamp(noSpace=False):

    TS = str(datetime.datetime.now()).split(".")[0]
    if noSpace:
        return TS.replace(" ", "_").replace(":", "-")
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

    return EnvInfos


############################################################################


def resetDirectory(Path, Purge=False, Verbose=True):

    NeedCreation = True

    if os.path.isdir(Path):
        if Purge:
            shutil.rmtree(Path)
        else:
            NeedCreation = False

    if NeedCreation:
        os.makedirs(Path)
        if Verbose:
            maxLen = 50
            if len(Path) > maxLen:
                print("-- Created path: ...%s" % Path[-50:])
            else:
                print("-- Created path: %s" % Path[-30:])


############################################################################


def printStage(Text):

    print("################################################################")
    print(" "+Text)
    print("################################################################")

    return "# "+Text


############################################################################
outputLogRedirect = {"OUT":logging.info, "ERR":logging.error}

def subprocessCall(Command, FilePath="", CommandCwd=".", OutputInShell=False, OutputAsReturn=False, CustomEnv=None): # TODO check if "." == os.getcwd() in every case

    mergeLogs = True
    ReturnCode = 1
    out, err = "", ""
    if OutputInShell:
        try:
            P = subprocess.Popen(Command,cwd=CommandCwd, env=CustomEnv)
            P.wait()
            out = "No logged output since option --shell activated."
            ReturnCode = P.returncode
        except OSError as e:
            print(e)
    else:
        try:
            if mergeLogs:
                P = subprocess.Popen(Command,cwd=CommandCwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=CustomEnv)
                out = P.communicate()[0]
            else:
                P = subprocess.Popen(Command,cwd=CommandCwd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=CustomEnv)
                out, err = P.communicate()
            ReturnCode = P.returncode
        except OSError as e:
            print(e)
            out, err = "", str(e)

    Outputs = {"ERR":err, "OUT":out}
    for Output in ["OUT", "ERR"]:
        if type(Outputs[Output]) != str:
            Outputs[Output] = Outputs[Output].decode("utf-8")
        if len(Outputs[Output]) > 0:
            if FilePath != "":
                addToLogFile(FilePath, Output+":\n"+Outputs[Output])
            else:
                outputLogRedirect[Output](Outputs[Output])
    if OutputAsReturn:
        return Outputs
            
    return ReturnCode

############################################################################


def addToLogFile(StepFile, Content, TS=0):

    try:
        f = open(StepFile, "a+", encoding="utf8")
    except IOError:
        logging.warning("Can't open log file %s" % StepFile)
        return

    if TS == 0:
        TS = currentTimestamp()

    Line = str(TS)+"\t"+Content+"\n"
    f.write(Line)
    f.close()


############################################################################


def findSubdirs(path):
    try:
        return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]
    except IOError:
        logging.error("Can't find directory %s" % path)
        return []
        


############################################################################


def procedureDict(StatusTable, Metadata):
    Steps = list(StatusTable.keys())
    Procedure = {}
    if Metadata != {}:
        Procedure["metadata"] = Metadata
    Procedure["steps"] = []
    for Step in Steps:
        Number, Name = Step.split("_")
        Procedure["steps"].append({
            "number": Number,
            "name": Name,
            "success": StatusTable[Step]["ReturnCode"],
            "duration": StatusTable[Step]["Duration"]
        })
    return Procedure


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
            print(" % s%s\t%r" % (Prefix, StepName, StatusTable[Step]))
        print("-"*10)

    else:

        # Json generation
        logging.info("\nGenerates Build-machine summary...")
        Procedure = procedureDict(StatusTable, Metadata)

        ReportName = 'report.json'
        JsonFile = os.path.join(OutputDir, ReportName)
        with open(JsonFile, 'w') as Outfile:
            Outfile.write(json.dumps(Procedure, indent=4))

        logging.info("%s generated." % ReportName)

        # Generates html
        HtmlContent = "<table>\n"
        HtmlContent += "    <tr><td>Step</td><td>Duration (s)</td><td>Success</td><td>Log file</td></tr>\n"
        for Step in Steps:
            LogPath = os.path.join(LogDir, "%s.txt" % Step)
            HtmlContent += "    <tr>\n"
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

            HtmlContent += "\t<td>%s%s</td>\n\t<td>%.3f</td>\n" % (Prefix, StepName, StatusTable[Step]["Duration"])
            HtmlContent += "\t<td style='color:%s;'>%s</td>\n" % (Color, SuccessHtml)
            HtmlContent += "\t<td><a href='%s'>log</a></td>\n" % LogPath
            HtmlContent += "    </tr>\n"
        HtmlContent += "</table>\n"

        HtmlPath = os.path.join(OutputDir, "report.html")
        f = open(HtmlPath, "w")
        f.write(HtmlContent)
        f.close()

        logging.info("file://%s written." % HtmlPath)
