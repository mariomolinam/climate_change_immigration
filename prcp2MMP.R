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
for(g in 1:length(unique.geo)){
  # get geocode
  geo = unique.geo[g]
  cat('\n', 'Geocode:', geo, '\n')
  # deompose geocode in: ent, mun, loc
  ent = substr(geo,1,2)
  mun = substr(geo,3,5)
  loc = substr(geo,6,9)
  
  # create new folder where to store data
  geo_folder_name = paste0('geo_',geo)
  geo_folder_path = paste0('mmp_prcp/',geo_folder_name)
  if( ! file.exists(geo_folder_path) ) dir.create(geo_folder_path)
  
  # use ent to find human footprint data at the state-level
  folder = paste0("mx",ent)
  path2folder = paste0(path.shapefiles, 'state_level_prcp/', folder)
  files = list.files(path2folder)
  for(f in files){
    # load year raster
    data.raster = readRDS( paste0(path2folder,"/",f)  )  
    
    # subset mx.loc 
    mx.loc.subset = subset(mmp.mexican.localities, geocode == geo)
    mx.loc.trans = spTransform( mx.loc.subset, proj4string(data.raster) ) 
    
    # extract values for geocode (normalize weights so that they contribute as much as they should)
    cat('\n', 'Extracting values with normalized weights...', '\n')
    values = raster::extract(data.raster, mx.loc.trans, method='bilinear', na.rm=TRUE, weights=TRUE, normalizeWeights=TRUE, small=TRUE)
    cat('Done!', '\n')
    
    # compute average for the geocode area
    # add column identifier (because some lsit entries have more than 1 row)
    for(val in 1:length(values)) values[[val]] = cbind(values[[val]], id=val)
    # create data frame with values
    values.df = as.data.frame( do.call(rbind, values) )
    
    # create weighted values by looping through columns. This process is fast because it
    # uses matrix operations (i.e. I don't loop through rows)
    pos.id = grep('id', names(values.df))
    pos.w = grep('weight', names(values.df))
    values.names = names(values.df)[-c(pos.id,pos.w)]
    for(name in values.names){
      new.col = paste0(name, '_weighted')
      values.df[,new.col] = values.df[,name] * values.df[,'weight']
    }
    
    # aggregate by id using a weighted mean
    names.agg = names(values.df)[grep('_weighted', names(values.df))]
    values.agg = aggregate( values.df[,names.agg], by=list(values.df$id), function(x) sum(x) )
    
    mx.loc.trans@data = cbind(mx.loc.trans@data, values.agg[,names.agg])
    
    # get year
    chunk1 = sub("(^.*_)","", f)
    year = sub("[.].*","", chunk1) 
    
    # save values as rds
    filename = paste0('geo_',geo, '_', year,'.rds')
    filepath = paste0(geo_folder_path, '/', filename)
    saveRDS( mx.loc.trans, filepath )
    
    # create column names only during first file
    if(g == 1) mmp[,names.agg] = NA
    
    # add values to mmp
    values.mean = apply(values.agg[,names.agg], 2, mean)
    mmp[mmp$geocode == geo, names(values.mean)] = values.mean
    
  }
}

stop = Sys.time()
print(stop - start)
