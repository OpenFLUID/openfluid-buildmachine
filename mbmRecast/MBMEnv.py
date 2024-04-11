# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os
import shutil

import logging
from ofbm import utils as ofbmutils
from mbm import MultiBuildMachine as MBM

currentPath = os.path.dirname(os.path.abspath(__file__))

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
        shutil.copyfile(currentPath+"/../mbmRecast/resources/basicConf.yml", os.path.join(EnvDir, "config.yml"))
        
        # add all necessary scripts
        os.makedirs(ScriptDir)
        shutil.copyfile(currentPath+"/../mbm/run-docker-image.sh", os.path.join(ScriptDir, "run-docker-image.sh"))
        for f in ["__init__.py", "OFBMInjector.py"]:
            shutil.copyfile(currentPath+"/../"+f, os.path.join(ScriptDir, f))
        if isFake:
            shutil.copytree(currentPath+"/../tests", os.path.join(ScriptDir, "tests"))
        shutil.copytree(currentPath+"/../ofbm", os.path.join(ScriptDir, "ofbm")) # TODO spot necessary scripts only
        print("-- Creating MBM environment - done")

    elif Mode == "run":
        print("-- Running MBM in environment")
        ExecDir = os.path.join(EnvDir, "exec_"+ofbmutils.currentTimestamp(noSpace=True))
        LogOutDir = os.path.join(ExecDir, "logs")
        LogOutFile = LogOutDir+"/mbm_run_logs.txt"

        ofbmutils.resetDirectory(ExecDir, Purge=True)
        ofbmutils.resetDirectory(LogOutDir, Verbose=False)

        print("MBM log destination: "+LogOutFile)
        
        shutil.copyfile(os.path.join(EnvDir, "config.yml"), os.path.join(ExecDir, "config.yml"))
        # triggers run

        ## Config logger
        MBMENV_logger = logging.getLogger(__name__)
        MBMENV_logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(LogOutFile, 'a')
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        MBMENV_logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        MBMENV_logger.addHandler(stream_handler)

        CMBM = MBM.MultiBuildMachine(OutputInShell=True, tryImageBuild=False, isFake=isFake)
        CMBM.logger = MBMENV_logger
        CMBM.triggerBuilds(os.path.join(ExecDir, "config.yml"), ExecDir, ScriptDir=ScriptDir)