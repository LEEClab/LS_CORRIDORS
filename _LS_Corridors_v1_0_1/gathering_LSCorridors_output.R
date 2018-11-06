########################################################
#
# Gathering LSCorridors output text files 
#  for different source-target pairs
#
# This is suitable for old (before 1.0.0) version of
#  LSCorridors
# 
# Felipe Martello - felipemartello at gmail.com
#
########################################################

# Installing and loading libraries
install.packages("stringr")
library(stringr)

# Setting working directory
# Set here the folder where LSCorridors output files were saved
setwd("C:\\BD_demo\\output")

# Listing all files
all.corr <- matrix(,,11)
corr.files <- list.files(pattern="txt")

# Gathering all outputs in the same data frame
for (i in 1:length(corr.files))
{
  corr.temp <- read.table(corr.files[i], header=T, sep=",")
  
  # Creating a character with Source-Target_ID
  sour.track <- str_locate(corr.files[i],"S_")
  tar.track <- str_locate(corr.files[i],"T_")
  end.track <- str_locate(corr.files[i],".txt")
  sour <- substr(corr.files[i], sour.track[,1], (tar.track[,1]-2))
  tar <- substr(corr.files[i], tar.track[,1], (end.track[,1]-1))
  ST_ID <- paste(sour,tar,sep="_")
  
  # Inserting Source-Target_ID in dataframe
  data.temp <- cbind(ST_ID,corr.temp)
  colnames(all.corr) <- colnames(data.temp)
  all.corr <- rbind(all.corr, data.temp)
  all.corr <- na.omit(all.corr)
}

# Saving complete data frame in output text file
# Text files gathering all corridors for all ST pairs
write.table(all.corr,file=paste(substr(corr.files[i],1,sour.track-2),"_allCorridors", ".txt", sep=""), sep=",", row.names=F)  