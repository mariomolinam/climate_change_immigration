period_interest = function(data){
  # period
  months = c("05","06","07","08","09","10")
  years = paste(1980:2017)
  
  # subset data of interest
  vals_interest = lapply(years, function(x){
    # month year
    month_year = paste0(x,".",months)
    # 
    vals_list = sapply(month_year, function(y){
      sub = data[,grep(y, colnames(data)) ]
    })
    # reset list names
    names(vals_list) = rep("",length(month_year))
    # combine dataframes
    vals = do.call("cbind", vals_list)
    # return(list(vals, colnames(vals)))
    return(vals)
  })
  # combine data frame
  vals_unpack = do.call("cbind",vals_interest)
  # # add state
  # mmp_st_names = mmp_state_names(data)
  # vals_unpack = cbind(geocode=data$geocode, state=mmp_st_names, vals_unpack)
  
  return(vals_unpack)
}

# GROWING DEGREE DAYS
growing_temp = function(tmax,tmin){
  # compute mean temp between tmax and tmin
  tmean = (tmax+tmin)/2
  # period of interest wiithn year (May 1 - Oct 31)
  sub = as.data.frame(period_interest(tmean))
  gdd = sub
  # if T <= 8
  gdd[gdd <= 8] = 0
  # if 8 < T < 32
  gdd[gdd > 8 & gdd < 32] = gdd[gdd > 8 & gdd < 32] - 8
  # if T > 32
  gdd[gdd >= 32] = 24
  
  years = paste(1980:2017)
  gdd_sum_yearly = sapply(years, function(x){
    sub = gdd[,grep(x, colnames(gdd))]
    gdd_sum = rowSums(sub)
  })
  # add state
  mmp_st_names = mmp_state_names(tmax)
  gdd_sum_yearly = cbind(geocode=tmax$geocode,state=mmp_st_names,gdd_sum_yearly)
  
  return(gdd_sum_yearly)
}

# HARMFUL DEGREE DAYS
harmful_temp = function(tmax,tmin){
  # compute mean temp between tmax and tmin
  tmean = (tmax+tmin)/2
  # period of interest wiithn year (May 1 - Oct 31)
  sub = as.data.frame(period_interest(tmean))
  
  years = paste(1980:2017)
  hdd_sum_yearly = sapply(years, function(x){
    hdd = sub[,grep(x, colnames(sub))]
    hdd_32 = apply(hdd, 1, function(x){
      # if T >= 32
      sum( x[x >= 32] - 32 )
    })
    return(hdd_32)
  })
  # add state
  mmp_st_names = mmp_state_names(tmax)
  hdd_sum_yearly = cbind(geocode=tmax$geocode,state=mmp_st_names,hdd_sum_yearly)
  
  return(hdd_sum_yearly)
}

# Store
###################################
setwd(path.shapefiles)

# GROWING DEGREE DAYS: 
#       - See https://onlinelibrary.wiley.com/doi/abs/10.1111/ecoj.12448 (p.238-240)
write.csv( x = growing_temp(tmax=tmax.mmp, tmin=tmin.mmp),
           file = "./mmp_data/gdd_mmp_1980-2017.csv", row.names = FALSE)


# HARMFUL DEGREE DAYS:
#       - See https://onlinelibrary.wiley.com/doi/abs/10.1111/ecoj.12448 (p.238-240)
write.csv( x = harmful_temp(tmax=tmax.mmp, tmin=tmin.mmp),
           file = "./mmp_data/hdd_mmp_1980-2017.csv", row.names = FALSE)
