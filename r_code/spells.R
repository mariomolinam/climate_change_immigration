
# SHORT-TERM NORM: 90TH PERCENTILE
short_norm_percentile = function(data, weather, operation, prob){
  
  # weather monthly
  weather_monthly = convert_weather_monthly(data, weather, operation)
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years.query = paste(1980:1984,collapse="|")
  years.ids = grep(years.query,colnames(weather_monthly))
  
  # Obtain percentile prob of the distribution of average weather_monthly between 1980 and 1984.
  norm_th = apply(weather_monthly[,years.ids], 1, function(x) quantile(x, probs=prob))
  
  # get short term norm
  shortterm_norm = cbind(state=mmp_st_names, norm_th=norm_th)
  
  return(shortterm_norm)
}

# WARM SPELLS: NUMBER OF TIMES THAT 6 CONSECUTIVE DAYS HAVE A HIGHER VALUE THAN THE (SHORT-TERM) NORM 1980-1984
warm_spells = function(data, weather, operation){
  
  # get short term norm 90th percentile.
  short_norm_90th = short_norm_percentile(data, weather, operation, prob=0.9)
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years = as.character(1985:2017)
  years.ids = lapply(years, function(x) grep(x, colnames(data)))
  
  spell_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  for(y in years){
    # ubset data by year
    sub = data[,grep(y,colnames(data))]
    # whether daily tmax is above the 90th percentile of short-term norm
    above_90th = sub > ( short_norm_90th[,"norm_th"] )
    # count number of times 6 consecutive days above norm happens.
    cons_occur = consecutive_days_spec(above_90th, cons_numb = 6) # for 6 consecutive numbers
    
    # add vector with # of consecutive occurrences
    spell_yearly = cbind(spell_yearly,cons_occur)
  }
  # update colnames
  colnames(spell_yearly) = c("geocode", "state",
                             paste0("spell-", weather,"-",years))
  
  return(spell_yearly)
}


# WET SPELLS: The No. of days of heavy precipitation is defined as the annual count of days 
# with more than 10 mm of precipitation (as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5079540/#APP1)
wet_spells = function(data){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years: 1980 - 2017
  years = as.character(1980:2017)

  # compute wet_years
  wet_years = cbind(geocode = data$geocode, state=mmp_st_names)
  for(y in years){
    sub = data[,grep(y,colnames(data))] >= 1
    wet_years = cbind(wet_years,rowSums(sub))
  }
  colnames(wet_years) = c("geocode", "state", paste0("wet_spell-",years))
  
  return(wet_years)
}

# DRY SPELLS: Max number of consecutive days when precip < 1mm
dry_spells = function(data){
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years: 1980 - 2017
  years = as.character(1980:2017)
  
  # compute wet_years
  dry_years = cbind(geocode = data$geocode, state=mmp_st_names)
  for(y in years){
    # obtain TRUE values for days with prcp < 1cm (or 10mm)
    sub = data[,grep(y,colnames(data))] < 1
    dry_days = consecutive_days_max(sub)
    # add column
    dry_years = cbind(dry_years,dry_days)
  }
  colnames(dry_years) = c("geocode", "state", paste0("wet_spell-",years))
  
  return(dry_years)
}

# COLD SPELLS:
cold_spells = function(data, weather, operation){
  
  # get short term norm: average temperature between 1980-1984
  short_norm_10th = short_norm_percentile(data, weather, operation, prob=0.1)
  
  # state names
  mmp_st_names = mmp_state_names(data)
  
  # years for short term norm: 1980-1984
  years = as.character(1985:2017)
  years.ids = lapply(years, function(x) grep(x, colnames(data)))
  
  spell_yearly = cbind(geocode=data$geocode, state=mmp_st_names)
  
  for(y in years){
    # ubset data by year
    sub = data[,grep(y,colnames(data))]
    # whether daily tmin is below the 10th percentile of short-term norm period
    below_10th = sub <  short_norm_10th[,"norm_th"]
    # count number of times 6 consecutive days above norm happens.
    cons_occur = consecutive_days_spec(below_10th, cons_numb = 6) # for 6 consecutive numbers
    
    # add vector with # of consecutive occurrences
    spell_yearly = cbind(spell_yearly,cons_occur)
  }
  # update colnames
  colnames(spell_yearly) = c("geocode", "state",
                             paste0("spell-", weather,"-",years))
  
  return(spell_yearly)
}

# Store
###################################
setwd(path.shapefiles)

# 12. WARM SPELLS: NUMBER OF TIMES THERE ARE 6 CONSECUTIVES DAYS WITH TEMPERATURE > SHORT NORM 1980-1984
#     - Short-term norm is computed using the average tmax over 1980-1984.
#     - It computes the number of times that daily temperature was above the 90th of short-term norm period
#       for SIX consecutive days.
write.csv( x = warm_spells(data=tmax.mmp, weather="tmax", operation="mean"),
           file = "./mmp_data/spell_warm_tmax_mmp_1985-2017.csv", row.names = FALSE)

# 13. WET SPELLS: The No. of days of heavy precipitation is defined as the annual count of days 
# with more than 10 mm of precipitation (as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5079540/#APP1)
write.csv( x = wet_spells(data=prcp.mmp),
           file = "./mmp_data/spell_wet_prcp_mmp_1980-2017.csv", row.names = FALSE)

# 14. COLD SPELLS: Annual count when at least six consecutive days of min temperature < 10th percentile
#         (as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5079540/#APP1)
write.csv( x = cold_spells(data=tmin.mmp, weather="tmin", operation="mean"),
           file = "./mmp_data/spell_cold_tmin_mmp_1980-2017.csv", row.names = FALSE)

# 15. DRY SPELLS: Max number of consecutive days when precip < 1mm (1cm)
#     (as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4674158/)
write.csv( x = dry_spells(data=prcp.mmp),
           file = "./mmp_data/spell_dry_prcp_mmp_1980-2017.csv", row.names = FALSE)

