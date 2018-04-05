#!/usr/bin/env python

###################################################################################
#
# MODULE:       r.ls.corridors
# AUTHOR(S):    John W. Ribeiro, Milton C. Ribeiro, and Bernardo B. S. Niebuhr
# PURPOSE:      Simulate multiple functional ecological corridors
# COPYRIGHT:    (C) 2015-2016 by John W. Ribeiro and Milton C. Ribeiro
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the license, 
#  or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
###################################################################################

#%module
#% description: Simulate multiple functional ecological corridors, given a resistance surface, a map of source-target locations, and a list of sources and targets.
#% keyword: raster
#% keyword: corridor
#% keyword: resistance
#% keyword: cost
#% keyword: least-cost
#% keyword: species perception
#% keyword: landscape influence
#%end

#%option G_OPT_R_INPUT
#% key: resistancemap
#% type: string
#% description: Name of input resistance map (raster map)
#% required: yes
#%end

#%option G_OPT_R_INPUT
#% key: stmap
#% type: string
#% description: Name of Source-Target (ST) map (raster map)
#% required: yes
#%end

#%option G_OPT_R_INPUT
#% key: stlist
#% type: string
#% label: List of Source-Target (ST) locations to be connected by corridors
#% description: Location or patch IDs in the list must be values of the ST map
#% required: yes
#%end

#%option G_OPT_R_OUTPUT
#% key: output_prefix
#% type: string
#% description: Text used as prefix of all output maps and files
#% required: no
#%end

#%option
#% key: variability
#% type: double
#% description: Value (or list of values) of variability for simulating corridors
#% multiple: yes
#% required: no
#% answer: 2.0
#%end

#%option
#% key: scale
#% type: double
#% description: Value (or list of values) of the scale of landscape influence in each pixel of the input resistance map, in meters; it is relevant only for methods MLmin, MLavg, and MLmax
#% multiple: yes
#% required: no
#% answer: 100
#%end

#%option
#% key: simulations
#% type: integer
#% description: Number of corridor simulations to be run
#% multiple: no
#% required: no
#% answer: 15
#%end

#%option
#% key: method
#% type: string
#% label:  method (or list of methods) to be simulated
#% description: MP does not consider landscape influence, i.e., resistance map is considered exactly as input. In MLmin, MLavg, MLmax, before simulating corridors, each pixel of the resistance map is replaced by the value of statistics inside a window around it (minimum, average, or maximum), whose size is defined by the scale parameter
#% options: MP, MLmin, MLavg, MLmax
#% multiple: yes
#% required: no
#% answer: MP
#%end

#%option
#% key: output_folder
#% type: string
#% description: Path of the folder where output maps and files will be saved
#% multiple: no
#% required: no
#%end

# Import modules and main script
import sys, os
import grass.script as grass
from grass.pygrass.modules.shortcuts import general as g
from LS_corridors_v1_0_0 import *

