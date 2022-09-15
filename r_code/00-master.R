########################## M A S T E R   F I L E ##########################

# clean environment
rm(list = ls())
gc() # garbage collection

# call libraries
library(ncdf4) # read ncdf4 to read nc4 files
library(readxl)
library(raster)
library(parallel)
library(foreach)
library(doParallel)
library(sf)
library(velox)
library(rgdal)
library(rgeos)
library(maps)
library(maptools)
library(mapdata)
library(data.table)
library(vioplot)
library(classInt)
library(RColorBrewer)
library(foreign)
library(ggmap)      # get geocodes with google (api key is needed)
##################################################################################################


#################################   P A T H S   ########################################
####
# get host name of machine
hostname = system('uname -n',intern=T)

if(hostname=="molina") {
  path.footprint = "/home/mario/Documents/environment_data/humanfootprint/"
  path.shapefiles = "/home/mario/Documents/environment_data/"
  path.git = "/home/mario/mm2535@cornell.edu/projects/migration_climate_change/climate_change_immigration"
  tmp = '/home/mario/Documents/environment_data/mexican_shapefiles/tmp_folder'
  # In external drive
  path.daymet = "/media/mario/Seagate Backup Plus Drive/daymet_data"
} else if(hostname=="sdl1"){
  path.shapefiles = '/home/mm2535/documents/data/climate_change'
  path.git = "/home/mm2535/documents/climate_change_immigration"
  path.daymet = "/home/mm2535/documents/data/climate_change/daymet"
  tmp = '/home/mm2535/documents/data/immigration_data/tmp_folder'
}



#################################   F U N C T I O N S   ########################################
setwd(path.git)
source("./r_code/functions_weather_data_for_ML_models.R")


#### M E X I C A N   S H A P E F I L E S
#####################################################

# Construct Mexico's shapefile (localidades only) from zip files.
# This files includes ALL Mexican states. It creates the shapefile "mx_localities"
setwd( path.git )
source('./r_code/01-mx_shapefile_construction.R')

# Construct Mexico's shapefile (entidades and municipios) from zip files. 
# These files can be used for visualization.
setwd( path.git )
source('./r_code/02-mx_shapefile_construction_ent-mun.R')
n
# Extract geocodes from MMP data for Mexican localities.
# It loads Mexico's shapefile (a large file)
# to create geocodes that combine ent, mun, and loc. Rural localities have their own geocode.
# This files includes ONLY Mexican states in the MMP geocodes. It creates the shapefile "mx_localities_mmp"
setwd( path.git )
source('./r_code/03-extract_geocode_mx_sh.R')


#### D A Y M E T
#####################################################

# IMPORTANT NOTE: 
#     - The following two files need access to dayment nc4 files. If unavailable, code will fail.
#       These files are large and the tasks will take a long time to run (~ 2-3 days)
#
# Daily climate information is extracted
setwd( path.git )
source("./r_code/04-daymet_extraction_mun.R")
#
# Daily climate information is added to MMP based on matching geocodes extracted 
# in file "03-extract_geocode_mx_sh.R" (see above)
setwd( path.git )
source("./r_code/05-daymet_extraction_loc.R")

# Create aggregate measures for MMP communities and all MEXICAN municipalities 
# and csv files with climate information.
setwd( path.git )
source("./r_code/06-climate_MMP.R")



#### V A R I A B L E   C O N S T R U C T I O N   
####        F O R   M L   M O D E L S
#####################################################

##################################################################################################
# Create several weather variables for ML models. This file calls several other files.
setwd( path.git )
source("07-00-create_weather_data_for_ML_models.R")

##################################################################################################
# Graph migration over time in Mexico's map (using all MMP data)
setwd( path.git )
source("08-plot_migration_over_time_mexico_map.R")
