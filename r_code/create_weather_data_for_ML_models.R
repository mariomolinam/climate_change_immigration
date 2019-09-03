# 
setwd(path.git)
source("./r_code/functions_weather_data_for_ML_models.R")

###########################################################################
######################### W E A T H E R
# R E A D   D A T A
########################################################################
setwd( path.shapefiles )
prcp.mmp = as.data.frame(fread("./mexican_shapefiles/mmp_w_prcp.csv"))
tmax.mmp = as.data.frame(fread("./mexican_shapefiles/mmp_w_tmax.csv"))
env = read.dta("./mmp_data/environs.dta")


#  C R E A T E   D A T A   F O R   M L   M O D E L S
###############################################################
setwd(path.shapefiles)
# 1. CRUDE PRCP
write.csv( x = crude_weather_yearly(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/crude_raw_prcp_monthly-average_mmp_1980-2017.csv", row.names = FALSE)

# 2. CRUDE TMAX: raw temperature
write.csv( x = crude_weather_yearly(data=tmax.mmp, weather="tmax", operation="mean"),
           file = "./mmp_data/crude_raw-tmax_monthly-average_mmp_1980-2017.csv", row.names = FALSE)

# 3. CRUDE TMAX: number of days > 30
write.csv( x = crude_weather_yearly(data=tmax.mmp, weather="tmax", operation="above30"),
          file = "./mmp_data/crude_above30-tmax_monthly-average_mmp_1980-2017.csv", row.names = FALSE)

# 4. NORM DEVIATION, LONG-TERM NORM 1960-1979: precipitation
write.csv( x = long_term_norm_deviation(data=prcp.mmp, data_historic=env, weather="prcp"),
           file = "./mmp_data/norm_deviation_longterm_mmp_1980-2017.csv", row.names = FALSE)

# 5. NORM DEVIATION, SHORT-TERM NORM 1980-1984: precipitation
write.csv( x = short_term_norm_deviation(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/norm_deviation_short-term_prcp_mmp_1985-2017.csv", row.names = FALSE)

# 6. NORM DEVIATION, SHORT-TERM NORM 1980-1984: tmax
write.csv( x = short_term_norm_deviation(data=tmax.mmp, weather="tmax", operation="above30"),
           file = "./mmp_data/norm_deviation_short-term_tmax_mmp_1985-2017.csv", row.names = FALSE)

# 7. NORM PERCENT, SHORT-TERM NORM 1980-1984: prcp
write.csv( x = short_term_norm_percent(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/norm_percent_short-term_prcp_mmp_1985-2017.csv", row.names = FALSE)

# 8. NORM PERCENT, SHORT-TERM NORM 1980-1984: tmax
write.csv( x = short_term_norm_percent(data=tmax.mmp, weather="tmax", operation="above30"),
           file = "./mmp_data/norm_percent_short-term_tmax_mmp_1985-2017.csv", row.names = FALSE)

# 9. WARM SPELLS: NUMBER OF TIMES THERE ARE 6 CONSECUTIVES DAYS WITH TEMPERATURE > SHORT NORM 1980-1984
write.csv( x = warm_spells(data=tmax.mmp, weather="tmax", operation="mean"),
           file = "./mmp_data/warm_spell_tmax_mmp_1985-2017.csv", row.names = FALSE)