# Main function
def main(resistancemap, stmap, stlist, output_prefix, output_folder, variability, scale, simulations, method):
    
    # Checking parameters and passing them to LSCorridors instance
    
    #---------------------
    # Initialize LSCorridors app class instance
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSCorridors", pos=(0,0), size=(560,450))
    corr = Corridors(frame, -1)    
    
    #---------------------
    # Define folder for output files
    if output_folder == '':
        output_folder = os.getcwd()
    # Try to change to output_folder
    try:
        os.chdir(output_folder)
        corr.path = os.getcwd()
        g.message('Folder for output files: '+corr.path)
    except:
        grass.fatal(_('GRASS GIS cannot access the folder '+output_folder+'. Please check if the folder exists'+
                      'and its access permissions.'))
    corr.OutDir_files_TXT = corr.path
    
    #---------------------
    # Check if the resistance map and ST map are inside the GRASS GIS mapset
    # If they are, define them as inputs for LSCorridors
    current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')  
    maps=grass.list_grouped('rast')[current_mapset]
    # Resistance map
    if resistancemap in maps:
        # Name of the input resistance map
        corr.OutArqResist = resistancemap
        g.message('Input resistance map: '+resistancemap)
    else:
        grass.fatal(_('Input: resistance map. There is no raster map called '+resistancemap+
                      ' inside the GRASS GIS mapset '+current_mapset+
                      '. Please import the map into GRASS GIS.'))
    if stmap in maps:
        # Name of the input resistance map
        corr.OutArqST = stmap
        g.message('Input Source-Target (ST) map: '+stmap)
    else:
        grass.fatal(_('Input: ST map. There is no raster map called '+stmap+
                      ' inside the GRASS GIS mapset '+current_mapset+
                      '. Please import the map into GRASS GIS.'))
    
    #---------------------
    # Transforms stlist into a python list nad checks if the list is ok
    corr.patch_id_list = stlist.split(',')
    corr.patch_id_list_bkp = corr.patch_id_list
    lenlist = len(corr.patch_id_list)
    
    ##########################
    # include a flag with the possibility of being a txt file
    
    # Tests if the list has more than one element
    if lenlist <= 1: 
        grass.fatal(_("Incorrect ST list. List length is smaller than 2! "+
                      "Please check the list."))
    # Tests if the length of the ST list is even
    elif lenlist > 1 and int(lenlist)%2 == 1:
        grass.fatal(_("Incorrect ST list. List length cannot be odd. "+
                      "Please check the list."))
    else:
        g.message('ST list checked and OK.')
    
    #---------------------
    # Gets prefix for output files and puts that into output final names
    if output_prefix == '':
        corr.NEXPER_FINAL = corr.NEXPER_AUX+'_'+resistancemap
        corr.NEXPER_FINAL_txt = corr.NEXPER_AUX_txt+'_'+resistancemap
    else:
        corr.NEXPER_FINAL = corr.NEXPER_AUX+'_'+output_prefix
        corr.NEXPER_FINAL_txt = corr.NEXPER_AUX_txt+'_'+output_prefix
    g.message('Prefix of the output files: '+corr.NEXPER_FINAL)
    
    #---------------------
    # Variability parameter
    # Checks if the values are positive and real
    
    try:
        # If no varibility parameter was passed, use the standard option
        if variability == '' or variability == '2.0':
            # Define the LSCorridors variability list
            corr.ruidos_float = [2.0]
        # If values of variability were passed, check that
        else:
            varlist = [float(i) for i in variability.split(',')]
            
            if len(varlist) < 1:
                grass.fatal(_('The list has no elements. Please check it.'))
            elif any(i < 0.0 for i in varlist):
                grass.fatal(_('Incorrect variability parameter(s). Variability must be '+
                              'a number equal to or greater than zero! '+
                              'Please check the parameter(s).'))
            else:
                # Define the LSCorridors variability list
                corr.ruidos_float = varlist
        g.message("Variability parameter(s): "+', '.join(str(i) for i in corr.ruidos_float))
    except:
        grass.fatal(_('One or more of the variability values is not a real number. Check it.'))
    
    
    #---------------------
    # Methods and number of simulations

    # Checks if number of simulations is integer and positive
    try:
        if int(simulations) < 1:
            grass.fatal(_('The number of simulations must be a positive integer value.'))
    except:
        grass.fatal(_('The number of simulations must be numeric.'))
        
    # Checks if the methods are valid
    if method == '':
        # If not parameter was passed, used the standard 'MP'
        method = 'MP'
    else:
        possible_methods = ['MP', 'MLmin', 'MLavg', 'MLmax']
        method_list = method.split(',')
        if all(i in possible_methods for i in method_list):
            pass
        else:
            grass.fatal(_('At list one of the methods is not valid. They must be one of these:'+
                          'MP, MLmin, MLavg, or MLmax'))
        
    # Define number of simulations for each method
    if 'MP' in method_list:
        corr.Nsimulations1 = int(simulations)
        g.message('Number of simulations for method MP: '+simulations)
    else:
        corr.Nsimulations1 = 0
    if 'MLmin' in method_list:
        corr.Nsimulations2 = int(simulations)
        g.message('Number of simulations for method MLmin: '+simulations)
    else:
        corr.Nsimulations2 = 0
    if 'MLavg' in method_list:
        corr.Nsimulations3 = int(simulations)
        g.message('Number of simulations for method MLavg: '+simulations)
    else:
        corr.Nsimulations3 = 0
    if 'MLmax' in method_list:
        corr.Nsimulations4 = int(simulations)
        g.message('Number of simulations for method MLmax: '+simulations)
    else:
        corr.Nsimulations4 = 0
    
    #---------------------
    # Scale parameter
    # Checks if the values are positive and real
        
    try:
        # If no scale parameter was passed, use the standard option
        if scale == '' or scale == '100':
            # Define the LSCorridors scale list
            corr.escalas = [100]
        # If values of scale were passed, check that
        else:
            scalelist = [int(i) for i in scale.split(',')]
            
            # First, defining GRASS GIS region as output map region
            grass.run_command('g.region', rast=resistancemap)

            # Second, reading map resolution
            res = grass.read_command('g.region', rast=resistancemap, flags='m')
            res2 = res.split('\n')
            res3 = res2[5]
            res3 = float(res3.replace('ewres=',''))

            # Third, calculate window size (landscape scale x 2) in number of pixels
            escalas_pixels = [float(i)*2/res3 for i in scalelist]

            # Finally, tests if any of the scales are lower than the pixel size
            #  (this only matters if methods MLmin, MLavg, or MLmax are going to be simulated)
            if any(i < 2.0 for i in escalas_pixels) and (corr.Nsimulations2 > 0 or corr.Nsimulations3 > 0 or corr.Nsimulations4 > 0):
                #print 'oi '+res3
                grass.fatal(_("There may a problem with scale parameter. "+
                            "Input map resolution is "+`round(res3,1)`+" meters, scale should be greater than that! "+
                            "Please check the parameter(s)."))
            else:
                # Define the LSCorridors variability list
                corr.escalas = scalelist
        g.message("Scale parameter(s): "+', '.join(str(i) for i in corr.escalas))
    except:
        grass.fatal(_('One or more of the scale values is not a real number. Check it.'))
    
    # Tests are going to be performed; however, as one do not want dialog boxes to be 
    #  shown, we keep this option as True
    corr.perform_tests = True
    
    # Event to test RUN SIMULATIONS        
    evt10 = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, 10)
    corr.OnClick(evt10)
             
    # Delete .pyc created
    #os.remove('LS_corridors_v1_0_0.pyc')
    os.remove('*.pyc')
    
    # call run START button

    return 0


if __name__ == "__main__":
    
    #---------------------
    # Reading options
    options, flags = grass.parser()
    resistancemap = options['resistancemap']
    stmap = options['stmap']
    stlist = options['stlist']
    output_prefix = options['output_prefix']
    output_folder = options['output_folder']
    variability = options['variability']
    scale = options['scale']
    simulations = options['simulations']
    method = options['method']    
    
    # Run main function
    sys.exit(main(resistancemap, stmap, stlist, output_prefix, output_folder, variability, scale, simulations, method))

