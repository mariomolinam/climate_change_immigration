########################## M A S T E R   F I L E ##########################

# clean environment
rm(list = ls())
gc() # garbage collection

#################################   L I B R A R I E S   ########################################
###  I F   I N    S D L  1
# libraries
# local.lib = '/home/mm2535/R/x86_64-pc-linux-gnu-library'
#
# library(readxl, lib=local.lib)
# library(sp, lib=local.lib)
# library(raster, lib=local.lib)
# library(parallel, lib=local.lib)
# library(sf, lib=local.lib)
# library(velox, lib=local.lib)
# library(rgdal, lib=local.lib)
# library(maps, lib=local.lib)
# library(mapdata, lib=local.lib)
# library(crayon, lib=local.lib)
# library(withr, lib=local.lib)
# library(ggplot2, lib=local.lib)
# library(rgeos, lib=local.lib)
# library(ggmap, lib=local.lib)
# library(data.table, lib=local.lib)
# library(ncdf4, lib=local.lib)


# call libraries
library(ncdf4) # read ncdf4 to read nc4 files
library(readxl)
library(raster)
library(parallel)
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
}else if(hostname=="sdl1"){
  path.shapefiles = '/home/mm2535/documents/data/immigration_data'
  path.git = "/home/mm2535/documents/climate_change_immigration"
  path.daymet = "/home/mm2535/documents/data/climate_change/daymet"
  tmp = '/home/mm2535/documents/data/immigration_data/tmp_folder'
}

# In external drive
path.daymet = "/media/mario/Seagate Backup Plus Drive/daymet_data"


#################################   F U N C T I O N S   ########################################
setwd(path.git)
source("./r_code/functions_weather_data_for_ML_models.R")

##################################################################################################
# Construct Mexico's shapefile (localidades only) from zip files.
setwd( path.git )
source('mx_shapefile_construction.R')

##################################################################################################
# Construct Mexico's shapefile (entidades and municipios) from zip files.
setwd( path.git )
source('mx_shapefile_construction_ent-mun.R')

##################################################################################################
# Extract state-level information from footprint files
setwd( path.git )
source('subset_polygons_mx_hf.R')

##################################################################################################
# Extract geocodes from MMP data for Mexican localities.
# It loads Mexico's shapefile (which is very large)
# to create geocodes that combine ent, mun, and loc. Rural localities have their own geocode.
setwd( path.git )
source('extract_geocode_mx_sh.R')

##################################################################################################
# NOT CURRENTLY USED
# Human footprints are added to MMP based on matching geocodes extracted in
# "extract_geocode_mx_sh.R". This file also relies on objects created in "extract_geocode_mx_sh.R".
# setwd( path.git )
# source("hf2MMP.R")

##################################################################################################
# IMPORTANT: This file needs access to dayment nc4 files. If unavailable, code will fail.
#
# Daily climate information is added to MMP based on matching geocodes extracted in
# "extract_geocode_mx_sh.R"
setwd( path.git )
source("daymet_extraction_loc.R")

##################################################################################################
# Daily climate information is extracted 
# "extract_geocode_mx_sh.R"
setwd( path.git )
source("daymet_extraction_mun.R")

##################################################################################################
# Create aggregate measure for MMP localities and csv files with climate information. It uses
# files from external drive
setwd( path.git )
source("climate_MMP.R")

##################################################################################################
# Create plots based on human footprint and climate information
setwd( path.git )
source("create_plots.R")

##################################################################################################
# Create several climate change variables form ML models
setwd( path.git )
source("create_weather_data_for_ML_models.R")

##################################################################################################
# Extract geocodes from crossing points for Mexican municipalities
setwd( path.git )
source("extract_geocode_crossing_points.R")

##################################################################################################
# Graph migration over time in Mexico's map (using all MMP data)
setwd( path.git )
source("plot_migration_over_time_mexico_map.R")
