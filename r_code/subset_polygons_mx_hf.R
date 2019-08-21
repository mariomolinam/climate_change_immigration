################################################################
# read human footprint data and construct and multiraster object
setwd(path.footprint)
tif.files = list.files()[ grep(".tif$", list.files()) ]
raster = list()
for( i in 1:length(tif.files) ){
  raster[[i]] = raster(tif.files[i], layer=i)
}
# stack raster together
raster_layers = stack(unlist(raster))

################################################################
# shapefiles for Mexican STATES (not localities)
setwd(path.shapefiles)

# create directory if it doesn't exist
if( ! file.exists('state_level_footprints') ) dir.create('state_level_footprints')
# all zip files
all.files = list.files(pattern='.zip') # only zip files

for(i in 1:length(all.files)){
  cat('\n', '########################################################')
  # file name
  file.name = all.files[i] 
  cat('\n', file.name, '\n\n')  # print
  # unzip file
  files = unzip(file.name, exdir='tmp_folder')   
  conjunto = list.files(tmp)[ grep('conjunto', list.files(tmp)) ]
  # build path to tmp folder
  build_path = paste0("tmp_folder/",conjunto, '/.') 
  # extract file pattern to unzip
  pattern = paste0( substr(file.name, 1,2), 'ent' ) # 'a' excluded
  
  # read state shapefile
  # f.read = readOGR(dsn = build_path, layer = pattern)
  f.read = st_read(dsn = build_path, layer = pattern)
  
  
  # ESPG code that matches human footprint: "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"
  # I got this ESPG code from the internet: http://faculty.baruch.cuny.edu/geoportal/resources/practicum/gisprac_2017july_fd.pdf
  mx.new.crs = st_transform(f.read, 54009)
  # mx.new.crs = spTransform(f.read, "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs") 
  
  # extract subset of the raster
  mx.pol = as(extent(mx.new.crs),'SpatialPolygons')
  number = substr(all.files[i], 1,2)
  name = paste0("state_level_footprints/",number,"_hf")
  foot.new.raster = crop( raster_layers, filename=name, mx.pol, snap="in", overwrite=TRUE)
  
  # save as RDS
  filepath = paste0("state_level_footprints/",number,"_hf.rds")
  saveRDS(foot.new.raster,filepath)
  
  # delete tmp folder
  unlink('tmp_folder/', recursive = TRUE)
}




