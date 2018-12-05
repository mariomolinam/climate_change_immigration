# set working directory 
setwd(path.shapefiles)

# directory where new files will be stored
store.dir = paste0(path.shapefiles, 'state_level_prcp/')

# Get all shapefiles for Mexican states
path.mx_sh = paste0(path.shapefiles, 'mx_sh/.')
all.states = list.files(path.mx_sh)
mx_sh.unique = unique(sub("[.].+", "", all.states))
mx_sh.unique = mx_sh.unique

# get all years for prcp files
prcp.years = as.character(seq(1980, 2017,1))

# loop over every Mexican state
for(st in mx_sh.unique){
  
  cat('\n', 'State:', st, '\n\n')
  
  # read shapefile for Mexican state
  mx = readOGR(path.mx_sh, layer = st)
  
  # create directory for Mexican state
  new.dir = paste0(store.dir,st)
  if( ! file.exists(new.dir) ) dir.create(new.dir)
  
  # loop over every prcp file (from 1981-2017)
  for(y in prcp.years){
    cat('Year:', y, '\n')
    # build prcp file name 
    start = "daymet_v3_prcp_"
    year = y
    tail = "_na.nc4"
    f = paste0(start,year,tail)
    path_to_f = paste0(path.prcp,'/',f)
    
    # load raster brick
    r = brick(path_to_f, varname='prcp') # read file as brick for multiple layers
    # get projection of brick raster
    proj = projection(r)
    # reproject mx state 
    r.proj = spTransform( mx, CRSobj=proj )
    # extract precipitation information for Mexican state only
    prcp.mx = crop(r, extent(r.proj) )
    
    # store prcp file
    prcp.mx.path = paste0(new.dir, '/', st,'_', y,".tif")
    outfile = writeRaster(prcp.mx, filename=prcp.mx.path, format="GTiff", overwrite=TRUE,options=c("INTERLEAVE=BAND","COMPRESS=LZW"))
    # saveRDS(object=prcp.mx, file=prcp.mx.path)
    
    # remove files and run garbage collector
    rm(r, r.proj, prcp.mx, outfile); gc()
  }
  # remove files and run garbage collector
  rm(mx); gc()
}




# plot(prcp.mx[['X1980.01.02']])
# plot(r.proj, add=T)
