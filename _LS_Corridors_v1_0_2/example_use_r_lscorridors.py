
# Import modules
import grass.script as grass
import os, imp
import numpy as np

# Change to dir where the script is
os.chdir('/home/leecb/Github/LS_CORRIDORS/_LS_Corridors_v1_0_0_stable')

# Import modules
r_ls_corridors = imp.load_source('main', 'r.ls.corridors.py')

#--------------
# Run many maps

# Supose we imported the following maps into GRASS GIS: 'map_name1', 'map_name2', and 'map_name3'
maps = ['map_name1', 'map_name2', 'map_name3']

# Or it is possible to get these names from the GRASS mapset
# For example:
# maps = grass.list_grouped('rast', pattern = 'map_name')['PERMANENT']

# And the following ST maps: 'st1', 'st2', and 'st3'
sts = ['st1', 'st2', 'st3']

# We should have three lists of ST pairs
pairs = ['1,2', '7,8,9,10', '1,5,6,7,8,9,11,12']

# Then, it is possible to run corridors for each set of maps and parameters

# Iterate from i = 0 to i = 2
for i in range(len(maps)):
    
    resist = maps[i]
    st = sts[i]
    pair_list = pairs[i]
    
    # Run corridors
    r_ls_corridors.main(resistancemap = resist, stmap = st, stlist = pair_list, output_prefix = '', 
                        output_folder = '/choose/output/folder', variability = '2.0', scale = '200', 
                        simulations = '100', method = 'MLavg')
    

#--------------
# Run one map randomly sampling the scale parameter from a list

# Supose now we have only one map, 'map_name1', as well as ST map and ST list:
resist_map = 'map_name1'

st_map = 'st1'

pair = '1,2,3,4'

# We are going to run 100 corridor simulations, sampling the scale parameter from the following list:
n_simulations = 100

scales = ['100', '150', '200', '250', '300', '350', '400', '450', '500']

# Random scale list
random_scales = np.random.choice(scales, n_simulations, replace = True)

# Iterate from each scale value (100 in total)
for scale in random_scales:

    print 'Running corridors for scale = '+scale
    
    # Run corridors - '1 corridor for each scale value
    r_ls_corridors.main(resistancemap = resist_map, stmap = st_map, stlist = pair, output_prefix = '', 
                        output_folder = '/choose/output/folder', variability = '2.0', scale = scale, 
                        simulations = '1', method = 'MLavg')
    
    # The problem with this approach is that 100 different output files will be generated; also, a raster
    # map with all corridors will not be generated... gathering this would have to be done after simulations...
    # We still have to further develop that!


