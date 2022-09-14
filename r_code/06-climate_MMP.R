# setwd( path.daymet )
setwd( path.shapefiles)

########################################################
# PRECIPITATION (MMP)
prcp = list.files("./daymet")[grep('mmp_prcp', list.files("./daymet"))]
d = fread( paste0("./daymet/", prcp[1]) )
prcp.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(p in prcp[-1]){
  print(p)
  d = fread(paste0("./daymet/", p))
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  prcp.mmp = merge(prcp.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with prcp data
setwd( path.shapefiles )
fwrite(prcp.mmp,file="./daymet/mmp_w_prcp.csv")

############################

# PRECIPITATION (MX MUN)
prcp = list.files("./daymet")[grep('mun_prcp', list.files("./daymet"))]
d = fread( paste0("./daymet/", prcp[1]) )
prcp.mun = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  

for(p in prcp[-1]){
  print(p)
  d = fread(paste0("./daymet/", p))
  d.agg = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  
  prcp.mun = merge(prcp.mun, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with prcp data
setwd( path.shapefiles )
fwrite(prcp.mun,file="./daymet/mx-mun_w_prcp.csv")

########################################################
# MAX TEMPERATURE (MMP)
tmax = list.files("./daymet")[grep('mmp_tmax', list.files("./daymet"))]
d = fread(paste0("./daymet/", tmax[1]))
tmax.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(t in tmax[-1]){
  print(t)
  d = fread(paste0("./daymet/", t))
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  tmax.mmp = merge(tmax.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmax data
setwd( path.shapefiles )
fwrite(tmax.mmp,file="./daymet/mmp_w_tmax.csv")

############################

# MAX TEMPERATURE (MUN)
tmax = list.files("./daymet")[grep('mun_tmax', list.files("./daymet"))]
d = fread(paste0("./daymet/", tmax[1]))
tmax.mun = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  

for(t in tmax[-1]){
  print(t)
  d = fread(paste0("./daymet/", t))
  d.agg = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  
  tmax.mun = merge(tmax.mun, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmax data
setwd( path.shapefiles )
fwrite(tmax.mun,file="./daymet/mx-mun_w_tmax.csv")


########################################################
# MIN TEMPERATURE (MMP)
tmin = list.files("./daymet")[grep('mmp_tmin', list.files("./daymet"))]
d = fread(paste0("./daymet/", tmin[1]))
tmin.mmp = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  

for(t in tmin[-1]){
  print(t)
  d = fread(paste0("./daymet/", t))
  d.agg = aggregate(d[,2:dim(d)[2]], by=list(geocode=d$geo.climate), function(x) mean(x))  
  tmin.mmp = merge(tmin.mmp, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmin data
setwd( path.shapefiles )
fwrite(tmin.mmp,file="./daymet/mmp_w_tmin.csv")

############################

# MIN TEMPERATURE (MUN)
tmin = list.files("./daymet")[grep('mun_tmin', list.files("./daymet"))]
d = fread(paste0("./daymet/", tmin[1]))
tmin.mun = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  

for(t in tmin[-1]){
  print(t)
  d = fread(paste0("./daymet/", t))
  d.agg = aggregate(d[,2:ncol(d)], by=list(geocode=d$mun_id), function(x) mean(x))  
  tmin.mun = merge(tmin.mun, d.agg, by='geocode')
  rm(d, d.agg); gc()
}

# save mmp geocodes with tmin data
setwd( path.shapefiles )
fwrite(tmin.mun,file="./daymet/mx-mun_w_tmin.csv")

