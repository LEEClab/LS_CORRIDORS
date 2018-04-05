####################################################################
#
# Calculating connectivity index (CI) based on ecological corridors
#
# This is the code to calculate the connectivity index based on 
#   the Euclidean distance between source-target points and 
#   the cost of corridors linking these points, using 
#   corridor simulation through LSCorridors package.
# The CI is calculated as (Euclidean distance/Corridor cost), so that
#   the higher the cost the lower the connectivity, given a fixed 
#   distance between source and target patches.
# 
# More information: https://github.com/LEEClab/LS_CORRIDORS/wiki
#
# Bernardo Niebuhr <bernardo_brandaum@yahoo.com.br>
# Juliana S. Santos <juliana.silveiradossantos@gmail.com>
# Milton Ribeiro <mcr@rc.unesp.br>
# John Ribeiro <jw.ribeiro.rc@gmail.com>
# Israel Schneiberg <israelschneiberg@gmail.com>
#
# Dec. 2016
# Feel free to modify and share this code
####################################################################

# Set working dir
setwd("/home/leecb/Dropbox/Israel")

# Load data
 
# Directories with output - one folder for each landscape
# These folders contain the text file with corridor information, 
#   an output of LSCorridors
dirs <- list.dirs(recursive = F)
dirs <- dirs[2:8] # Selecting only directories with results

# Initializing data
ConectIndexTable <- data.frame(matrix(NA, nrow = length(dirs), ncol = 2, dimnames = list(NULL, c("LandscapeID", "ConnectivityIndex"))))

# Loop for each local landscape
for(i in 1:length(dirs)) {
  
  # Selecting LSCorridors output file
  txts <- list.files(dirs[i], pattern = "txt") # list txt files in folder
  file <- txts[2] # first element is the log file; the second is the output
  
  # Reading data
  dat <- read.table(paste(dirs[i], file, sep = "/"), header = TRUE, sep = ",") # read output table
  
  # Selecting only simulations considering the variability parameter = 10
  dat <- subset(dat, VARIABILITY == 10)

  print(paste("Number of simulations:", nrow(dat)))
  print(paste("Patch source ID      :", source <- unique(dat$SOURCE)[1]))
  print(paste("Patch target IDs     :", paste(unique(dat$TARGET), collapse = ", ")))

  # This is the calculus if the number of simulations per ST pair is the same (as it is the case)
  # Here we calculate the mean cost and distance for all corridors of all STs pooled
  IC <- mean(dat$EUCLIDEAN_DISTANCE)/mean(dat$CORRIDOR_COST)

  # This would be the calculus if the number of simulations per ST pair was not the same
  # Here we calculate the mean cost and distance for each ST, and then average that over all STs
  #IC <- mean(aggregate(dat$EUCLIDEAN_DISTANCE, by = list(dat$TARGET), FUN = mean)[,2])/mean(aggregate(dat$CORRIDOR_COST, by = list(dat$TARGET), FUN = mean)[,2])
  
  ConectIndexTable[i,] <- c(source, IC)
}
  
write.table(ConectIndexTable, file = "ConectIndexTable.txt", sep = "\t", row.names = F)


