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
from datetime import datetime

ID_ABOUT=101
ID_IBMCFG=102
ID_EXIT=110

VERSION = 'v. 1.0'

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

def defineregion(mapa1, mapa2, influenceprocess):
  '''
  This function uses two input vector maps and takes the limits 
  of the minimum GRASS GIS region (a rectangle) that encompasses these maps
  After that, for enabling noise processes and variability, a fixed value of scale
  ("influenceprocess") is added to the map limits and this is defined as the
  GRASS GIS region
  Input:
  - mapa1: vetor map inside GRASS GIS Database
  - mapa2: vetor map inside GRASS GIS Database
  - influenceprocess: float/integer - distance/scale to be added to the limits of the map, in meters
  No Outputs, the region is set.
  '''
  
  grass.run_command("g.region", vect=mapa1+","+mapa2)
  dicregion = grass.region()
  n = float(dicregion['n'])
  s = float(dicregion['s'])
  e = float(dicregion['e'])
  w = float(dicregion['w'])
  
  n = n+influenceprocess
  s = s-influenceprocess
  e = e+influenceprocess
  w = w-influenceprocess

  grass.run_command("g.region", n=n, e=e, s=s, w=w)


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
        Form1.InArqResist='Name of the file + ext '
        
        # Loads the name of the source-target map
        Form1.InArqST=''
        
        # Loads the name of a map to be imported into GRASS GIS and used for simulations
        Form1.OutArqResist=''
        
        # Variables with 'C' are used to generate output names for auxiliary maps M2,M3,M4
        # Name of mode map (M2)
        Form1.C2='M2_MODE'
        
        # Name of maximum map (M3)
        Form1.C3='M3_MAXIMUM'
        
        # Name of average map (M4)
        Form1.C4='M4_AVERAGE'
        
        # String to show an example of how the ST list should look like
        Form1.edtstart_list='Ex:1,2,3,4,...'
        
        # List of combinations of STs used in the simulation
        Form1.patch_id_list='' # List of combination of STs in list format
        Form1.patch_id_list_aux=''  # List of combination of STs in string format
        Form1.patch_id_list_aux_b='' # Aux list of combination of STs - list format, used to create all possible combinations
        
        #Formulas
        
        Form1.S1='' # Variable to select source points
        Form1.T1='' # Variable to select target points
        Form1.S1FORMAT='' # Variable to select source points, with zeros in front of it - for output files
        Form1.T1FORMAT='' # Variable to select target points, with zeros in front of it - for output files
        Form1.PAISAGEM='' # Prefix of the output text file with corridor information
        Form1.ARQSAIDA='' # Output text file with corridor information
        Form1.NEXPER_AUX='MSP' # Prefix for output files
        Form1.NEXPER_APOIO='' # Aux variable for defining output name
        Form1.NEXPER_FINAL='' # Final output map name
    
        # Variables used for mapcalc definition and calculation     
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
        
        # Variable to check if output folder exists
        Form1.checkfolder=''
    
    
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
        
        Form1.outline=''
        Form1.outline1=''
        Form1.outdir=''        
    

        Form1.arquivo=''
        Form1.M='' # Methods string for recording it in output text files
        
        Form1.var_cost_sum='' # Sum of cost map along LCP for one corridor, as float
        Form1.var_dist_line=0.0 # Length of the LCP for one corridor, as float
        
        Form1.cabecalho='' # Variable with headers for output text corridor information 
        Form1.linha='' # Variable with one line/simulation for output text corridor information 
        
        Form1.readtxt='' # Variable to recieve the name of ST combination input file
        Form1.lenlist=0.0
        Form1.lenlist_b=0.0
        Form1.Nsimulations=0 # Total number of simulations (independent of method)
        Form1.Nsimulations1=15 # Number of simulation of method M1
        Form1.Nsimulations2=15 # Number of simulation of method M2 (mode)
        Form1.Nsimulations3=15 # Number of simulation of method M3 (average)
        Form1.Nsimulations4=15 # Number of simulation of method M4 (maximum)
        
        Form1.escalafina=0
        Form1.esc=100 # Animal movement scale, in meters
                
        # Variables to calculate map resolution, to define the size of moving windows
        Form1.res='' # Aux variable
        Form1.res2=[] # Aux variable2
        Form1.res3='' # Final resolution of the map
        
        # Variables used to calculate the cost of LCP corridor
        Form1.x='' # Cost map statistics for one corridor, string format
        Form1.x_b='' # Cost map statistics for one corridor, list format
        Form1.x_c='' # Sum of cost map along LCP for one corridor, as string                
        
        # Variables for calculating length of the LCP
        Form1.length='' # Statistics for corridor
        Form1.length_b='' # String element for sum of number of pixels of the corridor
        Form1.length_c='' # Final LCP length value, string format
        Form1.length_d='' # Final LCP length value, in pixels
        Form1.length_e=0.0 # Final LCP length value, in meters
        
        # Variables for calculating Euclidean distance between points

        # Variables for position of ST points - string
        Form1.var_source_x='' # x (long) value for source point, as string
        Form1.var_source_y='' # y (lat) value for source point, as string
        Form1.var_target_x='' # x (long) value for target point, as string
        Form1.var_target_y='' # y (lat) value for target point, as string
        # Variables for position of ST points - float
        Form1.var_source_x_b_int=0.0 # x (long) value for source point, as float
        Form1.var_source_y_b_int=0.0 # y (lat) value for source point, as float
        Form1.var_target_x_b_int=0.0 # x (long) value for target point, as float
        Form1.var_target_y_b_int=0.0 # y (lat) value for target point, as float        
        # Aux variables
        Form1.euclidean_a=0.0 # Aux variable for calculating euclidean distance
        Form1.euclidean_b=0.0 # Aux variable for calculating euclidean distance        
        
        
        Form1.ChecktTry=True # Aux variable for using in loops        

        Form1.ruido='2.0' # Variability scale for generating the noise map, in string format
        Form1.ruido_float=2.0 # Variability scale for generating the noise map, in float format
        Form1.listafinal=[] # List of resistance maps to be simulated
        Form1.escfinal=0
        Form1.escE=''
        Form1.escW=''
        Form1.escfinal=0.0
        Form1.frag=''
        Form1.frag_list=''
        Form1.frag_list2=''
        Form1.selct=''   
        Form1.defaultsize_moviwin_allcor=7 # Default moving window size to calculate resistance maps for methods M2, M3, M4
        ###
        Form1.txt_log=''
        
        # Start time
        Form1.time = 0 # INSTANCE
        Form1.day_start=0 # Start day
        Form1.month_start=0 # Start month
        Form1.year_start=0 # Start year
        Form1.hour_start=0 # Start hour
        Form1.minuts_start=0 # Start minutes
        Form1.second_start=0 # Start seconds
       
        # End time
        Form1.time = '' # INSTANCE
        Form1.day_end=0 # End day
        Form1.month_end=0 # End month
        Form1.year_end=0 # End year
        Form1.hour_end=0 # # End hour
        Form1.minuts_end=0 # End minutes
        Form1.second_end=0 # End seconds  
        
        # Header for log file
        Form1.header_log=''
        
        # Time for log file name
        Form1.time = 0 # INSTANCE
        Form1.day=0 # Day
        Form1.month=0 # Month
        Form1.year=0 # Year
        Form1.hour=0 # Hour
        Form1.minuts=0 # Minutes
        Form1.second=0 # Second             
        
        # Current time - to be used while simulations are performed
        Form1.time = 0 # INSTANCE
        Form1.day_now=0 # Current day
        Form1.month_now=0 # Current month
        Form1.year_now=0 # Current year
        Form1.hour_now=0 # Current hour
        Form1.minuts_now=0 # Current minute
        Form1.second_now=0 # Current second
        
        Form1.listErrorLog=[] # List of error messages to be written to the log file
        Form1.difference_time='' # Time lag for processing simulations
        
        Form1.n=''
        Form1.s=''
        Form1.e=''
        Form1.w=''
        Form1.dicregion=''
        Form1.influenceprocess=10000 # Distance to consider variability in corridors and ST points, in meters
        Form1.influenceprocess_boll=False # Boolean - is the variability in the region around ST points to be considered?
        
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #-------------------------------------------------------------------INITIALIZING GUI----------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        try:
          grass.run_command('r.mask', flags='r')
        except:
          pass
        
        
        #---------------------------------------------#
        #-------------- STATIC TEXT ------------------#
        #---------------------------------------------#
        
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

        #---------------------------------------------#
        #----------------- LAB LOGO ------------------#
        #---------------------------------------------#

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
        self.lbllista = wx.StaticText(self, -1, "Enter a list manually:", wx.Point(20,150))
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
        self.editname3 = wx.TextCtrl(self, 186, str(Form1.ruido_float), wx.Point(455,55), wx.Size(30,-1))
        self.editname4 = wx.TextCtrl(self, 190, str(Form1.Nsimulations1), wx.Point(90,228), wx.Size(35,-1))
        #### ADD MESSAGE HERE!!!!
        self.editname5 = wx.TextCtrl(self, 191, str(Form1.Nsimulations2), wx.Point(150,228), wx.Size(35,-1))
        self.editname6 = wx.TextCtrl(self, 192, str(Form1.Nsimulations3), wx.Point(210,228), wx.Size(35,-1))
        self.editname7 = wx.TextCtrl(self, 193, str(Form1.Nsimulations4), wx.Point(270,228), wx.Size(35,-1))
        self.editname8 = wx.TextCtrl(self, 196, str(Form1.esc), wx.Point(405,175), wx.Size(50,-1))
         
         
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
        Resistance Map name is stored in a variable called Form1.OutArqResist
        Variable Form1.NEXPER_FINAL also stores resistance map name; if the user does not inform 
        an output name for the simulation, corridor output names will have the same name as the input 
        resistance map
        """
        
        if event.GetId()==93:   
            # Gets resistance map name and stores it in Form1.OutArqResist
            Form1.OutArqResist=event.GetString()
            
            # Gets resistance map name and stores it in Form1.NEXPER_FINAL (in case the user does not provide an output file name)
            Form1.NEXPER_FINAL=event.GetString()
            Form1.NEXPER_FINAL=Form1.NEXPER_AUX+'_'+Form1.NEXPER_FINAL
            
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
          grass.run_command ('r.in.gdal', flags='o', input=Form1.InArqResist, output=Form1.OutArqResist, overwrite=True, verbose = False)
          
          # Imports a ST map, ignoring projections
          grass.run_command ('r.in.gdal', flags='o', input=Form1.InArqST, output= Form1.OutArqST, overwrite=True, verbose = False)
          
          # Setting GRASS GIS region to the largest (resistance) map
          grass.run_command('g.region', rast=Form1.OutArqResist, verbose=False)
          
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
        variable Form1.patch_id_list, which is then used to generate simulations
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
            Form1.patch_id_list=Form1.patch_id_list_aux_b
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
        
        if event.GetId() == 205:   #205==export maps
        
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
                    
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------SELECT ST MAP INSIDE A DIRECTORY: ID 210-------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
         
        """
        ID 210: Allows the user to select the file that corresponds to the ST Map
        The name of the map is stored, but the map is not imported unless the button "IMPORT FILES" is pressed
        If imported and no other map is selected in the combobox, this ST Map is selected for the simulations
        """
        
        if event.GetId() == 210:   #210==Select ST map file
          # Message in the Dialog box
          self.logger.AppendText("Waiting ... :\n")
          
          # Calls selectfile function, that returns the file name in the variable Form1.InArqST
          Form1.InArqST=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            Form1.OutArqST=Form1.InArqST.split('\\')
          elif platform.system() == 'Linux':
            Form1.OutArqST=Form1.InArqST.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")
          Form1.OutArqST=Form1.OutArqST[-1].replace('.','_')
          
          # Message in the Dialog box
          self.logger.AppendText('Selected File: \n'+Form1.OutArqST+'\n')
          #self.logger.AppendText("Automatically Map ST Selected:\n")
          #self.logger.AppendText(Form1.OutArqST+"\n")
         
         
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
                         
         
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #--------------------------------------------------------SELECT RESISTANCE MAP INSIDE A DIRECTORY: ID 230-------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        """
        ID 230: Allows the user to select the file that corresponds to the Resistance Map
        The name of the map is stored, but the map is not imported unless the button "IMPORT FILES" is pressed
        If imported and no other map is selected in the combobox, this Resistance Map is selected for the simulations
        """        
        
        if event.GetId() == 230:   #230==Select resistance map file
          # Message in the Dialog box
          self.logger.AppendText("Waiting ... :\n")
          
          # Calls selectfile function, that returns the file name in the variable Form1.InArqST
          Form1.InArqResist=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            Form1.OutArqResist=Form1.InArqResist.split('\\')
          elif platform.system() == 'Linux':
            Form1.OutArqResist=Form1.InArqResist.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")            
          Form1.OutArqResist=Form1.OutArqResist[-1].replace('.','_')
          
          # Messages in the Dialog box
          self.logger.AppendText('Selected File: \n'+Form1.OutArqResist+'\n')
          
          # Updating output file name in the variable Form1.NEXPER_FINAL
          Form1.NEXPER_FINAL=Form1.NEXPER_AUX+'_'+Form1.OutArqResist
          self.logger.AppendText("Automatically Map Cost Selected:\n")
          self.logger.AppendText(Form1.NEXPER_FINAL+"\n")
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
                           
           
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #--------------------------------------------------------READS EXTERNAL LIST OF ST COMBINATIONS: ID 250---------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        """
        ID 250: Allows the user to select the file that corresponds to a pre-defined list of source-target combinations
        """

        if event.GetId() == 250:   #250==Select file with list of STs
          # Message in the Dialog box
          self.logger.AppendText("Waiting ... :\n")
          
          # Calls selectfile function, that returns the file name in the variable Form1.readtxt
          Form1.readtxt=selectfile()
          
          # Opens and reads the list as a string and transforms it into a list
          Form1.fileHandle = open(Form1.readtxt, 'r')
          Form1.patch_id_list_aux=Form1.fileHandle.read()
          Form1.fileHandle.close()
          Form1.patch_id_list=Form1.patch_id_list_aux.split(',')
          
          # Prints list of ST combinations
          print Form1.patch_id_list
          self.logger.AppendText("TXT Combinations:\n"+`Form1.patch_id_list`+"\n")
          

        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #--------------------------------------------------------START SIMULATION BUTTON: ID 10-------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        """
        ID 10: This is the button that really starts the simulations, given the options set before
        """
        
        if event.GetId() == 10:   #10==START BUTTON
          
          #---------------------------------------------#
          #--------------- CHECK ST LIST ---------------#
          #---------------------------------------------#
                
          # Message in the Dialog box
          self.logger.AppendText("Checking the list \n")
          
          # Size of the ST list
          Form1.lenlist=len(Form1.patch_id_list)
         
          # Tests if the length of the ST list is > 1
          if  Form1.lenlist <= 1: 
            d= wx.MessageDialog(self, "Incorrect list\n"+
                                "List length is smaller than 1!\n"+
                                "Please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
          
          # Tests if the length of the ST list is even
          elif Form1.lenlist > 1 and int (Form1.lenlist)%2 == 1:
            
            d= wx.MessageDialog(self, "Incorrect list\n"+
                                "List length cannot be odd,"+
                                "please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
          
          # If everything ok with list length, go on
          else:
            
            # List of STs: Form1.patch_id_list
            self.logger.AppendText("List ok.\n")
            self.logger.AppendText("Waiting...\n")
            
            # Selects output directory for text files
            d=wx.MessageDialog(self, "Select the output folder for\n"+
                                "text files.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            Form1.OutDir_files_TXT = selectdirectory()
            self.logger.AppendText("Selected output folder: \n"+Form1.OutDir_files_TXT)
          
            # Start running
            self.logger.AppendText("Running...:\n")
            
          self.logger.AppendText("\nList of source-targets: \n"+`Form1.patch_id_list`+'\n') 
          d = wx.MessageDialog(self,"Click OK and wait for simulation processing;\n"+
                              "A message will warn you at the end of simulations."+
                              "Thank you.","", wx.OK)
          retCode=d.ShowModal() # Shows 
          d.Close(True) # Finally destroy it when finished.
          
          #---------------------------------------------#
          #--------------- PREPARE SIMULATIONS ---------#
          #---------------------------------------------#
          # Simulation settings
          
          # Start time
          Form1.time = datetime.now() # INSTANCE
          Form1.day_start=Form1.time.day # Start day
          Form1.month_start=Form1.time.month # Start month
          Form1.year_start=Form1.time.year # Start year
          Form1.hour_start=Form1.time.hour # Start hour
          Form1.minuts_start=Form1.time.minute # Start minute
          Form1.second_start=Form1.time.second # Start second
          
          # Current time
          Form1.time = datetime.now() # INSTANCE
          Form1.day=Form1.time.day # Current day
          Form1.month=Form1.time.month # Current month
          Form1.year=Form1.time.year # Current year
          Form1.hour=Form1.time.hour # Current hour
          Form1.minuts=Form1.time.minute # Current minute
          Form1.second=Form1.time.second # Current second
          
          # Change to output directory
          os.chdir(Form1.OutDir_files_TXT)
          
          # Starting log file
          Form1.header_log="___Log_Year_"+`Form1.year`+"-Month"+`Form1.month`+"-Day_"+`Form1.day`+"_Time_"+`Form1.hour`+"_"+`Form1.minuts`+"_"+`Form1.second`
          Form1.txt_log=open(Form1.header_log+".txt","w")       
          Form1.txt_log.write("Start time       : Year "+`Form1.year_start`+"-Month "+`Form1.month_start`+"-Day "+`Form1.day_start`+" ---- time: "+`Form1.hour_start`+":"+`Form1.minuts_start`+":"+`Form1.second_start`+"\n")
          
          #######################################3
          Form1.S1="" # Variable to select a source point
          Form1.T1="" # Variable to select a target point
          Form1.C2=Form1.C2+''
          Form1.C3=Form1.C3+''
          Form1.C4=Form1.C4+''
          
          # Defining GRASS GIS region as output map region
          grass.run_command('g.region', rast=Form1.OutArqResist)#, res=Form1.res3)
          
          # Reading map resolution
          Form1.res = grass.read_command('g.region', flags='m')
          Form1.res2 = Form1.res.split('\n')
          Form1.res3 = Form1.res2[5]
          Form1.res3 = float(Form1.res3.replace('ewres=',''))
          
          # Defining the size of the moving windows, in pixels
          # It is defined given the animal movement scale (user defined parameter)
          #  and the resolution of the map (map grain or pixel size) 
          Form1.escfina1=(Form1.esc*2)/Form1.res3
          
          # Checking if number of pixels of moving window is integer
          #  and correcting it if necessary
          if Form1.escfina1%2==0:
            Form1.escfina1=int(Form1.escfina1)
            Form1.escfina1=Form1.escfina1+1
          else:
            Form1.escfina1=int(round(Form1.escfina1, ndigits=0))
          
          # Defining GRASS GIS region as output map region
          # grass.run_command('g.region', rast=Form1.OutArqResist)#, res=Form1.res3)          
          
          # If methods M2, M3, M4 are going to be simulated, this command prepares
          # the resistance map tanking into consider these methods
          if Form1.Nsimulations2 > 0: # mode
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors', input=Form1.OutArqResist, output=Form1.C2, method='mode', size=Form1.escfina1, overwrite = True)
            
          if Form1.Nsimulations3 > 0: # average
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors', input=Form1.OutArqResist, output=Form1.C3, method='average', size=Form1.escfina1, overwrite = True)
          
          if Form1.Nsimulations4 > 0: # maximum
            Form1.defaultsize_moviwin_allcor=Form1.escfina1
            grass.run_command('r.neighbors', input=Form1.OutArqResist, output=Form1.C4, method='maximum', size=Form1.escfina1, overwrite = True)
          
          # Organizes names of resistance maps to be used in simulations
          Form1.listafinal=[]
          
          for i in range(Form1.Nsimulations1):
            Form1.listafinal.append(Form1.OutArqResist)
          for i in range(Form1.Nsimulations2):
            Form1.listafinal.append(Form1.C2)
          for i in range(Form1.Nsimulations3):
            Form1.listafinal.append(Form1.C3)
          for i in range(Form1.Nsimulations4):
            Form1.listafinal.append(Form1.C4)
          
          # Not necessary
          #grass.run_command('g.region', rast=Form1.OutArqResist, res=Form1.res3)
          
          # Total number of simulations (M! + M2 + M3 + M4)
          Form1.Nsimulations = Form1.Nsimulations1 + Form1.Nsimulations2 + Form1.Nsimulations3 + Form1.Nsimulations4
          
          # Transforming list of STs in integers (for recongnizing them in the map)       
          Form1.patch_id_list=map(int,Form1.patch_id_list)
          
          #---------------------------------------------#
          #--------------- START SIMULATIONS -----------#
          #---------------------------------------------#
          
          # For each ST pair in the list:
          while (len(Form1.patch_id_list)>1):
            
            Form1.ChecktTry=True
            # Change to output dir
            os.chdir(Form1.OutDir_files_TXT)
            
            # Select a pair from the list and prepare vectors for processing
            while Form1.ChecktTry==True:
              try:
                # Selects from the beginning to the end of the list
                Form1.S1=Form1.patch_id_list[0]
                Form1.T1=Form1.patch_id_list[1]
                Form1.S1FORMAT='000000'+`Form1.S1`
                Form1.S1FORMAT=Form1.S1FORMAT[-5:]
                Form1.T1FORMAT='000000'+`Form1.T1`
                Form1.T1FORMAT=Form1.T1FORMAT[-5:]
                
                # Selects pair and delete it from the original ST combination list
                del Form1.patch_id_list[0:2]
                Form1.PAISAGEM='EXPERIMENT'
                Form1.ARQSAIDA=Form1.PAISAGEM+'_s'+Form1.S1FORMAT+'_t'+Form1.T1FORMAT # Name of ouput text file                  
                self.logger.AppendText("Processing ST pair: \n"+Form1.S1FORMAT+' & '+Form1.T1FORMAT+ '\n')  
                Form1.S1=(int(str(Form1.S1)))
                Form1.T1=(int(str(Form1.T1)))
                
                # Generates rasters with only the region of the source and terget points
                Form1.form_02='source = if('+Form1.OutArqST+' != '+`Form1.S1`+', null(), '+`Form1.S1`+ ')'
                grass.mapcalc(Form1.form_02, overwrite = True, quiet = True)
                Form1.form_03='target = if('+Form1.OutArqST+' != '+`Form1.T1`+', null(), '+`Form1.T1`+ ')'
                grass.mapcalc(Form1.form_03, overwrite = True, quiet = True)
                
                # Transform source and target rasters into vectors
                grass.run_command('g.region', rast=Form1.OutArqST, verbose=False)
                grass.run_command('r.to.vect', input='source', out='source_shp', type='area', verbose=False, overwrite = True ) 
                grass.run_command('r.to.vect', input='target', out='target_shp', type='area', verbose=False, overwrite = True ) 
                # Adds x and y coordinates as columns to the vectors attribute
                grass.run_command ('v.db.addcolumn', map='source_shp', columns='x double precision,y double precision', overwrite = True)
                grass.run_command ('v.db.addcolumn', map='target_shp', columns='x double precision,y double precision', overwrite = True)
                
                grass.read_command ('v.to.db', map='source_shp', option='coor', columns="x,y", overwrite = True)
                grass.read_command ('v.to.db', map='target_shp', option='coor', columns="x,y", overwrite = True)
                
                # Selects x,y coordinates of source point
                Form1.var_source_x=grass.vector_db_select('source_shp', columns = 'x')['values'][1][0]
                Form1.var_source_y=grass.vector_db_select('source_shp', columns = 'y')['values'][1][0]
                # Selects x,y coordinates of source point
                Form1.var_target_x=grass.vector_db_select('target_shp', columns = 'x')['values'][1][0]
                Form1.var_target_y=grass.vector_db_select('target_shp', columns = 'y')['values'][1][0]
                Form1.ChecktTry=False
                
              # In case the list of x,y is invalid, skips the simulation pair of STs with Error message, and keeps on simulating other pairs
              except:
                Form1.ChecktTry=True
                # Error message on GRASS GIS console
                print ("Error def Rasterize ST, Add cols, Get x,y cords...")
                Form1.time = datetime.now() # INSTANCE
                Form1.day_now=Form1.time.day # Error day
                Form1.month_now=Form1.time.month # Error month
                Form1.year_now=Form1.time.year # Error year
                Form1.hour_now=Form1.time.hour # Error hour
                Form1.minuts_now=Form1.time.minute # Error minute
                Form1.second_now=Form1.time.second # Error second
                
                # Updates Log file
                Form1.listErrorLog.append("[Error ->-> :] <- Rasterize ST, Add cols, Get x,y corrd : "+Form1.ARQSAIDA+" -> ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                Form1.listErrorLog.append("[Error ->-> :] <- Skip STS: " + Form1.ARQSAIDA)
                
                # Finishes the simulation process if there are no more ST pairs
                if len(Form1.patch_id_list)==0:
                  
                  Form1.txt_log.close() 
                  d= wx.MessageDialog( self,"Error: STs invalid, please check them!", "", wx.OK)
                  retCode=d.ShowModal() # Shows
                  d.Close(True) # Closes
                  break                
            
            # Transforms ST coordinates in float
            Form1.var_source_x_b_int=float(Form1.var_source_x)
            Form1.var_source_y_b_int=float(Form1.var_source_y)
            Form1.var_target_x_b_int=float(Form1.var_target_x)
            Form1.var_target_y_b_int=float(Form1.var_target_y)
            
           
            # Set region defined by the limits of source and target points + fixed distance (Form1.influenceprocess)
            #  This reduces simulation time, since map processing may be restricted to 
            #  the region where points are located
            defineregion("source_shp", "target_shp", Form1.influenceprocess) 
            
            # Name of the corridor output map
            Form1.mapa_corredores_sem0=Form1.NEXPER_FINAL+'_'+'S_'+Form1.S1FORMAT+"_T_"+Form1.T1FORMAT
            
            # Checks if the output folder for text files exists; 
            # If not, creates it.
            Form1.checkfolder=os.path.exists('Line_'+Form1.mapa_corredores_sem0)
            
            if Form1.chekfolder==False:
              os.mkdir('Line_'+str(Form1.mapa_corredores_sem0))
              if platform.system() == 'Windows':
                Form1.outdir=Form1.OutDir_files_TXT+'\Line_'+Form1.mapa_corredores_sem0
              elif platform.system() == 'Linux':
                Form1.outdir=Form1.OutDir_files_TXT+'Line_'+Form1.mapa_corredores_sem0
              else:
                # Improve it to Mac OS - how does it work?
                raise Exception("What platform is yours?? It's not Windows or Linux...")
            else:
              d= wx.MessageDialog( self, "Folder for text files already exists!\n"+
                                   "Please select another directory to save the output.\n", "", wx.OK) # Create a message dialog box
              d.ShowModal() # Shows it
              d.Destroy() # Closes
              Form1.outdir=selectdirectory() # Choose output folder, if the previous one already exists
              
            # Initializes corridor and auxiliary map
            Form1.form_04='mapa_corredores = 0'
            grass.mapcalc(Form1.form_04, overwrite = True, quiet = True)
            Form1.form_16='corredores_aux = 0'
            grass.mapcalc(Form1.form_16, overwrite = True, quiet = True)
            
            # Open output text file and writes headers      
            Form1.arquivo = open(Form1.mapa_corredores_sem0+'.txt','w')
            Form1.cabecalho='EXPERIMENT'','+'M'+','+'SIMULATION'+','+'LENGTHVECT'+','+'COST'+','+'Coord_source_x'+','+'Coord_source_y'+','+'Coord_target_x'+','+'Coord_target_y'+','+'Euclidean_Distance' '\n'
            Form1.arquivo.write(Form1.cabecalho)
            
            #---------------------------------------------#
            #-------- PERFORMS EACH SIMULATION -----------#
            #---------------------------------------------#
            cont=0
            for i in range(Form1.Nsimulations):
                # Set region defined by the limits of source and target points + fixed distance (Form1.influenceprocess)
                defineregion("source_shp","target_shp", Form1.influenceprocess)
                
                # Selecting resistance map
                Form1.form_08='mapa_resist = '+Form1.listafinal[cont]
                grass.mapcalc(Form1.form_08, overwrite = True, quiet = True)  
                
                # Number of simulation   
                c=i+1
                
                # Message in dialog box
                self.logger.AppendText('=======> Running simulation '+`c`+ '\n')
                
                #---------- RANDOM SOURCE POINT -------#
                # Defines a random source point inside the input/source region
                grass.run_command('r.mask', raster='source') # Mask - look only at source region
                grass.run_command('g.region', vect='source_shp', verbose=False, overwrite = True)
                
                # Select a random source point
                Form1.ChecktTry=True
                while Form1.ChecktTry==True:
                  try:
                    # Generates random points
                    grass.run_command('v.random', output='temp_point1_s', n=30, overwrite = True)
                    # Selects random points that overlap with source region
                    grass.run_command('v.select', ainput='temp_point1_s', binput='source_shp', output='temp_point2_s', operator='overlap', overwrite = True)
                    # Creates attribute table and connects to the random points inside source region
                    grass.run_command('v.db.addtable', map='temp_point2_s', columns="temp double precision")
                    grass.run_command('v.db.connect', flags='p', map='temp_point2_s')
                    # List of such random points inside Python
                    Form1.frag_list2=grass.vector_db_select('temp_point2_s', columns = 'cat')['values']
                    Form1.frag_list2=list(Form1.frag_list2)
                    # Selects the first (a random) point of the list
                    Form1.selct="cat="+`Form1.frag_list2[0]`
                    grass.run_command('v.extract', input='temp_point2_s', output='pnts_aleat_S', where=Form1.selct, overwrite = True)
                    
                    if len(Form1.frag_list2)>0:
                      Form1.ChecktTry=False
                    else:
                      Form1.ChecktTry=True
                      
                  # If an error in selecting a random source point occurs, this is registered here and a new random point is selected
                  except:
                    Form1.ChecktTry=True
                    # Error message on GRASS GIS console
                    print ("Error Randomize source points...")                    
                    # Registering error in logfile
                    Form1.time = datetime.now() # INSTANCE
                    Form1.day_now=Form1.time.day # Error day
                    Form1.month_now=Form1.time.month # Error month
                    Form1.year_now=Form1.time.year # Error year
                    Form1.hour_now=Form1.time.hour # Error hour
                    Form1.minuts_now=Form1.time.minute # Error minute
                    Form1.second_now=Form1.time.second # Error second
                    Form1.listErrorLog.append("[Error ->-> :] <- Randomize source points: "+Form1.ARQSAIDA+" -> ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                    
                
                # Removing mask
                grass.run_command('r.mask',flags='r')
                
                #---------- RANDOM TARGET POINT -------#
                # Defines a random target point inside the input/target region
                grass.run_command('r.mask',raster='target')
                grass.run_command('g.region', vect='target_shp',verbose=False,overwrite = True)
                # Select a random target point
                Form1.ChecktTry=True
                while Form1.ChecktTry==True:
                  try:
                    # Generates random points
                    grass.run_command('v.random', output='temp_point1_t',n=30 ,overwrite = True)
                    # Selects random points that overlap with target region
                    grass.run_command('v.select',ainput='temp_point1_t',binput='target_shp',output='temp_point2_t',operator='overlap',overwrite = True)
                    # Creates attribute table and connects to the random points inside target region
                    grass.run_command('v.db.addtable', map='temp_point2_t',columns="temp double precision")
                    grass.run_command('v.db.connect',flags='p',map='temp_point2_t')
                    
                    # List of such random points inside Python
                    Form1.frag_list2=grass.vector_db_select('temp_point2_t', columns = 'cat')['values']
                    Form1.frag_list2=list(Form1.frag_list2)

                    # Selects the first (a random) point of the list
                    Form1.selct="cat="+`Form1.frag_list2[0]`                
                    grass.run_command('v.extract',input='temp_point2_t',output='pnts_aleat_T',where=Form1.selct,overwrite = True)  
                    
                    if len(Form1.frag_list2)>0:
                      Form1.ChecktTry=False
                    else:
                      Form1.ChecktTry=True
                      
                  # If an error in selecting a random target point occurs, this is registered here and a new random point is selected
                  except:
                    Form1.ChecktTry=True
                    # Error message on GRASS GIS console
                    print ("Error Randomize target points...")                     
                    # Registering error in logfile
                    Form1.time = datetime.now() # INSTANCE
                    Form1.day_now=Form1.time.day # Error day
                    Form1.month_now=Form1.time.month # Error month
                    Form1.year_now=Form1.time.year # Error year
                    Form1.hour_now=Form1.time.hour # Error hour
                    Form1.minuts_now=Form1.time.minute # Error minute
                    Form1.second_now=Form1.time.second # Error second
                    Form1.listErrorLog.append("[Error ->-> :] <- Randomize target points: "+Form1.ARQSAIDA+" -> ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- time : "+`Form1.hour_now `+":"+`Form1.second_now`)

                # Removing mask
                grass.run_command('r.mask',flags='r')
                
                ######################################################
                # If the user wants to consider only the region around ST points, this region
                #  is selected as GRASS region; otherwise, the whole resistance map region is set
                #  as GRASS region
                if Form1.influenceprocess_boll:
                  defineregion("source_shp","target_shp", Form1.influenceprocess)  
                else:
                  grass.run_command('g.region', rast=Form1.OutArqResist,verbose=False)
                
                #---------- GENERATE CORRIDOR -------#
                Form1.ChecktTry=True  
                while Form1.ChecktTry==True:
                  try:
                    Form1.form_05='corredores_aux = mapa_corredores'
                    grass.mapcalc(Form1.form_05, overwrite = True, quiet = True)
                    Form1.ChecktTry=False
                  except:
                    Form1.ChecktTry=True
                    
                  Form1.ChecktTry=True
                  while Form1.ChecktTry==True:
                    try:
                      # Creates a raster of uniformely distributed random values in the interval [1,100)
                      Form1.form_06="aleat = rand(1,100)"
                      grass.mapcalc(Form1.form_06, seed=random.randint(1, 10000), overwrite = True, quiet = True)
                      # Transforms raster map of random values to the range [0.1*noise, noise), where "noise" is
                      #  the variability factor defined by the user (variable Form1.ruido_float)
                      Form1.form_06="aleat2 = aleat/100.0 * "+`Form1.ruido_float`
                      grass.mapcalc(Form1.form_06, overwrite = True, quiet = True)
                      # Multiply resistance map by random noise map
                      Form1.form_07='resist_aux = mapa_resist * aleat2'
                      grass.mapcalc(Form1.form_07, overwrite = True, quiet = True)
                      # Sets null cells as vistually infinite resistance
                      Form1.form_07='resist_aux2 = if(isnull(resist_aux), 10000000, resist_aux)'
                      grass.mapcalc(Form1.form_07, overwrite = True, quiet = True)
                      
                      # Sets GRASS region
                      defineregion("source_shp","target_shp", Form1.influenceprocess)
                      
                      # Generating cumulative cost raster map for linking S and T points
                      grass.run_command('r.cost', flags='k', input='resist_aux2', output='custo_aux_cost', start_points='pnts_aleat_S', stop_points='pnts_aleat_T', overwrite = True)
                      # Tracing the least cost path (corridor) - the flow based on cumulative cost map
                      grass.run_command('r.drain', input='custo_aux_cost', output='custo_aux_cost_drain', start_points='pnts_aleat_T', overwrite = True)
                      # Transforms null cells (no corridor) in zeros
                      # Now we have a corridor map
                      grass.run_command('r.series', input='corredores_aux,custo_aux_cost_drain', output='mapa_corredores', method='sum', overwrite = True)
                      Form1.ChecktTry=False
                      
                    # If an error in generating corridors, this is registered here and the algoeithm tries to generate the corridor again
                    except:
                      Form1.ChecktTry=True
                      # Error message on GRASS GIS console
                      print ("Error Corridor methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series...")
                      # Registering error in logfile
                      Form1.time = datetime.now() # INSTANCE
                      Form1.day_now=Form1.time.day # Error day
                      Form1.month_now=Form1.time.month # Error month
                      Form1.year_now=Form1.time.year # Error year
                      Form1.hour_now=Form1.time.hour # Error hour
                      Form1.minuts_now=Form1.time.minute # Error minute
                      Form1.second_now=Form1.time.second # Error second
                      Form1.listErrorLog.append("[Error ->-> :] <- Methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series: "+Form1.ARQSAIDA+" -> ---"+`Form1.year_now`+"-"+ `Form1.month_now` + "-"+ `Form1.day_now`+" --- Time : "+`Form1.hour_now `+":"+`Form1.second_now`)
                      
                # Multiply corridor map (binary - 0/1) by the original resistance map
                # Now we get a raster with the cost of each pixel along the LCP
                Form1.form_09='custo_aux_cost_drain_sum = custo_aux_cost_drain * '+Form1.listafinal[0]
                grass.mapcalc(Form1.form_09, overwrite = True, quiet = True)  
               
                # CALCULATES COST
                Form1.x = grass.read_command('r.univar', map='custo_aux_cost_drain_sum')
                # List of corridor statistics
                Form1.x_b = Form1.x.split('\n')
                # Sum of the cost of each pixel along the LCP, string format
                Form1.x_c = str(Form1.x_b[14])
                # Value of the LCP total cost, float format
                Form1.var_cost_sum = float(Form1.x_c.replace("sum: ",""))
                
                
                # Defining GRASS region
                if Form1.influenceprocess_boll:
                  defineregion("source_shp", "target_shp", Form1.influenceprocess)  
                else:
                  grass.run_command('g.region', rast=Form1.OutArqResist, verbose=False)
                
                # Corridor map with NULL cells instead of zeros
                Form1.form_10=Form1.mapa_corredores_sem0+' = if(mapa_corredores == 0, null(), mapa_corredores)'
                grass.mapcalc(Form1.form_10, overwrite = True, quiet = True)
                
                # CALCULATES LCP LENGTH using corridor map (with NULL values)
                Form1.length = grass.read_command('r.univar', map='custo_aux_cost_drain')
                # List of statistics
                Form1.length_b=Form1.length.split('\n')
                # Sum of pixels (value 1) of the corridor, string format
                Form1.length_c=str(Form1.length_b[14])
                # Sum of pixels of the corridor, float format
                Form1.length_d=Form1.length_c[5:9]
                Form1.length_e=float(Form1.length_d)
                # Distance in meters (multiply map resolution by distance in pixels)
                Form1.var_dist_line=Form1.res3*Form1.length_e
               
                # CALCULATES EUCLIDEAN DISTANCE between S and T points
                Form1.euclidean_a = float((Form1.var_source_x_b_int-Form1.var_target_x_b_int)**2 + (Form1.var_source_y_b_int-Form1.var_target_y_b_int)**2)
                Form1.euclidean_b = Form1.euclidean_a**0.5
                
                # Recording corridor method in output text files
                if Form1.listafinal[cont]==Form1.OutArqResist:
                  Form1.M="M1"
                if Form1.listafinal[cont]=='M2_MODE':
                  Form1.M="M2"
                if Form1.listafinal[cont]=='M3_MAXIMUM':
                  Form1.M="M3"              
                if Form1.listafinal[cont]=='M4_AVERAGE':
                  Form1.M="M4"              
                if Form1.listafinal[cont]=='M5_AVERAGE_VIEW': ##### ?????????????????????????
                  Form1.M="M5"                
                if Form1.listafinal[cont]=='M6_Unikon': ###### ?????????????????
                  Form1.M="M6"                
                     
                # Produces information for one corridor - to be appended to the output text file
                Form1.linha=Form1.listafinal[cont].replace("@PERMANENT",'')+','+Form1.M+','+`c`+','+ `Form1.var_dist_line`+','+ `Form1.var_cost_sum`+','+ `Form1.var_source_x`+','+ `Form1.var_source_y`+','+ `Form1.var_target_x`+','+ `Form1.var_target_y`+','+ `Form1.euclidean_b`+ "\n"
                Form1.linha=Form1.linha.replace('\'','')
                
                # Writes corridor information on output text file
                Form1.arquivo.write(Form1.linha)
                
                # Generates a vector line map for each corridor (vectorizing raster map)
                Form1.outline1='000000'+`c`  
                Form1.outline1=Form1.outline1[-3:]
                Form1.outline1=Form1.mapa_corredores_sem0+"_SM_"+Form1.outline1
                
                # Vectorizes corridor raster map
                grass.run_command('g.region', rast='custo_aux_cost_drain')
                grass.run_command('r.to.vect', input='custo_aux_cost_drain', output=Form1.outline1, type='line',verbose=False, overwrite = True)
                # Add column with corridor (LCP) length, in meters
                grass.run_command ('v.db.addcolumn', map=Form1.outline1, columns='dist double precision', overwrite = True)
                grass.read_command ('v.to.db', map=Form1.outline1, option='length', type='line', col='dist', units='me', overwrite = True)
                # Exports output vector
                os.chdir(Form1.outdir)
                grass.run_command('v.out.ogr', input=Form1.outline1,dsn=Form1.outline1+'.shp',verbose=False,type='line')              
                grass.run_command('g.remove', type="vect", name=Form1.outline1, flags='f')              
                cont=cont+1
                
                # Re-initializes corridor variables
                Form1.var_dist_line=0.0
                Form1.var_cost_sum=0.0                
                Form1.linha=""                
                
                # -------- HERE ENDS THE SIMULATION OF ONE CORRIDOR ------------------#
                # -------- THE LOOPS CONTINUES UNTIL ALL CORRIDORS ARE SIMULATES -----#
                
            # All corridors were simulated - close output text file    
            Form1.arquivo.close()
            
            # Exports raster map with all corridors for the selected ST pair
            Form1.listExport.append(Form1.mapa_corredores_sem0)
            grass.run_command('g.region', rast=Form1.mapa_corredores_sem0)
            
            os.chdir(Form1.OutDir_files_TXT)
            grass.run_command('r.out.gdal', input=Form1.mapa_corredores_sem0, out=Form1.mapa_corredores_sem0+'.tif', nodata=-9999)
            self.logger.AppendText("Removing auxiliary files... \n")  
            
            #grass.run_command('g.remove', type="vect", name='temp_point1_s,M2_MODE,M3_MAXIMUM,M4_AVERAGE,temp_point2_s,temp_point1_t,temp_point2_t,pnts_aleat_S,pnts_aleat_T,source_shp,target_shp,custo_aux_cost_drain_sem0_line', flags='f')
            #grass.run_command('g.remove', type="rast", name='mapa_resist,resist_aux2,mapa_corredores,custo_aux_cost_drain,source,target,custo_aux_cost_drain_sum,custo_aux_cost_drain_sem0,custo_aux_cost,resist_aux,corredores_aux,aleat,aleat2,aleat2_Gros,aleat3,aleat_Gros', flags='f')
            
            
          #---------------------------------------------#
          #-------- EXPORTS SYNTHESIS MAPS -------------#
          #---------------------------------------------#
          
          # If there is more than one combination of STs, two maps are generated:
          #  - CorrJoin, a map with the maximum frequency value for each pixel
          #  - LargeZone_Corridors, an average map of corridors, considering all simulations all STs
          if len(Form1.listExport)>1:
            
            grass.run_command('r.series', input=Form1.listExport, out=Form1.NEXPER_FINAL+'CorrJoin', method="maximum")
            grass.run_command('g.region', rast=Form1.NEXPER_FINAL+'CorrJoin', verbose=False)
            grass.run_command('r.neighbors', input=Form1.NEXPER_FINAL+'CorrJoin', out=Form1.NEXPER_FINAL+"_LargeZone_Corridors", method='average', size=Form1.defaultsize_moviwin_allcor, overwrite = True)
            grass.run_command('r.out.gdal', input=Form1.NEXPER_FINAL+"_LargeZone_Corridors", out=Form1.NEXPER_FINAL+"_LargeZone_Corridors.tif", nodata=-9999, overwrite = True)
            grass.run_command('r.out.gdal', input=Form1.NEXPER_FINAL+'CorrJoin', out=Form1.NEXPER_FINAL+'CorrJoin.tif', nodata=-9999, overwrite = True)

            grass.run_command('g.region', rast=Form1.NEXPER_FINAL+"_LargeZone_Corridors")
          
          # If there is only one combination of STs, one map is generated:
          #  - LargeZone_Corridors, an average map of corridors, considering all simulations all STs
          else:
            grass.run_command('r.neighbors', input=Form1.mapa_corredores_sem0, out=Form1.NEXPER_FINAL+"_LargeZone_Corridors", method='average', size=Form1.defaultsize_moviwin_allcor, overwrite = True)
            grass.run_command('r.out.gdal', input=Form1.NEXPER_FINAL+"_LargeZone_Corridors", out=Form1.NEXPER_FINAL+"_LargeZone_Corridors.tif", nodata=-9999, overwrite = True)
                     
          #---------------------------------------------#
          #------------ WRITES LOG FILES ---------------#
          #---------------------------------------------#            
          
          # Output directory
          os.chdir(Form1.OutDir_files_TXT)
          
          
          # Simulation end time
          Form1.time = datetime.now() # INSTANCE
          Form1.day_end=Form1.time.day # End day
          Form1.month_end=Form1.time.month # End month
          Form1.year_end=Form1.time.year # End year
          Form1.hour_end=Form1.time.hour # End hour
          Form1.minuts_end=Form1.time.minute # End minute
          Form1.second_end=Form1.time.second # End second
          
          Form1.txt_log.write("End time         : Year "+`Form1.year_end`+"-Month "+`Form1.month_end`+"-Day "+`Form1.day_end`+" ---- Time: "+`Form1.hour_end`+":"+`Form1.minuts_end`+":"+`Form1.second_end`+"\n")
          
          # Simulation time
          Form1.difference_time=`Form1.month_end - Form1.month_start`+" Month - "+`abs(Form1.day_end - Form1.day_start)`+" Day - "+" Time: "+`abs(Form1.hour_end - Form1.hour_start)`+":"+`abs(Form1.minuts_end - Form1.minuts_start)`+":"+`abs(Form1.second_end - Form1.second_start)`
          
          # Writes log file
          Form1.txt_log.write("Processing time  : "+Form1.difference_time+"\n\n")
          
          Form1.txt_log.write("Inputs : \n")
          Form1.txt_log.write("	Resistance Map          : "+Form1.OutArqResist+" \n")
          Form1.txt_log.write("	Source Target Map       : "+Form1.OutArqST+" \n")
          Form1.txt_log.write("	Variability             : "+`Form1.ruido_float`+" \n")
          Form1.txt_log.write("	Perception of scale (m) : "+`Form1.esc`+" \n")
          Form1.txt_log.write("	Number of simulations M1: "+`Form1.Nsimulations1`+" \n")
          Form1.txt_log.write("	Number of simulations M2: "+`Form1.Nsimulations2`+"\n")
          Form1.txt_log.write("	Number of simulations M3: "+`Form1.Nsimulations3`+"\n")
          Form1.txt_log.write("	Number of simulations M4: "+`Form1.Nsimulations4`+"\n")    
          
          Form1.txt_log.write("Output location : \n")
          Form1.txt_log.write("	"+Form1.OutDir_files_TXT+"\n\n")          
          
          for logERR in Form1.listErrorLog:
            Form1.txt_log.write(logERR+"\n")
          
          Form1.txt_log.close() 
          d = wx.MessageDialog(self,"Corridor simulation finished!"+
                              "Thanks for simulating using LSCorridors "+VERSION+"!", "", wx.OK)
          retCode = d.ShowModal() # Shows 
          d.Close(True) # Closes
                

    def EvtText(self, event):
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------TEXT EVENTS------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
      
        """
        ID 180: Reads list of ST points
        """
        if event.GetId() == 180: #180=list of STs
          Form1.patch_id_list_aux=event.GetString()
          Form1.patch_id_list=Form1.patch_id_list_aux.split(',')
        
        """
        ID 186: Defines the variability of the map - noise factor
        """
        if event.GetId() == 186: #180=variability factor
          Form1.ruido=event.GetString()
          Form1.ruido_float=float(Form1.ruido)        

        """
        ID 185: Reads output map name
        """
        if event.GetId() == 185: #185=base name
          Form1.NEXPER_APOIO=event.GetString()
          Form1.NEXPER_FINAL=Form1.NEXPER_AUX+"_"+Form1.NEXPER_APOIO
          Form1.NEXPER_FINAL=Form1.NEXPER_FINAL.replace('@PERMANENT','')
          self.logger.AppendText('Output map base name: \n'+Form1.NEXPER_FINAL+ '\n')
            
        """
        ID 190-193: Reads number of simulations for each method: M!, M2, M3, M4
        """
        # Method M!
        if event.GetId() == 190: #190=number of simulations
          Form1.Nsimulations1=int(event.GetString())
        # Method M2
        if event.GetId() == 191: #191=number of simulations
          Form1.Nsimulations2=int(event.GetString())  
        # Method M3
        if event.GetId() == 192: #192=number of simulations
          Form1.Nsimulations3=int(event.GetString())
        # Method M4
        if event.GetId() == 193: #193=number of simulations
          Form1.Nsimulations4=int(event.GetString())  
        
    #############################################
    def OnExit(self, event):
        d= wx.MessageDialog(self, " Thanks for simulating using\n"
                            " LSCorridors "+ VERSION +" R.R", "Good bye", wx.OK) # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 


#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
  
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSCorridors "+VERSION, pos=(0,0), size=(530,450))
    Form1(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
