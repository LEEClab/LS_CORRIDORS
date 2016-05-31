#---------------------------------------------------------------------------------------
"""
 LandScape Corridors -  Testing script

 Authors:
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Milton C. Ribeiro - mcr@rc.unesp.br

 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 Contributors:
 Bernardo Niebuhr - bernardo_brandaum@yahoo.com.br
 Juliana Silveira dos Santos - juliana.silveiradossantos@gmail.com
 Felipe Martello - felipemartello@gmail.com
 Pavel Dodonov - pdodonov@gmail.com
 
 To run tests:
 python test_LS_corridors.py
 
 Copyright (C) 2015-2016 by John W. Ribeiro and Milton C. Ribeiro.
"""
#---------------------------------------------------------------------------------------

import unittest

import grass.script as grass
import wx
import os, shutil

from LS_corridors_v1_0 import *

PARENT_DIR = os.getcwd()

#-----------------------------------------------------------#
#------------------- Test class ----------------------------#
#-----------------------------------------------------------#
class LS_corridors_test(unittest.TestCase):
    """
    Tests for 'LS_corridors_v_1_0.py'
    """

    #-----------------------------------------------------------------------------------#
    #--------------------------------- Preparing to test -------------------------------#
    #-----------------------------------------------------------------------------------#
    def setUp(self):
        """ Setting up for the tests """
        print "\n\nLS Corridors test => setUp -> begin"
                    
        #self.path = os.getcwd()
        #if self.path.split('/')[-1] == 'results_test':
        os.chdir(PARENT_DIR)
        self.path = os.getcwd()
               
        self.app = wx.PySimpleApp()
        self.frame = wx.Frame(None, -1, "LSCorridors", pos=(0,0), size=(560,450))
        self.corr = Corridors(self.frame, -1)
        
        # Files to test IMPORT FILES and combine_st
        self.corr.InArqResist = '../DB_demo/Resistance_map1.img'
        self.corr.OutArqResist = 'resist_test_rast'
        self.corr.InArqST = '../DB_demo/ST_map1.img'
        self.corr.OutArqST = 'st_test_rast'
            
        # For writing results
        self.corr.remove_aux_maps = False
        self.corr.perform_tests = True
            
        outdir = self.path+'/results_test'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
                
        self.corr.OutDir_files_TXT = outdir
        self.corr.NEXPER_FINAL=self.corr.NEXPER_AUX+'_'+self.corr.OutArqResist
            
        self.corr.Nsimulations1 = 2
        self.corr.Nsimulations2 = 2
        self.corr.Nsimulations3 = 2
        self.corr.Nsimulations4 = 2
        self.corr.patch_id_list = ['1', '2', '5', '6']
        
        # Event to test IMPORT FILES
        self.evt240 = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, 240)
        
        # Event to test RUN SIMULATIONS        
        self.evt10 = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, 10)
                 
        print "LS Corridors test => setUp -> end"    
    
    #-----------------------------------------------------------------------------------#
    #--------------------------------- Ending the test ---------------------------------#
    #-----------------------------------------------------------------------------------#    
    def tearDown(self):
        
        testName = self.shortDescription()
        if (testName == 'finish'):
            grass.run_command('g.remove', flags='f', type='raster', pattern='*')
            grass.run_command('g.remove', flags='f', type='vector', pattern='*')
            
            os.remove('LS_corridors_v1_0.pyc')
            shutil.rmtree('results_test')
            #pass


    #-----------------------------------------------------------------------------------#
    #--------------------------------------- Tests -------------------------------------#
    #-----------------------------------------------------------------------------------# 
            
    #-----------------------------------
    # Test IMPORT FILES button
    #-----------------------------------
    def test_1Corridors_OnClick_import_files(self):
        '''test Corridors OnClick 240 import files'''
        print 'test Corridors OnClick 240 import files'
        
        self.corr.OnClick(self.evt240)
        list_rast = grass.list_grouped('raster', pattern = '*test_rast')['PERMANENT']
        
        self.assertTrue(list_rast, ['resist_test_rast', 'st_test_rast'])
        
    #-----------------------------------
    # Test combine_st function; it is the same as testing button 260 - CREATES ST COMBINATION LIST
    #-----------------------------------       
    def test_2Combine_st(self):
        '''test Combine st'''
        print "test Combine st"
        
        self.assertTrue(combine_st(self.corr.OutArqST),
                        '1,2,1,3,1,4,1,5,1,6,1,7,1,8,1,9,1,10,1,11,1,12,1,13,1,14,1,15,1,16,1,17,1,18,1,19,2,3,2,4,2,5,2,6,2,7,2,8,2,9,2,10,2,11,2,12,2,13,2,14,2,15,2,16,2,17,2,18,2,19,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,4,5,4,6,4,7,4,8,4,9,4,10,4,11,4,12,4,13,4,14,4,15,4,16,4,17,4,18,4,19,5,6,5,7,5,8,5,9,5,10,5,11,5,12,5,13,5,14,5,15,5,16,5,17,5,18,5,19,6,7,6,8,6,9,6,10,6,11,6,12,6,13,6,14,6,15,6,16,6,17,6,18,6,19,7,8,7,9,7,10,7,11,7,12,7,13,7,14,7,15,7,16,7,17,7,18,7,19,8,9,8,10,8,11,8,12,8,13,8,14,8,15,8,16,8,17,8,18,8,19,9,10,9,11,9,12,9,13,9,14,9,15,9,16,9,17,9,18,9,19,10,11,10,12,10,13,10,14,10,15,10,16,10,17,10,18,10,19,11,12,11,13,11,14,11,15,11,16,11,17,11,18,11,19,12,13,12,14,12,15,12,16,12,17,12,18,12,19,13,14,13,15,13,16,13,17,13,18,13,19,14,15,14,16,14,17,14,18,14,19,15,16,15,17,15,18,15,19,16,17,16,18,16,19,17,18,17,19,18,19')
        
    #-----------------------------------
    # Test main algorithm - LSCorridors simulation; button 10 - OnClick Run
    #-----------------------------------  
    def test_3Corridors_OnClick_run_simulation(self):
        '''test Corridors OnClick 10 run simulation'''
        print 'test Corridors OnClick 10 run simulation'
        
        self.corr.remove_aux_maps = False
        os.chdir(self.path)
        
        #raw_input()
        self.corr.OnClick(self.evt10)
        list_rast = grass.list_grouped('raster', pattern = 'Results*')['PERMANENT']
        
        # number of outputs = 4 methods * (length_of_list + 1_final_output)
        self.assertTrue(len(list_rast), (4*(len(self.corr.patch_id_list)/2 + 1)))
        
        out_files = os.listdir('.')
        self.assertTrue(len(out_files), (4*(len(self.corr.patch_id_list)/2 + 1) + len(self.corr.patch_id_list)/2 + 1))
        
        self.assertIn(self.corr.NEXPER_FINAL+'_M1_RSFI.tif', out_files)
        self.assertIn(self.corr.NEXPER_FINAL+'_M2_RSFI.tif', out_files)
        self.assertIn(self.corr.NEXPER_FINAL+'_M3_RSFI.tif', out_files)
        self.assertIn(self.corr.NEXPER_FINAL+'_M4_RSFI.tif', out_files)
        #self.assertIn(self.corr.NEXPER_FINAL+'_LargeZone_Corridors.tif', out_files)
        
        out_tif = []
        out_txt = []
        for i in out_files:
            if '.tif' in i:
                out_tif.append(i)
            if '.txt' in i:
                out_txt.append(i)
                
        self.assertTrue(len(out_tif), 4*(len(self.corr.patch_id_list)/2 + 1))
        self.assertTrue(len(out_txt), (len(self.corr.patch_id_list)/2 + 1))

    #-----------------------------------
    # Test function Define_region
    #-----------------------------------         
    def test_4Define_region(self):
        '''test Define region'''
        
        defineregion("source_shp", "target_shp", influenceprocess=345)
        
        dicregion = grass.region()
        n = float(dicregion['n'])
        s = float(dicregion['s'])
        e = float(dicregion['e'])
        w = float(dicregion['w'])
        
        print 'n = '+`n`+'; s = '+`s`+'; e = '+`e`+'; w = '+`w`
        self.assertAlmostEqual(n, 7497687.0308)
        self.assertAlmostEqual(s, 7494657.0308)
        self.assertAlmostEqual(e, 763554.124316)
        self.assertAlmostEqual(w, 760014.124316)
        
    #-----------------------------------
    # Finishes tests, deletes temp dirs and files
    #-----------------------------------      
    def test_finishes(self):
        '''finish'''
        print "Tests finished"


#-----------------------------------------------------------#
#------------------- Run tests -----------------------------#
#-----------------------------------------------------------#
if __name__ == '__main__':
    unittest.main()