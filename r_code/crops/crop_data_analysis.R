# set working directory and file name
setwd(path.shapefiles)
file = paste0("Mexico crop data/Agt_cierre_80_16_Filiz.csv")

# read data
crop = read.csv(file)

# DELETE LINE (AND THIS COMMENT) WHEN FINISHED
colnames(crop)


### G E O C O D E
#################################################
# create geocode key for State and Municipality

# State
est = as.character(crop$CveEstado)
est = ifelse(nchar(est)==1, paste0("0",est), est)

# Municipality
mun = as.character(crop$CveMpio)
mun = ifelse(nchar(mun)==1, paste0("00",mun),
             ifelse(nchar(mun)==2, paste0("0",mun), mun))

crop[,"geocode"] = paste0(est,mun)

# When municipality is unknown, we will use state ID.
crop[,"geocode"] = ifelse(crop$Municipio=="no determinado" | mun=="000", est, crop$geocode)


### R A N K   T O P   C R O P S
#################################################
# sort by 1) geocode and then by 2) year
crop_test = crop[order(crop$geocode, crop$YearAgricola),]

# Produccion as numeric
volume_crops = gsub(",","",as.character(crop_test$Produccion))

crop_test[,"Produccion"] = as.numeric(volume_crops)
crop_test[,"new.crop"] = as.character(crop_test[,"new.crop"])


### R E N A M E   C R O P S   W I T H   C O M M O N   N A M E S
#################################################
# group same crops by names summing up: Produccion, Sembrada, Cosechada, Rendimiento, Valor
crop_common = aggregate( cbind(Produccion, Sembrada, Cosechada, Rendimiento, Valor) ~
                           geocode + YearAgricola + new.crop,
                  data=crop_test, FUN=sum )

# sort by Produccion (descending)
crop_common = crop_common[ order(crop_common$geocode,        # ascending
                                 crop_common$YearAgricola,   # ascending
                                -crop_common$Produccion),    # descending
                           ]

# remove crop with names "otros" or "otro"
crop_common = crop_common[-grep("otro",crop_common$new.crop),]

# select crops with highest VOLUME (by geocode and by year)
crop_vol = aggregate(Produccion ~ geocode + YearAgricola, data=crop_common, FUN=max)

# merge using "geocode", "YearAgricola", "Produccion" with crop_common to obtain crop names
crop_vol = merge(crop_vol,crop_common[,c("geocode","YearAgricola", "Produccion","new.crop")],
                 by=c("geocode","YearAgricola", "Produccion"))

# save top crops as csv file
setwd(path.shapefiles)
top_crops = data.frame(crops=names(table(crop_vol$new.crop)))
write.csv(top_crops, file="top_crops_by_volume.csv",row.names = FALSE)

### C R O P S   F O R   M M P   C O M M U N I T I E S / S T A T E S
#################################################
# select only crops that are relevant for MMP communities or states

# get MMP geocodes and convert them to state and community level
setwd(path.shapefiles)
mmp_geocode = fread("./mexican_shapefiles/mmp_w_prcp.csv", select=c("geocode"), colClasses=c("character"))

mmp_geocode[,"geocode"] = ifelse( nchar(mmp_geocode$geocode)==8,
                                    paste0("0",mmp_geocode$geocode), mmp_geocode$geocode)
# distinguish between state- and community-level geocodes
mmp_geocode[,"est_geo"] = substr(mmp_geocode$geocode, 1, 2)
mmp_geocode[,"mun_geo"] = substr(mmp_geocode$geocode, 1, 5)

# combine unique geocodes for state- and municipality-level
mmp_geocode_unique = c(unique(mmp_geocode$est_geo),unique(mmp_geocode$mun_geo))
# obtain only crops that are relevant for MMP communities
top_crops_mmp = crop_vol[crop_vol$geocode %in% mmp_geocode_unique,]

# save top crops as csv file
setwd(path.shapefiles)
top_crops = data.frame(CROPS=unique(top_crops_mmp$new.crop))
write.csv(top_crops, file="top_crops_by_volume_MMP.csv",row.names=FALSE)


##################################################################################################
# NEW CODE ADDED AFTER COLLECTING INFORMATION ON TOP CROPS (harvest date)
##################################################################################################

# set working directory and load data
setwd(path.shapefiles)
# crop_info = fread("./Mexico crop data/top_crops_by_volume_complete_v1.csv")
crop_info = read_excel("./Mexico crop data/top_crops_by_volume_complete_v3.xlsm")
if(!is.data.table(crop_info)) crop_info = as.data.table(crop_info)

# remove empty rows
crop_info = crop_info[Crop!="" | !is.na(Crop)]

# remove rows for which info is still being collected
crop_info = crop_info[!(month_harvested=="" | month_harvested=="NA"), c("Crop","month_harvested", "temp_celcius","rain_annual_mm")]

# min max temp
extract_info = function(x, min_max){
  if(min_max=="min") pos = 1 else pos = 2
  out = strsplit(x, "-")
 lapply(out, function(x) x[pos])
}

# min temp and rain
crop_info[,c("temp_min", "rain_min") := lapply(.SD, function(x) extract_info(x,"min")), .SDcols=c("temp_celcius","rain_annual_mm")]


# max temp and rain
crop_info[,c("temp_max", "rain_max") := lapply(.SD, function(x) extract_info(x,"max")), .SDcols=c("temp_celcius","rain_annual_mm")]


# merge data using crop name
crop_all = merge(crop_vol, crop_info, by.x="new.crop",by.y="Crop", all.x=TRUE)

# sort data by geocode and year
crop_sorted = crop_all[ order(crop_all$geocode, crop_all$YearAgricola), ]

# write dataset
setwd(path.shapefiles)
fwrite(crop_sorted, file="./Mexico crop data/top_crops_sorted_w_info.csv",row.names = FALSE)
