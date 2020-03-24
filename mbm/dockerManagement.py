# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import subprocess
import os.path

from mbm import settings
from ofbm import utils as ofbmutils

import logging

def getImages(NameOnly=False):
    """Detects existing docker images"""
    #TODO Need improvement when several versions of image ?
    P = subprocess.Popen(["docker", "image", "ls"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
    out, err = P.communicate()
    Outputs = {"ERR":err, "OUT":out}
    Images = []
    if Outputs["ERR"]:
        logging.info("getImages")
        logging.error(Outputs["ERR"])
    for Line in Outputs["OUT"].split("\n")[1:]:
        if len(Line)>0:
            if NameOnly:
                Images += [Line.split()[0]]
            else:
                Images += [Line.split()[:3]]
    return Images


######################################################
######################################################


def getVolumeAvailableSpace():
    """Returns available disk space on target_volume"""
    P = subprocess.Popen(["df"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
    out, err = P.communicate()
    Outputs = {"ERR":err, "OUT":out}
    if Outputs["ERR"]:
        logging.info("getVolumeAvailableSpace")
        logging.error(Outputs["ERR"])
    Images = []
    for Line in Outputs["OUT"].split("\n")[1:-1]:
        if len(Line)>0:
            Columns = Line.split()
            MountedOn, Free = Columns[5], int(Columns[3])
            if MountedOn == settings.TARGET_VOLUME:
                return Free
    logging.error("Volume %s not found"%settings.TARGET_VOLUME)
    return 0


######################################################
######################################################


def generateImage(Image):
    """Build a Docker image following Dockerfiles in openfluid-devtools"""
    # check if Dockerfile exists for wanted Image
    #     unify sources location ? otherwiser make clean and obvious parameter for devtools folder location
    if settings.MAX_IMAGE_SIZE > getVolumeAvailableSpace():
        logging.error("generateImage: not enough space for image creation (estimated)")
        return 1
    
    DockerfilesDir = settings.DOCKERFILES_LOCATION
    WantedDir = Image
    OFPrefix = "ofbuild/"
    if WantedDir.startswith(OFPrefix):
        logging.debug("generateImage: removing ofbuild prefix to image name")
        WantedDir = WantedDir[len(OFPrefix):]
    if not WantedDir.endswith("-qt5"):
        logging.debug("generateImage: adding qt-5 suffix to image name")
        WantedDir += "-qt5"
    
    OutputFile = ""
    
    if os.path.isfile(os.path.join(DockerfilesDir, WantedDir, "Dockerfile")):
        DockerBuildCommand = "docker build --pull=true --no-cache -t ofbuild/%s ./%s" % (WantedDir, WantedDir)
        DockerBuildCommand = DockerBuildCommand.split()
        SubReturnCode = ofbmutils.subprocessCall(DockerBuildCommand, FilePath=OutputFile, CommandCwd=DockerfilesDir, OutputInShell=True)
        return SubReturnCode
    else:
        logging.error("generateImage: Dockerfile not found in folder %s"%os.path.join(DockerfilesDir, WantedDir))
        return 1


######################################################
######################################################


def launchInDocker(Image, Cmd, ScriptDir, SharedDir=settings.SHARED_DIR, SrcDir=settings.SHARED_DIR+"/src/"):
    """Run a given command Cmd into a docker image Image via script run-docker-image"""
    #os.system('chmod 777 -R %s'%ScriptDir)
    os.system('chmod 777 -R %s'%SrcDir)
    os.makedirs(SharedDir)
    os.system('chmod 777 -R %s'%SharedDir)
    FullCmd = ["sh", ScriptDir+"/run-docker-image.sh", ScriptDir, SharedDir, SrcDir, Image, "%s"%Cmd]
    #print(FullCmd)
    logging.info("Command to be launched in docker image %s, path %s: [[%s]]"%(Image,SharedDir," ".join(FullCmd)))
    P = subprocess.Popen(FullCmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = P.communicate()
    Outputs = {"ERR":err, "OUT":out}
    for Output in Outputs:
        ofbmutils.outputLogRedirect[Output](Outputs[Output])
    return Outputs
