############################################################
#########    F U N C T I O N S   W E A T H E R    #########
############################################################


# CRUDE DATA: MONTHLY AVERAGE BY YEAR
########################################################
# Returns list with column indices for each month-year
id_columns_for_monthly_values = function(data){
  # it returns a list where each entry corresponds to a year.
  #     and each value within entry corresponds to a column id for the start of a month
  ncol = ncol(data) - 1 # last column is "state.rain.norm.monthly"
  nmonths = list() 
  months = c( 31,28,31,30,31,30,31,31, 30,31,30,31 )
  years = as.character(1980:2017)
  for(y in 1:length(years)) {
    if(y==1) {
      nmonths[[y]] = cumsum(c(1,months))
    } else {
      nmonths[[y]] =  cumsum( c( (365*(y-1)+1), (months)) )    # c( (365*(y-1)+1),(365*y) ) 
    }
    
  }
  return(nmonths)
}

#  STATE NAMES
mmp_state_names = function(data){
  # get only state names that appear in mmp data
  state.names = sapply( data$geocode, function(x) {
    if(nchar(x) == 8) st = substr(x, start = 1, stop = 1) else st = substr(x, start = 1, stop = 2)
    return(as.numeric(st))
  } )
  return(state.names)
}

# MONTH-YEAR COLNAMES
month_year_colnames = function(data, weather){
  # add column names
  months = c("jan", "feb", "mar", "apr", 
             "may", "jun", "jul", "ago", 
             "sep", "oct", "nov", "dec")
  year.month = c()
  years = as.character(1980:2017)
  for(y in years) year.month = c(year.month, paste0(months, "-", y))
  year.month = paste0(weather,"-",year.month)
  
  return(year.month)
}

convert_weather_monthly = function(data, weather, operation){
  
  # get monthly columns indexes
  id_col_monthly = id_columns_for_monthly_values(data)
  # add state names to data
  data[,"state"] = mmp_state_names(data)
  
  # monthly weather
  ncol = ncol(data)
  weather_monthly = data[,c("geocode", "state")]
  weather_data_prel = data[,3:ncol]
  
  for(y in 1:length(id_col_monthly) ){
    # for each year in id_col_monthly
    month = id_col_monthly[[y]]
    for(m in 2:length(month)){
      # for each month in id_col_monthly[year]
      range.month = (month[m-1]):(month[m]-1)
      if(operation=="sum"){
        operation.monthly = rowSums(weather_data_prel[,range.month])  
      } else if(operation=="mean"){
        operation.monthly = rowMeans(weather_data_prel[,range.month])  
      } else if(operation=="above30"){
        operation.monthly = rowSums( weather_data_prel[,range.month] > 30 )
      }else if(operation=="longterm-norm"){
        
      }
      # monthly operation
      weather_monthly = cbind( weather_monthly, operation.monthly )   
    }
  }
  # add month-year colnames
  colnames(weather_monthly) = c("geocode", 
                                "state", 
                                month_year_colnames(weather_monthly, weather) )
  return(weather_monthly)
}

# CRUDE DATA FOR WEATHER
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

# LONG-TERM NORM
long_term_norm = function(data.env, data, weather){
  
  # E N V I R O N S   D A T A
  # rain at state level. data coming environs.dta
  months = c( "jan", "feb", "mar", "apr", 
              "may", "jun", "jul", "ago", 
              "sep", "oct", "nov", "dec" )
  rain.year = paste0("rai", 60:79)
  rain.6079 = as.vector( sapply(months, function(x) paste0(x, rain.year)) )
  
  # state names from weather data (e.g. prcp.mmp, tmax.mmp)
  mmp_state_names = unique( mmp_state_names(data) )
  
  # rain monthly norm at state level (1960-1979)
  if(weather=="prcp"){
    # average prcp 1960-1979
    longterm_norm_mean = rowMeans( data.env[ mmp_state_names , rain.6079 ] )
    # std prcp  1960-1979
    long_term_sd = apply(data.env[ mmp_state_names , rain.6079 ], 1, sd)
    longterm_norm = cbind(norm_mean=longterm_norm_mean, norm_sd=long_term_sd)
    # add state names
    longterm_norm = cbind( longterm_norm, state=mmp_state_names)
  }
  return(longterm_norm)
}

short_term_norm = function(data, weather, operation){
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # state names
  mmp_state_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years = as.character(1980:1984)
  years.ids = unlist( lapply(years, function(x) grep(x, colnames(weather_monthly))) )
  
  # norm mean and sd
  norm_mean = rowMeans( weather_monthly[,years.ids] )
  norm_sd = apply( weather_monthly[,years.ids], 1, sd )
  
  # get short term norm
  shortterm_norm = cbind(state=mmp_state_names, norm_mean=norm_mean, norm_sd=norm_sd)
  
  return(shortterm_norm)
}

