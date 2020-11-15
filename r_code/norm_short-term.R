
# FUNCTION: LONG-TERM NORM FOR WEATHER
########################################

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


# SHORT-TERM NORM DEVIATION (1980-1984)
short_term_norm_deviation = function(data, weather, operation){
  
  # get short term norm
  short_norm = short_term_norm(data, weather, operation)
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # remove years: 1980-1984, and update weather_monthly
  years.query = paste(1980:1984,collapse="|")
  years.ids = grep(years.query,colnames(weather_monthly))
  weather_monthly = weather_monthly[, -1 * years.ids ]
  
  # get deviation of each month from norm, then normalize using SD
  norm.deviation = ( weather_monthly[,grep(weather,colnames(weather_monthly))] - short_norm[,"norm_mean"] ) / short_norm[,"norm_sd"]
  norm.deviation = cbind(weather_monthly[,c("state", "geocode")], norm.deviation)
  
  # get the average deviation from short term norm
  norm_deviation_yearly = norm_weather_yearly(norm.deviation, weather)
  
  return(norm_deviation_yearly)
}


short_term_norm_deviation_categories = function(data, weather, operation){
  
  # get long-term norm deviations
  norm.deviation = short_term_norm_deviation( data=prcp.mmp, 
                                             weather=weather,
                                             operation=operation)
  
  # create categories
  norm.deviation.cats = norm.deviation[,-c(1,2)]
  norm.deviation.cats = ifelse(norm.deviation.cats > -1 & norm.deviation.cats < 1, "(-1,1)",
                               ifelse(norm.deviation.cats > -2 & norm.deviation.cats <= -1, "(-2,-1]", 
                                      ifelse(norm.deviation.cats <= -2, "<= -2",
                                             ifelse(norm.deviation.cats >=1  & norm.deviation.cats < 2, "[1,2)", ">=2"))))
  # add state and geocode variables
  norm.deviation.cats = cbind(norm.deviation[,c("state","geocode")],norm.deviation.cats)
  
  return(norm.deviation.cats)
}


# SHORT-TERM NORM: PERCENT OF MONTHS ABOVE NORM 1980-1984
short_term_norm_percent = function(data, weather, operation){
  # get short term norm
  short_norm = short_term_norm(data, weather, operation)
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # remove years: 1980-1984, and update weather_monthly
  years.query = paste(1980:1984,collapse="|")
  years.ids = grep(years.query,colnames(weather_monthly))
  weather_monthly = weather_monthly[, -1 * years.ids ]
  
  # percentage of months above norm
  years = as.character(1985:2017)
  weather_yearly = sapply(years, function(x) {
    # subset weather_monthly by year
    chunk = weather_monthly[,grep(x, colnames(weather_monthly))]
    # calculate proportion of months in a year above the norm
    year_percent_norm = rowSums(chunk > short_norm[,"norm_mean"]) / ncol(chunk)
    return(year_percent_norm)
  })
  
  # add geocode and state variables
  weather_yearly = cbind(weather_monthly[,c("geocode", "state")], weather_yearly)
  
  # update column names
  colnames(weather_yearly) = c("geocode", "state",
                               paste0("norm_%-", weather, "-", years))
  
  return(weather_yearly)
}


# Store
###################################
setwd(path.shapefiles)

# 6. NORM DEVIATION, SHORT-TERM NORM 1980-1984: precipitation
#     - First, we calculate the yearly average total amount of rain per month.
#     - Second, we compute the deviation from the community-level short-term norm 
#       normalized by SD.
write.csv( x = short_term_norm_deviation(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/norm_deviation_short-term_prcp_mmp_1985-2017.csv", row.names = FALSE)

# 7. NORM DEVIATION CATEGORIES, SHORT-TERM NORM 1980-1984: precipitation
#     - First, we calculate the yearly average total amount of rain per month.
#     - Second, we compute the deviation from the community-level short-term norm 
#       normalized by SD.
#     - Third, we create categories that group standard deviations: (-1,1), (-2,-1], <=-2, [1,2), and >= 2.
write.csv( x = short_term_norm_deviation_categories(data=prcp.mmp, weather="prcp", operation="sum"),
           file = "./mmp_data/norm_deviation_short-term_cats_prcp_mmp_1985-2017.csv", row.names = FALSE)

# 8. NORM DEVIATION, SHORT-TERM NORM 1980-1984: tmax
#     - First, we compute the number of non-consecutive days above 30C in a month.
#     - Second, we compute the deviation from the community-level short-term norm 
#       normalized by SD.
write.csv( x = short_term_norm_deviation(data=tmax.mmp, weather="tmax", operation="above30-notconsecutive"),
           file = "./mmp_data/norm_deviation_short-term_tmax_mmp_1985-2017.csv", row.names = FALSE)

# 9. NORM DEVIATION CATEGORIES, SHORT-TERM NORM 1980-1984: tmax
#     - First, we compute the number of non-consecutive days above 30C in a month.
#     - Second, we compute the deviation from the community-level short-term norm 
#       normalized by SD.
#     - Third, we create categories that group standard deviations: (-1,1), (-2,-1], <=-2, [1,2), and >= 2.
write.csv( x = short_term_norm_deviation_categories(data=tmax.mmp, weather="tmax", operation="above30-notconsecutive"),
           file = "./mmp_data/norm_deviation_short-term_cats_tmax_mmp_1985-2017.csv", row.names = FALSE)

# 10. NORM PERCENT, SHORT-TERM NORM 1980-1984: prcp
#     - First, we calculate the yearly average total amount of rain per month.
#     - Second, we count the number of months in a year that were above the short-term norm
#     - Third, we divide by 12 to obtain the proportion.
write.csv( x = short_term_norm_percent( data=prcp.mmp, weather="prcp", operation="sum"),
          file = "./mmp_data/norm_percent_short-term_prcp_mmp_1985-2017.csv", row.names = FALSE)

# 11. NORM PERCENT, SHORT-TERM NORM 1980-1984: tmax
#     - First, we compute the number of non-consecutive days above 30C in a month.
#     - Second, we count the number of months in a year that were above the short-term norm
#     - Third, we divide by 12 to obtain the proportion.
write.csv( x = short_term_norm_percent(data=tmax.mmp, weather="tmax", operation="above30-notconsecutive"),
           file = "./mmp_data/norm_percent_short-term_tmax_mmp_1985-2017.csv", row.names = FALSE)



