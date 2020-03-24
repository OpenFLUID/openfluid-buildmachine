# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import unittest

import yaml
import os


from mbm import utils
from mbm import MultiBuildMachine as MBM

######################################################
######################################################

ressourceDir = os.path.dirname(os.path.abspath(__file__))+"/resources/"


class MainTest(unittest.TestCase):
    
    def test_yamlImport(self):
      
        Setups = utils.importYaml(ressourceDir+"/theoricalconf.yml")
        self.assertTrue("active-setups" in Setups)
        BadSetups = utils.importYaml(ressourceDir+"/noactiveconf.yml")
        self.assertFalse("active-setups" in BadSetups)
        
  
    ####################################################
    
    
    def test_mbm(self):
        
        CMBM = MBM.MultiBuildMachine(OutputInShell=True, isFake=True)
        CMBM.triggerBuilds(ressourceDir+"/theoricalconf.yml")
    
    
    ####################################################
        
        
    def test_mbm_docker(self):
        
        CMBM = MBM.MultiBuildMachine(isFake=True)
        CMBM.triggerBuilds(ressourceDir+"/basicconf.yml")

    
    ####################################################
    
    
    def _test_mbm_real(self):
      
        CMBM = MBM.MultiBuildMachine(OutputInShell=True)
        CMBM.triggerBuilds(ressourceDir+"/theoricalconf.yml")
        


if __name__ == '__main__':
    unittest.main()