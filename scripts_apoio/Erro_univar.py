# Import modules
import grass.script as grass
from PIL import Image
import wx
import random, math
import os, sys, re, platform
from datetime import datetime

x =grass.parse_command('r.univar', map='custo_aux_cost_drain_sum')
print x
# List of corridor statistics
#self.x_b = self.x.split('\n')

# Sum of the cost of each pixel along the LCP, string format

#self.x_c = str(self.x_b[14])
#x_c  = float(x['sum'])