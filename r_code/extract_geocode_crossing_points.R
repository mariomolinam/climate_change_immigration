#######################################################
# select right mx communities for MMP
#######################################################

setwd(path.ra_filiz)

# read MMP geo codes
cross_pts = read_xlsx("CrossingPlace_GPSInfo.xlsx")
cross_pts = as.data.frame(cross_pts)

# make geocodes characters
cross_pts[,'placename'] = as.character(cross_pts[,'placename'])
cross_pts = na.omit(cross_pts)

# add ", Mexico" to make calls to google maps
crossing_points_names = paste0(cross_pts$placename, ", Mexico")

# GOOGLE MAPS
#########################################
# use google maps to get crossing points at Mexican border
crossing_filename = "crossing_points.csv"
if( ! crossing_filename %in% list.files(path.ra_filiz)) {

  # get google api key
  myAPIkey = readLines("google.api")
  register_google(key = myAPIkey)
  
  # crosing points for Mexican border
  crossing_points = geocode(crossing_points_names, source="google")
  crossing_points = data.frame(placename=cross_pts[,'placename'], crossing_points)
  
  # save only if file doesn't exist
  write.csv(crossing_points, crossing_filename, row.names = FALSE)
} else{
  crossing_points = read.csv(crossing_filename)
}

# TRANSFORM TO SPATIAL POINTS (SP)
coordinates(crossing_points) =~ lon+lat

# projection used by GOOGLE MAPS
proj4string(crossing_points)=CRS("+init=epsg:4326")


# EXTRACT DAYMENT data
######################################################
# get all daymet folders
setwd(path.daymet)
daymet_folders = list.dirs(recursive = FALSE)

# loop through each folder
for( folder in daymet_folders){
  # list all files inside folder
  all.files = list.files( folder )  
  
  # loop over all files within folder
  for(t in 1:length(all.files)){
    
    # create R object that will store all daymet values
    geo.climate = data.frame(crossing_points@data)
    
    # initialize proj.r
    if(t==1) proj.r = ""
    
    cat('\n', 'Reading daymet file...', '\n')
    
    # read prcp as raster brick
    file.path = paste0(folder,'/',all.files[t]) 
    print(file.path)
    r = brick(file.path)
    
    # transform mx.loc.mmp only if projections are different.
    if( ! identical(proj.r, proj4string(r)) ) {
      
      # update projection
      proj.r = proj4string(r)
      
      # transform mx.loc.mmp 
      pts = spTransform( crossing_points,proj4string(r) )
    }
    # cat('Done!', '\n')
    
    # loop over all raster layers in the brick raster
    cat('\tLoop over all raster...', '\n')
    for(i in 1:nlayers(r)){
      val.cells = cellFromXY(r[[i]], coordinates(pts))
      values = as.data.frame( r[[i]][val.cells] )
      colnames(values) = names(r[[i]])
      # update 
      geo.climate = cbind(geo.climate, values )
    }
    # save as csv file after visiting all files in one folder
    year = sub('.*(\\d+{4}).*$','\\1',all.files[t])
    file.name = paste0('crossing_weather_',sub('./','', folder), year, '.csv')
    print(file.name)
    fwrite(x=geo.climate, file=file.name, append = TRUE)
    cat('Done!', '\n') 
  }
}



# 
# ####################################################
# # read ALL mexican localities
# setwd(path.shapefiles)
# cat('\n', 'Reading Mexican shapefiles...', '\n')
# mx.loc = readOGR(".", layer='mx_localities')
# cat('Done!', '\n')
# 
# # Keys Labels (in Spanish):
# #   CVE_ENT: CLAVE DE ENTIDAD
# #   CVE_LOC: CLAVE DE LOCALIDAD
# #   CVE_MUN: CLAVE DE MUNICIPIO
# #   CVE_AGEB: CLAVE DE AGEB
# #   CVE_GEO: CLAVE CONCATENADA
# 
# # create geocode by combining STATE (ENT), MUNICIPALITY (MUN), and LOCALITY (LOC) .
# handle.geocode = function(x){
#   rows = c("CVE_ENT", "CVE_MUN")
#   if(sum(is.na(x[rows])) == 0) paste0( x[rows][1], x[rows][2] )
#   else x["CVEGEO"]
# }
# cat('\n', 'Creating geocode...', '\n')
# mx.loc@data[,'geocode'] = apply(mx.loc@data, 1, function(x) handle.geocode(x)) 
# cat('Done!', '\n')
# 
# # save shapefile for MMP Mexican localities only
# mx_loc_crossing_points = subset(mx.loc, geocode %in% cross_pts[1:4,"Geo Code"])
# plot(mx_loc_crossing_points)
# 
# writeOGR(obj=mx_loc_crossing_points, dsn='.', layer='mx_municipalities_crossing_points', driver = 'ESRI Shapefile') 
