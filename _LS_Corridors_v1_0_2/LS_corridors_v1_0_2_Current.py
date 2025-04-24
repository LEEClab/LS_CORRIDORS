
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
 
 Contributors:
 Bernardo Niebuhr - bernardo_brandaum@yahoo.com.br
 Juliana Silveira dos Santos - juliana.silveiradossantos@gmail.com
 Felipe Martello - felipemartello@gmail.com
 Pavel Dodonov - pdodonov@gmail.com
 
 Description:
 LSCorridors is a free and open source package developed in Python 
 that simulates multiples functional ecological corridors.
 The software runs in a GRASS GIS environment.
 It can also be found at: https://github.com/LEEClab/LS_CORRIDORS
 
 To run LSCorridors:
 python LS_corridors_v1_0.py
 
 To run tests:
 python test_LS_corridors.py
 
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
 along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
#---------------------------------------------------------------------------------------

# Import modules
import grass.script as grass
from PIL import Image
import wx
import random, math
import os, sys, re, platform
from datetime import datetime
from osgeo import gdal, ogr, osr

# LS Corridors Version:
VERSION = 'v. 2.0'

#----------------------------------------------------------------------------------
# Auxiliary functions

def definy_Gproj():
  f = open("EPSG.txt", "r")
  EPSGNumber=int(f.readline())
  f.close()
  
 
  #grass.run_command("g.proj", flags='c',epsg=EPSG)
  
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
    print (">>..................",dialog.GetPath())
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
  dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.FD_OPEN)
  if dialog.ShowModal() == wx.ID_OK:
    print (">>..................",dialog.GetPath())
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
  '''
  # define reginon for processing
  # 
  grass.run_command('g.region', rast=st_map, verbose=False)
  
  listRstats=grass.read_command('r.stats', input=st_map, flags='n', separator='space')
  b=[]
  b=listRstats.split('\n')
  del b[-1]
  print (b)
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
   

def  StaticText(self):
  self.quote = wx.StaticText(self, id=-1, label="Import Maps:", pos=wx.Point(20,95))    
  font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
  self.quote.SetForegroundColour("red")
  self.quote.SetFont(font)
  
  
  
# GLOBAIS TEMPORARIAS
in_path = ""
out_path =""
src_ds = ""
##
srcband = ""
dst_layername = ""
drv = ""
sp_ref = ""
dst_layer = ""

fld = ""
dst_layer =""
dst_field = ""

remove_raster_external= ""
caminho=""
nameFile=""
caminho=""

print("......................................................................................................................")
epsg=open("EPSG.txt",'r')
epsgline=int(epsg.readline())
if  epsgline != "":
  grass.run_command('g.proj',flags='c',epsg=epsgline)
  print("......................................................................................................................",epsgline)
  




definy_Gproj()
class Corridors(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        
        # Takes the current mapset and looks for maps only inside it
        self.current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')
        
        # List of possible resistance and ST maps (already loaded inside GRASS GIS DataBase)
        self.listmaps=grass.list_grouped('rast')[self.current_mapset]
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------BLOCK OF VARIABLE DESCRIPTION--------------------------------------------------------------------------------------------#
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        # Remove aux maps in the end?
        self.remove_aux_maps = True
        
        # Performing tests on the code?
        self.perform_tests = False
        
        # Loads the output directory - only for RUN EXPORT button
        self.OutDir_files='Path of the files'

        # Loads the path to the output files - used while running the corridors
        self.OutDir_files_TXT=''
        
        # Loads the name of the resistance matrix
        self.InArqResist='Name of the file + ext'
        
        # Loads the name of the source-target map
        self.InArqST=''
        
        # Loads the name of a map to be imported into GRASS GIS and used for simulations
        self.OutArqResist=''
        
        # List of methods to be simulated
        self.methods=[]
        
        # Variables with 'C' are used to generate output names for auxiliary maps MLmin,MLavg,MLmax
        # Name of minimum map (MLmin)
        self.C2_pre='MLmin_MINIMUM'
        
        # Name of average map (MLavg)
        self.C3_pre='MLavg_AVERAGE'
        
        # Name of maximum map (MLmax)
        self.C4_pre='MLmax_MAXIMUM'
        
        # String to show an example of how the ST list should look like
        self.edtstart_list='Ex:1,2,3,4,...'
        
        # List of combinations of STs used in the simulation
        self.patch_id_list='' # List of combination of STs in list format
        self.patch_id_list_aux=''  # List of combination of STs in string format
        self.patch_id_list_aux_b='' # Aux list of combination of STs - list format, used to create all possible combinations
        
        # For defining output corridor map name
        self.NEXPER_AUX='MSP' # Prefix for output files
        self.NEXPER_AUX_txt='Results' # Prefix for output files
        self.NEXPER_APOIO='' # Aux variable for defining output name
        self.NEXPER_FINAL='' # Final output map name
        self.NEXPER_FINAL_txt='' # Final output text name
        
        # GUI Parameters
        self.ruido='2.0' # Variability scale for generating the noise map, in string format
        self.ruidos_float=[2.0] # Variability scale for generating the noise map, in float format
        
        self.escalas=[100] # Animal movement scale, in meters
        
        self.Nsimulations =0 # Total number of simulations (independent of method)
        self.Nsimulations1=15 # Number of simulation of method MP
        self.Nsimulations2=15 # Number of simulation of method MLmin (minimum)
        self.Nsimulations3=15 # Number of simulation of method MLavg (average)
        self.Nsimulations4=15 # Number of simulation of method MLmax (maximum)
        
        self.influence_factor = 1.1 # In case we are going to close the computing window, its size is increased by 110% the scale paramater in each side
        self.influenceprocess = self.influence_factor * float(self.escalas[0]) # Distance beyond the window size of a given ST pair, in meters
        self.influenceprocess_boll = False # Boolean - are we going to close the computing window around each ST map?
        
        # Auxiliary variables
        
        self.S1='' # Variable to select source points
        self.T1='' # Variable to select target points
        self.S1FORMAT='' # Variable to select source points, with zeros in front of it - for output files
        self.T1FORMAT='' # Variable to select target points, with zeros in front of it - for output files
        self.PAISAGEM='' # Prefix of the output text file with corridor information
        self.ARQSAIDA='' # Output text file with corridor information        
    
        # Variables used for mapcalc definition and calculation     
        self.form_02=''
        self.form_03=''
        self.form_04=''
        self.form_05=''
        self.form_06=''
        self.form_07=''
        self.form_08=''
        self.form_09=''
        self.form_10=''
        self.form_11=''
        self.form_12=""
        self.form_13=''
        self.form_14=""
        self.form_15=''
        self.form_16=''
        self.form_17=""
        self.form_18=""
        
        # Output
        
        # Variable to check if output folder exists
        self.checkfolder=''
    
        self.listExport=[] # List of corridor raster maps to be exported in the end of simulations
        self.listExportMethod=[] # List of method for corridor raster maps to be exported in the end of simulations

        self.outline1='' # Aux variable for transforming each corridor in a vector map
        self.outdir='' # Output dir for text files
        self.arquivo='' # File where to write corridor information
        self.M='' # Methods string for recording it in output text files
        
        self.txt_log='' # File where to write simulation log
        self.cabecalho='' # Variable with headers for output text corridor information
        self.linha='' # Variable with one line/simulation for output text corridor information
        
        self.readtxt='' # Variable to recieve the name of ST combination input file
        self.lenlist=0.0
        self.lenlist_b=0.0
                
        # Variables to calculate map resolution, to define the size of moving windows
        self.res='' # Aux variable
        self.res2=[] # Aux variable2
        self.res3='' # Final resolution of the map
        
        # Variables used to calculate the cost of LCP corridor
        self.x='' # Cost map statistics for one corridor, string format
        self.x_b='' # Cost map statistics for one corridor, list format
        self.x_c='' # Sum of cost map along LCP for one corridor, as string                
        
        # Variables for calculating length of the corridor
        self.length='' # Statistics for corridor
        self.length_b='' # String element for sum of number of pixels of the corridor
        self.length_c='' # Final corridor length value, string format
        self.length_d='' # Final corridor length value, in pixels
        self.length_e=0.0 # Final corridor length value, in meters
        
        # Variables for calculating Euclidean distance between points

        # Variables for position of ST points - string
        self.var_source_x='' # x (long) value for source point, as string
        self.var_source_y='' # y (lat) value for source point, as string
        self.var_target_x='' # x (long) value for target point, as string
        self.var_target_y='' # y (lat) value for target point, as string
        # Variables for position of ST points - float
        self.var_source_x_b_int=0.0 # x (long) value for source point, as float
        self.var_source_y_b_int=0.0 # y (lat) value for source point, as float
        self.var_target_x_b_int=0.0 # x (long) value for target point, as float
        self.var_target_y_b_int=0.0 # y (lat) value for target point, as float        
        # Aux variables
        self.euclidean_a=0.0 # Aux variable for calculating euclidean distance
        self.euclidean_b=0.0 # Aux variable for calculating euclidean distance
        
        # Variables where corridor cost and length are loaded
        self.var_cost_sum='' # Sum of cost map along LCP for one corridor, as float
        self.var_dist_line=0.0 # Length of the LCP for one corridor, as float        
        
        # Other aux variables
        self.ChecktTry=True # Aux variable for using in loops        

        self.listafinal=[] # List of resistance maps to be simulated
        self.frag_list2='' # Aux list variable for generating random source/target points
        self.selct='' # Aux variable for generating random source/target points 
        self.defaultsize_moviwin_allcor=7 # Default moving window size to calculate resistance maps for methods MLmin, MLavg, MLmax
        
        # Start time
        self.time = 0 # INSTANCE
        self.day_start=0 # Start day
        self.month_start=0 # Start month
        self.year_start=0 # Start year
        self.hour_start=0 # Start hour
        self.minuts_start=0 # Start minutes
        self.second_start=0 # Start seconds
       
        # End time
        self.time = '' # INSTANCE
        self.day_end=0 # End day
        self.month_end=0 # End month
        self.year_end=0 # End year
        self.hour_end=0 # # End hour
        self.minuts_end=0 # End minutes
        self.second_end=0 # End seconds  
        
        # Header for log file
        self.header_log=''          
        
        # Current time - to be used while simulations are performed
        self.time = 0 # INSTANCE
        self.day_now=0 # Current day
        self.month_now=0 # Current month
        self.year_now=0 # Current year
        self.hour_now=0 # Current hour
        self.minuts_now=0 # Current minute
        self.second_now=0 # Current second
        
        self.listErrorLog=[] # List of error messages to be written to the log file
        self.difference_time='' # Time lag for processing simulations
        
        
        
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
        
        #if not self.perform_tests:
        self.imageFile0 = 'img_lscorr.jpg'
        im0 = Image.open(self.imageFile0)
        jpg0 = wx.Image(self.imageFile0, wx.BITMAP_TYPE_ANY).Scale(250, 64).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg0, (20,20), (jpg0.GetWidth(), jpg0.GetHeight()), style=wx.SUNKEN_BORDER)          
        
        #self.quote = wx.StaticText(self, id=-1, label="LandScape Corridors",pos=wx.Point(20, 20))
        
        #font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        #self.quote.SetForegroundColour("blue")
        #self.quote.SetFont(font)
        
        #__________________________________________________________________________________________ 
        StaticText(self)
        #self.quote = wx.StaticText(self, id=-1, label="Import Maps:", pos=wx.Point(20,95))    
        #font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        #self.quote.SetForegroundColour("red")
        #self.quote.SetFont(font)   
                
        #__________________________________________________________________________________________                
        self.quote = wx.StaticText(self, id=-1, label="Using Maps Already Imported:", pos=wx.Point(20,150))
        
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)          
        
        #__________________________________________________________________________________________
        self.quote = wx.StaticText(self, id=-1, label="Number of Simulations:", pos=wx.Point(20,268))
                
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)                      
      
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self,5, "",wx.Point(20,409), wx.Size(320,100),wx.TE_MULTILINE | wx.TE_READONLY)
      
        #---------------------------------------------#
        #-------------- BUTTONS ----------------------#
        #---------------------------------------------#
        
        self.button =wx.Button(self, 10, "START SIMULATIONS", wx.Point(20,519))
        wx.EVT_BUTTON(self, 10, self.OnClick)
  
        self.button =wx.Button(self, 205, "RUN EXPORT FILES ", wx.Point(145,519))
        wx.EVT_BUTTON(self, 205, self.OnClick)
        
        self.button =wx.Button(self, 210, "SELECT FILE", wx.Point(286,115))#st
        wx.EVT_BUTTON(self, 210, self.OnClick)
        
        self.button =wx.Button(self, 230, "SELECT FILE", wx.Point(102,115)) #cost
        wx.EVT_BUTTON(self, 230, self.OnClick)
        
        
        self.button =wx.Button(self, 240, "IMPORT FILE", wx.Point(369,115))
        wx.EVT_BUTTON(self, 240, self.OnClick)
        
        self.button =wx.Button(self, 250, "READ LIST TXT", wx.Point(322,202))
        wx.EVT_BUTTON(self, 250, self.OnClick)

        self.button =wx.Button(self, 260, "COMBINE ALL", wx.Point(418,202))
        wx.EVT_BUTTON(self, 260, self.OnClick)
        
        self.button =wx.Button(self, 8, "EXIT", wx.Point(265, 519))
        wx.EVT_BUTTON(self, 8, self.OnExit)

        #---------------------------------------------#
        #----------------- LAB LOGO ------------------#
        #---------------------------------------------#

        #if not self.perform_tests:
        self.imageFile = 'logo_lab.png'
        im1 = Image.open(self.imageFile)
        jpg1 = wx.Image(self.imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (348,410), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------STATIC TEXTS-----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.lblname = wx.StaticText(self, -1, "Resistance-Mp:", wx.Point(20,118))
        self.lblname2 = wx.StaticText(self, -1, "Source\Target-Mp:", wx.Point(186,120))
        self.lblname2 = wx.StaticText(self, -1, "Variability:", wx.Point(459,120))
        self.lblname = wx.StaticText(self, -1, "Resistance:", wx.Point(20,175))
        self.lblname = wx.StaticText(self, -1, "ST:", wx.Point(300,175))
        self.lbllista = wx.StaticText(self, -1, "Enter a list manually:", wx.Point(20,207))
        self.lblname = wx.StaticText(self, -1, "Without landscape influence:", wx.Point(70,290))
        self.lblname = wx.StaticText(self, -1, "MP:", wx.Point(70,315))
        self.lblname = wx.StaticText(self, -1, "With landscape influence:", wx.Point(70,345))
        self.lblname = wx.StaticText(self, -1, "MLmin (minimum):", wx.Point(70,370))
        self.lblname = wx.StaticText(self, -1, "MLavg (average):", wx.Point(230,370))
        self.lblname = wx.StaticText(self, -1, "MLmax (maximum):", wx.Point(390,370))
        self.lblname = wx.StaticText(self, -1, "Name of output corridor:", wx.Point(20,240))
        self.lblname = wx.StaticText(self, -1, "Scale (meters):", wx.Point(370,240))
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------TEXT CONTROLS----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.editname1 = wx.TextCtrl(self, 180, self.edtstart_list, wx.Point(132,203), wx.Size(189,-1))
        self.editname2 = wx.TextCtrl(self, 185, 'Proposed name of the cost map', wx.Point(154,235), wx.Size(195,-1))
        self.editname3 = wx.TextCtrl(self, 186, ','.join(str(i) for i in self.ruidos_float), wx.Point(515,115), wx.Size(30,-1))
        self.editname3.SetToolTip(wx.ToolTip("Variability factor, x: in each simulation, "+
                                             "resistance value for each pixel in the resistance surface map is multiplied "+
                                             "by a uniformly randomly distributed number in the interval [0.1*x, x)."))
        self.editname4 = wx.TextCtrl(self, 190, str(self.Nsimulations1), wx.Point(93,312), wx.Size(35,-1))
        self.editname4.SetToolTip(wx.ToolTip("Method MP: no spatial influence"))
        
        self.editname5 = wx.TextCtrl(self, 191, str(self.Nsimulations2), wx.Point(175,367), wx.Size(35,-1))
        self.editname5.SetToolTip(wx.ToolTip("Method MLmin: minimum\n\n"+
                                             "Each resistance surface pixel is replaced by the minimum of pixel values "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))
        
        self.editname6 = wx.TextCtrl(self, 192, str(self.Nsimulations3), wx.Point(322,367), wx.Size(35,-1))
        self.editname6.SetToolTip(wx.ToolTip("Method MLavg: average\n\n"+
                                             "Each resistance surface pixel is replaced by the mean pixel value "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))  
        
        self.editname7 = wx.TextCtrl(self, 193, str(self.Nsimulations4), wx.Point(500,367), wx.Size(35,-1))
        self.editname7.SetToolTip(wx.ToolTip("Method MLmax: maximum\n\n"+
                                             "Each resistance surface pixel is replaced by the maximum pixel value "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))  
        
        self.editname8 = wx.TextCtrl(self, 196, ','.join(str(i) for i in self.escalas), wx.Point(450,235), wx.Size(50,-1))
        self.editname8.SetToolTip(wx.ToolTip("This parameters controls the scale of landscape influence on local "+
                                             "resistance (the size of the window around each pixel). It affects only the "+
                                             "results of simulations using methods MLmin, MLavg, and MLmax.\n"+
                                             "Scale may be related to the species' landscape perception, for example."))
         
         
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
        self.editspeciesList=wx.ComboBox(self, 93, 'Click to select', wx.Point(80, 172), wx.Size(215, -1),
                                         self.listmaps, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
        wx.EVT_TEXT(self, 93, self.EvtText)
        #--------------------------------------------------------------------------------------------------
        
        # SOURCE TARGET MAP
        # List of maps taken from GRASS GIS database, using the command "grass.list_grouped"
        self.editspeciesList=wx.ComboBox(self, 95, 'Click to select', wx.Point(320, 172), wx.Size(215, -1),
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
        Resistance Map name is stored in a variable called self.OutArqResist
        Variable self.NEXPER_FINAL also stores resistance map name; if the user does not inform 
        an output name for the simulation, corridor output names will have the same name as the input 
        resistance map
        """
        
        if event.GetId()==93:
          
            #select_resistance_map()
            
            # Gets resistance map name and stores it in self.OutArqResist
            self.OutArqResist=event.GetString()
            
            # Gets resistance map name and stores it in self.NEXPER_FINAL (in case the user does not provide an output file name)
            self.NEXPER_FINAL=event.GetString()
            self.NEXPER_FINAL=self.NEXPER_AUX+'_'+self.NEXPER_FINAL
            self.NEXPER_FINAL_txt=self.NEXPER_AUX_txt+'_'+self.NEXPER_FINAL
            
            # Shows selection in the Dialog Box
            self.logger.AppendText('Resistance Map Selected:\n')
            self.logger.AppendText('%s\n' % event.GetString())
        
        
        
        """
        ST MAP
        ID 95: event performed by a combobox, from a list of raster maps already in GRASS GIS DataBase
        Source-Target Map is stored in a variable called self.OutArqST
        """
        
        if event.GetId()==95: 
          
          # Gets source target map name and stores it in self.OutArqST
          self.OutArqST=event.GetString()
          
          # Shows selection in the Dialog Box
          self.logger.AppendText('Souce-Target Map:\n')
          self.logger.AppendText('%s\n' % event.GetString())
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
             
        
       
    def OnClick(self, event):
        '''
        This function controls what happens when a button of the GUI is pressed
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
          grass.run_command ('r.in.gdal', flags='o', input=self.InArqResist, output=self.OutArqResist, overwrite=True, verbose = False)
          
          # Imports a ST map, ignoring projections
          grass.run_command ('r.in.gdal', flags='o', input=self.InArqST, output= self.OutArqST, overwrite=True, verbose = False)
          
          # Setting GRASS GIS region to the largest (resistance) map
          grass.run_command('g.region', rast=self.OutArqResist, verbose=False)
          
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
        variable self.patch_id_list, which is then used to generate simulations
        """
        
        if event.GetId()==260: #combine list
          
          # Diolog Box Message
          self.logger.AppendText('Generating combinations... \n')
          
          # Creating ST combination list based on information of ST map
          # The result is a string with combinations; e.g.: 1,2,1,3,1,4...
          self.patch_id_list_aux = combine_st(st_map = self.OutArqST)
          
          # Transforms the string into a list, using comma as separator
          self.patch_id_list_aux_b=self.patch_id_list_aux.split(',')
          
          # Length of the list
          self.lenlist=len(self.patch_id_list_aux_b)
          
          # Number of combination pairs
          self.lenlist_b=self.lenlist/2
          
          # Sends confirmation message
          self.logger.AppendText('Waiting... \n')
          
          #d = wx.MessageDialog(self, "Simulate all possible ("+`self.lenlist_b`+") combinations?\n", "", wx.YES_NO)

          d = wx.MessageDialog(self, "Simulate all possible{}combinations?\n".format(self.lenlist_b), "", wx.YES_NO)
          retCode = d.ShowModal() # Shows
          d.Close(True)  # Close the frame. 
          
          # If the user choses "yes", it meand that it was chosen to simulate all ST possible combinations;
          # otherwise, the process is simply canceled
          if (retCode == wx.ID_YES):
            self.patch_id_list=self.patch_id_list_aux_b
            self.logger.AppendText('\nCreated list. \n')
            
            # Backup of the list of ST patches
            self.patch_id_list_bkp = self.patch_id_list            
          else:
              print ("")
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
          p=grass.mlist_grouped ('rast', pattern='*MSP*') [self.current_mapset]
          j=len(p)
          
          self.logger.AppendText('Found: '+j+' files.')
          d= wx.MessageDialog(self, "Export files?\n", "", wx.YES_NO) # Create a message dialog box
          retCode=d.ShowModal() # Shows 
          d.Close(True) # Close the frame.
          
          # If the user confirms exporting, export!
          if (retCode == wx.ID_YES):
            
            # Select output directory
            self.logger.AppendText('Please select the directory... \n')
            self.OutDir_files=selectdirectory()
            os.chdir(self.OutDir_files)
            
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
          
          # Calls selectfile function, that returns the file name in the variable self.InArqST
          self.InArqST=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            self.OutArqST=self.InArqST.split('\\')
          elif platform.system() == 'Linux':
            self.OutArqST=self.InArqST.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")
          self.OutArqST=self.OutArqST[-1].replace('.','_')
          
          # Message in the Dialog box
          self.logger.AppendText('Selected File: \n'+self.OutArqST+'\n')
          #self.logger.AppendText("Automatically ST Map Selected:\n")
          #self.logger.AppendText(self.OutArqST+"\n")
         
         
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
          
          # Calls selectfile function, that returns the file name in the variable self.InArqST
          self.InArqResist=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            self.OutArqResist=self.InArqResist.split('\\')
          elif platform.system() == 'Linux':
            self.OutArqResist=self.InArqResist.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")            
          self.OutArqResist=self.OutArqResist[-1].replace('.','_')
          
          # Messages in the Dialog box
          self.logger.AppendText('Selected File: \n'+self.OutArqResist+'\n')
          
          # Updating output file name in the variable self.NEXPER_FINAL
          self.NEXPER_FINAL=self.NEXPER_AUX+'_'+self.OutArqResist
          self.NEXPER_FINAL_txt=self.NEXPER_AUX_txt+'_'+self.OutArqResist

          self.logger.AppendText("Automatically Resistance Map Selected:\n")
          self.logger.AppendText(self.NEXPER_FINAL+"\n")
        
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
          
          # Calls selectfile function, that returns the file name in the variable self.readtxt
          self.readtxt=selectfile()
          
          # Opens and reads the list as a string and transforms it into a list
          self.fileHandle = open(self.readtxt, 'r')
          self.patch_id_list_aux = self.fileHandle.read()
          self.fileHandle.close()
          self.patch_id_list = self.patch_id_list_aux.split(',')
          
          # Backup of the list of ST patches
          self.patch_id_list_bkp = self.patch_id_list
          
          # Prints list of ST combinations
          #print self.patch_id_list
          self.logger.AppendText("TXT Combinations:\n{}\n".format(self.patch_id_list))
          

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
          
          # Retrieving ST list from backup of the list of ST patches
          self.patch_id_list = self.patch_id_list_bkp
          
          # Size of the ST list
          self.lenlist=len(self.patch_id_list)
         
          # Tests if variability parameter is greater than 1.0
          if any(i < 0.0 for i in self.ruidos_float): 
            d= wx.MessageDialog(self, "Incorrect variability parameter(s)\n"+
                                "Variability must be a number equal to or greater than zero!\n"+
                                "Please check the parameter(s).\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Tests if scale parameter is greater than zero
          #print 'escalas = '+','.join(str(i) for i in self.escalas)
          if any(i <= 0 for i in self.escalas): 
            d= wx.MessageDialog(self, "Incorrect scale parameter(s)\n"+
                                "Scale must be a number greater than zero!\n"+
                                "Please check the parameter(s).\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Checks if the size of the window (landscape scale x 2) is greater than the pixel size
          #  if it is, ok
          #  if not, and we are going to simulate method MLmin, MLavg, or MLmax, warn the user!
          
          # First, defining GRASS GIS region as output map region
          grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3)
                      
          # Second, reading map resolution
          self.res = grass.parse_command('g.region', rast=self.OutArqResist, flags='m')
          
          self.res3 = float(self.res['ewres'])
          
          # Third, calculate window size (landscape scale x 2) in number of pixels
          self.escalas_pixels = [float(i)*2/self.res3 for i in self.escalas]
          
          # Finally, tests if any of the scales are lower than the pixel size
          #  (this only matters if methods MLmin, MLavg, or MLmax are going to be simulated)
          if any(i < 2.0 for i in self.escalas_pixels) and (self.Nsimulations2 > 0 or self.Nsimulations3 > 0 or self.Nsimulations4 > 0): 
            d= wx.MessageDialog(self, "There may a problem with scale parameter. \n"+
                                "Input map resolution is m, scale should be greater than that!\n"+
                                "Please check the parameter(s).\n".format(round(self.res3,1)), "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()           
            
          # Tests if number of simulations is >= 0
          if self.Nsimulations1 < 0 or self.Nsimulations2 < 0 or self.Nsimulations3 < 0 or self.Nsimulations4 < 0:
            d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                "Number of simulations must be equal to or greater than zero!\n"+
                                "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Tests if number of simulations for at is > 0 for at least one simulation method
          if (self.Nsimulations1 + self.Nsimulations2 + self.Nsimulations3 + self.Nsimulations4) <= 0:
            d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                "Number of simulations must greater than zero fot at least one simulation method!\n"+
                                "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
          
         
          # Tests if the length of the ST list is > 1
          if  self.lenlist <= 1: 
            d= wx.MessageDialog(self, "Incorrect list\n"+
                                "List length is smaller than 1!\n"+
                                "Please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          
          # Tests if the length of the ST list is even
          elif self.lenlist > 1 and int (self.lenlist)%2 == 1:
            
            d= wx.MessageDialog(self, "Incorrect list.\n"+
                                "List length cannot be odd,"+
                                "please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            sys.exit()
            
          
          # If everything ok with list length, go on
          else:
            
            # List of STs: self.patch_id_list
            self.logger.AppendText("List ok.\n")
            self.logger.AppendText("Waiting...\n")
            
            # Selects output directory for text files
            d=wx.MessageDialog(self, "Please, select the output folder for text files.\n", "", wx.OK) # Create a message dialog box
            if not self.perform_tests:
              d.ShowModal() # Shows it
              d.Destroy() # Finally destroy it when finished.
              
            if self.OutDir_files_TXT == '' and self.perform_tests == False:
              self.OutDir_files_TXT = selectdirectory()
            self.logger.AppendText("Selected output folder: \n"+self.OutDir_files_TXT+"\n\n")
          
            # Start running
            self.logger.AppendText("Running...:\n")
            
          self.logger.AppendText('\nList of source-targets: \n{}\n'.format(round(self.res3,1)))

          d = wx.MessageDialog(self,"Click OK and wait for simulation processing;\n"+
                              "A message will warn you at the end of simulations.\n"+
                              "Thank you.".format(),"", wx.OK)
          
          if not self.perform_tests:
            retCode=d.ShowModal() # Shows 
            d.Close(True) # Finally destroy it when finished.
          
          #---------------------------------------------#
          #--------------- PREPARE SIMULATIONS ---------#
          #---------------------------------------------#
          # Simulation settings
          
          # Start time
          self.time_start = datetime.now() # INSTANCE
          self.day_start=self.time_start.day # Start day
          self.month_start=self.time_start.month # Start month
          self.year_start=self.time_start.year # Start year
          self.hour_start=self.time_start.hour # Start hour
          self.minuts_start=self.time_start.minute # Start minute
          self.second_start=self.time_start.second # Start second
          
          # Change to output directory
          os.chdir(self.OutDir_files_TXT)
          
          # Starting log file
          #self.header_log="___Log_Year_"+`self.year_start`+"-Month"+`self.month_start`+"-Day_"+`self.day_start`+"_Time_"+`self.hour_start`+"_"+`self.minuts_start`+"_"+`self.second_start`
          self.header_log = "___Log_Year_" "-Month{}-Day_{}_Time_{}_{}_{}".format(self.year_start,self.month_start,self.day_start,self.hour_start,self.minuts_start,self.second_start)
          
          self.txt_log=open(self.header_log+".txt","w")       
          self.txt_log.write("LS Corridors log file\n")
          self.txt_log.write("---------------------\n\n")
          
          self.txt_log.write("Inputs: \n")
          self.txt_log.write("	Resistance map                                                : "+self.OutArqResist+"\n")
          self.txt_log.write("	Source-Target map                                             : "+self.OutArqST+"\n")
          self.txt_log.write("	Resistance map resolution (m)                                 : {}\n".format(self.res3))
          self.txt_log.write("	Variability factor(s)                                         : "+', '.join(str(i) for i in self.ruidos_float)+"\n")
          self.txt_log.write("	Scale(s) of influence (m)                                     : "+', '.join(str(i) for i in self.escalas)+"\n")
          self.txt_log.write("	Number of simulations MP    (without landcape influence)      : {}\n".format(self.Nsimulations1))
          self.txt_log.write("	Number of simulations MLmin (with landscape influence-minimum): {}\n".format(self.Nsimulations2))
          self.txt_log.write("	Number of simulations MLavg (with landscape influence-average): {}\n".format(self.Nsimulations3))
          self.txt_log.write("	Number of simulations MLmax (with landscape influence-maximum): {}\n".format(self.Nsimulations4))
          self.txt_log.write("	Source-Target pairs simulated                                 : {}\n".format(', '.join(str(i) for i in self.patch_id_list_bkp)))
        
          self.txt_log.write("Output prefix: \n")
          self.txt_log.write("	"+self.NEXPER_FINAL+"\n\n")          
        
          self.txt_log.write("Output folder: \n")
          self.txt_log.write("	"+self.OutDir_files_TXT+"\n\n")          
          self.txt_log.close()
          
          # Open output text file and writes headers      
          self.arquivo = open(self.NEXPER_FINAL_txt+'.txt','w')
          self.cabecalho='EXPERIMENT'+','+'VARIABILITY'+','+'SCALE'+','+'SIMULATION_METHOD'+','+'SIMULATION_NUMBER'+','+'SOURCE'+','+'TARGET'+','+'CORRIDOR_LENGTH'+','+'CORRIDOR_COST'+','+'EUCLIDEAN_DISTANCE'+','+'COORD_SOURCE_X'+','+'COORD_SOURCE_Y'+','+'COORD_TARGET_X'+','+'COORD_TARGET_Y'+ '\n'
          self.arquivo.write(self.cabecalho)
          self.arquivo.close()
          
          #######################################
          ## Review that
          self.S1="" # Variable to select a source point
          self.T1="" # Variable to select a target point
          
          # A series of simulations for each value of variability defined by the user
          for ruido_float in self.ruidos_float:
          
            self.logger.AppendText("Running corridors for variability = {}.\n".format(ruido_float))
            
            # Defining GRASS GIS region as output map region
            grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3)
            
            # Reading map resolution
            self.res = grass.parse_command('g.region', flags='m')
            self.res3 = float(self.res['ewres'])
            
            # This variables are used to define whether simulations for method MP were already 
            #  performed when there is more than one scale; in this case, there's no need to 
            #  simulate it again for method MP, only for methods MLmin, MLavg, and MLmax
            
            self.n_scales = len(self.escalas) # Number of scales

            
            self.scale_counter = 1 # Scale counter
            
            # A series of simulations for each landscape scale value defined by the user
            for esc in self.escalas:
              
              self.logger.AppendText("Running corridors for landscape scale = {}.\n".format(esc))
              
              # Names of input maps for each scale and each method
              self.C2=self.OutArqResist+'_'+self.C2_pre+'_scale_{}'.format(esc)
              self.C3=self.OutArqResist+'_'+self.C3_pre+'_scale_{}'.format(esc)
              self.C4=self.OutArqResist+'_'+self.C4_pre+'_scale_{}'.format(esc)
              
              # Refreshing the list of methods to be simulated, and outputs
              self.methods = []
              self.listExport = []
              self.listExportMethod = []
            
              # Size of the influence process when computing a certain ST pair
              self.influenceprocess = self.influence_factor * float(esc)
            
              # Defining the size of the moving windows, in pixels
              # It is defined given the animal movement scale (user defined parameter)
              #  and the resolution of the map (map grain or pixel size)
              self.escfina1=(float(esc)*2)/self.res3
              
              # Checking if number of pixels of moving window is integer and even
              #  and correcting it if necessary
              if int(self.escfina1)%2 == 0:
                self.escfina1=int(self.escfina1)
                self.escfina1=self.escfina1+1
              else:
                self.escfina1=int(self.escfina1)
                #self.escfina1=int(round(self.escfina1, ndigits=0))
              
              # Defining GRASS GIS region as output map region
              grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3) 
              
              if self.n_scales > 1 and self.scale_counter > 1:
                self.Nsimulations1_tobe_realized = 0
              else:
                self.Nsimulations1_tobe_realized = self.Nsimulations1
              
              # If methods MLmin, MLavg, MLmax are going to be simulated, this command prepares
              # the resistance map taking into consider these methods
              # Also, the list of methods to be simulated is defined
              if self.Nsimulations1_tobe_realized > 0: # no influence of landscape
                self.methods.append('MP')
              
              if self.Nsimulations2 > 0: # minimum
                self.methods.append('MLmin')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C2)[self.current_mapset]
                if len(map_exists) == 0:
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C2, method='minimum', size=self.escfina1, overwrite = True)
                
              if self.Nsimulations3 > 0: # average
                self.methods.append('MLavg')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C3)[self.current_mapset]
                if len(map_exists) == 0:              
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C3, method='average', size=self.escfina1, overwrite = True)
              
              if self.Nsimulations4 > 0: # maximum
                self.methods.append('MLmax')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C4)[self.current_mapset]
                if len(map_exists) == 0:                
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C4, method='maximum', size=self.escfina1, overwrite = True)
              
              # Organizes names of resistance maps to be used in simulations
              self.listafinal=[]
              self.listamethods=[]
              
              for i in range(self.Nsimulations1_tobe_realized):
                self.listafinal.append(self.OutArqResist)
                self.listamethods.append('MP')
              for i in range(self.Nsimulations2):
                self.listafinal.append(self.C2)
                self.listamethods.append('MLmin')
              for i in range(self.Nsimulations3):
                self.listafinal.append(self.C3)
                self.listamethods.append('MLavg')
              for i in range(self.Nsimulations4):
                self.listafinal.append(self.C4)
                self.listamethods.append('MLmax')
              
              # Not necessary
              #grass.run_command('g.region', rast=self.OutArqResist, res=self.res3)
              
              # Total number of simulations (M! + MLmin + MLavg + MLmax)
              self.Nsimulations = self.Nsimulations1_tobe_realized + self.Nsimulations2 + self.Nsimulations3 + self.Nsimulations4
              
              # Transforming list of STs in integers (for recongnizing them in the map)       
              self.patch_id_list=list(map(int,self.patch_id_list_bkp))
              print(self.patch_id_list)
              
              #---------------------------------------------#
              #--------------- START SIMULATIONS -----------#
              #---------------------------------------------#
              #definy_Gproj() # corrigindo as informacoes de datum
              
              # For each ST pair in the list:
              while (len(self.patch_id_list)>1):
                grass.run_command('g.region', rast=self.OutArqResist, verbose=False)
                # List of number of corridors already simulated - to be updated as simulations run
                self.simulated = [1, 1, 1, 1]                              
                
                self.ChecktTry=True
                # Change to output dir
                os.chdir(self.OutDir_files_TXT)
                
                # Select a pair from the list and prepare vectors for processing
                while self.ChecktTry==True:
                  try:
                    # Selects from the beginning to the end of the list
                    self.S1=self.patch_id_list[0]
                    self.T1=self.patch_id_list[1]
                    self.S1FORMAT='000000{}'.format(self.S1)
                    self.S1FORMAT=self.S1FORMAT[-5:]
                    self.T1FORMAT='000000{}'.format(self.T1)
                    self.T1FORMAT=self.T1FORMAT[-5:]
                    
                    # Selects pair and delete it from the original ST combination list
                    del self.patch_id_list[0:2]
                    self.PAISAGEM='EXPERIMENT'
                    self.ARQSAIDA=self.PAISAGEM+'_s'+self.S1FORMAT+'_t'+self.T1FORMAT # Name of ouput text file                  
                    self.logger.AppendText("Processing ST pair: \n"+self.S1FORMAT+' & '+self.T1FORMAT+ '\n')  
                    self.S1=(int(str(self.S1)))
                    self.T1=(int(str(self.T1)))
                    
                    # Generates rasters with only the region of the source and terget points
                    self.form_02='source = if('+self.OutArqST+' != {}, null(), {})'.format(self.S1,self.S1)
                    grass.mapcalc(self.form_02, overwrite = True, quiet = True)
                    self.form_03='target = if('+self.OutArqST+' != {}, null(), {} )'.format(self.T1,self.T1)
                    grass.mapcalc(self.form_03, overwrite = True, quiet = True)
                    
                    # Transform source and target rasters into vectors
                    grass.run_command('g.region', rast=self.OutArqST, verbose=False)
                    grass.run_command('r.to.vect', input='source', out='source_shp', type='area', verbose=False, overwrite = True ) 
                    grass.run_command('r.to.vect', input='target', out='target_shp', type='area', verbose=False, overwrite = True ) 
                    # Adds x and y coordinates as columns to the vectors attribute
                    grass.run_command ('v.db.addcolumn', map='source_shp', columns='x double precision,y double precision', overwrite = True)
                    grass.run_command ('v.db.addcolumn', map='target_shp', columns='x double precision,y double precision', overwrite = True)
                    
                    grass.read_command ('v.to.db', map='source_shp', option='coor', columns="x,y", overwrite = True)
                    grass.read_command ('v.to.db', map='target_shp', option='coor', columns="x,y", overwrite = True)
                    
                    # Selects x,y coordinates of source point
                    self.var_source_x=grass.vector_db_select('source_shp', columns = 'x')['values'][1][0]
                    self.var_source_y=grass.vector_db_select('source_shp', columns = 'y')['values'][1][0]
                    # Selects x,y coordinates of source point
                    self.var_target_x=grass.vector_db_select('target_shp', columns = 'x')['values'][1][0]
                    self.var_target_y=grass.vector_db_select('target_shp', columns = 'y')['values'][1][0]
                    self.ChecktTry=False
                    
                  # In case the list of x,y is invalid, skips the simulation pair of STs with Error message, and keeps on simulating other pairs
                  except:
                    self.ChecktTry=True
                    # Error message on GRASS GIS console
                    print ("Error def Rasterize ST, Add cols, Get x,y cords...")
                    self.time = datetime.now() # INSTANCE
                    self.day_now=self.time.day # Error day
                    self.month_now=self.time.month # Error month
                    self.year_now=self.time.year # Error year
                    self.hour_now=self.time.hour # Error hour
                    self.minuts_now=self.time.minute # Error minute
                    self.second_now=self.time.second # Error second
                    
                    # Updates Log file
                    self.listErrorLog.append("[Error ->-> :] <- Rasterize ST, Add cols, Get x,y coord : "+self.ARQSAIDA+" -> ---{}-{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                    self.listErrorLog.append("[Error ->-> :] <- Skip STS: " + self.ARQSAIDA)
                    
                    # Finishes the simulation process if there are no more ST pairs
                    if len(self.patch_id_list)==0:
                      
                      #self.txt_log.close() 
                      d= wx.MessageDialog( self,"Error: STs invalid, please check them!", "", wx.OK)
                      retCode=d.ShowModal() # Shows
                      d.Close(True) # Closes
                      break                
                
                # Transforms ST coordinates in float
                self.var_source_x_b_int=float(self.var_source_x)
                self.var_source_y_b_int=float(self.var_source_y)
                self.var_target_x_b_int=float(self.var_target_x)
                self.var_target_y_b_int=float(self.var_target_y)
                
               
                # Set region defined by the limits of source and target points + fixed distance (self.influenceprocess)
                #  This reduces simulation time, since map processing may be restricted to 
                #  the region where points are located
                defineregion("source_shp", "target_shp", self.influenceprocess) 
                
                # Name of the corridor output map
                self.mapa_corredores_sem0=self.NEXPER_FINAL+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+'S_'+self.S1FORMAT+"_T_"+self.T1FORMAT
                self.mapa_corredores_sem0_txt=self.NEXPER_FINAL_txt+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+'S_'+self.S1FORMAT+"_T_"+self.T1FORMAT
              
                # Checks if the output folder for text files exists; 
                # If not, creates it.
                self.checkfolder=os.path.exists('Line_'+self.mapa_corredores_sem0)
                
                if self.checkfolder==False:
                  os.mkdir('Line_'+str(self.mapa_corredores_sem0))
                  if platform.system() == 'Windows':
                    self.outdir=self.OutDir_files_TXT+'\Line_'+self.mapa_corredores_sem0
                  elif platform.system() == 'Linux':
                    self.outdir=self.OutDir_files_TXT+'/Line_'+self.mapa_corredores_sem0
                  else:
                    # Improve it to Mac OS - how does it work?
                    raise Exception("What platform is yours?? It's not Windows or Linux...")
                else:
                  d= wx.MessageDialog( self, "Folder for text files already exists!\n"+
                                       "Please select another directory to save the output.\n", "", wx.OK) # Create a message dialog box
                  d.ShowModal() # Shows it
                  d.Destroy() # Closes
                  self.outdir=selectdirectory() # Choose output folder, if the previous one already exists
                  
                # Initializes corridor and auxiliary map
                for method in self.methods:
                  self.form_04='mapa_corredores_'+method+' = 0'
                  grass.mapcalc(self.form_04, overwrite = True, quiet = True)
                  #self.form_16='corredores_aux = 0'
                  #grass.mapcalc(self.form_16, overwrite = True, quiet = True)
                
                ## Open output text file and writes headers      
                #self.arquivo = open(self.mapa_corredores_sem0_txt+'.txt','w')
                #self.cabecalho='EXPERIMENT'+','+'VARIABILITY'+','+'SCALE'+','+'SIMULATION_METHOD'+','+'SIMULATION_NUMBER'+','+'SOURCE'+','+'TARGET'+','+'CORRIDOR_LENGTH'+','+'CORRIDOR_COST'+','+'EUCLIDEAN_DISTANCE'+','+'COORD_SOURCE_X'+','+'COORD_SOURCE_Y'+','+'COORD_TARGET_X'+','+'COORD_TARGET_Y'+ '\n'
                #self.arquivo.write(self.cabecalho)
                
                #---------------------------------------------#
                #-------- PERFORMS EACH SIMULATION -----------#
                #---------------------------------------------#
                cont=0
                for i in range(self.Nsimulations):
                    # Set region defined by the limits of source and target points + fixed distance (self.influenceprocess)
                    defineregion("source_shp","target_shp", self.influenceprocess)
                    
                    # Selecting resistance map
                    self.form_08='mapa_resist = '+self.listafinal[cont]
                    grass.mapcalc(self.form_08, overwrite = True, quiet = True)
                    self.M = self.listamethods[cont]
                    
                    # Number of simulation   
                    c = i+1
                    # Number of simulation for a given method
                    if self.M == "MP":
                      c_method = self.simulated[0]
                      self.simulated[0] = self.simulated[0] + 1
                    if self.M == "MLmin":
                      c_method = self.simulated[1]
                      self.simulated[1] = self.simulated[1] + 1
                    if self.M == "MLavg":
                      c_method = self.simulated[2]             
                      self.simulated[2] = self.simulated[2] + 1
                    if self.M == "MLmax":
                      c_method = self.simulated[3]
                      self.simulated[3] = self.simulated[3] + 1
                    
                    # Message in dialog box
                    self.logger.AppendText('=======> Running simulation {}\n'.format(c))
                    
                    #---------- RANDOM SOURCE POINT -------#
                    # Defines a random source point inside the input/source region
                    grass.run_command('r.mask', raster='source') # Mask - look only at source region
                    grass.run_command('g.region', vect='source_shp', verbose=False, overwrite = True)
                    
                    # Select a random source point
                    self.ChecktTry=True
                    
                    while self.ChecktTry==True:
                      try:
                        # Generates random points
                        grass.run_command('v.random', output='temp_point1_s', n=30, overwrite = True)
                        # Selects random points that overlap with source region
                        grass.run_command('v.select', ainput='temp_point1_s', binput='source_shp', output='temp_point2_s', operator='overlap', overwrite = True)
                        # Creates attribute table and connects to the random points inside source region
                        grass.run_command('v.db.addtable', map='temp_point2_s', columns="temp double precision")
                        grass.run_command('v.db.connect', flags='p', map='temp_point2_s')
                        # List of such random points inside Python
                        self.frag_list2=grass.vector_db_select('temp_point2_s', columns = 'cat')['values']
                        self.frag_list2=list(self.frag_list2)
                        # Selects the first (a random) point of the list
                        self.selct="cat={}".format(self.frag_list2[0])
                        grass.run_command('v.extract', input='temp_point2_s', output='pnts_aleat_S', where=self.selct, overwrite = True)
                        
                        if len(self.frag_list2)>0:
                          self.ChecktTry=False
                        else:
                          self.ChecktTry=True
                          
                      # If an error in selecting a random source point occurs, this is registered here and a new random point is selected
                      except:
                        self.ChecktTry=True
                        # Error message on GRASS GIS console
                        print ("Error Randomize source points...")                    
                        # Registering error in logfile
                        self.time = datetime.now() # INSTANCE
                        self.day_now=self.time.day # Error day
                        self.month_now=self.time.month # Error month
                        self.year_now=self.time.year # Error year
                        self.hour_now=self.time.hour # Error hour
                        self.minuts_now=self.time.minute # Error minute
                        self.second_now=self.time.second # Error second
                        self.listErrorLog.append("[Error ->-> :] <- Randomize source points: "+self.ARQSAIDA+" -> ---{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                        
                    
                    # Removing mask
                    grass.run_command('r.mask',flags='r')
                    
                    #---------- RANDOM TARGET POINT -------#
                    # Defines a random target point inside the input/target region
                    grass.run_command('r.mask',raster='target')
                    grass.run_command('g.region', vect='target_shp',verbose=False,overwrite = True)
                    # Select a random target point
                    self.ChecktTry=True
                    while self.ChecktTry==True:
                      try:
                        # Generates random points
                        grass.run_command('v.random', output='temp_point1_t',n=30 ,overwrite = True)
                        # Selects random points that overlap with target region
                        grass.run_command('v.select',ainput='temp_point1_t',binput='target_shp',output='temp_point2_t',operator='overlap',overwrite = True)
                        # Creates attribute table and connects to the random points inside target region
                        grass.run_command('v.db.addtable', map='temp_point2_t',columns="temp double precision")
                        grass.run_command('v.db.connect',flags='p',map='temp_point2_t')
                        
                        # List of such random points inside Python
                        self.frag_list2=grass.vector_db_select('temp_point2_t', columns = 'cat')['values']
                        self.frag_list2=list(self.frag_list2)
    
                        # Selects the first (a random) point of the list
                        self.selct="cat={}".format(self.frag_list2[0])                
                        grass.run_command('v.extract',input='temp_point2_t',output='pnts_aleat_T',where=self.selct,overwrite = True)  
                        
                        if len(self.frag_list2)>0:
                          self.ChecktTry=False
                        else:
                          self.ChecktTry=True
                          
                      # If an error in selecting a random target point occurs, this is registered here and a new random point is selected
                      except:
                        self.ChecktTry=True
                        # Error message on GRASS GIS console
                        print ("Error Randomize target points...")                     
                        # Registering error in logfile
                        self.time = datetime.now() # INSTANCE
                        self.day_now=self.time.day # Error day
                        self.month_now=self.time.month # Error month
                        self.year_now=self.time.year # Error year
                        self.hour_now=self.time.hour # Error hour
                        self.minuts_now=self.time.minute # Error minute
                        self.second_now=self.time.second # Error second
                        self.listErrorLog.append("[Error ->-> :] <- Randomize source points: "+self.ARQSAIDA+" -> ---{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                               
                    # Removing mask
                    grass.run_command('r.mask',flags='r')
                    
                    # If the user wants to consider only the region around ST points, this region
                    #  is selected as GRASS region; otherwise, the whole resistance map region is set
                    #  as GRASS region
                    if self.influenceprocess_boll:
                      defineregion("source_shp","target_shp", self.influenceprocess)  
                    else:
                      grass.run_command('g.region', rast=self.OutArqResist,verbose=False)
                    
                    #---------- GENERATE CORRIDOR -------#
                    self.ChecktTry=True  
                    while self.ChecktTry==True:
                      try:
                        self.form_05='corredores_aux = mapa_corredores_'+self.M
                        grass.mapcalc(self.form_05, overwrite = True, quiet = True)
                        self.ChecktTry=False
                      except:
                        self.ChecktTry=True
                        
                      self.ChecktTry=True
                      while self.ChecktTry==True:
                        try:
                          # Creates a raster of uniformely distributed random values in the interval [1,100)
                          self.form_06="aleat = rand(0,100)"
                          grass.mapcalc(self.form_06, seed=random.randint(1, 10000), overwrite = True, quiet = True)
                          # Transforms raster map of random values to the range [0.1*noise, noise), where "noise" is
                          #  the variability factor defined by the user (variable ruido_float)
                          self.form_06="aleat2 = aleat/100.0 * {} + 1.0".format(ruido_float)
                          grass.mapcalc(self.form_06, overwrite = True, quiet = True)
                          # Multiply resistance map by random noise map
                          self.form_07='resist_aux = mapa_resist * aleat2'
                          grass.mapcalc(self.form_07, overwrite = True, quiet = True)
                          # Sets null cells as vistually infinite resistance
                          self.form_07='resist_aux2 = if(isnull(resist_aux), 10000000, resist_aux)'
                          grass.mapcalc(self.form_07, overwrite = True, quiet = True)
                  
                          # Generating cumulative cost raster map for linking S and T points
                          grass.run_command('r.cost', flags='k', input='resist_aux2', output='custo_aux_cost', start_points='pnts_aleat_S', stop_points='pnts_aleat_T', overwrite = True)
                          # Tracing the least cost path (corridor) - the flow based on cumulative cost map
                          grass.run_command('r.drain', input='custo_aux_cost', output='custo_aux_cost_drain', start_points='pnts_aleat_T', overwrite = True)
                          # Transforms null cells (no corridor) in zeros
                          # Now we have a corridor map
                          grass.run_command('r.series', input='corredores_aux,custo_aux_cost_drain', output='mapa_corredores_'+self.M, method='sum', overwrite = True)
                          self.ChecktTry=False
                          
                        # If an error in generating corridors, this is registered here and the algoeithm tries to generate the corridor again
                        except:
                          self.ChecktTry=True
                          # Error message on GRASS GIS console
                          print ("Error Corridor methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series...")
                          # Registering error in logfile
                          self.time = datetime.now() # INSTANCE
                          self.day_now=self.time.day # Error day
                          self.month_now=self.time.month # Error month
                          self.year_now=self.time.year # Error year
                          self.hour_now=self.time.hour # Error hour
                          self.minuts_now=self.time.minute # Error minute
                          self.second_now=self.time.second # Error second
                          self.listErrorLog.append("[Error ->-> :] <- Methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series: "+self.ARQSAIDA+" -> ---{}-{}-{} --- Time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                          
                    # Multiply corridor map (binary - 0/1) by the original resistance map
                    # Now we get a raster with the cost of each pixel along the corridor
                    self.form_09='custo_aux_cost_drain_sum = custo_aux_cost_drain * '+self.listafinal[0]
                    grass.mapcalc(self.form_09, overwrite = True, quiet = True)  
                   
                    # CALCULATES COST
                    self.x = grass.read_command('r.univar', map='custo_aux_cost_drain_sum')
                    # List of corridor statistics
                    self.x_b = self.x.split('\n')
                    # Sum of the cost of each pixel along the corridor, string format
                    self.x_c = str(self.x_b[14])
                    # Value of the corridor total cost, float format
                    self.var_cost_sum = float(self.x_c.replace("sum: ",""))
                    
                    # If the user wants to consider only the region around ST points, this region
                    #  is selected as GRASS region; otherwise, the whole resistance map region is set
                    #  as GRASS region
                    if self.influenceprocess_boll:
                      defineregion("source_shp", "target_shp", self.influenceprocess)  
                    else:
                      grass.run_command('g.region', rast=self.OutArqResist, verbose=False)
                    
                    # Corridor map with NULL cells instead of zeros
                    self.form_10=self.mapa_corredores_sem0+'_'+self.M+' = if(mapa_corredores_'+self.M+' == 0, null(), mapa_corredores_'+self.M+')'
                    grass.mapcalc(self.form_10, overwrite = True, quiet = True)
                    
                    # CALCULATES CORRIDOR LENGTH using corridor map (with NULL values)
                    self.length = grass.read_command('r.univar', map='custo_aux_cost_drain')
                    # List of statistics
                    self.length_b=self.length.split('\n')
                    # Sum of pixels (value 1) of the corridor, string format
                    self.length_c=str(self.length_b[14])
                    # Sum of pixels of the corridor, float format
                    self.length_d=self.length_c[5:9]
                    self.length_e=float(self.length_d)
                    # Distance in meters (multiply map resolution by distance in pixels)
                    self.var_dist_line=self.res3*self.length_e
                   
                    # CALCULATES EUCLIDEAN DISTANCE between S and T points
                    self.euclidean_a = float((self.var_source_x_b_int-self.var_target_x_b_int)**2 + (self.var_source_y_b_int-self.var_target_y_b_int)**2)
                    self.euclidean_b = self.euclidean_a**0.5         
                         
                    # Produces information for one corridor - to be appended to the output text file
                    self.linha=self.listafinal[cont].replace("@PERMANENT",'')+',{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(ruido_float,esc,self.M,c_method,self.S1,self.T1,self.var_dist_line,self.var_cost_sum,self.euclidean_b,self.var_source_x,self.var_source_y,self.var_target_x,self.var_target_y)
                    self.linha=self.linha.replace('\'','')
                    
                    # Output directory
                    os.chdir(self.OutDir_files_TXT)                    
                    
                    # Writes corridor information on output text file
                    self.arquivo = open(self.NEXPER_FINAL_txt+'.txt','a')
                    self.arquivo.write(self.linha)
                    self.arquivo.close()
                    
                    # Generates a vector line map for each corridor (vectorizing raster map)
                    self.outline1='000000{}'.format(c_method)
                    self.outline1=self.outline1[-3:]
                    self.outline1=self.mapa_corredores_sem0+'_'+self.M+"_SM_"+self.outline1
                    
                    # Vectorizes corridor raster map
                    grass.run_command('g.region', rast='custo_aux_cost_drain')
                    grass.run_command('r.to.vect', input='custo_aux_cost_drain', output=self.outline1, type='line',verbose=False, overwrite = True)
                    os.chdir(self.outdir)
                    grass.run_command('v.out.ogr', input=self.outline1, dsn=self.outline1+'.shp',verbose=False,type='line')
                    
                    
                    #-------------------------------------------------------------------------------------------------------------------------#
                    #---------------------_________----convert to vect rasters for mensure len lines----------_________-----------------------#
                    #-------------------------------------------------------------------------------------------------------------------------#
                    

                    
                    #-------------------------------------------------------------------------------------------------------------------------#
                    #---------------------_________-----------------------------------------------------------_________-----------------------#
                    #-------------------------------------------------------------------------------------------------------------------------#                    
                    
                    
                    
                    
                    #print(".........................................",self.outline1)
                    
                    cont=cont+1
                    
                    #--------------------------------------------------#
                    # Opens he log file and writes the errors in the log
                    # Output directory
                    os.chdir(self.OutDir_files_TXT)
                  
                    # Open Log file
                    self.txt_log = open(self.header_log+'.txt','a')                    
                  
                    # Errors
                    for logERR in self.listErrorLog:
                      self.txt_log.write(logERR+"\n")
                  
                    # Close log file
                    self.txt_log.close()                       
                    
                    #---------------------------------#
                    # Re-initializes corridor variables and list of errors
                    self.var_dist_line = 0.0
                    self.var_cost_sum = 0.0                
                    self.linha = ''
                    self.listErrorLog = []
                    
                    # -------- HERE ENDS THE SIMULATION OF ONE CORRIDOR ------------------#
                    # -------- THE LOOPS CONTINUES UNTIL ALL CORRIDORS ARE SIMULATES -----#
                
                # Exports raster maps with all corridors for the selected ST pair, for each simulated method
                for method in self.methods:
                
                  self.listExport.append(self.mapa_corredores_sem0+'_'+method)
                  self.listExportMethod.append(method)
                  
                  grass.run_command('g.region', rast=self.mapa_corredores_sem0+'_'+method)
                
                  os.chdir(self.OutDir_files_TXT)
                  grass.run_command('r.out.gdal', input=self.mapa_corredores_sem0+'_'+method, out=self.mapa_corredores_sem0+'_'+method+'.tif', nodata=-9999,overwrite = True)
                
                
              #---------------------------------------------#
              #-------- EXPORTS SYNTHESIS MAPS -------------#
              #---------------------------------------------#
              
              # If the number of simulations for a given method is > 1 or there is more than um ST pair, two summary maps are generated, for each method:
              #  - RSFI, a map with the route selection frequency index value for each pixel (the number of routes that passes by each pixel)
              #  - LargeZone_Corridors, an average map of corridors, considering all simulations all STs
              for method in self.methods:
                
                # name of the final corridor raster maps and output files
                self.output_file_name = self.NEXPER_FINAL+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+method
                
                index = [i for i, v in enumerate(self.listExportMethod) if v == method] # get indexes of simulations that were each of method
                export = [self.listExport[i] for i in index] # select map names simulated simulated for each 'method'
                if method == 'MP':
                  Nsims = self.Nsimulations1
                elif method == 'MLmin':
                  Nsims = self.Nsimulations2
                elif method == 'MLavg':
                  Nsims = self.Nsimulations3            
                elif method == 'MLmax':
                  Nsims = self.Nsimulations4
                else:
                  print ('No method selected for generating synthesis maps!')
                  break
                  
                self.listExport
                if len(export) > 1:
                  
                  # Check this
                  grass.run_command('r.series', input=export, out=self.output_file_name+'_RSFI', method="sum", overwrite = True)
                  #grass.run_command('r.series', input=export, out=self.output_file_name+'_RSFI', method="maximum", overwrite = True)
    
                  grass.run_command('g.region', rast=self.output_file_name+'_RSFI', verbose=False)
                  #grass.run_command('r.neighbors', input=self.output_file_name+'_RSFI', out=self.output_file_name+"_LargeZone_Corridors", method='average', size=self.defaultsize_moviwin_allcor, overwrite = True)
                  grass.run_command('r.out.gdal', input=self.output_file_name+'_RSFI', out=self.output_file_name+'_RSFI.tif', nodata=-9999, overwrite = True)
                  #grass.run_command('r.out.gdal', input=self.output_file_name+"_LargeZone_Corridors", out=self.output_file_name+"_LargeZone_Corridors.tif", nodata=-9999, overwrite = True)
      
                  #grass.run_command('g.region', rast=self.output_file_name+"_LargeZone_Corridors")
              
                elif Nsims > 1 and len(export) == 1:
                  
                  grass.run_command('g.region', rast=export, verbose=False)
                  grass.run_command('r.out.gdal', input=export, out=self.output_file_name+'_RSFI.tif', nodata=-9999, overwrite = True)
                
              #---------------------------------------------#
              #---- REMOVE AUX MAPS FROM GRASS DATABASE ----#
              #---------------------------------------------#
              self.logger.AppendText("Removing auxiliary files... \n")
              
              if self.remove_aux_maps:
                grass.run_command('g.remove', type="vect", name='temp_point1_s,temp_point2_s,temp_point1_t,temp_point2_t,pnts_aleat_S,pnts_aleat_T,source_shp,target_shp', flags='f')
                grass.run_command('g.remove', type="rast", name='source,target,resist_aux,resist_aux2,mapa_resist,mapa_corredores_MP,mapa_corredores_MLmin,mapa_corredores_MLavg,mapa_corredores_MLmax,aleat,aleat2,custo_aux_cost,custo_aux_cost_drain,custo_aux_cost_drain_sum,corredores_aux,MLmin_MINIMUM,MLavg_AVERAGE,MLmax_MAXIMUM', flags='f')
              
              #----------------------------------------------------------#  
              # Here we finish the simulations for each landscape scale  #
              #----------------------------------------------------------#
              self.scale_counter += 1
            
            #-------------------------------------------------------------#  
            # Here we finish the simulations for each variability factor  #            
            #-------------------------------------------------------------#
                     
          #---------------------------------------------#
          #------------ WRITES LOG FILES ---------------#
          #---------------------------------------------#            
          
          # Output directory
          os.chdir(self.OutDir_files_TXT)
          
          # Open Log file
          self.txt_log = open(self.header_log+'.txt','a')
          
          # Simulation end time
          self.time_end = datetime.now() # INSTANCE
          self.day_end = self.time_end.day # End day
          self.month_end = self.time_end.month # End month
          self.year_end = self.time_end.year # End year
          self.hour_end = self.time_end.hour # End hour
          self.minuts_end = self.time_end.minute # End minute
          self.second_end = self.time_end.second # End second
          
          self.difference_time = self.time_end - self.time_start
          weeks, days = divmod(self.difference_time.days, 7)
          minutes, seconds = divmod(self.difference_time.seconds, 60)
          hours, minutes = divmod(minutes, 60)          
          
          self.txt_log.write("Start time       : Year {}-Month {}-Day {} ---- time: {}:{}:{}\n" .format(
              self.year_start,self.month_start,self.day_start,self.hour_start,self.minuts_start,self.second_start
          ))

          self.txt_log.write("End time         : Year {}-Month {}-Day {} ---- Time: {}:{}:{}\n".format(
              self.year_end,self.month_end,self.day_end,self.hour_end,self.minuts_end,self.second_end))
          
          # Simulation time
          self.difference_time="{} Weeks - {} Days - "+" Time: {}:{}:{}".format(
              weeks,days,hours,minutes,seconds
          )
          
          # Writes log file
          self.txt_log.write("Processing time: "+self.difference_time+"\n\n")
          
          # Close log file
          self.txt_log.close()
          
          # Re-initializes output dir, in case new corridors are produced by clicking START SIMULATIONS button
          self.OutDir_files_TXT = ''
          
          # FINISH SIMULATIONS
          d = wx.MessageDialog(self,"Corridor simulation finished!\n"+
                              "Thanks for simulating using\n LSCorridors "+VERSION+"!", "", wx.OK)
          
          if not self.perform_tests:
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
          self.patch_id_list_aux = event.GetString()
          self.patch_id_list = self.patch_id_list_aux.split(',')
          
          # Backup of the list of ST patches
          self.patch_id_list_bkp = self.patch_id_list          
        
        """
        ID 186: Defines the variability of the map - noise factor
        """
        if event.GetId() == 186: #186=variability factor
          self.ruido = event.GetString()
          #self.ruido_float=float(self.ruido)
          try:
            self.ruidos_float = map(float, self.ruido.split(','))
            self.logger.AppendText('Variability factor(s): \n'+','.join(str(i) for i in self.ruidos_float)+ '\n')
          except:
            self.ruidos_float = [-1.0]
            print ("Could not convert at least one of the variability values to a float.")
          
        """
        ID 186: Defines the scale of influence for methods MLmin, MLavg, and MLmax
        """
        if event.GetId() == 196: #196=animal perception scale
          #self.esc=float(event.GetString())
          # this transforms values separated by commas into a list 
          # and turns these numbers into floating point values
          try:
            self.escalas = map(int, event.GetString().split(','))
            self.escalas = list(self.escalas)
            print('escalas:,,,,,,,,,,,,,,,,,,,',len(self.escalas))    
            self.logger.AppendText('Landscape scale(s): \n'+','.join(str(i) for i in self.escalas)+ '\n')            
          except:
            self.escalas = [-1]
            print ("Could not convert at least one of the scale values to an integer.")

        """
        ID 185: Reads output map name
        """
        if event.GetId() == 185: #185=base name
          self.NEXPER_APOIO = event.GetString()
          self.NEXPER_FINAL = self.NEXPER_AUX+"_"+self.NEXPER_APOIO
          self.NEXPER_FINAL = self.NEXPER_FINAL.replace('@PERMANENT','')
          self.NEXPER_FINAL_txt = self.NEXPER_AUX_txt+"_"+self.NEXPER_APOIO
          self.NEXPER_FINAL_txt = self.NEXPER_FINAL_txt.replace('@PERMANENT','')          
          self.logger.AppendText('Output map base name: \n'+self.NEXPER_FINAL+ '\n')
            
        """
        ID 190-193: Reads number of simulations for each method: M!, MLmin, MLavg, MLmax
        """
        # Method MP
        if event.GetId() == 190: #190=number of simulations
          try:
            self.Nsimulations1=int(event.GetString())
          except ValueError:
            self.Nsimulations1=0
            
        # Method MLmin
        if event.GetId() == 191: #191=number of simulations
          try:
            self.Nsimulations2=int(event.GetString())
          except ValueError:
            self.Nsimulations2=0  
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()
            
        # Method MLavg
        if event.GetId() == 192: #192=number of simulations
          try:
            self.Nsimulations3=int(event.GetString())
          except ValueError:
            self.Nsimulations3=0          
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()          
        # Method MLmax
        if event.GetId() == 193: #193=number of simulations
          try:
            self.Nsimulations4=int(event.GetString())
          except ValueError:
            self.Nsimulations4=0
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()          
        
    def OnExit(self, event):
      
        d= wx.MessageDialog(self, " Thanks for simulating using\n"
                            " LSCorridors "+ VERSION+"!", "Good Bye!", wx.OK) # Create a message dialog box
        if not self.perform_tests:
          d.ShowModal() # Shows it
          d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 


#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
  
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSCorridors "+VERSION, pos=(0,0), size=(570,590))
    Corridors(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
#=======
#!/c/Python27 python
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
 
 Contributors:
 Bernardo Niebuhr - bernardo_brandaum@yahoo.com.br
 Juliana Silveira dos Santos - juliana.silveiradossantos@gmail.com
 Felipe Martello - felipemartello@gmail.com
 Pavel Dodonov - pdodonov@gmail.com
 
 Description:
 LSCorridors is a free and open source package developed in Python 
 that simulates multiples functional ecological corridors.
 The software runs in a GRASS GIS environment.
 It can also be found at: https://github.com/LEEClab/LS_CORRIDORS
 
 To run LSCorridors:
 python LS_corridors_v1_0_1.py
 
 To run tests:
 python test_LS_corridors.py
 
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
 along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
#---------------------------------------------------------------------------------------

# Import modules
import grass.script as grass
from PIL import Image
import wx
import random, math
import os, sys, re, platform
from datetime import datetime

# LS Corridors Version:
VERSION = 'v. 1.0.1'

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
    print (">>.................."),dialog.GetPath()
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
  '''
  
  grass.run_command('g.region', rast=st_map, verbose=False)
  listRstats=grass.read_command('r.stats', input=st_map, flags='n', separator='space')
  b=[]
  b=listRstats.split('\n')
  del b[-1]
  print (b)
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
# Corridors is the main class, in which the software is initialized and runs
   
class Corridors(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # Takes the current mapset and looks for maps only inside it
        self.current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')
        
        # List of possible resistance and ST maps (already loaded inside GRASS GIS DataBase)
        self.listmaps=grass.list_grouped('rast')[self.current_mapset]
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------BLOCK OF VARIABLE DESCRIPTION--------------------------------------------------------------------------------------------#
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        # Remove aux maps in the end?
        self.remove_aux_maps = True
        
        # Performing tests on the code?
        self.perform_tests = False
        
        # Loads the output directory - only for RUN EXPORT button
        self.OutDir_files='Path of the files'

        # Loads the path to the output files - used while running the corridors
        self.OutDir_files_TXT=''
        
        # Loads the name of the resistance matrix
        self.InArqResist='Name of the file + ext'
        
        # Loads the name of the source-target map
        self.InArqST=''
        
        # Loads the name of a map to be imported into GRASS GIS and used for simulations
        self.OutArqResist=''
        
        # List of methods to be simulated
        self.methods=[]
        
        # Variables with 'C' are used to generate output names for auxiliary maps MLmin,MLavg,MLmax
        # Name of minimum map (MLmin)
        self.C2_pre='MLmin_MINIMUM'
        
        # Name of average map (MLavg)
        self.C3_pre='MLavg_AVERAGE'
        
        # Name of maximum map (MLmax)
        self.C4_pre='MLmax_MAXIMUM'
        
        # String to show an example of how the ST list should look like
        self.edtstart_list='Ex:1,2,3,4,...'
        
        # List of combinations of STs used in the simulation
        self.patch_id_list='' # List of combination of STs in list format
        self.patch_id_list_aux=''  # List of combination of STs in string format
        self.patch_id_list_aux_b='' # Aux list of combination of STs - list format, used to create all possible combinations
        
        # For defining output corridor map name
        self.NEXPER_AUX='MSP' # Prefix for output files
        self.NEXPER_AUX_txt='Results' # Prefix for output files
        self.NEXPER_APOIO='' # Aux variable for defining output name
        self.NEXPER_FINAL='' # Final output map name
        self.NEXPER_FINAL_txt='' # Final output text name
        
        # GUI Parameters
        self.ruido='2.0' # Variability scale for generating the noise map, in string format
        self.ruidos_float=[2.0] # Variability scale for generating the noise map, in float format
        
        self.escalas=[100] # Animal movement scale, in meters
        
        self.Nsimulations=0 # Total number of simulations (independent of method)
        self.Nsimulations1=15 # Number of simulation of method MP
        self.Nsimulations2=15 # Number of simulation of method MLmin (minimum)
        self.Nsimulations3=15 # Number of simulation of method MLavg (average)
        self.Nsimulations4=15 # Number of simulation of method MLmax (maximum)
        
        self.influence_factor = 1.1 # In case we are going to close the computing window, its size is increased by 110% the scale paramater in each side
        self.influenceprocess = self.influence_factor * float(self.escalas[0]) # Distance beyond the window size of a given ST pair, in meters
        self.influenceprocess_boll = False # Boolean - are we going to close the computing window around each ST map?
        
        # Auxiliary variables
        
        self.S1='' # Variable to select source points
        self.T1='' # Variable to select target points
        self.S1FORMAT='' # Variable to select source points, with zeros in front of it - for output files
        self.T1FORMAT='' # Variable to select target points, with zeros in front of it - for output files
        self.PAISAGEM='' # Prefix of the output text file with corridor information
        self.ARQSAIDA='' # Output text file with corridor information        
    
        # Variables used for mapcalc definition and calculation     
        self.form_02=''
        self.form_03=''
        self.form_04=''
        self.form_05=''
        self.form_06=''
        self.form_07=''
        self.form_08=''
        self.form_09=''
        self.form_10=''
        self.form_11=''
        self.form_12=""
        self.form_13=''
        self.form_14=""
        self.form_15=''
        self.form_16=''
        self.form_17=""
        self.form_18=""
        
        # Output
        
        # Variable to check if output folder exists
        self.checkfolder=''
    
        self.listExport=[] # List of corridor raster maps to be exported in the end of simulations
        self.listExportMethod=[] # List of method for corridor raster maps to be exported in the end of simulations

        self.outline1='' # Aux variable for transforming each corridor in a vector map
        self.outdir='' # Output dir for text files
        self.arquivo='' # File where to write corridor information
        self.M='' # Methods string for recording it in output text files
        
        self.txt_log='' # File where to write simulation log
        self.cabecalho='' # Variable with headers for output text corridor information
        self.linha='' # Variable with one line/simulation for output text corridor information
        
        self.readtxt='' # Variable to recieve the name of ST combination input file
        self.lenlist=0.0
        self.lenlist_b=0.0
                
        # Variables to calculate map resolution, to define the size of moving windows
        self.res='' # Aux variable
        self.res2=[] # Aux variable2
        self.res3='' # Final resolution of the map
        
        # Variables used to calculate the cost of LCP corridor
        self.x='' # Cost map statistics for one corridor, string format
        self.x_b='' # Cost map statistics for one corridor, list format
        self.x_c='' # Sum of cost map along LCP for one corridor, as string                
        
        # Variables for calculating length of the corridor
        self.length='' # Statistics for corridor
        self.length_b='' # String element for sum of number of pixels of the corridor
        self.length_c='' # Final corridor length value, string format
        self.length_d='' # Final corridor length value, in pixels
        self.length_e=0.0 # Final corridor length value, in meters
        
        # Variables for calculating Euclidean distance between points

        # Variables for position of ST points - string
        self.var_source_x='' # x (long) value for source point, as string
        self.var_source_y='' # y (lat) value for source point, as string
        self.var_target_x='' # x (long) value for target point, as string
        self.var_target_y='' # y (lat) value for target point, as string
        # Variables for position of ST points - float
        self.var_source_x_b_int=0.0 # x (long) value for source point, as float
        self.var_source_y_b_int=0.0 # y (lat) value for source point, as float
        self.var_target_x_b_int=0.0 # x (long) value for target point, as float
        self.var_target_y_b_int=0.0 # y (lat) value for target point, as float        
        # Aux variables
        self.euclidean_a=0.0 # Aux variable for calculating euclidean distance
        self.euclidean_b=0.0 # Aux variable for calculating euclidean distance
        
        # Variables where corridor cost and length are loaded
        self.var_cost_sum='' # Sum of cost map along LCP for one corridor, as float
        self.var_dist_line=0.0 # Length of the LCP for one corridor, as float        
        
        # Other aux variables
        self.ChecktTry=True # Aux variable for using in loops        

        self.listafinal=[] # List of resistance maps to be simulated
        self.frag_list2='' # Aux list variable for generating random source/target points
        self.selct='' # Aux variable for generating random source/target points 
        self.defaultsize_moviwin_allcor=7 # Default moving window size to calculate resistance maps for methods MLmin, MLavg, MLmax
        
        # Start time
        self.time = 0 # INSTANCE
        self.day_start=0 # Start day
        self.month_start=0 # Start month
        self.year_start=0 # Start year
        self.hour_start=0 # Start hour
        self.minuts_start=0 # Start minutes
        self.second_start=0 # Start seconds
       
        # End time
        self.time = '' # INSTANCE
        self.day_end=0 # End day
        self.month_end=0 # End month
        self.year_end=0 # End year
        self.hour_end=0 # # End hour
        self.minuts_end=0 # End minutes
        self.second_end=0 # End seconds  
        
        # Header for log file
        self.header_log=''          
        
        # Current time - to be used while simulations are performed
        self.time = 0 # INSTANCE
        self.day_now=0 # Current day
        self.month_now=0 # Current month
        self.year_now=0 # Current year
        self.hour_now=0 # Current hour
        self.minuts_now=0 # Current minute
        self.second_now=0 # Current second
        
        self.listErrorLog=[] # List of error messages to be written to the log file
        self.difference_time='' # Time lag for processing simulations
        
        
        
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
        
        #if not self.perform_tests:
        self.imageFile0 = 'img_lscorr.jpg'
        im0 = Image.open(self.imageFile0)
        jpg0 = wx.Image(self.imageFile0, wx.BITMAP_TYPE_ANY).Scale(250, 64).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg0, (20,20), (jpg0.GetWidth(), jpg0.GetHeight()), style=wx.SUNKEN_BORDER)          
        
        #self.quote = wx.StaticText(self, id=-1, label="LandScape Corridors",pos=wx.Point(20, 20))
        
        #font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        #self.quote.SetForegroundColour("blue")
        #self.quote.SetFont(font)
        
        #__________________________________________________________________________________________                
        self.quote = wx.StaticText(self, id=-1, label="Import Maps:", pos=wx.Point(20,95))
        
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)   
                
        #__________________________________________________________________________________________                
        self.quote = wx.StaticText(self, id=-1, label="Using Maps Already Imported:", pos=wx.Point(20,150))
        
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)          
        
        #__________________________________________________________________________________________
        self.quote = wx.StaticText(self, id=-1, label="Number of Simulations:", pos=wx.Point(20,268))
                
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("red")
        self.quote.SetFont(font)                      
      
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self,5, "",wx.Point(20,409), wx.Size(320,100),wx.TE_MULTILINE | wx.TE_READONLY)
      
        #---------------------------------------------#
        #-------------- BUTTONS ----------------------#
        #---------------------------------------------#
        
        self.button =wx.Button(self, 10, "START SIMULATIONS", wx.Point(20,519))
        wx.EVT_BUTTON(self, 10, self.OnClick)
  
        self.button =wx.Button(self, 205, "RUN EXPORT FILES ", wx.Point(145,519))
        wx.EVT_BUTTON(self, 205, self.OnClick)
        
        self.button =wx.Button(self, 210, "SELECT FILE", wx.Point(280,115))#st
        wx.EVT_BUTTON(self, 210, self.OnClick)
        
        self.button =wx.Button(self, 230, "SELECT FILE", wx.Point(107,115)) #cost
        wx.EVT_BUTTON(self, 230, self.OnClick)
        
        self.button =wx.Button(self, 240, "IMPORT FILE", wx.Point(358,115))
        wx.EVT_BUTTON(self, 240, self.OnClick)
        
        self.button =wx.Button(self, 250, "READ LIST TXT", wx.Point(322,202))
        wx.EVT_BUTTON(self, 250, self.OnClick)

        self.button =wx.Button(self, 260, "COMBINE ALL", wx.Point(418,202))
        wx.EVT_BUTTON(self, 260, self.OnClick)
        
        self.button =wx.Button(self, 8, "EXIT", wx.Point(265, 519))
        wx.EVT_BUTTON(self, 8, self.OnExit)

        #---------------------------------------------#
        #----------------- LAB LOGO ------------------#
        #---------------------------------------------#

        #if not self.perform_tests:
        self.imageFile = 'logo_lab.png'
        im1 = Image.open(self.imageFile)
        jpg1 = wx.Image(self.imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (348,410), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------STATIC TEXTS-----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.lblname = wx.StaticText(self, -1, "Resistance Mp:", wx.Point(20,118))
        self.lblname2 = wx.StaticText(self, -1, "Source\Target Map:", wx.Point(180,120))
        self.lblname2 = wx.StaticText(self, -1, "Variability:", wx.Point(455,120))
        self.lblname = wx.StaticText(self, -1, "Resistance:", wx.Point(20,175))
        self.lblname = wx.StaticText(self, -1, "ST:", wx.Point(300,175))
        self.lbllista = wx.StaticText(self, -1, "Enter a list manually:", wx.Point(20,207))
        self.lblname = wx.StaticText(self, -1, "Without landscape influence:", wx.Point(70,290))
        self.lblname = wx.StaticText(self, -1, "MP:", wx.Point(70,315))
        self.lblname = wx.StaticText(self, -1, "With landscape influence:", wx.Point(70,345))
        self.lblname = wx.StaticText(self, -1, "MLmin (minimum):", wx.Point(70,370))
        self.lblname = wx.StaticText(self, -1, "MLavg (average):", wx.Point(230,370))
        self.lblname = wx.StaticText(self, -1, "MLmax (maximum):", wx.Point(390,370))
        self.lblname = wx.StaticText(self, -1, "Name of output corridor:", wx.Point(20,240))
        self.lblname = wx.StaticText(self, -1, "Scale (meters):", wx.Point(370,240))
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #----------------------------------------------------------------TEXT CONTROLS----------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        self.editname1 = wx.TextCtrl(self, 180, self.edtstart_list, wx.Point(132,203), wx.Size(191,-1))
        self.editname2 = wx.TextCtrl(self, 185, 'Proposed name of the cost map', wx.Point(153,235), wx.Size(195,-1))
        self.editname3 = wx.TextCtrl(self, 186, ','.join(str(i) for i in self.ruidos_float), wx.Point(515,115), wx.Size(30,-1))
        self.editname3.SetToolTip(wx.ToolTip("Variability factor, x: in each simulation, "+
                                             "resistance value for each pixel in the resistance surface map is multiplied "+
                                             "by a uniformly randomly distributed number in the interval [0.1*x, x)."))
        self.editname4 = wx.TextCtrl(self, 190, str(self.Nsimulations1), wx.Point(90,312), wx.Size(35,-1))
        self.editname4.SetToolTip(wx.ToolTip("Method MP: no spatial influence"))
        self.editname5 = wx.TextCtrl(self, 191, str(self.Nsimulations2), wx.Point(166,367), wx.Size(35,-1))
        self.editname5.SetToolTip(wx.ToolTip("Method MLmin: minimum\n\n"+
                                             "Each resistance surface pixel is replaced by the minimum of pixel values "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))
        self.editname6 = wx.TextCtrl(self, 192, str(self.Nsimulations3), wx.Point(325,367), wx.Size(35,-1))
        self.editname6.SetToolTip(wx.ToolTip("Method MLavg: average\n\n"+
                                             "Each resistance surface pixel is replaced by the mean pixel value "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))        
        self.editname7 = wx.TextCtrl(self, 193, str(self.Nsimulations4), wx.Point(486,367), wx.Size(35,-1))
        self.editname7.SetToolTip(wx.ToolTip("Method MLmax: maximum\n\n"+
                                             "Each resistance surface pixel is replaced by the maximum pixel value "+
                                             "inside a window around it; this window represents the spatial context "+
                                             "influence and is controlled by the scale parameter."))        
        self.editname8 = wx.TextCtrl(self, 196, ','.join(str(i) for i in self.escalas), wx.Point(450,235), wx.Size(50,-1))
        self.editname8.SetToolTip(wx.ToolTip("This parameters controls the scale of landscape influence on local "+
                                             "resistance (the size of the window around each pixel). It affects only the "+
                                             "results of simulations using methods MLmin, MLavg, and MLmax.\n"+
                                             "Scale may be related to the species' landscape perception, for example."))
         
         
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
        self.editspeciesList=wx.ComboBox(self, 93, 'Click to select', wx.Point(80, 172), wx.Size(215, -1),
                                         self.listmaps, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
        wx.EVT_TEXT(self, 93, self.EvtText)
        #--------------------------------------------------------------------------------------------------
        
        # SOURCE TARGET MAP
        # List of maps taken from GRASS GIS database, using the command "grass.list_grouped"
        self.editspeciesList=wx.ComboBox(self, 95, 'Click to select', wx.Point(320, 172), wx.Size(215, -1),
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
        Resistance Map name is stored in a variable called self.OutArqResist
        Variable self.NEXPER_FINAL also stores resistance map name; if the user does not inform 
        an output name for the simulation, corridor output names will have the same name as the input 
        resistance map
        """
        
        if event.GetId()==93:
          
            #select_resistance_map()
            
            # Gets resistance map name and stores it in self.OutArqResist
            self.OutArqResist=event.GetString()
            
            # Gets resistance map name and stores it in self.NEXPER_FINAL (in case the user does not provide an output file name)
            self.NEXPER_FINAL=event.GetString()
            self.NEXPER_FINAL=self.NEXPER_AUX+'_'+self.NEXPER_FINAL
            self.NEXPER_FINAL_txt=self.NEXPER_AUX_txt+'_'+self.NEXPER_FINAL
            
            # Shows selection in the Dialog Box
            self.logger.AppendText('Resistance Map Selected:\n')
            self.logger.AppendText('%s\n' % event.GetString())
        
        
        
        """
        ST MAP
        ID 95: event performed by a combobox, from a list of raster maps already in GRASS GIS DataBase
        Source-Target Map is stored in a variable called self.OutArqST
        """
        
        if event.GetId()==95: 
          
          # Gets source target map name and stores it in self.OutArqST
          self.OutArqST=event.GetString()
          
          # Shows selection in the Dialog Box
          self.logger.AppendText('Souce-Target Map:\n')
          self.logger.AppendText('%s\n' % event.GetString())
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#        
             
        
       
    def OnClick(self, event):
        '''
        This function controls what happens when a button of the GUI is pressed
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
          grass.run_command ('r.in.gdal', flags='o', input=self.InArqResist, output=self.OutArqResist, overwrite=True, verbose = False)
          
          # Imports a ST map, ignoring projections
          grass.run_command ('r.in.gdal', flags='o', input=self.InArqST, output= self.OutArqST, overwrite=True, verbose = False)
          
          # Setting GRASS GIS region to the largest (resistance) map
          grass.run_command('g.region', rast=self.OutArqResist, verbose=False)
          
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
        variable self.patch_id_list, which is then used to generate simulations
        """
        
        if event.GetId()==260: #combine list
          
          # Diolog Box Message
          self.logger.AppendText('Generating combinations... \n')
          
          # Creating ST combination list based on information of ST map
          # The result is a string with combinations; e.g.: 1,2,1,3,1,4...
          self.patch_id_list_aux = combine_st(st_map = self.OutArqST)
          
          # Transforms the string into a list, using comma as separator
          self.patch_id_list_aux_b=self.patch_id_list_aux.split(',')
          
          # Length of the list
          self.lenlist=len(self.patch_id_list_aux_b)
          
          # Number of combination pairs
          self.lenlist_b=self.lenlist/2
          
          # Sends confirmation message
          self.logger.AppendText('Waiting... \n')
          
          d = wx.MessageDialog(self, "Simulate all possible ({}) combinations?\n".format(self.lenlist_b), "", wx.YES_NO)
          retCode = d.ShowModal() # Shows
          d.Close(True)  # Close the frame. 
          
          # If the user choses "yes", it meand that it was chosen to simulate all ST possible combinations;
          # otherwise, the process is simply canceled
          if (retCode == wx.ID_YES):
            self.patch_id_list=self.patch_id_list_aux_b
            self.logger.AppendText('\nCreated list. \n')
            
            # Backup of the list of ST patches
            self.patch_id_list_bkp = self.patch_id_list            
          else:
              print ("")
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
          p=grass.mlist_grouped ('rast', pattern='*MSP*') [self.current_mapset]
          j=len(p)
          
          self.logger.AppendText('Found: '+j+' files.')
          d= wx.MessageDialog(self, "Export files?\n", "", wx.YES_NO) # Create a message dialog box
          retCode=d.ShowModal() # Shows 
          d.Close(True) # Close the frame.
          
          # If the user confirms exporting, export!
          if (retCode == wx.ID_YES):
            
            # Select output directory
            self.logger.AppendText('Please select the directory... \n')
            self.OutDir_files=selectdirectory()
            os.chdir(self.OutDir_files)
            
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
          
          # Calls selectfile function, that returns the file name in the variable self.InArqST
          self.InArqST=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            self.OutArqST=self.InArqST.split('\\')
          elif platform.system() == 'Linux':
            self.OutArqST=self.InArqST.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")
          self.OutArqST=self.OutArqST[-1].replace('.','_')
          
          # Message in the Dialog box
          self.logger.AppendText('Selected File: \n'+self.OutArqST+'\n')
          #self.logger.AppendText("Automatically ST Map Selected:\n")
          #self.logger.AppendText(self.OutArqST+"\n")
         
         
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
          
          # Calls selectfile function, that returns the file name in the variable self.InArqST
          self.InArqResist=selectfile()
          
          # Removing file name extension 
          if platform.system() == 'Windows':
            self.OutArqResist=self.InArqResist.split('\\')
          elif platform.system() == 'Linux':
            self.OutArqResist=self.InArqResist.split('/')
          else:
            # Improve it to Mac OS - how does it work?
            raise Exception("What platform is yours?? It's not Windows or Linux...")            
          self.OutArqResist=self.OutArqResist[-1].replace('.','_')
          
          # Messages in the Dialog box
          self.logger.AppendText('Selected File: \n'+self.OutArqResist+'\n')
          
          # Updating output file name in the variable self.NEXPER_FINAL
          self.NEXPER_FINAL=self.NEXPER_AUX+'_'+self.OutArqResist
          self.NEXPER_FINAL_txt=self.NEXPER_AUX_txt+'_'+self.OutArqResist

          self.logger.AppendText("Automatically Resistance Map Selected:\n")
          self.logger.AppendText(self.NEXPER_FINAL+"\n")
        
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
          
          # Calls selectfile function, that returns the file name in the variable self.readtxt
          self.readtxt=selectfile()
          
          # Opens and reads the list as a string and transforms it into a list
          self.fileHandle = open(self.readtxt, 'r')
          self.patch_id_list_aux = self.fileHandle.read()
          self.fileHandle.close()
          self.patch_id_list = self.patch_id_list_aux.split(',')
          
          # Backup of the list of ST patches
          self.patch_id_list_bkp = self.patch_id_list
          
          # Prints list of ST combinations
          #print self.patch_id_list
          self.logger.AppendText("TXT Combinations:\n{}").format(self.patch_id_list)
          

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
          
          # Retrieving ST list from backup of the list of ST patches
          self.patch_id_list = self.patch_id_list_bkp
          
          # Size of the ST list
          self.lenlist=len(self.patch_id_list)
         
          # Tests if variability parameter is greater than 1.0
          if any(i < 0.0 for i in self.ruidos_float): 
            d= wx.MessageDialog(self, "Incorrect variability parameter(s)\n"+
                                "Variability must be a number equal to or greater than zero!\n"+
                                "Please check the parameter(s).\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Tests if scale parameter is greater than zero
          #print 'escalas = '+','.join(str(i) for i in self.escalas)
          if any(i <= 0 for i in self.escalas): 
            d= wx.MessageDialog(self, "Incorrect scale parameter(s)\n"+
                                "Scale must be a number greater than zero!\n"+
                                "Please check the parameter(s).\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Checks if the size of the window (landscape scale x 2) is greater than the pixel size
          #  if it is, ok
          #  if not, and we are going to simulate method MLmin, MLavg, or MLmax, warn the user!
          
          # First, defining GRASS GIS region as output map region
          grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3)
                      
          # Second, reading map resolution
          self.res = grass.read_command('g.region', rast=self.OutArqResist, flags='m')
          self.res2 = self.res.split('\n')
          #self.res3 = self.res2[5] 
          # The position of the ewres resolution parameter changes from GRASS 7.0 to grass 7.2 - let's change that!
          self.res3 = filter(lambda x: 'ewres' in x, self.res2)[0]
          self.res3 = float(self.res3.replace('ewres=',''))
          
          # Third, calculate window size (landscape scale x 2) in number of pixels
          self.escalas_pixels = [float(i)*2/self.res3 for i in self.escalas]
          
          # Finally, tests if any of the scales are lower than the pixel size
          #  (this only matters if methods MLmin, MLavg, or MLmax are going to be simulated)
          if any(i < 2.0 for i in self.escalas_pixels) and (self.Nsimulations2 > 0 or self.Nsimulations3 > 0 or self.Nsimulations4 > 0): 
            d= wx.MessageDialog(self, "There may a problem with scale parameter. \n"+
                                "Input map resolution is {} m, scale should be greater than that!\n"+
                                "Please check the parameter(s).\n".format(round(self.res3,1)), "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()           
            
          # Tests if number of simulations is >= 0
          if self.Nsimulations1 < 0 or self.Nsimulations2 < 0 or self.Nsimulations3 < 0 or self.Nsimulations4 < 0:
            d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                "Number of simulations must be equal to or greater than zero!\n"+
                                "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          # Tests if number of simulations for at is > 0 for at least one simulation method
          if (self.Nsimulations1 + self.Nsimulations2 + self.Nsimulations3 + self.Nsimulations4) <= 0:
            d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                "Number of simulations must greater than zero fot at least one simulation method!\n"+
                                "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
          
         
          # Tests if the length of the ST list is > 1
          if  self.lenlist <= 1: 
            d= wx.MessageDialog(self, "Incorrect list\n"+
                                "List length is smaller than 1!\n"+
                                "Please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            self.logger.AppendText()
            sys.exit()
            
          
          # Tests if the length of the ST list is even
          elif self.lenlist > 1 and int (self.lenlist)%2 == 1:
            
            d= wx.MessageDialog(self, "Incorrect list.\n"+
                                "List length cannot be odd,"+
                                "please check the list.\n", "", wx.OK) # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # Finally destroy it when finished.
            sys.exit()
            
          
          # If everything ok with list length, go on
          else:
            
            # List of STs: self.patch_id_list
            self.logger.AppendText("List ok.\n")
            self.logger.AppendText("Waiting...\n")
            
            # Selects output directory for text files
            d=wx.MessageDialog(self, "Please, select the output folder for text files.\n", "", wx.OK) # Create a message dialog box
            if not self.perform_tests:
              d.ShowModal() # Shows it
              d.Destroy() # Finally destroy it when finished.
              
            if self.OutDir_files_TXT == '' and self.perform_tests == False:
              self.OutDir_files_TXT = selectdirectory()
            self.logger.AppendText("Selected output folder: \n"+self.OutDir_files_TXT+"\n\n")
          
            # Start running
            self.logger.AppendText("Running...:\n")
            
          self.logger.AppendText('\nList of source-targets: \n{}\n').format(self.patch_id_list)
          d = wx.MessageDialog(self,"Click OK and wait for simulation processing;\n"+
                              "A message will warn you at the end of simulations.\n"+
                              "Thank you.","", wx.OK)
          
          if not self.perform_tests:
            retCode=d.ShowModal() # Shows 
            d.Close(True) # Finally destroy it when finished.
          
          #---------------------------------------------#
          #--------------- PREPARE SIMULATIONS ---------#
          #---------------------------------------------#
          # Simulation settings
          
          # Start time
          self.time_start = datetime.now() # INSTANCE
          self.day_start=self.time_start.day # Start day
          self.month_start=self.time_start.month # Start month
          self.year_start=self.time_start.year # Start year
          self.hour_start=self.time_start.hour # Start hour
          self.minuts_start=self.time_start.minute # Start minute
          self.second_start=self.time_start.second # Start second
          
          # Change to output directory
          os.chdir(self.OutDir_files_TXT)
          
          # Starting log file
          self.header_log="___Log_Year_{}-Month{}-Day_{}_Time_{}_{}_{}".format(
              self.year_start,self.month_start,self.day_start,self.hour_start,self.minuts_start,self.second_start
          )
          self.txt_log=open(self.header_log+".txt","w")       
          self.txt_log.write("LS Corridors log file\n")
          self.txt_log.write("---------------------\n\n")
          
          self.txt_log.write("Inputs: \n")
          self.txt_log.write("	Resistance map                                                : "+self.OutArqResist+"\n")
          self.txt_log.write("	Source-Target map                                             : "+self.OutArqST+"\n")
          self.txt_log.write("	Resistance map resolution (m)                                 : {}\n").format(self.res3)
          self.txt_log.write("	Variability factor(s)                                         : "+', '.join(str(i) for i in self.ruidos_float)+"\n")
          self.txt_log.write("	Scale(s) of influence (m)                                     : "+', '.join(str(i) for i in self.escalas)+"\n")
          self.txt_log.write("	Number of simulations MP    (without landcape influence)      : {}\n").format(self.Nsimulations1)
          self.txt_log.write("	Number of simulations MLmin (with landscape influence-minimum): {}\n").format(self.Nsimulations2)
          self.txt_log.write("	Number of simulations MLavg (with landscape influence-average): {}\n").format(self.Nsimulations3)
          self.txt_log.write("	Number of simulations MLmax (with landscape influence-maximum): {}\n").format(self.Nsimulations4)
          self.txt_log.write("	Source-Target pairs simulated                                 : {}\n").format(', '.join(str(i) for i in self.patch_id_list_bkp))
        
          self.txt_log.write("Output prefix: \n")
          self.txt_log.write("	"+self.NEXPER_FINAL+"\n\n")          
        
          self.txt_log.write("Output folder: \n")
          self.txt_log.write("	"+self.OutDir_files_TXT+"\n\n")          
          self.txt_log.close()
          
          # Open output text file and writes headers      
          self.arquivo = open(self.NEXPER_FINAL_txt+'.txt','w')
          self.cabecalho='EXPERIMENT'+','+'VARIABILITY'+','+'SCALE'+','+'SIMULATION_METHOD'+','+'SIMULATION_NUMBER'+','+'SOURCE'+','+'TARGET'+','+'CORRIDOR_LENGTH'+','+'CORRIDOR_COST'+','+'EUCLIDEAN_DISTANCE'+','+'COORD_SOURCE_X'+','+'COORD_SOURCE_Y'+','+'COORD_TARGET_X'+','+'COORD_TARGET_Y'+ '\n'
          self.arquivo.write(self.cabecalho)
          self.arquivo.close()
          
          #######################################
          ## Review that
          self.S1="" # Variable to select a source point
          self.T1="" # Variable to select a target point
          
          # A series of simulations for each value of variability defined by the user
          for ruido_float in self.ruidos_float:
          
            self.logger.AppendText("Running corridors for variability = {}.\n").format(ruido_float)
            
            # Defining GRASS GIS region as output map region
            grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3)
            
            # Reading map resolution
            self.res = grass.read_command('g.region', flags='m')
            self.res2 = self.res.split('\n')
            # self.res3 = self.res2[5]
            # The position of the ewres resolution parameter changes from GRASS 7.0 to grass 7.2 - let's change that!
            self.res3 = filter(lambda x: 'ewres' in x, self.res2)[0]
            self.res3 = float(self.res3.replace('ewres=',''))
            
            # This variables are used to define whether simulations for method MP were already 
            #  performed when there is more than one scale; in this case, there's no need to 
            #  simulate it again for method MP, only for methods MLmin, MLavg, and MLmax
            self.n_scales = len(self.escalas) # Number of scales
            self.scale_counter = 1 # Scale counter
            
            # A series of simulations for each landscape scale value defined by the user
            for esc in self.escalas:
              
              self.logger.AppendText("Running corridors for landscape scale = {}.\n").format(esc)
              
              # Names of input maps for each scale and each method
              self.C2=self.OutArqResist+'_'+self.C2_pre+'_scale_{}'.format(esc)
              self.C3=self.OutArqResist+'_'+self.C3_pre+'_scale_{}'.format(esc)
              self.C4=self.OutArqResist+'_'+self.C4_pre+'_scale_{}'.format(esc)
              
              # Refreshing the list of methods to be simulated, and outputs
              self.methods = []
              self.listExport = []
              self.listExportMethod = []
            
              # Size of the influence process when computing a certain ST pair
              self.influenceprocess = self.influence_factor * float(esc)
            
              # Defining the size of the moving windows, in pixels
              # It is defined given the animal movement scale (user defined parameter)
              #  and the resolution of the map (map grain or pixel size)
              self.escfina1=(float(esc)*2)/self.res3
              
              # Checking if number of pixels of moving window is integer and even
              #  and correcting it if necessary
              if int(self.escfina1)%2 == 0:
                self.escfina1=int(self.escfina1)
                self.escfina1=self.escfina1+1
              else:
                self.escfina1=int(self.escfina1)
                #self.escfina1=int(round(self.escfina1, ndigits=0))
              
              # Defining GRASS GIS region as output map region
              grass.run_command('g.region', rast=self.OutArqResist)#, res=self.res3) 
              
              if self.n_scales > 1 and self.scale_counter > 1:
                self.Nsimulations1_tobe_realized = 0
              else:
                self.Nsimulations1_tobe_realized = self.Nsimulations1
              
              # If methods MLmin, MLavg, MLmax are going to be simulated, this command prepares
              # the resistance map taking into consider these methods
              # Also, the list of methods to be simulated is defined
              if self.Nsimulations1_tobe_realized > 0: # no influence of landscape
                self.methods.append('MP')
              
              if self.Nsimulations2 > 0: # minimum
                self.methods.append('MLmin')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C2)[self.current_mapset]
                if len(map_exists) == 0:
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C2, method='minimum', size=self.escfina1, overwrite = True)
                
              if self.Nsimulations3 > 0: # average
                self.methods.append('MLavg')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C3)[self.current_mapset]
                if len(map_exists) == 0:              
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C3, method='average', size=self.escfina1, overwrite = True)
              
              if self.Nsimulations4 > 0: # maximum
                self.methods.append('MLmax')
                self.defaultsize_moviwin_allcor=self.escfina1
                
                # Generates the input map, but only if it does not exist
                map_exists = grass.list_grouped('rast', pattern=self.C4)[self.current_mapset]
                if len(map_exists) == 0:                
                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C4, method='maximum', size=self.escfina1, overwrite = True)
              
              # Organizes names of resistance maps to be used in simulations
              self.listafinal=[]
              self.listamethods=[]
              
              for i in range(self.Nsimulations1_tobe_realized):
                self.listafinal.append(self.OutArqResist)
                self.listamethods.append('MP')
              for i in range(self.Nsimulations2):
                self.listafinal.append(self.C2)
                self.listamethods.append('MLmin')
              for i in range(self.Nsimulations3):
                self.listafinal.append(self.C3)
                self.listamethods.append('MLavg')
              for i in range(self.Nsimulations4):
                self.listafinal.append(self.C4)
                self.listamethods.append('MLmax')
              
              # Not necessary
              #grass.run_command('g.region', rast=self.OutArqResist, res=self.res3)
              
              # Total number of simulations (M! + MLmin + MLavg + MLmax)
              self.Nsimulations = self.Nsimulations1_tobe_realized + self.Nsimulations2 + self.Nsimulations3 + self.Nsimulations4
              
              # Transforming list of STs in integers (for recongnizing them in the map)       
              self.patch_id_list=map(int,self.patch_id_list_bkp)
              
              #---------------------------------------------#
              #--------------- START SIMULATIONS -----------#
              #---------------------------------------------#
              
              # For each ST pair in the list:
              while (len(self.patch_id_list)>1):
                
                # List of number of corridors already simulated - to be updated as simulations run
                self.simulated = [1, 1, 1, 1]                              
                
                self.ChecktTry=True
                # Change to output dir
                os.chdir(self.OutDir_files_TXT)
                
                # Select a pair from the list and prepare vectors for processing
                while self.ChecktTry==True:
                  try:
                    # Selects from the beginning to the end of the list
                    self.S1=self.patch_id_list[0]
                    self.T1=self.patch_id_list[1]
                    self.S1FORMAT='000000{}'.format(self.S1)
                    self.S1FORMAT=self.S1FORMAT[-5:]
                    self.T1FORMAT='000000{}'.format(self.T1)
                    self.T1FORMAT=self.T1FORMAT[-5:]
                    
                    # Selects pair and delete it from the original ST combination list
                    del self.patch_id_list[0:2]
                    self.PAISAGEM='EXPERIMENT'
                    self.ARQSAIDA=self.PAISAGEM+'_s'+self.S1FORMAT+'_t'+self.T1FORMAT # Name of ouput text file                  
                    self.logger.AppendText("Processing ST pair: \n"+self.S1FORMAT+' & '+self.T1FORMAT+ '\n')  
                    self.S1=(int(str(self.S1)))
                    self.T1=(int(str(self.T1)))
                    
                    # Generates rasters with only the region of the source and terget points
                    self.form_02='source = if('+self.OutArqST+' != {}, null(), {})'.format(self.S1,self.S1)
                    grass.mapcalc(self.form_02, overwrite = True, quiet = True)
                    self.form_03='target = if('+self.OutArqST+' != {}, null(), {})'.format(self.T1,self.T1)
                    grass.mapcalc(self.form_03, overwrite = True, quiet = True)
                    
                    # Transform source and target rasters into vectors
                    grass.run_command('g.region', rast=self.OutArqST, verbose=False)
                    grass.run_command('r.to.vect', input='source', out='source_shp', type='area', verbose=False, overwrite = True ) 
                    grass.run_command('r.to.vect', input='target', out='target_shp', type='area', verbose=False, overwrite = True ) 
                    # Adds x and y coordinates as columns to the vectors attribute
                    grass.run_command ('v.db.addcolumn', map='source_shp', columns='x double precision,y double precision', overwrite = True)
                    grass.run_command ('v.db.addcolumn', map='target_shp', columns='x double precision,y double precision', overwrite = True)
                    
                    grass.read_command ('v.to.db', map='source_shp', option='coor', columns="x,y", overwrite = True)
                    grass.read_command ('v.to.db', map='target_shp', option='coor', columns="x,y", overwrite = True)
                    
                    # Selects x,y coordinates of source point
                    self.var_source_x=grass.vector_db_select('source_shp', columns = 'x')['values'][1][0]
                    self.var_source_y=grass.vector_db_select('source_shp', columns = 'y')['values'][1][0]
                    # Selects x,y coordinates of source point
                    self.var_target_x=grass.vector_db_select('target_shp', columns = 'x')['values'][1][0]
                    self.var_target_y=grass.vector_db_select('target_shp', columns = 'y')['values'][1][0]
                    self.ChecktTry=False
                    
                  # In case the list of x,y is invalid, skips the simulation pair of STs with Error message, and keeps on simulating other pairs
                  except:
                    self.ChecktTry=True
                    # Error message on GRASS GIS console
                    print ("Error def Rasterize ST, Add cols, Get x,y cords...")
                    self.time = datetime.now() # INSTANCE
                    self.day_now=self.time.day # Error day
                    self.month_now=self.time.month # Error month
                    self.year_now=self.time.year # Error year
                    self.hour_now=self.time.hour # Error hour
                    self.minuts_now=self.time.minute # Error minute
                    self.second_now=self.time.second # Error second
                    
                    # Updates Log file
                    self.listErrorLog.append("[Error ->-> :] <- Rasterize ST, Add cols, Get x,y coord : "+self.ARQSAIDA+" -> ---{}-{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                    self.listErrorLog.append("[Error ->-> :] <- Skip STS: " + self.ARQSAIDA)
                    
                    # Finishes the simulation process if there are no more ST pairs
                    if len(self.patch_id_list)==0:
                      
                      #self.txt_log.close() 
                      d= wx.MessageDialog( self,"Error: STs invalid, please check them!", "", wx.OK)
                      retCode=d.ShowModal() # Shows
                      d.Close(True) # Closes
                      break                
                
                # Transforms ST coordinates in float
                self.var_source_x_b_int=float(self.var_source_x)
                self.var_source_y_b_int=float(self.var_source_y)
                self.var_target_x_b_int=float(self.var_target_x)
                self.var_target_y_b_int=float(self.var_target_y)
                
               
                # Set region defined by the limits of source and target points + fixed distance (self.influenceprocess)
                #  This reduces simulation time, since map processing may be restricted to 
                #  the region where points are located
                defineregion("source_shp", "target_shp", self.influenceprocess) 
                
                # Name of the corridor output map
                self.mapa_corredores_sem0=self.NEXPER_FINAL+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+'S_'+self.S1FORMAT+"_T_"+self.T1FORMAT
                self.mapa_corredores_sem0_txt=self.NEXPER_FINAL_txt+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+'S_'+self.S1FORMAT+"_T_"+self.T1FORMAT
              
                # Checks if the output folder for text files exists; 
                # If not, creates it.
                self.checkfolder=os.path.exists('Line_'+self.mapa_corredores_sem0)
                
                if self.checkfolder==False:
                  os.mkdir('Line_'+str(self.mapa_corredores_sem0))
                  if platform.system() == 'Windows':
                    self.outdir=self.OutDir_files_TXT+'\Line_'+self.mapa_corredores_sem0
                  elif platform.system() == 'Linux':
                    self.outdir=self.OutDir_files_TXT+'/Line_'+self.mapa_corredores_sem0
                  else:
                    # Improve it to Mac OS - how does it work?
                    raise Exception("What platform is yours?? It's not Windows or Linux...")
                else:
                  d= wx.MessageDialog( self, "Folder for text files already exists!\n"+
                                       "Please select another directory to save the output.\n", "", wx.OK) # Create a message dialog box
                  d.ShowModal() # Shows it
                  d.Destroy() # Closes
                  self.outdir=selectdirectory() # Choose output folder, if the previous one already exists
                  
                # Initializes corridor and auxiliary map
                for method in self.methods:
                  self.form_04='mapa_corredores_'+method+' = 0'
                  grass.mapcalc(self.form_04, overwrite = True, quiet = True)
                  #self.form_16='corredores_aux = 0'
                  #grass.mapcalc(self.form_16, overwrite = True, quiet = True)
                
                ## Open output text file and writes headers      
                #self.arquivo = open(self.mapa_corredores_sem0_txt+'.txt','w')
                #self.cabecalho='EXPERIMENT'+','+'VARIABILITY'+','+'SCALE'+','+'SIMULATION_METHOD'+','+'SIMULATION_NUMBER'+','+'SOURCE'+','+'TARGET'+','+'CORRIDOR_LENGTH'+','+'CORRIDOR_COST'+','+'EUCLIDEAN_DISTANCE'+','+'COORD_SOURCE_X'+','+'COORD_SOURCE_Y'+','+'COORD_TARGET_X'+','+'COORD_TARGET_Y'+ '\n'
                #self.arquivo.write(self.cabecalho)
                
                #---------------------------------------------#
                #-------- PERFORMS EACH SIMULATION -----------#
                #---------------------------------------------#
                cont=0
                for i in range(self.Nsimulations):
                    # Set region defined by the limits of source and target points + fixed distance (self.influenceprocess)
                    defineregion("source_shp","target_shp", self.influenceprocess)
                    
                    # Selecting resistance map
                    self.form_08='mapa_resist = '+self.listafinal[cont]
                    grass.mapcalc(self.form_08, overwrite = True, quiet = True)
                    self.M = self.listamethods[cont]
                    
                    # Number of simulation   
                    c = i+1
                    # Number of simulation for a given method
                    if self.M == "MP":
                      c_method = self.simulated[0]
                      self.simulated[0] = self.simulated[0] + 1
                    if self.M == "MLmin":
                      c_method = self.simulated[1]
                      self.simulated[1] = self.simulated[1] + 1
                    if self.M == "MLavg":
                      c_method = self.simulated[2]             
                      self.simulated[2] = self.simulated[2] + 1
                    if self.M == "MLmax":
                      c_method = self.simulated[3]
                      self.simulated[3] = self.simulated[3] + 1
                    
                    # Message in dialog box
                    self.logger.AppendText('=======> Running simulation {}\n').format(c)
                    
                    #---------- RANDOM SOURCE POINT -------#
                    # Defines a random source point inside the input/source region
                    grass.run_command('r.mask', raster='source') # Mask - look only at source region
                    grass.run_command('g.region', vect='source_shp', verbose=False, overwrite = True)
                    
                    # Select a random source point
                    self.ChecktTry=True
                    
                      
                    # Generates random points
                    grass.run_command('v.random', output='temp_point1_s', n=30, overwrite = True)                       
                    # Selects random points that overlap with source region
                    grass.run_command('v.select', ainput='temp_point1_s', binput='source_shp', output='temp_point2_s', operator='overlap', overwrite = True)
                    
                    # Creates attribute table and connects to the random points inside source region
                    grass.run_command('v.db.addtable', map='temp_point2_s', columns="temp double precision")
                    grass.run_command('v.db.connect', flags='p', map='temp_point2_s')
                    # List of such random points inside Python
                    self.frag_list2=grass.vector_db_select('temp_point2_s', columns = 'cat')['values']
                    self.frag_list2=list(self.frag_list2)
                    # Selects the first (a random) point of the list
                    self.selct="cat={}".format(self.frag_list2[0])
                    grass.run_command('v.extract', input='temp_point2_s', output='pnts_aleat_S', where=self.selct, overwrite = True)
                    
                   
                      
                  # If an error in selecting a random source point occurs, this is registered here and a new random point is selected
                  
                    self.ChecktTry=True
                    # Error message on GRASS GIS console           
                    # Registering error in logfile
                    self.time = datetime.now() # INSTANCE
                    self.day_now=self.time.day # Error day
                    self.month_now=self.time.month # Error month
                    self.year_now=self.time.year # Error year
                    self.hour_now=self.time.hour # Error hour
                    self.minuts_now=self.time.minute # Error minute
                    self.second_now=self.time.second # Error second
                    self.listErrorLog.append("[Error ->-> :] <- Randomize source points: "+self.ARQSAIDA+" -> ---{}-{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                        
                    
                    # Removing mask
                    grass.run_command('r.mask',flags='r')
                    
                    #---------- RANDOM TARGET POINT -------#
                    # Defines a random target point inside the input/target region
                    grass.run_command('r.mask', raster='target')
                    grass.run_command('g.region', vect='target_shp', verbose=False, overwrite = True)
                    # Select a random target point
                    self.ChecktTry=True
                    # Generates random points
                    grass.run_command('v.random', output='temp_point1_t', n=30, overwrite = True)
                    # Selects random points that overlap with target region
                    grass.run_command('v.select', ainput='temp_point1_t', binput='target_shp', output='temp_point2_t', operator='overlap', overwrite = True)
                    # Creates attribute table and connects to the random points inside target region
                    grass.run_command('v.db.addtable', map='temp_point2_t', columns="temp double precision")
                    grass.run_command('v.db.connect', flags='p', map='temp_point2_t')
                    
                    # List of such random points inside Python
                    self.frag_list2=grass.vector_db_select('temp_point2_t', columns = 'cat')['values']
                    self.frag_list2=list(self.frag_list2)

                    # Selects the first (a random) point of the list
                    self.selct="cat={}".format(self.frag_list2[0])
                    grass.run_command('v.extract', input='temp_point2_t', output='pnts_aleat_T', where=self.selct, overwrite = True)  
                        
                   
                          
                    # If an error in selecting a random target point occurs, this is registered here and a new random point is selected
                    
                    # Error message on GRASS GIS console
                    print ("Error Randomize target points...")                     
                    # Registering error in logfile
                    self.time = datetime.now() # INSTANCE
                    self.day_now=self.time.day # Error day
                    self.month_now=self.time.month # Error month
                    self.year_now=self.time.year # Error year
                    self.hour_now=self.time.hour # Error hour
                    self.minuts_now=self.time.minute # Error minute
                    self.second_now=self.time.second # Error second
                    self.listErrorLog.append("[Error ->-> :] <- Randomize target points: "+self.ARQSAIDA+" -> ---{}-{}-{} --- time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
    
                    # Removing mask
                    grass.run_command('r.mask',flags='r')
                    
                    # If the user wants to consider only the region around ST points, this region
                    #  is selected as GRASS region; otherwise, the whole resistance map region is set
                    #  as GRASS region
                    if self.influenceprocess_boll:
                      defineregion("source_shp","target_shp", self.influenceprocess)  
                    else:
                      grass.run_command('g.region', rast=self.OutArqResist,verbose=False)
                    
                    #---------- GENERATE CORRIDOR -------#
                    self.ChecktTry=True  
                    while self.ChecktTry==True:
                      try:
                        self.form_05='corredores_aux = mapa_corredores_'+self.M
                        grass.mapcalc(self.form_05, overwrite = True, quiet = True)
                        self.ChecktTry=False
                      except:
                        self.ChecktTry=True
                        
                      self.ChecktTry=True
                      while self.ChecktTry==True:
                        try:
                          # Creates a raster of uniformely distributed random values in the interval [1,100)
                          self.form_06="aleat = rand(0,100)"
                          grass.mapcalc(self.form_06, seed=random.randint(1, 10000), overwrite = True, quiet = True)
                          # Transforms raster map of random values to the range [0.1*noise, noise), where "noise" is
                          #  the variability factor defined by the user (variable ruido_float)
                          self.form_06="aleat2 = aleat/100.0 * {} + 1.0".format(ruido_float)
                          grass.mapcalc(self.form_06, overwrite = True, quiet = True)
                          # Multiply resistance map by random noise map
                          self.form_07='resist_aux = mapa_resist * aleat2'
                          grass.mapcalc(self.form_07, overwrite = True, quiet = True)
                          # Sets null cells as visually infinite resistance
                          self.form_07='resist_aux2 = if(isnull(resist_aux), 10000000, resist_aux)'
                          grass.mapcalc(self.form_07, overwrite = True, quiet = True)
                          
                          # Sets GRASS region
                          defineregion("source_shp","target_shp", self.influenceprocess)
                          
                          # Generating cumulative cost raster map for linking S and T points
                          grass.run_command('r.cost', flags='k', input='resist_aux2', output='custo_aux_cost', start_points='pnts_aleat_S', stop_points='pnts_aleat_T', overwrite = True)
                          # Tracing the least cost path (corridor) - the flow based on cumulative cost map
                          grass.run_command('r.drain', input='custo_aux_cost', output='custo_aux_cost_drain', start_points='pnts_aleat_T', overwrite = True)
                          # Transforms null cells (no corridor) in zeros
                          # Now we have a corridor map
                          grass.run_command('r.series', input='corredores_aux,custo_aux_cost_drain', output='mapa_corredores_'+self.M, method='sum', overwrite = True)
                          self.ChecktTry=False
                          
                        # If an error in generating corridors, this is registered here and the algoeithm tries to generate the corridor again
                        except:
                          self.ChecktTry=True
                          # Error message on GRASS GIS console
                          print ("Error Corridor methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series...")
                          # Registering error in logfile
                          self.time = datetime.now() # INSTANCE
                          self.day_now=self.time.day # Error day
                          self.month_now=self.time.month # Error month
                          self.year_now=self.time.year # Error year
                          self.hour_now=self.time.hour # Error hour
                          self.minuts_now=self.time.minute # Error minute
                          self.second_now=self.time.second # Error second
                          self.listErrorLog.append("[Error ->-> :] <- Methods: aleat, aleat2, resist_aux, r.cost, r.drain, r.series: "+self.ARQSAIDA+" -> ---{}-{}-{} --- Time : {}:{}".format(self.year_now,self.month_now,self.day_now,self.hour_now,self.second_now))
                          
                    # Multiply corridor map (binary - 0/1) by the original resistance map
                    # Now we get a raster with the cost of each pixel along the corridor
                    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    #!!!!!! CHECK THIS self.listafinal[0] OR self.listafinal[cont]
                    self.form_09='custo_aux_cost_drain_sum = custo_aux_cost_drain * '+self.listafinal[0]
                    grass.mapcalc(self.form_09, overwrite = True, quiet = True)  
                   
                    # CALCULATES COST
                    self.x = grass.read_command('r.univar', map='custo_aux_cost_drain_sum')
                    # List of corridor statistics
                    self.x_b = self.x.split('\n')
                    # Sum of the cost of each pixel along the corridor, string format
                    self.x_c = str(self.x_b[14])
                    # Value of the corridor total cost, float format
                    self.var_cost_sum = float(self.x_c.replace("sum: ",""))
                    
                    # If the user wants to consider only the region around ST points, this region
                    #  is selected as GRASS region; otherwise, the whole resistance map region is set
                    #  as GRASS region
                    if self.influenceprocess_boll:
                      defineregion("source_shp", "target_shp", self.influenceprocess)  
                    else:
                      grass.run_command('g.region', rast=self.OutArqResist, verbose=False)
                    
                    # Corridor map with NULL cells instead of zeros
                    self.form_10=self.mapa_corredores_sem0+'_'+self.M+' = if(mapa_corredores_'+self.M+' == 0, null(), mapa_corredores_'+self.M+')'
                    grass.mapcalc(self.form_10, overwrite = True, quiet = True)
                    
                    # CALCULATES CORRIDOR LENGTH using corridor map (with NULL values)
                    self.length = grass.read_command('r.univar', map='custo_aux_cost_drain')
                    # List of statistics
                    self.length_b=self.length.split('\n')
                    # Sum of pixels (value 1) of the corridor, string format
                    self.length_c=str(self.length_b[14])
                    # Sum of pixels of the corridor, float format
                    self.length_d=self.length_c[5:9]
                    self.length_e=float(self.length_d)
                    # Distance in meters (multiply map resolution by distance in pixels)
                    self.var_dist_line=self.res3*self.length_e
                   
                    # CALCULATES EUCLIDEAN DISTANCE between S and T points
                    self.euclidean_a = float((self.var_source_x_b_int-self.var_target_x_b_int)**2 + (self.var_source_y_b_int-self.var_target_y_b_int)**2)
                    self.euclidean_b = self.euclidean_a**0.5         
                         
                    # Produces information for one corridor - to be appended to the output text file
                    self.linha=self.linha.replace('\'','')
                    self.linha=self.listafinal[cont].replace("@PERMANENT",'')+',{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                        ruido_float,esc,self.M,c_method,self.S1,self.T1,self.var_dist_line,self.var_cost_sum,self.euclidean_b,self.var_source_x,self.var_source_y,self.var_target_x,self.var_target_y
                    )

                    # Output directory
                    os.chdir(self.OutDir_files_TXT)                    
                    
                    # Writes corridor information on output text file
                    self.arquivo = open(self.NEXPER_FINAL_txt+'.txt','a')
                    self.arquivo.write(self.linha)
                    self.arquivo.close()
                    
                    # Generates a vector line map for each corridor (vectorizing raster map)
                    self.outline1='000000{}'.format(c_method)
                    self.outline1=self.outline1[-3:]
                    self.outline1=self.mapa_corredores_sem0+'_'+self.M+"_SM_"+self.outline1
                    
                    # Vectorizes corridor raster map
                    grass.run_command('g.region', rast='custo_aux_cost_drain')
                    grass.run_command('r.to.vect', input='custo_aux_cost_drain', output=self.outline1, type='line',verbose=False, overwrite = True)
                    # Add column with corridor (LCP) length, in meters
                    grass.run_command ('v.db.addcolumn', map=self.outline1, columns='dist double precision', overwrite = True)
                    grass.read_command ('vv.to.db', map=self.outline1, option='length', type='line', col='dist', units='me', overwrite = True)
                    # Exports output vector
                    os.chdir(self.outdir)
                    print("exportanto em .................................................................",self.outdir)
                    xxxxxxxxx
                    grass.run_command('v.out.ogr', input=self.outline1, dsn=self.outline1+'.shp',verbose=False,type='line')
                    grass.run_command('g.remove', type="vect", name=self.outline1, flags='f')                        
                    cont=cont+1
                    
                    #--------------------------------------------------#
                    # Opens he log file and writes the errors in the log
                    # Output directory
                    os.chdir(self.OutDir_files_TXT)
                  
                    # Open Log file
                    self.txt_log = open(self.header_log+'.txt','a')                    
                  
                    # Errors
                    for logERR in self.listErrorLog:
                      self.txt_log.write(logERR+"\n")
                  
                    # Close log file
                    self.txt_log.close()                       
                    
                    #---------------------------------#
                    # Re-initializes corridor variables and list of errors
                    self.var_dist_line = 0.0
                    self.var_cost_sum = 0.0                
                    self.linha = ''
                    self.listErrorLog = []
                    
                    # -------- HERE ENDS THE SIMULATION OF ONE CORRIDOR ------------------#
                    # -------- THE LOOPS CONTINUES UNTIL ALL CORRIDORS ARE SIMULATES -----#
                
                # Exports raster maps with all corridors for the selected ST pair, for each simulated method
                for method in self.methods:
                
                  self.listExport.append(self.mapa_corredores_sem0+'_'+method)
                  self.listExportMethod.append(method)
                  
                  grass.run_command('g.region', rast=self.mapa_corredores_sem0+'_'+method)
                
                  os.chdir(self.OutDir_files_TXT)
                  grass.run_command('r.out.gdal', input=self.mapa_corredores_sem0+'_'+method, out=self.mapa_corredores_sem0+'_'+method+'.tif', nodata=-9999)
                
                
              #---------------------------------------------#
              #-------- EXPORTS SYNTHESIS MAPS -------------#
              #---------------------------------------------#
              
              # If the number of simulations for a given method is > 1 or there is more than um ST pair, two summary maps are generated, for each method:
              #  - RSFI, a map with the route selection frequency index value for each pixel (the number of routes that passes by each pixel)
              #  - LargeZone_Corridors, an average map of corridors, considering all simulations all STs
              for method in self.methods:
                
                # name of the final corridor raster maps and output files
                self.output_file_name = self.NEXPER_FINAL+'_'+'var_'+str(ruido_float).replace('.', '_')+'_'+'scale_'+str(esc)+'_'+method
                
                index = [i for i, v in enumerate(self.listExportMethod) if v == method] # get indexes of simulations that were each of method
                export = [self.listExport[i] for i in index] # select map names simulated simulated for each 'method'
                if method == 'MP':
                  Nsims = self.Nsimulations1
                elif method == 'MLmin':
                  Nsims = self.Nsimulations2
                elif method == 'MLavg':
                  Nsims = self.Nsimulations3            
                elif method == 'MLmax':
                  Nsims = self.Nsimulations4
                else:
                  print ('No method selected for generating synthesis maps!')
                  break
                  
                self.listExport
                if len(export) > 1:
                  
                  # Check this
                  grass.run_command('r.series', input=export, out=self.output_file_name+'_RSFI', method="sum", overwrite = True)
                  #grass.run_command('r.series', input=export, out=self.output_file_name+'_RSFI', method="maximum", overwrite = True)
    
                  grass.run_command('g.region', rast=self.output_file_name+'_RSFI', verbose=False)
                  #grass.run_command('r.neighbors', input=self.output_file_name+'_RSFI', out=self.output_file_name+"_LargeZone_Corridors", method='average', size=self.defaultsize_moviwin_allcor, overwrite = True)
                  grass.run_command('r.out.gdal', input=self.output_file_name+'_RSFI', out=self.output_file_name+'_RSFI.tif', nodata=-9999, overwrite = True)
                  #grass.run_command('r.out.gdal', input=self.output_file_name+"_LargeZone_Corridors", out=self.output_file_name+"_LargeZone_Corridors.tif", nodata=-9999, overwrite = True)
      
                  #grass.run_command('g.region', rast=self.output_file_name+"_LargeZone_Corridors")
              
                elif Nsims > 1 and len(export) == 1:
                  
                  grass.run_command('g.region', rast=export, verbose=False)
                  grass.run_command('r.out.gdal', input=export, out=self.output_file_name+'_RSFI.tif', nodata=-9999, overwrite = True)
                
              #---------------------------------------------#
              #---- REMOVE AUX MAPS FROM GRASS DATABASE ----#
              #---------------------------------------------#
              self.logger.AppendText("Removing auxiliary files... \n")
              
              if self.remove_aux_maps:
                grass.run_command('g.remove', type="vect", name='temp_point1_s,temp_point2_s,temp_point1_t,temp_point2_t,pnts_aleat_S,pnts_aleat_T,source_shp,target_shp', flags='f')
                grass.run_command('g.remove', type="rast", name='source,target,resist_aux,resist_aux2,mapa_resist,mapa_corredores_MP,mapa_corredores_MLmin,mapa_corredores_MLavg,mapa_corredores_MLmax,aleat,aleat2,custo_aux_cost,custo_aux_cost_drain,custo_aux_cost_drain_sum,corredores_aux,MLmin_MINIMUM,MLavg_AVERAGE,MLmax_MAXIMUM', flags='f')
              
              #----------------------------------------------------------#  
              # Here we finish the simulations for each landscape scale  #
              #----------------------------------------------------------#
              self.scale_counter += 1
            
            #-------------------------------------------------------------#  
            # Here we finish the simulations for each variability factor  #            
            #-------------------------------------------------------------#
                     
          #---------------------------------------------#
          #------------ WRITES LOG FILES ---------------#
          #---------------------------------------------#            
          
          # Output directory
          os.chdir(self.OutDir_files_TXT)
          
          # Open Log file
          self.txt_log = open(self.header_log+'.txt','a')
          
          # Simulation end time
          self.time_end = datetime.now() # INSTANCE
          self.day_end = self.time_end.day # End day
          self.month_end = self.time_end.month # End month
          self.year_end = self.time_end.year # End year
          self.hour_end = self.time_end.hour # End hour
          self.minuts_end = self.time_end.minute # End minute
          self.second_end = self.time_end.second # End second
          
          self.difference_time = self.time_end - self.time_start
          weeks, days = divmod(self.difference_time.days, 7)
          minutes, seconds = divmod(self.difference_time.seconds, 60)
          hours, minutes = divmod(minutes, 60)          
          
          self.txt_log.write("Start time       : Year {}-Month {}-Day {} ---- time: :{}:{}\n").format(
              self.year_start,self.month_start,self.day_start,self.hour_start,self.minuts_start,self.second_start
          )
          self.txt_log.write("End time         : Year {}-Month {}-Day {} ---- Time: {}:{}:{}\n").format(
              self.year_end,self.month_end,self.day_end,self.hour_end,self.minuts_end,self.second_end
          )
          
          # Simulation time
          self.difference_time="{} Weeks - {} Days - "+" Time: {}:{}:{}".format(
              weeks,days,hours,minutes,seconds
          )
          
          # Writes log file
          self.txt_log.write("Processing time: "+self.difference_time+"\n\n")
          
          # Close log file
          self.txt_log.close()
          
          # Re-initializes output dir, in case new corridors are produced by clicking START SIMULATIONS button
          self.OutDir_files_TXT = ''
          
          # FINISH SIMULATIONS
          d = wx.MessageDialog(self,"Corridor simulation finished!\n"+
                              "Thanks for simulating using\n LSCorridors "+VERSION+"!", "", wx.OK)
          
          if not self.perform_tests:
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
          self.patch_id_list_aux = event.GetString()
          self.patch_id_list = self.patch_id_list_aux.split(',')
          
          # Backup of the list of ST patches
          self.patch_id_list_bkp = self.patch_id_list          
        
        """
        ID 186: Defines the variability of the map - noise factor
        """
        if event.GetId() == 186: #186=variability factor
          self.ruido = event.GetString()
          #self.ruido_float=float(self.ruido)
          try:
            self.ruidos_float = map(float, self.ruido.split(','))
            self.logger.AppendText('Variability factor(s): \n'+','.join(str(i) for i in self.ruidos_float)+ '\n')
          except:
            self.ruidos_float = [-1.0]
            print ("Could not convert at least one of the variability values to a float.")
          
        """
        ID 186: Defines the scale of influence for methods MLmin, MLavg, and MLmax
        """
        if event.GetId() == 196: #196=animal perception scale
          #self.esc=float(event.GetString())
          # this transforms values separated by commas into a list 
          # and turns these numbers into floating point values
          try:
            self.escalas = map(int, event.GetString().split(','))
            self.logger.AppendText('Landscape scale(s): \n'+','.join(str(i) for i in self.escalas)+ '\n')            
          except:
            self.escalas = [-1]
            print ("Could not convert at least one of the scale values to an integer.")

        """
        ID 185: Reads output map name
        """
        if event.GetId() == 185: #185=base name
          self.NEXPER_APOIO = event.GetString()
          self.NEXPER_FINAL = self.NEXPER_AUX+"_"+self.NEXPER_APOIO
          self.NEXPER_FINAL = self.NEXPER_FINAL.replace('@PERMANENT','')
          self.NEXPER_FINAL_txt = self.NEXPER_AUX_txt+"_"+self.NEXPER_APOIO
          self.NEXPER_FINAL_txt = self.NEXPER_FINAL_txt.replace('@PERMANENT','')          
          self.logger.AppendText('Output map base name: \n'+self.NEXPER_FINAL+ '\n')
            
        """
        ID 190-193: Reads number of simulations for each method: M!, MLmin, MLavg, MLmax
        """
        # Method MP
        if event.GetId() == 190: #190=number of simulations
          try:
            self.Nsimulations1=int(event.GetString())
          except ValueError:
            self.Nsimulations1=0
            
        # Method MLmin
        if event.GetId() == 191: #191=number of simulations
          try:
            self.Nsimulations2=int(event.GetString())
          except ValueError:
            self.Nsimulations2=0  
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()
            
        # Method MLavg
        if event.GetId() == 192: #192=number of simulations
          try:
            self.Nsimulations3=int(event.GetString())
          except ValueError:
            self.Nsimulations3=0          
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()          
        # Method MLmax
        if event.GetId() == 193: #193=number of simulations
          try:
            self.Nsimulations4=int(event.GetString())
          except ValueError:
            self.Nsimulations4=0
            
          if self.Nsimulations2 <= 0 and self.Nsimulations3 <= 0 and self.Nsimulations4 <= 0:
            self.editname8.Disable()
          else:
            self.editname8.Enable()          
        
    def OnExit(self, event):
      
        d= wx.MessageDialog(self, " Thanks for simulating using\n"
                            " LSCorridors "+ VERSION+"!", "Good Bye!", wx.OK) # Create a message dialog box
        if not self.perform_tests:
          d.ShowModal() # Shows it
          d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 


#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSCorridors "+VERSION, pos=(0,0), size=(570,590))
    Corridors(frame,-1)
    frame.Show(1)
    app.MainLoop()
    

