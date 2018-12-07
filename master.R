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


# call libraries
library(ncdf4) # read ncdf4 to read nc4 files
library(readxl)
library(raster)
library(parallel)
library(sf)
library(velox)
library(rgdal)
library(maps)
library(mapdata)
library(parallel)
##################################################################################################


#################################   P A T H S   ########################################
####
path.footprint = "/home/mario/Documents/environment_data/humanfootprint/"
path.shapefiles = "/home/mario/Documents/environment_data/mexican_shapefiles/"
# path.shapefiles = "/media/mario/Seagate Backup Plus Drive/mexican_shapefiles/"
path.ra_filiz = "/home/mario/mm2535@cornell.edu/projects/ra_filiz"
path.git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"
path.prcp = "/home/mario/Documents/environment_data/prec_na/data"


##################################################################################################
# Construct Mexico's shapefile from zip files.
setwd( path.git )
source('mx_shapefile_construction.R')

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
# Human footprints are added to MMP based on matching geocodes extracted in "extract_geocode_mx_sh.R".
# This file also relies on objects created in "extract_geocode_mx_sh.R".
setwd( path.git )
source("hf2MMP.R")

##################################################################################################
# Daily precipitacions are added to MMP based on matching gecodes extracted in "extract_geocode_mx_sh.R".
# 
setwd( path.git )
source("prcp_mx.R")

#
setwd( path.git )
source("prcp2MMP.R")


