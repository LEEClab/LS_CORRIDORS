import grass.script as grass
projP=str(grass.read_command('g.proj', flags='g'))
projPSplt=projP.split('\n')
splitprojP=(projP.split('\n'))
splitprojP=splitprojP[:-1];del(splitprojP[0])

Listchav=[]
ListVal =[]
for i in splitprojP:
    var1=i.replace('\r','')
    var1spt=var1.split("=")
    Listchav.append(var1spt[0])
    ListVal.append(var1spt[1])
dictVar=list(zip(Listchav,ListVal))
dictVar=dict(dictVar)
dictVar['srid']=dictVar['srid'].replace('EPSG:','')
EPSG=int(dictVar['srid'])
print(EPSG)


    