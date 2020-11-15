
# WARMEST DAY. It works for:
#   - Max temperature
#   - Min temperature
warmest_day = function(data, weather){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  t_max_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    # get MAX value of daily tmax.
    vals = apply(sub, 1, max)
    # add year values
    t_max_yearly = cbind(t_max_yearly, vals)
  }
  # update colnames
  colnames(t_max_yearly) = c("geocode", "state",
                             paste0("max_val-", weather,"-",years))
  return(t_max_yearly)
}


coldest_day = function(data, weather){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  t_max_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    # get MIN value of daily tmax.
    vals = apply(sub, 1, min)
    # add year values
    t_max_yearly = cbind(t_max_yearly, vals)
  }
  # update colnames
  colnames(t_max_yearly) = c("geocode", "state",
                             paste0("max_val-", weather,"-",years))
  return(t_max_yearly)
}



# Store
###################################
setwd(path.shapefiles)

# ANNUAL WARMEST DAY: Annual max value of daily max temperature
write.csv( x = warmest_day(data=tmax.mmp, weather="tmax"),
           file = "./mmp_data/warmest_day_mmp_1980-2017.csv", row.names = FALSE)

# ANNUAL COLDEST DAY: Annual min value of daily max temperature
write.csv( x = coldest_day(data=tmax.mmp, weather="tmax"),
           file = "./mmp_data/coldest_day_mmp_1980-2017.csv", row.names = FALSE)

# ANNUAL WARMEST NIGHT: Annual max value of daily min temperature	
write.csv( x = warmest_day(data=tmin.mmp, weather="tmin"),
           file = "./mmp_data/warmest_night_mmp_1980-2017.csv", row.names = FALSE)
