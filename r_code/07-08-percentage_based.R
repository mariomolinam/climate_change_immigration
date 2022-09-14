
# COMPUTE SHORT-TERM NORM (1980-1984)
short_term_norm = function(data, weather, operation){
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years.query = paste(1980:1984,collapse="|")
  years.ids = grep(years.query,colnames(weather_monthly))
  
  # norm mean and sd
  norm_mean = rowMeans( weather_monthly[,years.ids] )
  norm_sd = apply( weather_monthly[,years.ids], 1, sd )
  
  # get short term norm
  shortterm_norm = cbind(state=mmp_st_names, norm_mean=norm_mean, norm_sd=norm_sd)
  
  return(shortterm_norm)
}


# PERCENTAGE OF WARMEST NIGHTS
perc_warmest_nights = function(data, weather){
  
    # select years of norm and compute 90th quantile
    weather_norm = data[,grep("1980|1981|1982|1983|1984", colnames(data))]
    norm_90th = apply(weather_norm, 1, function(x) quantile(x, probs=0.9) )
    
    # state names and add norm
    mmp_st_names = mmp_state_names(data)
    
    # define dataframe
    warmest_nights_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
    
    # loop over years 1985-2017
    years = as.character(1985:2017)
    for(y in years){
      # subset data
      sub = data[,grep(y, colnames(data))]
      # sums number of days above 90th quantile of norm 1980-1984
      total_warm_nights = rowSums(sub > norm_90th) / ncol(sub)
      
      # add year values
      warmest_nights_yearly = cbind(warmest_nights_yearly, total_warm_nights)
    }
    # update colnames
    colnames(warmest_nights_yearly) = c("geocode", "state",
                                         paste0("warm_night-", weather,"-",years))
    
    return(warmest_nights_yearly)
}


# PERCENTAGE OF COLD NIGHTS
perc_cold_nights = function(data, weather){
  
  # select years of norm and compute 90th quantile
  weather_norm = data[,grep("1980|1981|1982|1983|1984", colnames(data))]
  norm_10th = apply(weather_norm, 1, function(x) quantile(x, probs=0.1) )
  
  # state names and add norm
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  cold_nights_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years 1985-2017
  years = as.character(1985:2017)
  for(y in years){
    # subset data
    sub = data[,grep(y, colnames(data))]
    # sums number of days above 10th quantile of norm 1980-1984
    total_cold_nights = rowSums(sub < norm_10th) / ncol(sub)
    
    # add year values
    cold_nights_yearly = cbind(cold_nights_yearly, total_cold_nights)
  }
  
  # update colnames
  colnames(cold_nights_yearly) = c("geocode", "state",
                                      paste0("cold_night-", weather,"-",years))
  
  return(cold_nights_yearly)
}


# PERCENTAGE OF COLD DAYS
perc_cold_days = function(data, weather){
  
  # select years of norm and compute 10th quantile
  weather_norm = data[,grep("1980|1981|1982|1983|1984", colnames(data))]
  norm_10th = apply(weather_norm, 1, function(x) quantile(x, probs=0.1) )
  
  # state names and add norm
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  cold_days_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years 1985-2017
  years = as.character(1985:2017)
  for(y in years){
    # subset data
    sub = data[,grep(y, colnames(data))]
    # sums number of days above 10th quantile of norm 1980-1984
    total_cold_days = rowSums(sub < norm_10th) / ncol(sub)
    
    # add year values
    cold_days_yearly = cbind(cold_days_yearly, total_cold_days)
  }
  
  # update colnames
  colnames(cold_days_yearly) = c("geocode", "state",
                                   paste0("cold_day-", weather,"-",years))
  
  return(cold_days_yearly)
}


# PERCENTAGE CHANGE IN RAIN
perc_change_prcp = function(data, weather, operation){
  # select years of norm and compute 10th quantile
  weather_norm = short_term_norm(data, weather, operation)
  
  
  # convert to monthly prcp
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # remove years: 1980-1984, and update weather_monthly
  years.query = paste(1980:1984,collapse="|")
  years.ids = grep(years.query,colnames(weather_monthly))
  weather_monthly = weather_monthly[, -1 * years.ids ]
  
  # percentual change relative to norm
  years = paste(1985:2017)
  weather_yearly = sapply(years, function(x) {
    # subset weather_monthly by year
    chunk = weather_monthly[,grep(x,colnames(weather_monthly))]
    # calculate proportion of months in a year above the norm
    change = rowMeans(chunk - weather_norm[,"norm_mean"]) / weather_norm[,"norm_mean"]
    # convert decrease in rain to increase in dryness 
    # (as in Nawrotzki, Riosmena, and Hunter 2013, p. 9)
    change = -1 * change
    return(change)
  })
 
  # add geocode and state variables
  weather_yearly = cbind(weather_monthly[,c("geocode", "state")], weather_yearly)
  
  # update column names
  colnames(weather_yearly) = c("geocode", "state",
                               paste0("perc_change-", weather, "-", years))
  
}


# Store
###################################
setwd(path.shapefiles)

# PERCENTAGE WARMEST NIGHTS: 
#         - % days in year when daily min temp >90th percentile of the SHORT-term norm (1980-1984)
write.csv( x = perc_warmest_nights(data=tmin.mmp, weather="tmin"),
           file = "./mmp_data/perc_warmest_nights_mmp_1985-2017.csv", row.names = FALSE)


# PERCENTAGE COLD NIGHTS: 
#         - % of days in year when daily min temp <10th percentile of the SHORT-term norm (1980-1984)
write.csv( x = perc_cold_nights(data=tmin.mmp, weather="tmin"),
           file = "./mmp_data/perc_cold_nights_mmp_1985-2017.csv", row.names = FALSE)


# PERCENTAGE COLD DAYS: 
#         - % of days in year when daily max temp <10the percentile of the SHORT-term norm (1980-1984)
write.csv( x = perc_cold_days(data=tmax.mmp, weather="tmin"),
           file = "./mmp_data/perc_cold_days_mmp_1985-2017.csv", row.names = FALSE)


# PERCENTAGE CHANGE IN RAINFALL:
#         - annual % change in monthly rainfall relative to short-term norm (1980-1984)
#         - Short-term norm is calculated as annual average precipitation over months
#         - Accordinly, percnetual changes is computed by caluclating the deviation of each
#           month relative to this average and averaged over all months in a given year.
write.csv( x = perc_change_prcp(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/perc_change_prcp_mmp_1985-2017.csv", row.names = FALSE)

