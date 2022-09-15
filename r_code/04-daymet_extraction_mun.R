# read MMP geo codes
setwd(path.git)
mmp = read.csv("../mmp.csv")
# make geocodes characters
mmp[,'geocode'] = as.character(mmp[,'geocode'])
# add 0 to geocodes of length == 8; otherwise, do not change
mmp[,'geocode'] = ifelse( nchar(mmp$geocode) == 8, 
                          paste0('0', mmp$geocode), mmp$geocode )

# get Mexican localities
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.mun = readOGR("./mexican_shapefiles/", layer='mx_mun')
# mx.mun = readOGR("./mexican_shapefiles/mx_sh", layer='mx01')
cat('Done!', '\n')


# add MUN geocode as a string
mx.mun@data[,"geo-mun"] = as.character(paste0(mx.mun$CVE_ENT,mx.mun$CVE_MUN))

# get all daymet folders
setwd(path.daymet)
daymet_folders = list.dirs(recursive = FALSE)

# time it
start = Sys.time()

# loop through each folder
for( folder in daymet_folders){
  
  # list all files inside folder
  all.files = list.files( folder )  
  
  # parallel computing setup
  cat("\n Starting parallel computing...")
  cores=detectCores()
  cl = makeCluster(cores-1) # to avoid overloading your computer
  registerDoParallel(cl)
  # add local path lo load libraries from (only if in sdl1)
  if(hostname=="sdl1") {
    clusterEvalQ(cl, .libPaths('/home/mm2535/R/x86_64-pc-linux-gnu-library'))
  }
  
  # loop over all files in the folder
  for(t in 1:length(all.files)){
  
    # initialize proj.r
    if(t==1) proj.r = ""
    
    cat('\n', 'Reading daymet file...', '\n')
    # read prcp as raster brick
    file.path = paste0(folder,'/',all.files[t])
    r = brick(file.path)
    
    # transform mx.loc.mmp only if projections are different.
    if( ! identical(proj.r, proj4string(r)) ) {
      # update projection
      proj.r = proj4string(r)
      # transform mx.loc.mmp 
      mx.mun.trans = sp::spTransform( mx.mun, proj.r )  
    }
    cat('Done!', '\n')
    
    # LOOP over all Mexican states
    ############################
    # get states
    # mx_pol = unique(mx.mun$CVE_ENT)
    # mx_pol = unique(mx.mun$CVEGEO)
    
    start = Sys.time()
    # test = mx.mun.trans
    df = foreach(m=1:nrow(mx.mun.trans), .combine=rbind, .packages=c("raster","rgdal","sp")) %dopar% {
      
      # subset polygon dataframe
      # sub = mx.mun.trans[m,]
      sub = mx.mun.trans[m,]
      
      # crop raster using extent of sub
      r_crop = raster::crop(r,extent(sub))
      
      # mask raster and get only values of interest
      r_mask = raster::rasterize(sub, r_crop, mask=TRUE)
      
      # retrieve values from raster: getValues is very fast!
      vals = na.omit(raster::getValues(r_mask))
      
      # take mean over 1x1 m2 within municipalities each weather col
      # means = colMeans(vals)
      
      (colMeans(vals))
    }
    stop = Sys.time()
    print(stop-start)
    
    # add municipality ID
    mun_id = as.character( mx.mun@data[,'geo-mun'] )
    df = as.data.frame(cbind(mun_id, df))
    rownames(df) = NULL
    
    # SAVE as csv file after visiting all files in one folder
    ############################
    year = sub('.*(\\d+{4}).*$','\\1',all.files[t])
    file.name = paste0('mx-mun_',sub('./','', folder), year, '.csv')
    print(file.name)
    write.csv(x=df, file=file.name, row.names=FALSE) #, append = TRUE)
    # fwrite(x=df, file=file.name) #, append = TRUE)
    cat('Done!', '\n\n') 
    
    # remove items
    rm(r, df)
    gc() # garbage collection
  }
  # stop parallel computing
  stopCluster(cl)
}

# stop timer (this task took 1.5 days)
stop = Sys.time()
stop - start



