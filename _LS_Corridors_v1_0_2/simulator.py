#if event.GetId() == 10:   #10==START BUTTON



"""
Essa parte sera usada apenas para os testes. 
Quando for realmente rodar, as variaveis serao passadas
por parametro na funcao

"""
# definindo as variaves da funcao


def simulator():
          
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
          #
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
          #
          if any(i < 2.0 for i in self.escalas_pixels) and (self.Nsimulations2 > 0 or self.Nsimulations3 > 0 or self.Nsimulations4 > 0): 
                    d= wx.MessageDialog(self, "There may a problem with scale parameter. \n"+
                                        "Input map resolution is "+`round(self.res3,1)`+" m, scale should be greater than that!\n"+
                                        "Please check the parameter(s).\n", "", wx.OK) # Create a message dialog box
                    d.ShowModal() # Shows it
                    d.Destroy() # Finally destroy it when finished.
                    self.logger.AppendText()
                    sys.exit()
          #
          # Tests if number of simulations is >= 0
          if self.Nsimulations1 < 0 or self.Nsimulations2 < 0 or self.Nsimulations3 < 0 or self.Nsimulations4 < 0:
                    d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                        "Number of simulations must be equal to or greater than zero!\n"+
                                        "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
                    d.ShowModal() # Shows it
                    d.Destroy() # Finally destroy it when finished.
                    self.logger.AppendText()
                    sys.exit() 
          #
          # Tests if number of simulations for at is > 0 for at least one simulation method
          if (self.Nsimulations1 + self.Nsimulations2 + self.Nsimulations3 + self.Nsimulations4) <= 0:
                    d= wx.MessageDialog(self, "Incorrect number of simulations\n"+
                                        "Number of simulations must greater than zero fot at least one simulation method!\n"+
                                        "Please check the parameters.\n", "", wx.OK) # Create a message dialog box
                    d.ShowModal() # Shows it
                    d.Destroy() # Finally destroy it when finished.
                    self.logger.AppendText()
                    sys.exit()  
          #
          
          # Tests if the length of the ST list is > 1
          if  self.lenlist <= 1: 
                    d= wx.MessageDialog(self, "Incorrect list\n"+
                                        "List length is smaller than 1!\n"+
                                        "Please check the list.\n", "", wx.OK) # Create a message dialog box
                    d.ShowModal() # Shows it
                    d.Destroy() # Finally destroy it when finished.
                    self.logger.AppendText()
                    sys.exit()   
          
          
          elif self.lenlist > 1 and int (self.lenlist)%2 == 1:
            
                    d= wx.MessageDialog(self, "Incorrect list.\n"+
                                        "List length cannot be odd,"+
                                        "please check the list.\n", "", wx.OK) # Create a message dialog box
                    d.ShowModal() # Shows it
                    d.Destroy() # Finally destroy it when finished.
                    sys.exit()
          #
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
                      
          self.logger.AppendText("\nList of source-targets: \n"+`self.patch_id_list`+'\n') 
          d = wx.MessageDialog(self,"Click OK and wait for simulation processing;\n"+
                               "A message will warn you at the end of simulations.\n"+
                               "Thank you.","", wx.OK)  
          #
          if not self.perform_tests:
                    retCode=d.ShowModal() # Shows 
                    d.Close(True) # Finally destroy it when finished.    
          #
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
          self.header_log="___Log_Year_"+`self.year_start`+"-Month"+`self.month_start`+"-Day_"+`self.day_start`+"_Time_"+`self.hour_start`+"_"+`self.minuts_start`+"_"+`self.second_start`
          self.txt_log=open(self.header_log+".txt","w")       
          self.txt_log.write("LS Corridors log file\n")
          self.txt_log.write("---------------------\n\n")
          
          self.txt_log.write("Inputs: \n")
          self.txt_log.write("	Resistance map                                                : "+self.OutArqResist+"\n")
          self.txt_log.write("	Source-Target map                                             : "+self.OutArqST+"\n")
          self.txt_log.write("	Resistance map resolution (m)                                 : "+`self.res3`+"\n")
          self.txt_log.write("	Variability factor(s)                                         : "+', '.join(str(i) for i in self.ruidos_float)+"\n")
          self.txt_log.write("	Scale(s) of influence (m)                                     : "+', '.join(str(i) for i in self.escalas)+"\n")
          self.txt_log.write("	Number of simulations MP    (without landcape influence)      : "+`self.Nsimulations1`+"\n")
          self.txt_log.write("	Number of simulations MLmin (with landscape influence-minimum): "+`self.Nsimulations2`+"\n")
          self.txt_log.write("	Number of simulations MLavg (with landscape influence-average): "+`self.Nsimulations3`+"\n")
          self.txt_log.write("	Number of simulations MLmax (with landscape influence-maximum): "+`self.Nsimulations4`+"\n")
          self.txt_log.write("	Source-Target pairs simulated                                 : "+`', '.join(str(i) for i in self.patch_id_list_bkp)`+"\n")
        
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
                    
                    self.logger.AppendText("Running corridors for variability = "+`ruido_float`+".\n")
                    
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
                                  
                              self.logger.AppendText("Running corridors for landscape scale = "+`esc`+".\n")
                              
                              # Names of input maps for each scale and each method
                              self.C2=self.OutArqResist+'_'+self.C2_pre+'_scale_'+`esc`
                              self.C3=self.OutArqResist+'_'+self.C3_pre+'_scale_'+`esc`
                              self.C4=self.OutArqResist+'_'+self.C4_pre+'_scale_'+`esc`
                              
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
                              #
                              # If methods MLmin, MLavg, MLmax are going to be simulated, this command prepares
                              # the resistance map taking into consider these methods
                              # Also, the list of methods to be simulated is defined
                              if self.Nsimulations1_tobe_realized > 0: # no influence of landscape
                                        self.methods.append('MP') 
                              #
                              if self.Nsimulations2 > 0: # minimum
                                        self.methods.append('MLmin')
                                        self.defaultsize_moviwin_allcor=self.escfina1
                                        
                                        # Generates the input map, but only if it does not exist
                                        map_exists = grass.list_grouped('rast', pattern=self.C2)[self.current_mapset]
                                        if len(map_exists) == 0:
                                                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C2, method='minimum', size=self.escfina1, overwrite = True)   
                              #
                              if self.Nsimulations3 > 0: # average
                                        self.methods.append('MLavg')
                                        self.defaultsize_moviwin_allcor=self.escfina1
                                        
                                        # Generates the input map, but only if it does not exist
                                        map_exists = grass.list_grouped('rast', pattern=self.C3)[self.current_mapset]  
                                        if len(map_exists) == 0:              
                                                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C3, method='average', size=self.escfina1, overwrite = True)  
                              #
                              if self.Nsimulations4 > 0: # maximum
                                        self.methods.append('MLmax')
                                        self.defaultsize_moviwin_allcor=self.escfina1
                                        
                                        # Generates the input map, but only if it does not exist
                                        map_exists = grass.list_grouped('rast', pattern=self.C4)[self.current_mapset]   
                                        if len(map_exists) == 0:                
                                                  grass.run_command('r.neighbors', input=self.OutArqResist, output=self.C4, method='maximum', size=self.escfina1, overwrite = True)  
                              #
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
                              #
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
                                                            self.S1FORMAT='000000'+`self.S1`
                                                            self.S1FORMAT=self.S1FORMAT[-5:]
                                                            self.T1FORMAT='000000'+`self.T1`
                                                            self.T1FORMAT=self.T1FORMAT[-5:]
                                                            
                                                            # Selects pair and delete it from the original ST combination list   
                                                            del self.patch_id_list[0:2]
                                                            self.PAISAGEM='EXPERIMENT'
                                                            self.ARQSAIDA=self.PAISAGEM+'_s'+self.S1FORMAT+'_t'+self.T1FORMAT # Name of ouput text file                  
                                                            self.logger.AppendText("Processing ST pair: \n"+self.S1FORMAT+' & '+self.T1FORMAT+ '\n')  
                                                            self.S1=(int(str(self.S1)))
                                                            self.T1=(int(str(self.T1)))
                                                            
                                                            # Generates rasters with only the region of the source and terget points
                                                            self.form_02='source = if('+self.OutArqST+' != '+`self.S1`+', null(), '+`self.S1`+ ')'
                                                            grass.mapcalc(self.form_02, overwrite = True, quiet = True)
                                                            self.form_03='target = if('+self.OutArqST+' != '+`self.T1`+', null(), '+`self.T1`+ ')'
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
                                                  #
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
                                                            self.listErrorLog.append("[Error ->-> :] <- Rasterize ST, Add cols, Get x,y coord : "+self.ARQSAIDA+" -> ---"+`self.year_now`+"-"+ `self.month_now` + "-"+ `self.day_now`+" --- time : "+`self.hour_now `+":"+`self.second_now`)
                                                            self.listErrorLog.append("[Error ->-> :] <- Skip STS: " + self.ARQSAIDA)
                                                            
                                                            # Finishes the simulation process if there are no more ST pairs   
                                                            if len(self.patch_id_list)==0:
                                                                                  
                                                                      #self.txt_log.close() 
                                                                      d= wx.MessageDialog( self,"Error: STs invalid, please check them!", "", wx.OK)
                                                                      retCode=d.ShowModal() # Shows
                                                                      d.Close(True) # Closes
                                                                      break                                                               
                                                  #
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
                                                  #
                                                  # Initializes corridor and auxiliary map
                                                  for method in self.methods:
                                                            self.form_04='mapa_corredores_'+method+' = 0'
                                                            grass.mapcalc(self.form_04, overwrite = True, quiet = True)
                                                            #self.form_16='corredores_aux = 0'
                                                            #grass.mapcalc(self.form_16, overwrite = True, quiet = True) 
                                                  #
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
                                                  
                                                  #
                                                  
                                                  #
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
                                                            print 'No method selected for generating synthesis maps!'
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
                                                  #
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
                                                  #
                                                  #----------------------------------------------------------#  
                                                  # Here we finish the simulations for each landscape scale  #
                                                  #----------------------------------------------------------#
                                                  self.scale_counter += 1  
                                        #
                                        #-------------------------------------------------------------#  
                                        # Here we finish the simulations for each variability factor  #            
                                        #-------------------------------------------------------------# 
                              #
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
                              
                              self.txt_log.write("Start time       : Year "+`self.year_start`+"-Month "+`self.month_start`+"-Day "+`self.day_start`+" ---- time: "+`self.hour_start`+":"+`self.minuts_start`+":"+`self.second_start`+"\n")                   
                              self.txt_log.write("End time         : Year "+`self.year_end`+"-Month "+`self.month_end`+"-Day "+`self.day_end`+" ---- Time: "+`self.hour_end`+":"+`self.minuts_end`+":"+`self.second_end`+"\n")
                              
                              # Simulation time
                              self.difference_time=`weeks`+" Weeks - "+`days`+" Days - "+" Time: "+`hours`+":"+`minutes`+":"+`seconds`
                              
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
                 
            