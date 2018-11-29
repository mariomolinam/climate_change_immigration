#######################################################
# select right mx communities for MMP
#######################################################

# read MMP geo codes
setwd(path.ra_filiz)
mmp = read_xlsx("MMP161_community_identifiers_with_complete_geocodes-1.xlsx")
mmp = mmp[1:161,] # remove tail
mmp = as.data.frame(mmp)

# make geocodes characters
mmp[,'geocode'] = as.character(mmp[,'geocode'])
# add 0 to geocodes of length == 8; otherwise, do not change
mmp[,'geocode'] = ifelse( nchar(mmp$geocode) == 8, paste0('0', mmp$geocode), mmp$geocode )

####################################################
# read ALL mexican localities
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.loc = readOGR(".", layer='mx_localities')
cat('Done!', '\n')

# Keys Labels (in Spanish):
#   CVE_ENT: CLAVE DE ENTIDAD
#   CVE_LOC: CLAVE DE LOCALIDAD
#   CVE_MUN: CLAVE DE MUNICIPIO
#   CVE_AGEB: CLAVE DE AGEB
#   CVE_GEO: CLAVE CONCATENADA

# create geocode by combining STATE (ENT), MUNICIPALITY (MUN), and LOCALITY (LOC) .
handle.geocode = function(x){
  rows = c("CVE_ENT", "CVE_MUN", "CVE_LOC")
  if(sum(is.na(x[rows])) == 0) paste0( x[rows][1], x[rows][2], x[rows][3] )
  else x["CVEGEO"]
}
cat('\n', 'Creating geocode...', '\n')
mx.loc@data[,'geocode'] = apply(mx.loc@data, 1, function(x) handle.geocode(x)) 
cat('Done!', '\n')

# get missing geocodes
missing.geo = mmp$geocode[ ! mmp$geocode %in% mx.loc@data$geocode ]
if( length(missing.geo) > 0 ) cat('\n', 'Missing geocodes:', missing.geo, '\n') 


##########################################################################
# Extract human footprint info for MMP localities
mmp.mexican.localities = subset(mx.loc, geocode %in% mmp$geocode)
# unique geocodes
unique.geo = unique(mmp.mexican.localities$geocode)

if( ! file.exists('mmp_footprint') ) dir.create('mmp_footprint')

# add columns of average weighted human footprints 
mmp[,c("Built1994_weighted","Built2009_weighted","croplands1992_weighted","croplands2005_weighted",
       "HFP1993_int_weighted", "HFP1993_weighted","HFP2009_int_weighted", "HFP2009_weighted",
       "Lights1994_weighted","Lights2009_weighted","NavWater1994_weighted","NavWater2009_weighted",
       "Pasture1993_weighted","Pasture2009_weighted","Popdensity1990_weighted","Popdensity2010_weighted",
       "Railways_weighted", "Roads_weighted")] = NA

for(g in 1:length(unique.geo)){
  # get geocode
  geo = unique.geo[g]
  cat('\n', 'Geocode:', geo, '\n')
  # deompose geocode in: ent, mun, loc
  ent = substr(geo,1,2)
  mun = substr(geo,3,5)
  loc = substr(geo,6,9)
  
  # use ent to find human footprint data at the state-level
  folder = paste0(path.shapefiles, 'state_level_footprints/')
  file = paste0(ent,'_hf.rds')
  data.raster = readRDS( paste0(folder, file)  )
  
  # subset mx.loc 
  mx.loc.subset = subset(mmp.mexican.localities, geocode == geo)
  proj = proj4string(data.raster)
  mx.loc.trans = spTransform(mx.loc.subset, proj) 
  
  # extract values for geocode (normalize weights so that they contribute as much as they should)
  cat('\n', 'Extracting values with normalized weights...', '\n')
  values = extract(data.raster, mx.loc.trans, method='bilinear', na.rm=TRUE, weights=TRUE, normalizeWeights=TRUE)
  cat('Done!', '\n')
  # compute average for the geocode area
  # add column identifier (because some lsit entries have more than 1 row)
  for(val in 1:length(values)) values[[val]] = cbind(values[[val]], id=val)
  # create data frame with values
  values.df = as.data.frame( do.call(rbind, values) )
  # create weighted values by looping through columns. This process is fast because it
  # uses matrix operations (i.e. I don't loop through rows)
  for(name in names(values.df)[1:18]){
    new.col = paste0(name, '_weighted')
    values.df[,new.col] = values.df[,name] * values.df[,'weight']
  }
  # aggregate by id using a weighted mean
  names.agg = names(values.df)[grep('_weighted', names(values.df))]
  values.agg = aggregate(values.df[,names.agg], by=list(values.df$id), function(x) sum(x)  )
  
  mx.loc.trans@data = cbind(mx.loc.trans@data, values.agg[,names.agg])
  
  filename = paste0('geo_',geo,'.rds')
  filepath = paste0('mmp_footprint/', filename)
  saveRDS( mx.loc.trans, filepath )
  
  # add values to mmp
  values.mean = apply(values.agg[,names.agg], 2, mean)
  mmp[mmp$geocode == geo, names(values.mean)] = values.mean
  
}

# save mmp with human footprint data
setwd(path.ra_filiz)
write.csv(mmp, 'mmp_w_footprint.csv', row.names=FALSE)



