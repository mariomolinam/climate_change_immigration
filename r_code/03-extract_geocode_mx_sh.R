#######################################################
# select right mx communities for MMP
#######################################################

# read MMP geo codes
setwd(path.git)
mmp = read_xlsx("../MMP161_community_identifiers_with_complete_geocodes-2.xlsx")
mmp = mmp[1:170,] # remove tail from xlsx file
mmp = as.data.frame(mmp)

# turn geocodes into characters
class(mmp[,'geocode']) = "character"
# add 0 to geocodes of length == 8; otherwise, do not change
mmp[,'geocode'] = ifelse( nchar(mmp$geocode) == 8, paste0('0', mmp$geocode), mmp$geocode )

# REPLACE "lost" geocodes 
#     NOTE: some geocodes in the MMP data do not match the geocodes in
#         Mexican shapefiles, so they need to be corrected. For privacy reasons, 
#         we cannot show those geocodes
lost_geo_old = read.table("03-1-lost_geocodes_mmp_old.txt")
lost_geo_new = read.table("03-2-lost_geocodes_mmp_new.txt")

# we need characters
class(lost_geo_old[,1]) = "character"
class(lost_geo_new[,1]) = "character"

mmp[mmp$geocode==lost_geo_old[1,],"geocode"] = lost_geo_new[1,]
mmp[mmp$geocode==lost_geo_old[2,],"geocode"] = lost_geo_new[2,]
mmp[mmp$geocode==lost_geo_old[3,],"geocode"] = lost_geo_new[3,]
mmp[mmp$geocode==lost_geo_old[4,],"geocode"] = lost_geo_new[4,]


####################################################
# read ALL mexican localities
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.loc = readOGR("./mexican_shapefiles/.", layer='mx_localities')
cat('Done!', '\n')

# Keys Labels (in Spanish):
#       CVE_ENT:  CLAVE DE ENTIDAD
#       CVE_LOC:  CLAVE DE LOCALIDAD
#       CVE_MUN:  CLAVE DE MUNICIPIO
#       CVE_AGEB: CLAVE DE AGEB
#       CVE_GEO:  CLAVE CONCATENADA

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

# save shapefile for MMP Mexican localities only
mx.loc.mmp = subset(mx.loc, geocode %in% mmp$geocode)
writeOGR(obj=mx.loc.mmp, dsn='.', layer='mx_localities_mmp', driver = 'ESRI Shapefile') 

# save MMP data with new geocodes
setwd(path.git)
write.csv(mmp, file="../mmp.csv", row.names=FALSE)

