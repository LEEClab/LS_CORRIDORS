#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 LandScape Corridors
 Simulation of multiple ecological functional corridors

 Authors:
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Milton C. Ribeiro - mcr@rc.unesp.br

 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 Description:
 LSCorridors is a free and open source package developed in Python 
 that simulates multiples functional ecological corridors.
 The software runs in a GRASS GIS environment.
 It can also be found at: https://github.com/LEEClab/LS_CORRIDORS
 
 To run LSCorridors:
 python Ls_corridors_v01.py
 
 To run tests:
 python -m doctest [-v] Ls_corridors_v01.py
 
 Copyright (C) 2015-2016 by John W. Ribeiro and Milton C. Ribeiro.

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the license, 
 or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#---------------------------------------------------------------------------------------

import grass.script as grass
from PIL import Image
import wx
import random, math
import os, re, platform
#import time
from datetime import datetime
#import win32gui
#from win32com.shell import shell, shellcon
import numpy as np

ID_ABOUT=101
ID_IBMCFG=102
ID_EXIT=110


#def selecdirectori():
  #mydocs_pidl = shell.SHGetFolderLocation (0, shellcon.CSIDL_DESKTOP, 0, 0)
  #pidl, display_name, image_list = shell.SHBrowseForFolder (
    #win32gui.GetDesktopWindow (),
    #mydocs_pidl,
    #"Select a file or folder",
    #shellcon.BIF_BROWSEINCLUDEFILES,
    #None,
    #None
  #)
  
  #if (pidl, display_name, image_list) == (None, None, None):
    #print "Nothing selected"
  #else:
    #path = shell.SHGetPathFromIDList (pidl)
    
    #a=(path)
  
  #return a

#----------------------------------------------------------------------------------
# Auxiliary functions
  
