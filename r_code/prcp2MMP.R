# read MMP geo codes
setwd(path.ra_filiz)
mmp = read.csv("mmp_w_footprint.csv")
# make geocodes characters
mmp[,'geocode'] = as.character(mmp[,'geocode'])
# add 0 to geocodes of length == 8; otherwise, do not change
mmp[,'geocode'] = ifelse( nchar(mmp$geocode) == 8, paste0('0', mmp$geocode), mmp$geocode )


# set working directory
setwd(path.shapefiles)

# Extract human footprint info for MMP localities
mmp.mexican.localities = subset(mx.loc, geocode %in% mmp$geocode)
rm(mx.loc); gc()
# unique geocodes
unique.geo = unique(mmp.mexican.localities$geocode)

if( ! file.exists('mmp_prcp') ) dir.create('mmp_prcp')

# start timer
start = Sys.time()

# set tmp folder
rasterOptions(tmpdir="/tmp")

# run loop
for(g in 1:length(unique.geo)){
  # get geocode
  geo = unique.geo[g]
  cat('\n', 'Geocode:', geo, '\n')
  # deompose geocode in: ent, mun, loc
  ent = substr(geo,1,2)
  mun = substr(geo,3,5)
  loc = substr(geo,6,9)
  
  # go parallel at every geocode
  no_cores = detectCores() - 1
  cl = makeCluster(no_cores)
  clusterEvalQ(cl, c(library(sp), library(raster)) )
  
  
  # create new folder where to store data
  geo_folder_path = 'mmp_prcp/'

   # use ent to find human footprint data at the state-level
  folder = paste0("mx",ent)
  path2folder = paste0(path.shapefiles, 'state_level_prcp/', folder)
  files = list.files(path2folder)
  files.tif = files[-grep('.aux', files)]
  
  # subset mx.loc and send to cluster nodes 
  mx.loc.subset = subset(mmp.mexican.localities, geocode == geo)
  data.raster = parLapply(cl, paste0(path2folder,"/", files.tif), brick)
  # transform to raster projection
  clusterExport(cl, c("mx.loc.subset"))
  mx.loc.trans = parLapply(cl, data.raster, function(x) spTransform( mx.loc.subset, proj4string(x) ) ) 
  
  # combine o and mx.loc.trans
  combine_objs = list() 
  for(item in 1:length(data.raster)) {
    combine_objs[[item]] = c(data.raster[[item]], mx.loc.trans[[item]]) 
  }

  # extract values for geocode (normalize weights so that they contribute as much as they should)
  cat('\n', 'Extracting values with normalized weights...', '\n')
  values = parLapply(cl, combine_objs, 
                     function(x) {
                      raster::extract(x[[1]], x[[2]], method='bilinear', na.rm=TRUE, weights=TRUE, normalizeWeights=TRUE, small=TRUE )
                    }  )
  cat('Done!', '\n')
  
  
  # function that adds id to values
  add.id = function(x){
    for(val in 1:length(x)) x[[val]] = cbind(x[[val]], id=val)
    return(x)
  }
  # add id to values
  values.id = parLapply(cl, values, add.id)
  # convert each item of list in dataframe 
  values.df = parLapply( cl, values.id, function(x) {
    output = as.data.frame( do.call(rbind, x) )
    return(output) } )
  
  values.weighted = parLapply(cl, values.df, function(x){
    # create weighted values by looping through columns. This process is fast because it
    # uses matrix operations (i.e. I don't loop through rows)
    pos.id = grep('id', names(x))
    pos.w = grep('weight', names(x))
    values.names = names(x)[ -c(pos.id,pos.w) ]
    # loop through columns
    for(name in values.names){
      new.col = paste0(name, '_weighted')
      x[,new.col] = x[,name] * x[,'weight']
    }
    names.agg = names(x)[grep('_weighted', names(x))]
    # weighted sum of prcp values
    values.agg = aggregate( x[,names.agg], by=list(x$id), function(col) sum(col) )
    return(values.agg[,-1])
  })
  
  # combine objects
  mx.combine = list() 
  for(item in 1:length(mx.loc.trans)) {
    mx.combine[[item]] = list( mx.loc.trans[[item]], values.weighted[[item]]) 
  }
  
  # add weighted data to mx data
  output = parLapply(cl, mx.combine, function(x){
    x[[1]]@data = cbind(x[[1]]@data, x[[2]])
    return(x[[1]])
  })
  
  # save values as rds
  filename = paste0('geo_',geo,'.rds')
  filepath = paste0(geo_folder_path, filename)
  saveRDS( output, filepath )
  
  # create column names only during first file
  names.prcp.all = sapply(output, function(x) {
    names.out = names(x)[grep("_weighted", names(x))]
    return(names.out)
  } )
  
  if(g == 1) mmp[,names.prcp.all] = NA
  
  # add values to mmp
  values.mean = sapply( values.weighted, function(x) {
    apply(x, 2, mean)
  })
  
  mmp[mmp$geocode == geo, names.prcp.all] = values.mean

  # stop cluster
  stopCluster(cl)
    
  # remove some heavy objects and call garbage collector
  rm(values, values.df, values.id, 
     values.mean, values.weighted, mx.combine, 
     output, combine_objs, mx.loc.subtopset, mx.loc.trans,
     data.raster)
  gc()
}

stop = Sys.time()
print(stop - start)




