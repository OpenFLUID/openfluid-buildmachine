# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import unittest
import yaml
import shutil
import os


from mbmRecast import MBMEnv

######################################################
######################################################

resourceDir = os.path.dirname(os.path.abspath(__file__))+"/../"
targetEnv = resourceDir+"TEST_FAKE"

class MainTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        if os.path.isdir(targetEnv):
            shutil.rmtree(targetEnv)

    def test_create(self):
        MBMEnv.MBMEnv({"which":"create", "env_path":targetEnv})
        self.assertTrue(True)

    def test_run(self):
        MBMEnv.MBMEnv({"which":"run", "env_path":targetEnv}, isFake=True)
    
    
if __name__ == '__main__':
    unittest.main()

