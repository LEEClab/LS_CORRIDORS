import os
from datetime import datetime

os.chdir(r"E:\__data_2015\___john\Desenvolvimentos\aplications\Aplicacoes_grass\LSCorridors\___dados_cortados_teste_desenvolvimento")


now = datetime.now() # INSTANCE
day_start=now.day
month_start=now.month
year_start=now.year
hour_start=now.hour # GET START HOUR
minuts_start=now.minute #GET START MINUTS
second_start=now.second #GET START




now = datetime.now() # INSTANCE
day_end=now.day
month_end=now.month
year_end=now.year





header_log="_____Log__"+`year`+"-"+`month`+"-Day_"+`day`+"_Time_"+`hour_start`+"_"+`minuts_start`+"_"+`second_start`
txt_log=open(header_log+".txt","w")

txt_log.write("Start time       : Year "+`year_start`+"-Month "+`month_start`+"-Day "+`day_start`+" ---- time: "+`hour_start`+":"+`minuts_start`+":"+`second_start`+"\n")

hour_end=now.hour # GET end HOUR
minuts_end=now.minute #GET end MINUTS
second_end=now.second #GET end seconds

txt_log.write("End time         : Year "+`year_end`+"-Month "+`month_end`+"-Day "+`day_end`+" ---- time: "+`hour_end`+":"+`minuts_end`+":"+`second_end`+"\n")
diference_time=`month_end - month_start`+" month - "+`abs(day_end - day_start)`+" Day - "+" Time: "+`abs(hour_end - hour_start)`+":"+`abs(minuts_end - minuts_start)`+":"+`abs(second_end - second_start)`
txt_log.write("Processing time  : "+diference_time+"\n\n")

txt_log.write("Inputs : \n")
txt_log.write("	Cost Map               : xxxxx \n")
txt_log.write("	Source Target Map      : xxxxx \n")
txt_log.write("	Methods                : xxxxx \n")
txt_log.write("	Variability            : xxxxx \n")
txt_log.write("	Number interactions M1 : xxxxx \n")
txt_log.write("	Number interactions M1 : xxxxx \n")
txt_log.write("	Number interactions M1 : xxxxx \n")
txt_log.write("	Number interactions M1 : xxxxx \n\n")

txt_log.write("Output location : \n")
txt_log.write(r"	E:\__data_2015\___john\Desenvolvimentos\aplications\Aplicacoes_grass\LSCorridors\___dados_cortados_teste_desenvolvimento")

now = datetime.now() # INSTANCE
day_now=now.day
month_now=now.month
year_now=now.year
hour_now=now.hour # GET START HOUR
minuts_now=now.minute #GET START MINUTS
second_now=now.second #GET START
txt_log.write("\n\n")
txt_log.write("[Error ->-> :] xxx "+`year_now`+"-"+ `month_now` + "-"+ `day_now`+" --- time : "+`hour_now `+":"+`second_now`)
txt_log.close()









 


