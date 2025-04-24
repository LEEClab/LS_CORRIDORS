import grass.script as grass

port = grass.list_grouped ('vect', pattern = '*MSP*') ['PERMANENT']
#print(port)

for i in port:
    grass.run_command('g.remove', type="raster", name=i, flags='f')
 
