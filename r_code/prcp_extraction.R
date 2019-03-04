# read MMP geo codes
setwd(path.ra_filiz)
mmp = read.csv("mmp_w_footprint.csv")
# make geocodes characters
mmp[,'geocode'] = as.character(mmp[,'geocode'])
# add 0 to geocodes of length == 8; otherwise, do not change
mmp[,'geocode'] = ifelse( nchar(mmp$geocode) == 8, paste0('0', mmp$geocode), mmp$geocode )


# get Mexican localities
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.loc.mmp = readOGR(".", layer='mx_localities_mmp')
cat('Done!', '\n')

# get all daymet folders
setwd(path.daymet)
daymet_folders = list.files()

# time it
start = Sys.time()

# create csv file storing climate information (based on geocode)
geo.climate = as.character( mx.loc.mmp@data[,'geocode'] )

# loop through each folder
for( folder in daymet_folders){
  full.path = paste0(path.daymet, '/', folder)
  all.files = list.files( full.path )  
  
# loop over all files within folder
  for(t in 1:length(all.files)){
    # initialize proj.r
    if(t==1) proj.r = ""
    
    cat('\n', 'Reading prcp file...', '\n')
    # read prcp as raster brick
    r = brick(all.files[t])
    # transform mx.loc.mmp only if projections are different.
    if( ! identical(proj.r, proj4string(r)) ) {
      # update projection
      proj.r = proj4string(r)
      # transform mx.loc.mmp 
      mx.loc.mmp.trans = spTransform( mx.loc.mmp, proj.r )  
    }
    cat('Done!', '\n')
    
    # loop over all raster layers in the brick raster
    cat('Loop over all raster...', '\n')
    mx.coor = coordinates(mx.loc.mmp.trans)
    for(i in 1:nlayers(r)){
      print(i)
      val.cells = cellFromXY(r[[i]], mx.coor)
      val.prcp = as.data.frame( r[[i]][val.cells] )
      colnames(val.prcp) = names(r[[i]])
      geo.climate = cbind(geo.climate, val.prcp )
      
      # mx.loc.mmp.trans@data[,names(r[[i]])] = val.prcp
    }
    cat('Done!', '\n')
  }
  # save as csv file after visiting all files in one folder
  write.csv(geo.climate, 'mmp_all_daymet.csv')
  
}

# stop timer
stop = Sys.time()
stop - start

