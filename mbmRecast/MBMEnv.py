# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import os
import shutil

from ofbm import utils as ofbmutils
from mbm import MultiBuildMachine as MBM


def MBMEnv(Args):
    Mode = Args["which"]
    EnvDir = Args["env_path"]

    if Mode == "create":
        print("Create MBM environment")
        os.makedirs(EnvDir)
        shutil.copyfile("./mbmRecast/resources/basicConf.yml", os.path.join(EnvDir, "config.yml"))
        os.makedirs(os.path.join(EnvDir, "scripts"))
    
    elif Mode == "run":
        print("Run MBM environment")
        ExecDir = os.path.join(EnvDir, "exec_"+ofbmutils.currentTimestamp(noSpace=True))

        ofbmutils.resetDirectory(ExecDir, Purge=True)
        shutil.copyfile(os.path.join(EnvDir, "config.yml"), os.path.join(ExecDir, "config.yml"))
        # triggers run
        CMBM = MBM.MultiBuildMachine(OutputInShell=False, tryImageBuild=False)
        CMBM.triggerBuilds(os.path.join(ExecDir, "config.yml"), ExecDir)