# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os
import shutil

from ofbm import utils as ofbmutils
from mbm import MultiBuildMachine as MBM


def MBMEnv(Args, isFake=False):   
    if "which" in Args:
        Mode = Args["which"]
    else:
        print("Argument 'create' or 'run' needed")
        return 1
    EnvDir = Args["env_path"]
    ScriptDir = os.path.join(EnvDir, "scripts")
    
    if Mode == "create":
        print("-- Creating MBM environment")
        os.makedirs(EnvDir)
        shutil.copyfile("./mbmRecast/resources/basicConf.yml", os.path.join(EnvDir, "config.yml"))
        
        # add all necessary scripts
        os.makedirs(ScriptDir)
        shutil.copyfile("./mbm/run-docker-image.sh", os.path.join(ScriptDir, "run-docker-image.sh"))
        for f in ["__init__.py", "OFBMInjector.py"]:
            shutil.copyfile(f, os.path.join(ScriptDir, f))
        if isFake:
            shutil.copytree("tests", os.path.join(ScriptDir, "tests"))
        shutil.copytree("ofbm", os.path.join(ScriptDir, "ofbm")) # TODO spot necessary scripts only
        print("-- Creating MBM environment - done")

    elif Mode == "run":
        print("-- Running MBM in environment")
        ExecDir = os.path.join(EnvDir, "exec_"+ofbmutils.currentTimestamp(noSpace=True))

        ofbmutils.resetDirectory(ExecDir, Purge=True)
        shutil.copyfile(os.path.join(EnvDir, "config.yml"), os.path.join(ExecDir, "config.yml"))
        # triggers run
        CMBM = MBM.MultiBuildMachine(OutputInShell=True, tryImageBuild=False, isFake=isFake)
        CMBM.triggerBuilds(os.path.join(ExecDir, "config.yml"), ExecDir, ScriptDir=ScriptDir)