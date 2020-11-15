
# WET DAYS: 
wet_day_prcp = function(data, weather){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  wet_day_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    
    vals = apply(sub, 1, function(x){
      x_sub = x[x > 0.1]        # > 1 mm (same as 0.1 cm) 
      x_total = sum(x_sub) * 10 # convert from cm to mm.
      return(x_total)
    })
    
    # add year values
    wet_day_yearly = cbind(wet_day_yearly, vals)
  }
  # update colnames
  colnames(wet_day_yearly) = c("geocode", "state",
                             paste0("wet_val-", weather,"-",years))
  return(wet_day_yearly)
}


# HEAVY PRCP
heavy_prcp = function(data,weather){
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  heavy_prcp_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    
    vals_true = sub > 2.0 # 2cm
    vals = rowSums(vals_true)
    
    # add year values
    heavy_prcp_yearly = cbind(heavy_prcp_yearly, vals)
  }
  # update colnames
  colnames(heavy_prcp_yearly) = c("geocode", "state",
                               paste0("heavy-", weather,"-",years))
  return(heavy_prcp_yearly)
}


# LOW CUMULATIVE PRCP
low_cumulative = function(data, weather, operation){
  
  # cumulative history per month (total prcp per month)
  monthly_prcp = convert_weather_monthly(data, weather, operation)
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  low_cum_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  years = as.character(1980:2017)
  vals = sapply(years, function(x){
    sub = monthly_prcp[,grep(x, colnames(monthly_prcp)) ]
    # compute # of months with less than 1mm (=0.1cm)
    number_low_rain = rowSums(sub < 0.1)
    return(number_low_rain)
  })
  
  # add columns
  low_cum_yearly = cbind(low_cum_yearly, vals)
  # update colnames
  colnames(low_cum_yearly) = c("geocode", "state",
                                  paste0("low_cumulative-", weather,"-",years))
  return(low_cum_yearly) 
}

# FROST DAYS
frost_days = function(data,weather){
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  frost_days_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    
    vals_true = sub < 0 # < 0C
    vals = rowSums(vals_true)
    
    # add year values
    frost_days_yearly = cbind(frost_days_yearly, vals)
  }
  # update colnames
  colnames(frost_days_yearly) = c("geocode", "state",
                                  paste0("frost_days-", weather,"-",years))
  return(frost_days_yearly)
}


# MAX 5-DAY CONSECUTIVE
max_5day_cons = function(data,weather){
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # define dataframe
  max_5day_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  # loop over years
  years = as.character(1980:2017)
  for(y in years){
    sub = data[,grep(y, colnames(data))]
    days = 1:361
    cons_5day_max = rep(0,nrow(sub))
    for(i in days){
      # sum over 5 consecutive days
      cons = rowSums(sub[,i:(i+4)])
      # get ids when new vals > old values
      ids = which(cons > cons_5day_max)
      # update cons_5day_max vector
      cons_5day_max[ids] = cons[ids]
    }
    # convert from cm to mm
    cons_5day_max = cons_5day_max * 10
    
    # add year values
    max_5day_yearly = cbind(max_5day_yearly, cons_5day_max)
  }
  # update colnames
  colnames(max_5day_yearly) = c("geocode", "state",
                                  paste0("max_5day_cons-", weather,"-",years))
  return(max_5day_yearly)
}


# CUMULATIVE TMAX > 2SD
cumulative_temp_2sd = function(data, weather, operation){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # cumulative history per month (total prcp per month)
  monthly_temp = convert_weather_monthly(data, weather, operation)
  
  # get only years 1980 - 2017
  chunk_temp = monthly_temp[,grep(paste(1980:2017,collapse="|"), colnames(monthly_temp))]
  
  # standardize values for each geocode and take the transpose
  monthly_temp_sd = apply(chunk_temp, 1, function(x){
    temp_sd = (x - mean(x))/sd(x)
    return(temp_sd)
  }); monthly_temp_sd = t(monthly_temp_sd)
  
  # compute # of months per year with tmax standardized > 2sd
  years = as.character(1980:2017)
  vals = sapply(years, function(x, operation){
    sub = monthly_temp_sd[,grep(x, colnames(monthly_temp_sd)) ]
    # compute # of months higher than 2sd
    if(weather=="tmax") { 
      t_2sd = rowSums(sub > 2)
    } else{
      t_2sd = rowSums(sub < -2)
    }
    return(t_2sd)
  })
  
  # add columns
  temp_2sd_yearly = cbind(data[,"geocode"], mmp_st_names, vals)
  
  # update colnames
  colnames(temp_2sd_yearly) = c("geocode", "state",
                               paste0("cum_temp_2sd-", weather,"-",years))
  return(temp_2sd_yearly) 
}

# Store
###################################
setwd(path.shapefiles)

# WET DAYS: Annual total precip from days when precip > 1 cm.
#           Measure in mm (not in cm) --> see code for details.
write.csv( x = wet_day_prcp(data=prcp.mmp, weather="prcp"),
           file = "./mmp_data/prcp_total_wet_days_mmp_1980-2017.csv", row.names = FALSE)


# HEAVY PRCP: Annual count of days when precip > 20mm (> 2cm)
write.csv( x = heavy_prcp(data=prcp.mmp, weather="prcp"),
           file = "./mmp_data/prcp_total_heavy_mmp_1980-2017.csv", row.names = FALSE)


# LOW PRCP: Number of months when cumulative precipitation < 1mm (monthly shocks)
write.csv( x = low_cumulative(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/prcp_low_cum_mmp_1980-2017.csv", row.names = FALSE)


# MAX 5-DAY PRCP: Annual max consecutive 5-day precipitation amount
write.csv( x = max_5day_cons(data=prcp.mmp, weather="prcp"),
           file = "./mmp_data/max_5day_cons_mmp_1980-2017.csv", row.names = FALSE)


# FROST DAYS: Annual count when daily min temperature < 0°C
write.csv( x = frost_days(data=tmin.mmp, weather="tmin"),
           file = "./mmp_data/total_frost_days_mmp_1980-2017.csv", row.names = FALSE)


# CUMULATIVE TMAX > 2 SD
write.csv( x = cumulative_temp_2sd(data=tmax.mmp, weather="tmax", operation="mean"),
           file = "./mmp_data/tmax_cum_2sd_mmp_1980-2017.csv", row.names = FALSE)


# CUMULATIVE TMIN < -2 SD
write.csv( x = cumulative_temp_2sd(data=tmin.mmp, weather="tmin", operation="mean"),
           file = "./mmp_data/tmin_cum_2sd_mmp_1980-2017.csv", row.names = FALSE)
