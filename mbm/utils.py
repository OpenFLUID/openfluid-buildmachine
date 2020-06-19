# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os
import json
import yaml
import logging

from mbm import settings


def BMArgsFromParams(GlobalParams, BuildType, SubParserParams):
    ParserInput = ""
    for Param in GlobalParams:
        if Param[1] == "":
            ParserInput += " --%s" % Param[0]
        else:
            ParserInput += " --%s=%s"%(Param[0], Param[1])
    ParserInput += " "+BuildType
    for Param in SubParserParams:
        ParserInput += " --%s=%s"%(Param[0], Param[1])
    return ParserInput


######################################################
######################################################


def importYaml(ConfFile):
    """Returns a dictionnary based on a yaml file"""
    with open(ConfFile, 'r') as stream:
        try:
            Setups = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
    return Setups


######################################################
######################################################


def loadJsonSummary(FullPath):
    with open(FullPath, encoding='utf-8') as JsonFile:
        SummaryDict = json.load(JsonFile)
    return SummaryDict


######################################################
######################################################


def generateMultiBuildHTLMFromJSON(path=settings.OUTPUT_DIR+"/fullreport.json"):
    ProceduresSummary = loadJsonSummary(path)
    constructMultiBuildHTMLSummary(ProceduresSummary)
    

CSS="""table {
  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #ddd;
  padding: 8px;
}

tr:nth-child(even){background-color: #f2f2f2;}

tr:hover {background-color: #ddd;}

th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #47617b;
  color: white;
}

.subheader {
  background-color: #917c6f;
  text-align: center;
}

.ok {
  background-color: #86ae39;
  text-align: center;
}

.ok a {  
  color: green;
}

.ko {
  background-color: #AA3344;
  border-width: 2px;
  border-color: red;
}
"""


def constructMultiBuildHTMLSummary(ProceduresSummary, OutDir=".", LogFile=""):
    ### Generates html
    HtmlContent = "<style>%s</style>"%CSS
    if LogFile != "":
        HtmlContent += '<p><a href="%s">General logs</a></p>\n'%LogFile
    HtmlContent += '<div style="overflow-x:auto;">\n<table>\n'
    HtmlContent += "  <tr>\n"

    AllSteps = []
    for Build in ProceduresSummary:
        for Step in Build["steps"]:
            StepId = (Step["number"], Step["name"])
            if StepId not in AllSteps:
                AllSteps.append(StepId)

    HtmlContent += "<th>Build</th><th>Context</th>"
    for Step in AllSteps:
      HtmlContent += "<th>%s - %s</th>"%(Step[0], Step[1])
    HtmlContent += "</tr>\n"

    Category = ""
    for Build in ProceduresSummary:
        CurrentCategory = Build["metadata"]["setup"]["temp-dir"].split("/")[-1]
        if CurrentCategory != Category:
            Category = CurrentCategory
            HtmlContent += '  <tr><td colspan="2" class="subheader">%s</td></tr>\n'%Category#tr></tr>
        HtmlContent += "  <tr>\n    <td>%s</td><td>%s</td>"%(Build["metadata"]["setup"]["build-type"],
                                                             Build["metadata"]["context"])
        for Step in AllSteps:
            StatusClass, SuccessHtml = "", ""
            Color = "gray"
            for BuildStep in Build["steps"]:
                if BuildStep["number"] == Step[0] and BuildStep["name"] == Step[1]:
                    if BuildStep["success"]:
                        SuccessHtmlTxt = "OK"
                        StatusClass = "ok"
                    else:
                        SuccessHtmlTxt = "KO"
                        StatusClass = "ko"
                    if Build["metadata"]["log-path"]:
                        LogPath = os.path.join(Build["metadata"]["log-path"], "_".join([BuildStep["number"], BuildStep["name"]])+".txt")
                        SuccessHtml = "<a href='%s'>%s</a>"%(LogPath, SuccessHtmlTxt)
                    else:
                        SuccessHtml = SuccessHtmlTxt
            HtmlContent += '<td class="%s">%s</td>'%(StatusClass, SuccessHtml)
        ReportTxt = ""
        if Build["metadata"]["log-path"] != "":
            ReportTxt = "<a href='%s'>Steps report</a>"%(Build["metadata"]["log-path"]+"/report.html")
        HtmlContent += "  <td>%s</td></tr>\n"%ReportTxt
    HtmlContent += "</table>\n</div>"

    HtmlPath = os.path.join(OutDir, "globalreport.html")
    f = open(HtmlPath, "w")
    f.write(HtmlContent)
    f.close()

    logging.info("-- file://%s written."%HtmlPath)
