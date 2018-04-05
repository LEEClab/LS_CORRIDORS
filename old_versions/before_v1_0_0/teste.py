import grass.script as grass
import numpy as np
import random
import os
#from __future__ import print_function
from grass.script import array as garray


grass.run_command("g.region",vect="source_shp,target_shp")
influensprocess=5000
c= grass.region()
n=float(c['n'])
s=float(c['s'])
e=float(c['e'])
w=float(c['w'])


n=n+influensprocess
s=s-influensprocess
e=e+influensprocess
w=w-influensprocess



grass.run_command("g.region",n=n,e=e,s=s,w=w)












