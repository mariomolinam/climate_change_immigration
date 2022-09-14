
# FUNCTION: LONG-TERM NORM FOR WEATHER
########################################
# LONG-TERM NORM
long_term_norm = function(data.env, data, weather){
  
  # E N V I R O N S   D A T A
  # rain at state level. data coming environs.dta
  # colnames are differently specified
  months = c( "jan", "feb", "mar", "apr",
              "may", "jun", "jul", "ago",
              "sep", "oct", "nov", "dec" )
  rain.year = paste0("rai", 60:79)
  rain.6079 = as.vector( sapply(months, function(x) paste0(x, rain.year)) )
  
  # state names from weather data (e.g. prcp.mmp, tmax.mmp)
  mmp_st_names = unique( mmp_state_names(data) )
  
  # rain monthly norm at state level (1960-1979)
  if(weather=="prcp"){
    # average prcp 1960-1979
    longterm_norm_mean = rowMeans( data.env[ mmp_st_names , rain.6079 ] )
    # std prcp  1960-1979
    long_term_sd = apply(data.env[ mmp_st_names , rain.6079 ], 1, sd)
    longterm_norm = cbind(norm_mean=longterm_norm_mean, norm_sd=long_term_sd)
    # add state names
    longterm_norm = cbind( longterm_norm, state=mmp_st_names)
  }
  return(longterm_norm)
}

# LON-TERM NORM DEVIATION: 1960-1979 (FOR PRCP ONLY)
# COMPUTE STANDARDIZED 
long_term_norm_deviation = function(data, data_historic, weather){
  
  # get long term norm
  norm = long_term_norm(data_historic, data, weather)
  
  # get prcp yearly
  weather.yearly = crude_weather_yearly(data=data, weather, operation="sum")
  
  # merge norm and prcp yearly based on state
  norm.prcp = merge(weather.yearly, norm, by="state")
  
  # get norm deviation NORMALIZED by norm_sd per state
  norm.deviation = ( norm.prcp[,grep(weather, colnames(norm.prcp))] - norm.prcp[,"norm_mean"] ) / norm.prcp[,"norm_sd"]
  norm.deviation = cbind(norm.prcp[,c("state", "geocode")], norm.deviation)
  
  return(norm.deviation)
}


long_term_norm_deviation_categories = function(data, data_historic, weather){
  
  # get long-term norm deviations
  norm.deviation = long_term_norm_deviation( data=prcp.mmp, 
                                             data_historic=data_historic, 
                                             weather="prcp" )
  
  # create categories
  norm.deviation.cats = norm.deviation[,-c(1,2)]
  norm.deviation.cats = ifelse(norm.deviation.cats > -1 & norm.deviation.cats < 1, "(-1,1)",
                               ifelse(norm.deviation.cats > -2 & norm.deviation.cats <= -1, "(-2,-1]", 
                                      ifelse(norm.deviation.cats <= -2, "<= -2",
                                             ifelse(norm.deviation.cats >=1  & norm.deviation.cats < 2, "[1,2)", ">=2"))))
  norm.deviation.cats = cbind(norm.deviation[,c("state","geocode")],norm.deviation.cats)
  
  return(norm.deviation.cats)
}


# LONG-TERM NORM PERCENTILES
long_term_norm_th = function(data.env, data, weather, th){
  
  # E N V I R O N S   D A T A
  # rain at state level. data coming environs.dta
  # colnames are differently specified
  months = c( "jan", "feb", "mar", "apr",
              "may", "jun", "jul", "ago",
              "sep", "oct", "nov", "dec" )
  rain.year = paste0("rai", 60:79)
  rain.6079 = as.vector( sapply(months, function(x) paste0(x, rain.year)) )
  
  # state names from weather data (e.g. prcp.mmp, tmax.mmp)
  mmp_st_names = unique( mmp_state_names(data) )
  
  # rain monthly norm at state level (1960-1979)
  
  # quantile th for 1960-1979
  longterm_norm_th = apply( data.env[ mmp_st_names , rain.6079 ], 1, function(x){
    quant = quantile(x, probs=th)
    return(quant)
  } )
  # add state names
  longterm_norm = cbind( longterm_norm_th, state=mmp_st_names)
  
  return(longterm_norm)
}


# EXTREMELY WET DAYS
extremely_wet_days_99th = function(data, data_historic, weather){
  
  # state names and add norm
  mmp_st_names = as.data.frame(mmp_state_names(data))
  colnames(mmp_st_names) = "state"
  
  # get long term norm
  norm = long_term_norm_th(data_historic, data, weather, th=0.99)
  norm = merge(mmp_st_names,norm,by="state", by.x=TRUE)
  
  # get prcp monthly because quantiles are defined at the month level.
  weather.monthly = convert_weather_monthly(data=data, weather, operation="sum")
  
  # define dataframe
  extreme_wet_day_yearly = cbind(geocode=data$geocode, state=mmp_st_names$state)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = weather.monthly[,grep(y, colnames(weather.monthly))]
    
    vals = sapply(1:nrow(sub), function(i) {
      true_vals = sub[i,] > norm[i,"longterm_norm_th"]
      if(sum(true_vals) > 0){
        x_sub = sum(sub[i,true_vals]) * 10 # convert from cm to mm.  
      } else{
        x_sub = 0
      }
      return(x_sub)
    })
    
    # add year values
    extreme_wet_day_yearly = cbind(extreme_wet_day_yearly, vals)
  }
  # update colnames
  colnames(extreme_wet_day_yearly) = c("geocode", "state",
                               paste0("max_val-", weather,"-",years))
 
   return(extreme_wet_day_yearly)
}

# Store
###################################
setwd(path.shapefiles)

# NORM DEVIATION, LONG-TERM NORM 1960-1979: precipitation (continuous)
# Data: Long-term norm is calculated using data from the MMP dataset, which contains 
#       average total amount of rain per month over years.
#       Deviations of each state from their state-level norm are normalized using the stard
#       deviation of the state so that they can be compared to other states.
write.csv( x = long_term_norm_deviation(data=prcp.mmp, data_historic=env, weather="prcp"),
           file = "./mmp_data/norm_deviation_longterm_mmp_1980-2017.csv", row.names = FALSE)


# NORM DEVIATION, LONG-TERM NORM 1960-1979: precipitation (categorical)
# Data: Same as continuous long-term, but FIVE categories are created:
#         - (-1,1),  (-2,-1], <=-2, [1,2), >=2  
write.csv( x = long_term_norm_deviation_categories(data=prcp.mmp, data_historic=env, weather="prcp"),
           file = "./mmp_data/norm_deviation_longterm_cats_mmp_1980-2017.csv", row.names = FALSE)


# EXTREMELY WET DAYS: 
# Data: Annual total precip from days when precip > 99th percentile.
write.csv( x = extremely_wet_days_99th(data=prcp.mmp, data_historic=env, weather="prcp"),
           file = "./mmp_data/extremely_wet_longterm99th_mmp_1980-2017.csv", row.names = FALSE)