# LON-TERM NORM DEVIATION: 1960-1979 (FOR PRCP ONLY)
long_term_norm_deviation = function(data, data_historic, weather){
  # get long term norm
  norm = long_term_norm(data_historic, data, weather)
  # get prcp yearly
  weather.yearly = crude_weather_yearly(data=data, weather, operation="sum")
  # merge norm and prcp yearly based on state
  norm.prcp = merge(weather.yearly, norm, by="state")
  # get norm deviation noralized by norm_sd per state
  norm.deviation = ( norm.prcp[,grep(weather, colnames(norm.prcp))] - norm.prcp[,"norm_mean"] ) / norm.prcp[,"norm_sd"]
  norm.deviation = cbind(norm.prcp[,c("state", "geocode")], norm.deviation)
  
  return(norm.deviation)
}

norm_weather_yearly = function(data, weather){
  
  # yearly averages
  years = as.character(1985:2017)
  weather_yearly = data[,c("geocode", "state")]
  for(y in years){
    idx_year = grep(y, colnames(data))
    year_mean = rowMeans(data[,idx_year])
    weather_yearly = cbind(weather_yearly, year_mean)
  }
  # update weather_yearl colnames
  colnames(weather_yearly) = c("geocode", "state", paste0(weather,"-",years))
  
  return(weather_yearly)
}


# SHORT-TERM NORM DEVIATION: 1980-1984
short_term_norm_deviation = function(data, weather, operation){
  
  # get short term norm
  short_norm = short_term_norm(data, weather, operation)
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # remove years: 1980-1984, and update weather_monthly
  exclude_years = as.character(1980:1984)
  years.ids = unlist( lapply(exclude_years, function(x) grep(x, colnames(weather_monthly)) ) )
  weather_monthly = weather_monthly[, - years.ids ]
  
  # get norm deviation
  norm.deviation = ( weather_monthly[,grep(weather,colnames(weather_monthly))] - short_norm[,"norm_mean"] ) / short_norm[,"norm_sd"]
  norm.deviation = cbind(weather_monthly[,c("state", "geocode")], norm.deviation)
  
  # get the average deviation from short term norm
  norm_deviation_yearly = norm_weather_yearly(norm.deviation, weather)
  
  return(norm_deviation_yearly)
}


# SHORT-TERM NORM: PERCENT OF MONTHS ABOVE NORM 1980-1984
short_term_norm_percent = function(data, weather, operation){
  # get short term norm
  short_norm = short_term_norm(data, weather, operation)
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # remove years: 1980-1984, and update weather_monthly
  exclude_years = as.character(1980:1984)
  years.ids = unlist( lapply(exclude_years, function(x) grep(x, colnames(weather_monthly)) ) )
  weather_monthly = weather_monthly[, - years.ids ]
  
  # percentage of months above norm
  years = as.character(1985:2017)
  weather_yearly = weather_monthly[,c("geocode", "state")]
  for(y in years){
    sub = weather_monthly[,grep(y, colnames(weather_monthly))]
    year_percent_norm = rowSums(sub > short_norm[,"norm_mean"]) / ncol(sub)
    weather_yearly = cbind(weather_yearly, year_percent_norm)
  }
 
  # update column names
  colnames(weather_yearly) = c("geocode", "state", 
                               paste0("norm_%-", weather, "-", years))
  
  return(weather_yearly)
}



# WARM SPELLS: NUMBER OF TIMES THAT 6 CONSECUTIVE DAYS HAVE A HIGHER VALUE THAN THE (SHORT-TERM) NORM 1980-1984
warm_spells = function(data, weather, operation){
  
  # get short term norm: average temperature between 1980-1984
  short_norm = short_term_norm(data, weather, operation)
  
  # state names
  mmp_state_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years = as.character(1985:2017)
  years.ids = lapply(years, function(x) grep(x, colnames(data)))
  
  spell_yearly = cbind(geocode=data$geocode, state=mmp_state_names)
  # norm mean and sd
  for(y in 1:length(years.ids)){
    sub = data[,years.ids[[y]]]
    # loop through columns
    warm_spells_matrix = cbind() # 
    for(i in 1:(ncol(sub)-5)) {
      col_idx = i:(i+5)
      test = rowSums( sub[,col_idx] > ( short_norm[,"norm_mean"] ) * 0.9)
      test_idx = which(test==6)
      # create counter vector
      counter = rep(0, nrow(sub))
      if(length(test_idx) > 0) counter[test_idx] = 1
      
      # update warm_spells matrix
      warm_spells_matrix = cbind(warm_spells_matrix, counter)  
    }
    
    spell_yearly = cbind(spell_yearly, rowSums(warm_spells_matrix))
  }
  colnames(spell_yearly) = c("geocode", "state",
                             paste0("spell-", weather,"-",years))
  
  return(spell_yearly)
}
