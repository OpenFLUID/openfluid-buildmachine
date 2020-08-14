# -*- coding: utf-8 -*-

__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__   = "armel.thoni@inra.fr"
__license__ = "see LICENSE file"


import unittest
import os

from mbm import dockerManagement as DM

######################################################
######################################################


class MainTest(unittest.TestCase):

    def test_images(self):
        
        print(DM.getImages())
        print(DM.getImages(True))


    ####################################################


    def test_availableSpace(self):
        
        print(DM.getVolumeAvailableSpace())


    ####################################################


    def test_launchInDocker(self):
        
        Outputs = DM.launchInDocker(DM.getImages(True)[0], "echo TEST", "mbm", "sharedtestfolder")
        self.assertTrue(b"TEST" in Outputs["OUT"])
        os.rmdir("./sharedtestfolder/")


    ####################################################    

    
    def _test_imageGeneration(self):
        
        # DISABLED, probably too heavy for testing purpose without mocking
        DM.generateImage("debian-9-qt5")
    
    def tearDownClass():
        try:
            os.rmdir("./sharedtestfolder/")
        except:
            pass


if __name__ == '__main__':
    unittest.main()