def selectdirectory():
  '''
  This function allows the user to select a directory (for output files, for example)
  Input:
  - No input
  Output:
  - Complete path of the selected folder
  '''
  
  dialog = wx.DirDialog(None, "Select a file or folder:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
  if dialog.ShowModal() == wx.ID_OK:
    #print ">>..................",dialog.GetPath()
    return dialog.GetPath()
  
def selectfile():
  '''
  This function allows the user to select a file (input map files or combination of points, for example)
  Input:
  - No input
  Output:
  - Complete path of the selected file
  '''  
  
  wildcard = "All files (*.*)|*.*"
  dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
  if dialog.ShowModal() == wx.ID_OK:
    print ">>..................",dialog.GetPath()
    return dialog.GetPath() 

def defineregion(mapa1,mapa2,influensprocess):
  '''
  This function...
  '''
  
  grass.run_command("g.region",vect=mapa1+","+mapa2)
  dicregion = grass.region()
  n=float(dicregion['n'])
  s=float(dicregion['s'])
  e=float(dicregion['e'])
  w=float(dicregion['w'])
  
  n=n+influensprocess
  s=s-influensprocess
  e=e+influensprocess
  w=w-influensprocess

  grass.run_command("g.region",n=n,e=e,s=s,w=w)


def combine_st(st_map):
  '''
  This function reads the values of possible source target IDs from the ST map,
  creates a list of all possible combinations of STs and returns it as a string
  Input:
  - st_map: name of the source target map, from which ST IDs are extracted
  Output:
  - patchid_list_output: string with all possible combinations of STs. The list
    has a 'plain' form. E.g.: 1,2,5,7 shows two combinations of points: 1-2 and 5-7
    
  Testing function
  
  Test 1)
  >>> grass.run_command('r.in.gdal', flags='o', input='../DB_demo/ST_map1.img', output='test1_rast', overwrite=True, verbose = False)
  0
  >>> combine_st('test1_rast')
  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
  '1,2,1,3,1,4,1,5,1,6,1,7,1,8,1,9,1,10,1,11,1,12,1,13,1,14,1,15,1,16,1,17,1,18,1,19,2,3,2,4,2,5,2,6,2,7,2,8,2,9,2,10,2,11,2,12,2,13,2,14,2,15,2,16,2,17,2,18,2,19,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,4,5,4,6,4,7,4,8,4,9,4,10,4,11,4,12,4,13,4,14,4,15,4,16,4,17,4,18,4,19,5,6,5,7,5,8,5,9,5,10,5,11,5,12,5,13,5,14,5,15,5,16,5,17,5,18,5,19,6,7,6,8,6,9,6,10,6,11,6,12,6,13,6,14,6,15,6,16,6,17,6,18,6,19,7,8,7,9,7,10,7,11,7,12,7,13,7,14,7,15,7,16,7,17,7,18,7,19,8,9,8,10,8,11,8,12,8,13,8,14,8,15,8,16,8,17,8,18,8,19,9,10,9,11,9,12,9,13,9,14,9,15,9,16,9,17,9,18,9,19,10,11,10,12,10,13,10,14,10,15,10,16,10,17,10,18,10,19,11,12,11,13,11,14,11,15,11,16,11,17,11,18,11,19,12,13,12,14,12,15,12,16,12,17,12,18,12,19,13,14,13,15,13,16,13,17,13,18,13,19,14,15,14,16,14,17,14,18,14,19,15,16,15,17,15,18,15,19,16,17,16,18,16,19,17,18,17,19,18,19'
  >>> grass.run_command('g.remove', flags='f', type='raster', pattern='test1_rast')
  0
  
  '''
  
  listRstats=grass.read_command('r.stats', input=st_map, flags='n', separator='space')
  b=[]
  b=listRstats.split('\n')
  del b[-1]
  print b
  patchid_list=','.join(b)
    
  patchid_list_aux = patchid_list.split(",")

  patchid_list_output=""
  patchid_list_output_b=[]
  for i in range(len(patchid_list_aux)-1):
    for j in range(len(patchid_list_aux)):
      if (i <j):
        #print i, j
        patchid_list_output=patchid_list_output+patchid_list_aux[i]+","+patchid_list_aux[j]+","
  patchid_list_output_b=patchid_list_output.split(',')
  del patchid_list_output_b[-1]
  patchid_list_output=','.join(patchid_list_output_b)
  
  return patchid_list_output
  

#----------------------------------------------------------------------------------
# Form1 is the main class, in which the software is initialized and runs
   
class Form1(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # List of possible resistance and ST maps (already loaded inside GRASS GIS DataBase)
        self.listmaps=grass.list_grouped('rast')['PERMANENT']
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------BLOCK OF VARIABLE DESCRIPTION--------------------------------------------------------------------------------------------#
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        

        # Loads the output directory
        Form1.OutDir_files='Path of the files'

        # Loads the path to the txt output files
        Form1.OutDir_files_TXT=''
        
        # Loads the name of the resistance matrix
        Form1.InArqCost='Name of the file + ext '
        
        # Loads the name of the source-target map
        Form1.InArqST=''
        
        # Loads the name of a map to be imported into GRASS GIS and used for simulations
        Form1.OutArqRes=''
        
        # Variables with 'C' are used to generate output names for auxiliary maps M1,M2,M3,M4
        # Name of mode map (M2)
        Form1.C2='M2_MODE'
        
        # Name of maximum map (M3)
        Form1.C3='M3_MAXIMUM'
        
        # Name of average map (M4)
        Form1.C4='M4_AVERAGE'
          
  
        # List of combinations of STs
        Form1.lista=''
        Form1.listaApoioaleat3=[]
        
        # String to show an example of how the ST list should look like
        Form1.edtstart_list='Ex:1,2,3,4,...'
        
        # List of combinations of STs generated from reading a txt file
        Form1.patch_id_list=''
        
        
        Form1.edtCost='Name cost map'
        Form1.edtST='Map Name of Source and Target'
        Form1.escname=''
        
        
        Form1pares=''
        Form1.patch_id_list_aux=''
        Form1.patch_id_list_aux_b=''
        
        #Formulas
        
        Form1.S1=''
        Form1.T1=''
        Form1.S1FORMAT=''
        Form1.T1FORMAT=''
        Form1.PAISGEM=''
        Form1.ARQSAIDA=''
        Form1.NEXPER_AUX='MSP'
        Form1.NEXPER_APOIO=''
        Form1.NEXPER_FINAL=''
        
    
        Form1.Form_01=''        
        Form1.form_02=''
        Form1.form_03=''
        Form1.form_04=''
        Form1.form_05=''
        Form1.form_06=''
        Form1.form_07=''
        Form1.form_08=''
        Form1.form_09=''
        Form1.form_10=''
        Form1.form_11=''
        Form1.form_12=""
        Form1.form_13=''
        Form1.form_14=""
        Form1.form_15=''
        Form1.form_16=''
        Form1.form_17=""
        Form1.form_18=""
        Form1.chekfolder=''
    
    
        Form1.a=''
        Form1.b=''
        Form1.c=''
        Form1.d=''
        Form1.listExport=[]
        Form1.ap=0
        Form1.ap2=0
        Form1.ap3=0
        Form1.ap4=0
        Form1.ap5=0
        Form1.ap6=0
        
    
        Form1.var_source_x=''
        Form1.var_source_x_b=''
        Form1.var_source_y=''
        Form1.var_source_y_b=''
        Form1.var_target_x=''
        Form1.var_target_x_b=''
        Form1.var_target_y=''
        Form1.var_target_y_b=''
        Form1.outline=''
        Form1.outline1=''
        Form1.outdir=''        
    

        Form1.arquivo=''
        Form1.x=''
        Form1.x_b=''
        Form1.x_c=''
        
        
        Form1.M=''
        
        Form1.var_cost_sum=''
        Form1.var_dist_line=0.0
        Form1.linha=''
        Form1.readtxt=''
        Form1.ileHandle=''
        Form1.form_16=''
        Form1.lenlist=0.0
        Form1.lenlist_b=0.0
        Form1.Nsimulations=0
        Form1.Nsimulations1=15
        Form1.Nsimulations2=15
        Form1.Nsimulations3=15
        Form1.Nsimulations4=15
        Form1.NsimulationsStart='15'
        Form1.startscale='100'
        
        Form1.escalafina=0
        Form1.esc=100
        Form1.res=''
        Form1.res2=[]
        Form1.res3=''
        
        Form1.euclidean_a=0.0  
        Form1.euclidean_b=0.0  
        Form1.cabecalho=''
        
        Form1.length=''
        Form1.length_b=''
        Form1.length_c=''
        Form1.length_d=''
        Form1.length_e=0.0
        
                     
      
        Form1.ChecktTry=True
        
        Form1.var_source_x_b_int=0.0
        Form1.var_source_y_b_int=0.0
        Form1.var_target_x_b_int=0.0
        Form1.var_target_y_b_int=0.0
        Form1.ruido='2.0'
        Form1.ruido_float=2.0
        Form1.listafinal=[]
        Form1.escfinal=0
        Form1.escapoio1=''
        Form1.escapoio2=[]
        Form1.escE=''
        Form1.escW=''
        Form1.escfinal=0.0
        Form1.frag=''
        Form1.frag_list=''
        Form1.frag_list2=''
        Form1.selct=''   
        Form1.defaultsize_moviwin_allcor=7
        ###
        Form1.txt_log=''
        
        #start time
        Form1.time = 0 # INSTANCE
        Form1.day_start=0
        Form1.month_start=0
        Form1.year_start=0
        Form1.hour_start=0 # GET START Form1.hour
        Form1.minuts_start=0 #GET START Form1.minuts
        Form1.second_start=0 #GET START
       
        #end time
        Form1.time = '' # INSTANCE
        Form1.day_end=0
        Form1.month_end=0
        Form1.year_end=0
        Form1.hour_end=0 # GET end Form1.hour
        Form1.minuts_end=0 #GET end Form1.minuts
        Form1.second_end=0 #GET end Form1.seconds  
        
        Form1.header_log=''
  
        Form1.time = 0 # INSTANCE
        Form1.day=0
        Form1.month=0
        Form1.year=0
        Form1.hour=0 # GET START Form1.hour
        Form1.minuts=0 #GET START Form1.minuts
        Form1.second=0 #GET START             
        
        Form1.time = 0 # INSTANCE
        Form1.day_now=0
        Form1.month_now=0
        Form1.year_now=0
        Form1.hour_now=0 # GET START Form1.hour
        Form1.minuts_now=0 #GET START Form1.minuts
        Form1.second_now=0 #GET START      
        Form1.listErrorLog=[]
        Form1.diference_time=''
        
        Form1.n=''
        Form1.s=''
        Form1.e=''
        Form1.w=''
        Form1.dicregion=''
        Form1.influensprocess=10000
        Form1.influensprocess_boll=False
        
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #-------------------------------------------------------------------INITIALIZING GUI----------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        try:
          grass.run_command('r.mask', flags='r')
        except:
          pass
        
        self.quote = wx.StaticText(self, id=-1, label="LandScape Corridors",pos=wx.Point(20, 20))
        
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("blue")
        self.quote.SetFont(font)
        #__________________________________________________________________________________________
        self.quote = wx.StaticText(self, id=-1, label="Simulation Number:", pos=wx.Point(20,200))
                
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)        
                        
                    
                        
        #__________________________________________________________________________________________                
        self.quote = wx.StaticText(self, id=-1, label="Using Maps Already Imported:", pos=wx.Point(20,90))
                      
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)         
                        
      
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self,5, "",wx.Point(20,269), wx.Size(320,100),wx.TE_MULTILINE | wx.TE_READONLY)
        
        #---------------------------------------------#
        #-------------- BUTTONS ----------------------#
        #---------------------------------------------#
        
        self.button =wx.Button(self, 10, "START SIMULATIONS", wx.Point(20,379))
        wx.EVT_BUTTON(self, 10, self.OnClick)
  
        self.button =wx.Button(self, 205, "RUN EXPORT FILES ", wx.Point(137,379))
        wx.EVT_BUTTON(self, 205, self.OnClick)
        
        self.button =wx.Button(self, 210, "select files", wx.Point(230,55))#st
        wx.EVT_BUTTON(self, 210, self.OnClick)
        
        self.button =wx.Button(self, 230, "select files", wx.Point(72,55)) #cost
        wx.EVT_BUTTON(self, 230, self.OnClick)
        
        self.button =wx.Button(self, 240, "IMPORT FILES", wx.Point(308,55))
        wx.EVT_BUTTON(self, 240, self.OnClick)
        
        self.button =wx.Button(self, 250, "READ LIST TXT", wx.Point(322,145))
        wx.EVT_BUTTON(self, 250, self.OnClick)

        self.button =wx.Button(self, 260, "COMBINE ALL", wx.Point(418,145))
        wx.EVT_BUTTON(self, 260, self.OnClick)
        
        self.button =wx.Button(self, 8, "EXIT", wx.Point(260, 379))
        wx.EVT_BUTTON(self, 8, self.OnExit)

        ##------------ LEEClab_logo
        imageFile = 'logo_lab.png'
        im1 = Image.open(imageFile)
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (348,270), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------STATIC TEXTS-----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.lblname = wx.StaticText(self, -1, "Resistance Map:", wx.Point(20,58))
        self.lblname2 = wx.StaticText(self, -1, "Source-Target Map:", wx.Point(155,60))
        self.lblname2 = wx.StaticText(self, -1, "Variability:", wx.Point(400,60))
        self.lblname = wx.StaticText(self, -1, "Resistance:", wx.Point(20,115))
        self.lblname = wx.StaticText(self, -1, "ST:", wx.Point(270,115))
        Form1.lista = wx.StaticText(self, -1, "Enter a list manually:",wx.Point(20,150))
        self.lblname = wx.StaticText(self, -1, "M1:", wx.Point(70,230))
        self.lblname = wx.StaticText(self, -1, "M2:", wx.Point(130,230))
        self.lblname = wx.StaticText(self, -1, "M3:", wx.Point(190,230))
        self.lblname = wx.StaticText(self, -1, "M4:", wx.Point(250,230))
        self.lblname = wx.StaticText(self, -1, "Name of output corridor:", wx.Point(20,180))
        self.lblname = wx.StaticText(self, -1, "Scale (meters):", wx.Point(330,180))
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------TEXT CONTROLS----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.editname1 = wx.TextCtrl(self, 180, Form1.edtstart_list, wx.Point(126,146), wx.Size(195,-1))
        self.editname2 = wx.TextCtrl(self, 185, 'Proposed name of the cost map', wx.Point(130,175), wx.Size(195,-1))
        self.editname3 = wx.TextCtrl(self, 186, '2.0', wx.Point(455,55), wx.Size(30,-1))
        self.editname4 = wx.TextCtrl(self, 190, Form1.NsimulationsStart, wx.Point(90,228), wx.Size(35,-1))
        #### ADD MESSAGE HERE!!!!
        self.editname5 = wx.TextCtrl(self, 191, Form1.NsimulationsStart, wx.Point(150,228), wx.Size(35,-1))
        self.editname6 = wx.TextCtrl(self, 192, Form1.NsimulationsStart, wx.Point(210,228), wx.Size(35,-1))
        self.editname7 = wx.TextCtrl(self, 193, Form1.NsimulationsStart, wx.Point(270,228), wx.Size(35,-1))
        self.editname8 = wx.TextCtrl(self, 196, Form1.startscale, wx.Point(405,175), wx.Size(50,-1))
         
         
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
              
       
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------DEFINITION OF TEXT EVENTS----------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        wx.EVT_TEXT(self, 180, self.EvtText)   
        wx.EVT_TEXT(self, 185, self.EvtText)
        wx.EVT_TEXT(self, 186, self.EvtText)
        wx.EVT_TEXT(self, 190, self.EvtText)
        wx.EVT_TEXT(self, 191, self.EvtText)
        wx.EVT_TEXT(self, 192, self.EvtText)
        wx.EVT_TEXT(self, 193, self.EvtText)
        wx.EVT_TEXT(self, 194, self.EvtText)
        wx.EVT_TEXT(self, 195, self.EvtText)
        wx.EVT_TEXT(self, 196, self.EvtText)
        wx.EVT_TEXT(self, 265, self.EvtText)
        wx.EVT_TEXT(self, 266, self.EvtText)
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------COMBO BOXES----------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        

        # RESISTANCE MAP
        # List of maps taken from GRASS GIS database, using the command "grass.list_grouped"
        self.editspeciesList=wx.ComboBox(self, 93, 'Click to select', wx.Point(50, 112), wx.Size(215, -1),
                                         self.listmaps, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
        wx.EVT_TEXT(self, 93, self.EvtText)
        #--------------------------------------------------------------------------------------------------
        
        # SOURCE TARGET MAP
        # List of maps taken from GRASS GIS database, using the command "grass.list_grouped"
        self.editspeciesList=wx.ComboBox(self, 95, 'Click to select', wx.Point(290, 112), wx.Size(215, -1),
                                         self.listmaps, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 95, self.EvtComboBox)
        wx.EVT_TEXT(self, 95, self.EvtText)        
        #--------------------------------------------------------------------------------------------------
     
        
    def EvtComboBox(self, event):
      
      #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
      #----------------------------------------------------------------SELECTING MAPS USING COMBO BOX-----------------------------------------------------------------------------------------#
      #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
      
    
        """
        SELECT RESISTANCE MAP
        ID 93: event performed by a combobox, from a list of raster maps already in GRASS GIS DataBase
        Resistance Map name is stored in a variable called Form1.OutArqRes
        Variable Form1.NEXPER_FINAL also stores resistance map name; if the user does not inform 
        an output name for the simulation, corridor output names will have the same name as the input 
        resistance map
        """
        
        if event.GetId()==93:   
            # Gets resistance map name and stores it in Form1.OutArqRes
            Form1.OutArqRes=event.GetString()
            
            # Gets resistance map name and stores it in Form1.NEXPER_FINAL (in case the user does not provide an output file name)
            Form1.NEXPER_FINAL=event.GetString()
            Form1.NEXPER_FINAL='MSP_'+Form1.NEXPER_FINAL
            
            # Shows selection in the Dialog Box
            self.logger.AppendText('Resistance Map Selected:\n')
            self.logger.AppendText('%s\n' % event.GetString())
        
        
        
        """
        ST MAP
        ID 95: event performed by a combobox, from a list of raster maps already in GRASS GIS DataBase
        Source-Target Map is stored in a variable called Form1.OutArqST
        """
        
        if event.GetId()==95: 
          
          # Gets source target map name and stores it in Form1.OutArqST
          Form1.OutArqST=event.GetString()
          
          # Shows selection in the Dialog Box
          self.logger.AppendText('Map Souce Targetd:\n')
          self.logger.AppendText('%s\n' % event.GetString())
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
             
        
       
    def OnClick(self, event):
        '''
        This function controls what happens when a button of the GUI is pressed
        
        Testing BUTTON ID 260 (Create ST combination list)
        >>> app = wx.PySimpleApp()
        >>> frame = wx.Frame(None, -1, "LSCorridors v. 1.0", pos=(0,0), size=(530,450))
        >>> f1 = Form1(frame,-1)
        >>> f1.OutArqST = 'STs_img'
        >>> 
        f1.OnClick(260)
        
        wx.EVT_BUTTON(self, 260, self.OnClick)
         Form1.OnClick(self, 260)
        '''
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------IMPORTING EXTERNAL RASTER: ID 240--------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        """
        ID 240: IMPORT RASTER BUTTON
        When this button is cliked, two maps will be imported: resistance and ST maps.
        This maps are also selected as the resistance and ST maps to be used in the simulation.
        
        The end of map names (e.g., ".tif") will be replaced by (e.g., "_tif").
        Maps to be imported are those chosen from "select files" buttons with IDs 210 and 230.
        """        
        
        if event.GetId()==240: #Run import
          # Imports a resistance map, ignoring projections
          grass.run_command ('r.in.gdal', flags='o', input=Form1.InArqCost,output=Form1.OutArqRes, overwrite=True, verbose = False)
          
          # Imports a ST map, ignoring projections
          grass.run_command ('r.in.gdal', flags='o', input=Form1.InArqST,output= Form1.OutArqST, overwrite=True, verbose = False)
          
          # Setting GRASS GIS region to the largest (resistance) map
          grass.run_command('g.region', rast=Form1.OutArqRes, verbose=False)
          
          # Shows procedure in the Diolog Box
          self.logger.AppendText('\nImporting rasters... \n')
       
          
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
       
       
       
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------CREATES ST COMBINATION LIST: ID 240------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
       
        """
        ID 260: This event uses information contained inside ST map to create a list
        with all possible combination ST combinations, assigns this list to the 
        variable Form1.patch_id_list_aux, which is then used to generate simulations
        """
        
        if event.GetId()==260: #combine list
          
          # Diolog Box Message
          self.logger.AppendText('Generating combinations... \n')
          
          # Creating ST combination list based on information of ST map
          # The result is a string with combinations; e.g.: 1,2,1,3,1,4...
          Form1.patch_id_list_aux = combine_st(st_map = Form1.OutArqST)
          
          # Transforms the string into a list, using comma as separator
          Form1.patch_id_list_aux_b=Form1.patch_id_list_aux.split(',')
          
          # Length of the list
          Form1.lenlist=len(Form1.patch_id_list_aux_b)
          
          # Number of combination pairs
          Form1.lenlist_b=Form1.lenlist/2
          
          # Sends confirmation message
          self.logger.AppendText('Waiting... \n')
          
          d = wx.MessageDialog(self, "Simulate all possible ("+`Form1.lenlist_b`+") combinations?\n", "", wx.YES_NO)
          retCode = d.ShowModal() # Shows
          d.Close(True)  # Close the frame. 
          
          # If the user choses "yes", it meand that it was chosen to simulate all ST possible combinations;
          # otherwise, the process is simply canceled
          if (retCode == wx.ID_YES):
            Form1.patch_id_list=Form1.patch_id_list_aux.split(',')
            self.logger.AppendText('\nCreated list. \n')
            #print Form1.patch_id_list
          else:
              print ""
              self.logger.AppendText('\nList not created. \n')
          d.Destroy()

        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        
         
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------EXPORT SIMULATED CORRIDORS: ID 205-------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        """
        ID 205: This event is used to export all maps generated after all simulations
        """
        
        if event.GetId()==205:   #205==export maps
        
          # List raster resulting files and confirms if the user wants to export them
          p=grass.mlist_grouped ('rast', pattern='*MSP*') ['PERMANENT']
          j=len(p)
          
          self.logger.AppendText('Found: '+j+' files.')
          d= wx.MessageDialog(self, "Export files?\n", "", wx.YES_NO) # Create a message dialog box
          retCode=d.ShowModal() # Shows 
          d.Close(True) # Close the frame.
          
          # If the user confirms exporting, export!
          if (retCode == wx.ID_YES):
            
            # Select output directory
            self.logger.AppendText('Please select the directory... \n')
            Form1.OutDir_files=selectdirectory()
            os.chdir(Form1.OutDir_files)
            
            for i in p:
              grass.run_command('g.region', rast=i,verbose=False)
              grass.run_command('r.out.gdal', input=i, output=i+'.tif', format='GTiff', nodata=-9999)
              #print i
              self.logger.AppendText('Exporting:\n '+i +"\n" )
            else:
              #print "no"
              self.logger.AppendText('Export canceled \n' )
              d.Destroy()   
                    
        ############################################################################################################################################ 
                    

                                                
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------SELECIONANDO NA PASTA O MAPA DE ST ------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
         
        """
        ID 210: Permite com que o usuatio va ate uma pasta a parti de uma def  selectdirectory, onde sera retornado o nome do mapa mas nao sera importado ate que se aperte o botao import files
        
        """       
        if event.GetId()==210:   #210==Select files st
          # Menssagem de dialogo 
          self.logger.AppendText("Waiting ... :\n")
          
          #acessando def de selecionar diretorio e armazenando o retorno na Var Form1.InArqST
          Form1.InArqST=selectfile()
          
          # removing file name extension 
          if platform.system() == 'Windows':
            Form1.OutArqST=Form1.InArqST.split('\\')
          elif platform.system() == 'Linux':
            Form1.OutArqST=Form1.InArqST.split('/')
          else:
            # improve it to Mac OS
            raise Exception("What platform is yours?? It's not Windows or Linux...")         
          Form1.OutArqST=Form1.OutArqST[-1].replace('.','_')
          
          # Sending dialog message
          self.logger.AppendText('Selected File: \n'+Form1.OutArqST+'\n')
          #self.logger.AppendText("Automatically Map ST Selected:\n")
          #self.logger.AppendText(Form1.OutArqST+"\n")
         
         
          #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
          #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
          #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
                         
         
         
         
          
                  
        if event.GetId()==230:   #230==Select files cost
          self.logger.AppendText("Waiting ... :\n")
          Form1.InArqCost=selectfile()
          
          # removing file name extension 
          if platform.system() == 'Windows':
            Form1.OutArqRes=Form1.InArqCost.split('\\')
          elif platform.system() == 'Linux':
            Form1.OutArqRes=Form1.InArqCost.split('/')
          else:
            # improve it to Mac OS
            raise Exception("What platform is yours?? It's not Windows or Linux...")            
          Form1.OutArqRes=Form1.OutArqRes[-1].replace('.','_')
          
          self.logger.AppendText('Selected File: \n'+Form1.OutArqRes+'\n')
          Form1.NEXPER_FINAL=Form1.OutArqRes+'_'+Form1.NEXPER_AUX
          self.logger.AppendText("Automatically Map Cost Selected:\n")
          self.logger.AppendText(Form1.NEXPER_FINAL+"\n")
        
        
       
          
        if event.GetId()==250:
          self.logger.AppendText("Waiting ... :\n")
          Form1.readtxt=selectfile()
          Form1.fileHandle = open (Form1.readtxt, 'r' )
          Form1.patch_id_list=Form1.fileHandle.read() 
          Form1.patch_id_list_aux_b=Form1.patch_id_list.split(',')
          print Form1.patch_id_list_aux_b
          self.logger.AppendText("TXT Combinations \n"+`Form1.patch_id_list_aux_b`)
          
      

        if event.GetId()==10:   #10==START
                
          
         
          
          self.logger.AppendText("Checking the list \n")
          Form1.lenlist=len(Form1.patch_id_list_aux_b)
         
          
          if  Form1.lenlist <= 1: 
            d= wx.MessageDialog( self, " Incorrect list \n"
                                             ,"", wx.OK)
            # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # finally destroy it when finished.
            #frame.Close(True)  # Close the frame. 
            self.logger.AppendText(" Check list.. \n")
            
          elif Form1.lenlist > 1 and int (Form1.lenlist)%2 ==1 :
            
            d= wx.MessageDialog( self, "incorrect list \n Numbers odd patch, check the list \n  "
                                 ,"", wx.OK)
            # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # finally destroy it when finished.
              #frame.Close(True)  # Close the frame. 
          else:
            Form1.patch_id_list=Form1.patch_id_list_aux.split(',')
            self.logger.AppendText(" ok list \n")
            self.logger.AppendText(" waiting... \n")
            
           
            
           
            d= wx.MessageDialog( self, " Select the output folder for'\n' text files \n"
                               ,"", wx.OK)
            # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # finally destroy it when finished.
            Form1.OutDir_files_TXT=selectdirectory()
            self.logger.AppendText(" Selected output folder: \n"+Form1.OutDir_files_TXT)
            
          
            self.logger.AppendText(" running...: \n")
          self.logger.AppendText("\n creating list: \n"+`Form1.patch_id_list_aux_b`+'\n') 
          d= wx.MessageDialog( self," CLICK on ok and wait for the order di processing,\n the end will let you know , thank you"
                               ,"", wx.OK)
          
          retCode=d.ShowModal() # Shows 
          # finally destroy it when finished.
          d.Close(True)  
          
          #start time
          #start time
          Form1.time = datetime.now() # INSTANCE
          Form1.day_start=Form1.time.day
          Form1.month_start=Form1.time.month
          Form1.year_start=Form1.time.year
          Form1.hour_start=Form1.time.hour # GET START Form1.hour
          Form1.minuts_start=Form1.time.minute #GET START Form1.minuts
          Form1.second_start=Form1.time.second #GET START              
          
          
          Form1.time = datetime.now() # INSTANCE
          Form1.day=Form1.time.day
          Form1.month=Form1.time.month
          Form1.year=Form1.time.year
          Form1.hour=Form1.time.hour # GET START Form1.hour
          Form1.minuts=Form1.time.minute #GET START Form1.minuts
          Form1.second=Form1.time.second #GET START    
          
          
          
          os.chdir(Form1.OutDir_files_TXT)
          
          Form1.header_log="_____Log__Year_"+`Form1.year`+"-Month"+`Form1.month`+"-Day_"+`Form1.day`+"_Time_"+`Form1.hour`+"_"+`Form1.minuts`+"_"+`Form1.second`
          Form1.txt_log=open(Form1.header_log+".txt","w")       
          Form1.txt_log.write("Start time       : Year "+`Form1.year_start`+"-Month "+`Form1.month_start`+"-Day "+`Form1.day_start`+" ---- time: "+`Form1.hour_start`+":"+`Form1.minuts_start`+":"+`Form1.second_start`+"\n")
          
          
          Form1.S1=""
          Form1.T1=""
          Form1.C2=Form1.C2+''
          Form1.C3=Form1.C3+''
          Form1.C4=Form1.C4+''
          
          
          
          Form1.res=grass.read_command('g.region',flags='m')
          Form1.res2=Form1.res.split('\n')
          Form1.res3=Form1.res2[5]
          Form1.res3=float(Form1.res3.replace('ewres=',''))
          Form1.escfina1=(Form1.esc*2)/Form1.res3
          
          if Form1.escfina1%2==0:
            Form1.escfina1=int(Form1.escfina1)
            Form1.escfina1=Form1.escfina1+1
          else:
            Form1.escfina1=int(round(Form1.escfina1, ndigits=0))
             
          
          grass.run_command('g.region', rast=Form1.OutArqRes, res=Form1.res3)
          if Form1.Nsimulations2>0:
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors',input=Form1.OutArqRes,output=Form1.C2, method='mode',size=Form1.escfina1,overwrite = True)
            
          if Form1.Nsimulations3>0:
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors',input=Form1.OutArqRes,output=Form1.C3, method='average',size=Form1.escfina1,overwrite = True)
          
          if Form1.Nsimulations4>0:
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors',input=Form1.OutArqRes,output=Form1.C4, method='maximum',size=Form1.escfina1,overwrite = True)
          
          
          
         
          Form1.listafinal=[]
          
          for i in range(Form1.Nsimulations1):
            Form1.listafinal.append(Form1.OutArqRes)
            Form1.listaApoioaleat3.append('')
          for i in range(Form1.Nsimulations2):
            Form1.listafinal.append(Form1.C2)
            Form1.listaApoioaleat3.append('')
          for i in range(Form1.Nsimulations3):
            Form1.listafinal.append(Form1.C3)
            Form1.listaApoioaleat3.append('')
          for i in range(Form1.Nsimulations4):
            Form1.listafinal.append(Form1.C4)  
            Form1.listaApoioaleat3.append('')
          
          
            
            
          
            
            
          
          grass.run_command('g.region', rast=Form1.OutArqRes, res=Form1.res3)
          Form1.Nsimulations=Form1.Nsimulations1+Form1.Nsimulations2+Form1.Nsimulations3+Form1.Nsimulations4
          
                    
          #patch_id_list       
          Form1.patch_id_list=map(int,Form1.patch_id_list)
          while (len(Form1.patch_id_list)>1):
            Form1.ChecktTry=True
            os.chdir(Form1.OutDir_files_TXT)
            while Form1.ChecktTry==True:
              try:
                Form1.S1=Form1.patch_id_list[0]
                Form1.T1=Form1.patch_id_list[1]
                Form1.S1FORMAT='000000'+`Form1.S1`
                Form1.S1FORMAT=Form1.S1FORMAT[-5:]
                Form1.T1FORMAT='000000'+`Form1.T1`
                Form1.T1FORMAT=Form1.T1FORMAT[-5:]
              
                del Form1.patch_id_list[0:2]
                Form1.PAISGEM='EXPERIMENTO'
                Form1.ARQSAIDA=Form1.PAISGEM+'_s'+Form1.S1FORMAT+'_t'+Form1.T1FORMAT                  
                self.logger.AppendText(" suing pair: \n"+Form1.S1FORMAT+'&'+Form1.T1FORMAT+ '\n')  
                Form1.S1=(int(str(Form1.S1)))
                Form1.T1=(int(str(Form1.T1)))  
                Form1.form_02='source=if('+Form1.OutArqST+'!='+`Form1.S1`+',null(),'+`Form1.S1`+ ')'
                grass.mapcalc(Form1.form_02, overwrite = True, quiet = True)
                Form1.form_03='target=if('+Form1.OutArqST+'!='+`Form1.T1`+',null(),'+`Form1.T1`+ ')'
                grass.mapcalc(Form1.form_03, overwrite = True, quiet = True)
                
                grass.run_command('g.region', rast=Form1.OutArqST,verbose=False)
                grass.run_command('r.to.vect', input='source', out='source_shp', type='area',verbose=False, overwrite = True ) 
                grass.run_command('r.to.vect', input='target', out='target_shp', type='area',verbose=False, overwrite = True ) 
                grass.run_command ('v.db.addcolumn', map='source_shp', columns='x double precision,y double precision', overwrite = True)
                grass.run_command ('v.db.addcolumn', map='target_shp', columns='x double precision,y double precision', overwrite = True)
            
                grass.read_command ('v.to.db', map='source_shp', option='coor', columns="x,y", overwrite = True)
                grass.read_command ('v.to.db', map='target_shp', option='coor', columns="x,y", overwrite = True)
                
                Form1.var_source_x_b=grass.vector_db_select('source_shp', columns = 'x')['values'][1][0]
                Form1.var_source_y_b=grass.vector_db_select('source_shp', columns = 'y')['values'][1][0]
            
                Form1.var_target_x_b=grass.vector_db_select('target_shp', columns = 'x')['values'][1][0]
                Form1.var_target_y_b=grass.vector_db_select('target_shp', columns = 'y')['values'][1][0]
                Form1.ChecktTry=False
                
                #finaliza caso a lista esteja com valores invalidos no final
                
                  
              except:
                Form1.ChecktTry=True
                print ("Error defRasterize ST, Add col, Get x corrd ...")
                Form1.time = datetime.now() # INSTANCE
                Form1.day_now=Form1.time.day
                Form1.month_now=Form1.time.month
                Form1.year_now=Form1.time.year
                Form1.hour_now=Form1.time.hour # GET START Form1.hour
                Form1.minuts_now=Form1.time.minute #GET START Form1.minuts
                Form1.second_now=Form1.time.second #GET START                  
                Form1.listErrorLog.append("[Error ->-> :] < - Rasterize ST, Add col, Get x corrd : "+Form1.ARQSAIDA+" - > ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                Form1.listErrorLog.append("[Error ->-> :] < -Skip STS: "+Form1.ARQSAIDA)
                if len(Form1.patch_id_list)==0:
                  
                  Form1.txt_log.close() 
                  d= wx.MessageDialog( self," Error STs invalid , check please!"
                               ,"", wx.OK)
          
                  retCode=d.ShowModal() # Shows 
                  d.Close(True)         
                  break                
            
            Form1.var_source_x_b_int=float(Form1.var_source_x_b)
            Form1.var_source_y_b_int=float(Form1.var_source_y_b)
            Form1.var_target_x_b_int=float(Form1.var_target_x_b)
            Form1.var_target_y_b_int=float(Form1.var_target_y_b)
            
           
              
            defineregion("source_shp","target_shp", Form1.influensprocess) 
             
            
            
            
            
            
            
           
            Form1.mapa_corredores="corredores_s"+Form1.S1FORMAT+"_t"+Form1.T1FORMAT+'_COM0'
            Form1.mapa_corredores_sem0=Form1.NEXPER_FINAL+'_'+'S_'+Form1.S1FORMAT+"_T_"+Form1.T1FORMAT
            Form1.chekfolder=os.path.exists('Line_'+Form1.mapa_corredores_sem0)
            
            
            if Form1.chekfolder==False:
              os.mkdir('Line_'+str(Form1.mapa_corredores_sem0))
              Form1.outdir=Form1.OutDir_files_TXT+'\Line_'+Form1.mapa_corredores_sem0
            else:
              d= wx.MessageDialog( self, " Existing folder please select another location to save the lines \n"
                                   ,"", wx.OK)
              # Create a message dialog box
              d.ShowModal() # Shows it
              d.Destroy()              
              Form1.outdir=selectdirectory()            
            Form1.form_04='mapa_corredores=0'
            grass.mapcalc(Form1.form_04, overwrite = True, quiet = True)
            Form1.form_16='corredores_aux=0'
            grass.mapcalc(Form1.form_16, overwrite = True, quiet = True)
                            
            
              
              
              
            Form1.arquivo = open(Form1.mapa_corredores_sem0+'.txt','w')
            Form1.cabecalho='EXPERIMENT'','+'M'+','+'SIMULATION'+','+'LENGTHVECT'+','+'COST'+','+'Coord_source_x'+','+'Coord_source_y'+','+'Coord_target_x'+','+'Coord_target_y'+','+'Euclidean_Distance' '\n'
            Form1.arquivo.write(Form1.cabecalho)
            
            cont=0
            for i in range(Form1.Nsimulations):
                defineregion("source_shp","target_shp", Form1.influensprocess) 
                Form1.form_08='mapa_custo='+Form1.listafinal[cont]
                grass.mapcalc(Form1.form_08, overwrite = True, quiet = True)  
                
                grass.mapcalc("x = 0", overwrite = True, quiet = True) 
                
                      
                c=i+1
                
                self.logger.AppendText('=======> runing :'+`c`+ '\n' )
                
                grass.run_command('r.mask',raster='source')
                grass.run_command('g.region', vect='source_shp',verbose=False,overwrite = True)
                
                Form1.ChecktTry=True
                while Form1.ChecktTry==True:
                  try:
                    grass.run_command('v.random', output='temp_point1_s',n=30,overwrite = True)
                    grass.run_command('v.select',ainput='temp_point1_s',binput='source_shp',output='temp_point2_s',operator='overlap',overwrite = True)
                    grass.run_command('v.db.addtable', map='temp_point2_s',columns="temp double precision")
                    grass.run_command('v.db.connect',flags='p',map='temp_point2_s')
                    Form1.frag_list2=grass.vector_db_select('temp_point2_s', columns = 'cat')['values']
                    Form1.frag_list2=list(Form1.frag_list2)
                    Form1.selct="cat="+`Form1.frag_list2[0]`
                    grass.run_command('v.extract',input='temp_point2_s',output='pnts_aleat_S',where=Form1.selct,overwrite = True)
                    if len(Form1.frag_list2)>0:
                      Form1.ChecktTry=False
                    else:
                      Form1.ChecktTry=True
                  except:
                    Form1.ChecktTry=True
                    Form1.time = datetime.now() # INSTANCE
                    Form1.day_now=Form1.time.day
                    Form1.month_now=Form1.time.month
                    Form1.year_now=Form1.time.year
                    Form1.hour_now=Form1.time.hour # GET START Form1.hour
                    Form1.minuts_now=Form1.time.minute #GET START Form1.minuts
                    Form1.second_now=Form1.time.second #GET START                      
                    Form1.listErrorLog.append("[Error ->-> :] < - randomize points source : "+Form1.ARQSAIDA+" - > ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                    
                
                #
                grass.run_command('r.mask',flags='r')
                grass.run_command('r.mask',raster='target')
                grass.run_command('g.region', vect='target_shp',verbose=False,overwrite = True)
                Form1.ChecktTry=True
                while Form1.ChecktTry==True:
                  try:
                    grass.run_command('v.random', output='temp_point1_t',n=30 ,overwrite = True)
                    grass.run_command('v.select',ainput='temp_point1_t',binput='target_shp',output='temp_point2_t',operator='overlap',overwrite = True)
                    grass.run_command('v.db.addtable', map='temp_point2_t',columns="temp double precision")
                    grass.run_command('v.db.connect',flags='p',map='temp_point2_t')
                
                    Form1.frag_list2=grass.vector_db_select('temp_point2_t', columns = 'cat')['values']
                    Form1.frag_list2=list(Form1.frag_list2)
                    Form1.selct="cat="+`Form1.frag_list2[0]`                
                    grass.run_command('v.extract',input='temp_point2_t',output='pnts_aleat_T',where=Form1.selct,overwrite = True)  
                    if len(Form1.frag_list2)>0:
                      Form1.ChecktTry=False
                    else:
                      Form1.ChecktTry=True
                  except:
                    Form1.ChecktTry=True
                    Form1.time = datetime.now() # INSTANCE
                    Form1.day_now=Form1.time.day
                    Form1.month_now=Form1.time.month
                    Form1.year_now=Form1.time.year
                    Form1.hour_now=Form1.time.hour # GET START Form1.hour
                    Form1.minuts_now=Form1.time.minute #GET START Form1.minuts
                    Form1.second_now=Form1.time.second #GET START                      
                    Form1.listErrorLog.append("[Error ->-> :] < -  randomize points target : "+Form1.ARQSAIDA+" - > ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)

              
                
                grass.run_command('r.mask',flags='r')
                
                if Form1.influensprocess_boll:
                  defineregion("source_shp","target_shp", Form1.influensprocess)  
                else:
                  grass.run_command('g.region', rast=Form1.OutArqRes,verbose=False)
                
                
                Form1.ChecktTry=True  
                while Form1.ChecktTry==True:
                  try:
                    Form1.form_05='corredores_aux=mapa_corredores'
                    grass.mapcalc(Form1.form_05, overwrite = True, quiet = True)
                    Form1.ChecktTry=False
                  except:
                    Form1.ChecktTry=True
                    
                  Form1.ChecktTry=True
                  while Form1.ChecktTry==True:
                    try:
                      Form1.form_06="aleat=rand(1,100)"
                      grass.mapcalc(Form1.form_06,seed=random.randint(1, 10000),overwrite = True, quiet = True)
                      Form1.form_06="aleat2=aleat/100.0*"+`Form1.ruido_float`
                      grass.mapcalc(Form1.form_06, overwrite = True, quiet = True) 
                      Form1.form_07='custo_aux=mapa_custo*aleat2'
                      grass.mapcalc(Form1.form_07, overwrite = True, quiet = True)
                      Form1.form_07='custo_aux2=if(isnull(custo_aux),10000000,custo_aux)'
                      grass.mapcalc(Form1.form_07, overwrite = True, quiet = True)                      
                      defineregion("source_shp","target_shp", Form1.influensprocess) 
                      grass.run_command('r.cost', flags='k', input='custo_aux2', output='custo_aux_cost', start_points='pnts_aleat_S', stop_points='pnts_aleat_T',overwrite = True)
                      grass.run_command('r.drain', input='custo_aux_cost', output='custo_aux_cost_drain', start_points='pnts_aleat_T', overwrite = True)
                      grass.run_command('r.series',input='corredores_aux,custo_aux_cost_drain', output='mapa_corredores', method='sum',overwrite = True)
                      Form1.ChecktTry=False
                    except:
                      Form1.ChecktTry=True
                      Form1.time = datetime.now() # INSTANCE
                      Form1.day_now=Form1.time.day
                      Form1.month_now=Form1.time.month
                      Form1.year_now=Form1.time.year
                      Form1.hour_now=Form1.time.hour # GET START Form1.hour
                      Form1.minuts_now=Form1.time.minute #GET START Form1.minuts
                      Form1.second_now=Form1.time.second #GET START                       
                      Form1.listErrorLog.append("[Error ->-> :] < - Methods:aleat, aleat2, custo_aux, r.cost, r.drain, r.series  : "+Form1.ARQSAIDA+" - > ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- Time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                      
                    
                Form1.form_09='custo_aux_cost_drain_sum=custo_aux_cost_drain*'+Form1.listafinal[0]
                grass.mapcalc(Form1.form_09, overwrite = True, quiet = True)  
               
                
                #calculando custo
                Form1.x=grass.read_command('r.univar', map='custo_aux_cost_drain_sum')
                Form1.x_b=Form1.x.split('\n')
                Form1.x_c=str(Form1.x_b[14])
                Form1.var_cost_sum=float(Form1.x_c.replace("sum: ",""))
                
                
                             
                
                
                
                 
                if Form1.influensprocess_boll:
                  defineregion("source_shp","target_shp", Form1.influensprocess)  
                else:
                  grass.run_command('g.region', rast=Form1.OutArqRes,verbose=False)
                
                Form1.form_10=Form1.mapa_corredores_sem0+'=if(mapa_corredores==0,null(),mapa_corredores)'
                grass.mapcalc(Form1.form_10, overwrite = True, quiet = True)
                
               #calculando a distancia
                Form1.length=grass.read_command('r.univar', map='custo_aux_cost_drain')
                #print Form1.x
                Form1.length_b=Form1.length.split('\n')
                Form1.length_c=str(Form1.length_b[14])
                Form1.length_d=Form1.length_c[5:9]
                Form1.length_e=float(Form1.length_d)
                Form1.var_dist_line=Form1.res3*Form1.length_e
               
                
                Form1.euclidean_a =float((Form1.var_source_x_b_int-Form1.var_target_x_b_int)**2 + (Form1.var_source_y_b_int-Form1.var_target_y_b_int)**2)
                Form1.euclidean_b= Form1.euclidean_a**0.5
                if Form1.listafinal[cont]==Form1.OutArqRes:
                  Form1.M="M1"
                if Form1.listafinal[cont]=='M2_MODE':
                  Form1.M="M2"
                if Form1.listafinal[cont]=='M3_MAXIMUM':
                  Form1.M="M3"              
                if Form1.listafinal[cont]=='M4_AVERAGE':
                  Form1.M="M4"              
                if Form1.listafinal[cont]=='M5_AVERAGE_VIEW':
                  Form1.M="M5"                
                if Form1.listafinal[cont]=='M6_Unikon':
                  Form1.M="M6"                
                     
                                
                
                
                
                
                
                Form1.linha=Form1.listafinal[cont].replace("@PERMANENT",'')+','+Form1.M+','+`c`+','+ `Form1.var_dist_line`+','+ `Form1.var_cost_sum`+','+ `Form1.var_source_x_b`+','+ `Form1.var_source_y_b`+','+ `Form1.var_target_x_b`+','+ `Form1.var_target_y_b`+','+ `Form1.euclidean_b`+ "\n"
                Form1.linha=Form1.linha.replace('\'','')
                
                Form1.var_dist_line=0.0
                Form1.var_cost_sum=0.0
                
                
               
                Form1.arquivo.write(Form1.linha)
                Form1.linha=""
                
               
                Form1.outline1='000000'+`c`  
                Form1.outline1=Form1.outline1[-3:]
                Form1.outline1=Form1.mapa_corredores_sem0+"_SM_"+Form1.outline1
                
                grass.run_command('g.region',rast='custo_aux_cost_drain')
                grass.run_command('r.to.vect', input='custo_aux_cost_drain', output=Form1.outline1, type='line',verbose=False, overwrite = True )
                grass.run_command ('v.db.addcolumn', map=Form1.outline1, columns='dist double precision', overwrite = True)
                grass.read_command ('v.to.db', map=Form1.outline1, option='length', type='line', col='dist', units='me', overwrite = True)
                os.chdir(Form1.outdir)
                grass.run_command('v.out.ogr', input=Form1.outline1,dsn=Form1.outline1+'.shp',verbose=False,type='line')              
                grass.run_command('g.remove',type="vect",name=Form1.outline1, flags='f')              
                cont=cont+1
                
                
            Form1.arquivo.close()    
            Form1.listExport.append(Form1.mapa_corredores_sem0)
            grass.run_command('g.region', rast=Form1.mapa_corredores_sem0)
            
            os.chdir(Form1.OutDir_files_TXT)
            grass.run_command('r.out.gdal',input=Form1.mapa_corredores_sem0, out=Form1.mapa_corredores_sem0+'.tif',nodata=-9999)
            self.logger.AppendText(" removing auxiliary files...: \n")  
            
            #grass.run_command('g.remove',type="vect",name='temp_point1_s,M2_MODE,M3_MAXIMUM,M4_AVERAGE,temp_point2_s,temp_point1_t,temp_point2_t,pnts_aleat_S,pnts_aleat_T,source_shp,target_shp,custo_aux_cost_drain_sem0_line', flags='f')
            #grass.run_command('g.remove',type="rast",name='mapa_custo,custo_aux2,mapa_corredores,custo_aux_cost_drain,source,target,custo_aux_cost_drain_sum,custo_aux_cost_drain_sem0,custo_aux_cost,custo_aux,corredores_aux,aleat,aleat2,aleat2_Gros,aleat3,aleat_Gros,apoio1', flags='f')
            #grass.run_command('g.remove',type="rast",name='apoio2,apoio2b,apoio2c,apoio2d', flags='f')
            
            
            
            #grass.run_command('g.region', rast=Form1.OutArqRes,verbose=False)
          if len(Form1.listExport)>1:
            grass.run_command('r.series',input=Form1.listExport,out=Form1.NEXPER_FINAL+'CorrJoin',method="maximum")
            grass.run_command('g.region', rast=Form1.NEXPER_FINAL+'CorrJoin',verbose=False)
            grass.run_command('r.neighbors',input=Form1.NEXPER_FINAL+'CorrJoin',out=Form1.NEXPER_FINAL+"_LargeZone_Corridors", method='average',size=Form1.defaultsize_moviwin_allcor,overwrite = True)    
            grass.run_command('r.out.gdal',input=Form1.NEXPER_FINAL+"_LargeZone_Corridors", out=Form1.NEXPER_FINAL+"_LargeZone_Corridors.tif",nodata=-9999,overwrite = True)  
            grass.run_command('r.out.gdal',input=Form1.NEXPER_FINAL+'CorrJoin', out=Form1.NEXPER_FINAL+'CorrJoin.tif',nodata=-9999,overwrite = True)            

            grass.run_command('g.region', rast=Form1.NEXPER_FINAL+"_LargeZone_Corridors")
          else:
            grass.run_command('r.neighbors',input=Form1.mapa_corredores_sem0,out=Form1.NEXPER_FINAL+"_LargeZone_Corridors", method='average',size=Form1.defaultsize_moviwin_allcor,overwrite = True)    
            grass.run_command('r.out.gdal',input=Form1.NEXPER_FINAL+"_LargeZone_Corridors", out=Form1.NEXPER_FINAL+"_LargeZone_Corridors.tif",nodata=-9999,overwrite = True)  
                     
            
                      
          os.chdir(Form1.OutDir_files_TXT)
          
          
          #end time
          Form1.time = datetime.now() # INSTANCE
          Form1.day_end=Form1.time.day
          Form1.month_end=Form1.time.month
          Form1.year_end=Form1.time.year
          Form1.hour_end=Form1.time.hour # GET end Form1.hour
          Form1.minuts_end=Form1.time.minute #GET end Form1.minuts
          Form1.second_end=Form1.time.second #GET end Form1.seconds
          
          Form1.txt_log.write("End time         : Year "+`Form1.year_end`+"-Month "+`Form1.month_end`+"-Day "+`Form1.day_end`+" ---- Time: "+`Form1.hour_end`+":"+`Form1.minuts_end`+":"+`Form1.second_end`+"\n")
          Form1.diference_time=`Form1.month_end - Form1.month_start`+" Month - "+`abs(Form1.day_end - Form1.day_start)`+" Day - "+" Time: "+`abs(Form1.hour_end - Form1.hour_start)`+":"+`abs(Form1.minuts_end - Form1.minuts_start)`+":"+`abs(Form1.second_end - Form1.second_start)`
          
          Form1.txt_log.write("Processing time  : "+Form1.diference_time+"\n\n")
          
          
          Form1.txt_log.write("Inputs : \n")
          Form1.txt_log.write("	Cost Map               : "+Form1.OutArqRes+" \n")
          Form1.txt_log.write("	Source Target Map      : "+Form1.OutArqST+" \n")
          Form1.txt_log.write("	Variability            : "+`Form1.ruido_float`+" \n")
          Form1.txt_log.write("	Perception of scale    : "+`Form1.esc`+" \n")
          Form1.txt_log.write("	Number interactions M1 : "+`Form1.Nsimulations1`+" \n")
          Form1.txt_log.write("	Number interactions M2 : "+`Form1.Nsimulations2`+"\n")
          Form1.txt_log.write("	Number interactions M3 : "+`Form1.Nsimulations3`+"\n")
          Form1.txt_log.write("	Number interactions M4 : "+`Form1.Nsimulations4`+"\n")    
          
          Form1.txt_log.write("Output location : \n")
          Form1.txt_log.write("	"+Form1.OutDir_files_TXT+"\n\n")          
          
          for logERR in Form1.listErrorLog:
            Form1.txt_log.write(logERR+"\n")
          
          Form1.txt_log.close() 
          d= wx.MessageDialog( self," Finish"
                               ,"", wx.OK)
          
          retCode=d.ShowModal() # Shows 
            
          d.Close(True)         
                

                    
    def EvtText(self, event):
        

            
        if event.GetId()==180: #180=lista
          Form1.patch_id_list_aux=event.GetString()
          Form1.patch_id_list_aux_b=Form1.patch_id_list_aux.split(',')
          
          
          
              
          
          #print Form1.patch_id_list_aux_b
        if event.GetId()==186: #180=base name use
          Form1.ruido=event.GetString()
          Form1.ruido_float=float(Form1.ruido)        
        
        if event.GetId()==185: #183base name use
          Form1.NEXPER_APOIO=event.GetString()
          Form1.NEXPER_FINAL=Form1.NEXPER_AUX+"_"+Form1.NEXPER_APOIO
          Form1.NEXPER_FINAL=Form1.NEXPER_FINAL.replace('@PERMANENT','')
          self.logger.AppendText('Excerpt basename \n'+Form1.NEXPER_FINAL+ '\n')
          #print Form1.NEXPER_FINAL
            
        
        if event.GetId()==190: #190=numero de simulacoes
          Form1.Nsimulations1=int(event.GetString())
        if event.GetId()==191: #191=numero de simulacoes
          Form1.Nsimulations2=int(event.GetString())  
        if event.GetId()==192: #192=numero de simulacoes
          Form1.Nsimulations3=int(event.GetString())
        if event.GetId()==193: #193=numero de simulacoes
          Form1.Nsimulations4=int(event.GetString())  
          
             
          
          
          
          
        
            
             
                                
          
          
          
          
          
       
         
                    
                
          
          
          
          
          
          
          
          
       
      
        if event.GetId()==30: #30=popsize
            Form1.output_prefix=event.GetString()
        if event.GetId()==40: #40=timesteps
            not_int=0
            try: 
                int(event.GetString())
            except ValueError:
                not_int=1
                
            if not_int==1:
                Form1.timesteps=0
            else:
                Form1.timesteps=int(event.GetString())
                
        if event.GetId()==50: #50=numberruns
            not_int=0
            try: 
                int(event.GetString())
            except ValueError:
                not_int=1
                
            if not_int==1:
                Form1.numberruns=0
            else:
                Form1.numberruns=int(event.GetString()) 



                
    def EvtChar(self, event):
        self.logger.AppendText('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()
        
    def EvtCheckBox(self, event):
      if event.GetId()==94: #Form1.plotmovements
          if int(event.Checked())==1:
              Form1.plotmovements=1
          else:
              Form1.plotmovements=0
          self.logger.AppendText(' Plot Modeling: %s\n' % str(Form1.plotmovements))
          
    def OnExit(self, event):
        d= wx.MessageDialog( self, " Thanks for simulating using \n"
                            " LSCorridors V1.0 R.R", "Good bye", wx.OK)
                            # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 


#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
  
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSCorridors v. 1.0", pos=(0,0), size=(530,450))
    Form1(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
