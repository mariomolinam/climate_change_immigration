setwd( path.daymet )

############################
# PRECIPITATION
prcp = list.files()[grep('mmp_prcp', list.files())]
d = fread(prcp[1])
prcp.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(p in prcp[-1]){
  print(p)
  d = fread(p)
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  prcp.mmp = merge(prcp.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with prcp data
setwd( path.shapefiles )
fwrite(prcp.mmp,file="mmp_w_prcp.csv")


############################
# MAX TEMPERATURE
tmax = list.files()[grep('mmp_tmax', list.files())]
d = fread(tmax[1])
tmax.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(t in tmax[-1]){
  print(t)
  d = fread(t)
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  tmax.mmp = merge(tmax.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmax data
setwd( path.shapefiles )
fwrite(tmax.mmp,file="mmp_w_tmax.csv")


############################
# MIN TEMPERATURE
tmin = list.files()[grep('mmp_tmin', list.files())]
d = fread(tmin[1])
tmin.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(t in tmin[-1]){
  print(t)
  d = fread(t)
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  tmin.mmp = merge(tmin.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmin data
setwd( path.shapefiles )
fwrite(tmin.mmp,file="mmp_w_tmin.csv")

