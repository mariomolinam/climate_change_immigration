
# FUNCTION: CRUDE DATA FOR WEATHER
###################################
crude_weather_yearly = function(data, weather, operation){
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # yearly averages
  years = as.character(1980:2017)
  weather_yearly = weather_monthly[,c("geocode", "state")]
  for(y in years){
    idx_year = grep(y, colnames(weather_monthly))
    year_mean = rowMeans(weather_monthly[,idx_year])
    weather_yearly = cbind(weather_yearly, year_mean)
  }
  # update weather_yearl colnames
  colnames(weather_yearly) = c("geocode", "state", paste0(weather,"-",years))
  
  return(weather_yearly)
}


# ANNUAL MAXIMUM PRECIPITATION IN A MONTH
annual_maximum = function(data, weather, operation){
  
  # Monthly average precipitation 
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # yearly maximum
  years = as.character(1980:2017)
  weather_yearly = sapply(years, function(x) {
    # take the maximum
    val = apply(weather_monthly[,grep(x, colnames(weather_monthly))], 1, max) 
  }) 
  
  # add geocodes and states
  weather_yearly = cbind(weather_monthly[,c("geocode", "state")], weather_yearly)
  
  # update weather_yearl colnames
  colnames(weather_yearly) = c("geocode", "state", paste0(weather,"-",years))
  
  return(weather_yearly)
}


# ANNUAL MINIMUM PRECIPITATION IN A MONTH
annual_minimum = function(data, weather, operation){
  
  # Monthly average precipitation 
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # yearly minimum
  years = as.character(1980:2017)
  weather_yearly = sapply(years, function(x) {
    # take the minimum
    val = apply(weather_monthly[,grep(x, colnames(weather_monthly))], 1, min) 
  }) 
  
  # add geocodes and states
  weather_yearly = cbind(weather_monthly[,c("geocode", "state")], weather_yearly)
  
  # update weather_yearl colnames
  colnames(weather_yearly) = c("geocode", "state", paste0(weather,"-",years))
  
  return(weather_yearly)
}

# Store
###################################
setwd(path.shapefiles)

## 1.1 MMP
# Data: Yearly average total AMOUNT of rain per month.
#       We first calculate the total amount of rain per month (sum over days) and 
#       then average over months.
write.csv( x = crude_weather_yearly(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/prcp_total_yearly_average_mmp_1980-2017.csv", row.names = FALSE )

# Data: Yearly average of the monthly AVERAGE of rain per month.
#       We first calculate the average 
write.csv( x = crude_weather_yearly(data=prcp.mmp, weather="prcp", operation="mean"),
           file = "./mmp_data/prcp_average_yearly_average_mmp_1980-2017.csv.csv", row.names = FALSE )

# Data: Annual maximum precipitation (as averaged over days in a month).
#       We take the maximum monthly average value over the year
write.csv( x = annual_maximum(data=prcp.mmp, weather="prcp", operation="mean"),
           file = "./mmp_data/prcp_maximum_yearly_mmp_1980-2017.csv", row.names = FALSE )

# Data: Annual minimum precipitation (as averaged over days in a month).
#       We take the maximum monthly average value over the year
write.csv( x = annual_minimum(data=prcp.mmp, weather="prcp", operation="mean"),
           file = "./mmp_data/prcp_minimum_yearly_mmp_1980-2017.csv", row.names = FALSE )


## 1.2 MUN
write.csv( x = convert_weather_monthly(data=prcp.mun, weather="prcp", operation="sum"),
           file = "./mmp_data/crude_raw_prcp_monthly-sum_mun_1980-2017.csv", row.names = FALSE )

write.csv( x = convert_weather_monthly(data=prcp.mun, weather="prcp", operation="mean"),
           file = "./mmp_data/crude_raw_prcp_monthly-mean_mun_1980-2017.csv", row.names = FALSE )
