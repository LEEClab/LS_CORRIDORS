import unittest
import grass.script as grass
import wx
from Ls_corridors_v08_2016_02_d19_grass7 import *

class Ls_corridor_test(unittest.TestCase):
    """Tests for 'Ls_corridors.py'"""



    def test_combine_st(self):
        grass.run_command('r.in.gdal', flags='o', input='../DB_demo/ST_map1.img', output='test1_rast', overwrite=True, verbose = False)
        self.assertTrue(combine_st('test1_rast'), 
                        '1,2,1,3,1,4,1,5,1,6,1,7,1,8,1,9,1,10,1,11,1,12,1,13,1,14,1,15,1,16,1,17,1,18,1,19,2,3,2,4,2,5,2,6,2,7,2,8,2,9,2,10,2,11,2,12,2,13,2,14,2,15,2,16,2,17,2,18,2,19,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,4,5,4,6,4,7,4,8,4,9,4,10,4,11,4,12,4,13,4,14,4,15,4,16,4,17,4,18,4,19,5,6,5,7,5,8,5,9,5,10,5,11,5,12,5,13,5,14,5,15,5,16,5,17,5,18,5,19,6,7,6,8,6,9,6,10,6,11,6,12,6,13,6,14,6,15,6,16,6,17,6,18,6,19,7,8,7,9,7,10,7,11,7,12,7,13,7,14,7,15,7,16,7,17,7,18,7,19,8,9,8,10,8,11,8,12,8,13,8,14,8,15,8,16,8,17,8,18,8,19,9,10,9,11,9,12,9,13,9,14,9,15,9,16,9,17,9,18,9,19,10,11,10,12,10,13,10,14,10,15,10,16,10,17,10,18,10,19,11,12,11,13,11,14,11,15,11,16,11,17,11,18,11,19,12,13,12,14,12,15,12,16,12,17,12,18,12,19,13,14,13,15,13,16,13,17,13,18,13,19,14,15,14,16,14,17,14,18,14,19,15,16,15,17,15,18,15,19,16,17,16,18,16,19,17,18,17,19,18,19')
        grass.run_command('g.remove', flags='f', type='raster', pattern='test1_rast')
        
    def test_Form1_OnClick(self):
        
        number = wx.Button(self, id = 260)
        
        self.app = wx.PySimpleApp()
        self.frame = wx.Frame(None, -1, "LSCorridors v. 1.0", pos=(0,0), size=(530,450))
        self.f1 = Form1(self.frame,-1)
        wx.EVT_BUTTON(self, 260, self.f1.OnClick(number))
        #self.f1.OnClick(event = wx.EVT_BUTTON(self, 260))

if __name__ == '__main__':
    unittest.main()