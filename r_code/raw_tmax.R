


# Store
###################################
setwd(path.shapefiles)

## 2. MMP
# Data: Yearly average maximum temperature per month
#       We first calculate the average max temperature per month (over days in a month)
#       and then average over months.

write.csv( x = crude_weather_yearly(data=tmax.mmp, weather="tmax", operation="mean"),
           file = "./mmp_data/crude_raw-tmax_yearly-average_mmp_1980-2017.csv", row.names = FALSE)

# 3. CRUDE TMAX: number of days > 30C
## 3.1 MMP
# Data: Yearly average of # of days above 30C per month.
#       We first count # of days above 30C per month
#       and then average over months.
write.csv( x = crude_weather_yearly(data=tmax.mmp, weather="tmax", operation="above30-notconsecutive"),
          file = "./mmp_data/crude_above30-tmax_yearly-average_mmp_1980-2017.csv", row.names = FALSE)

## 3.2 MUN
# Data: Yearly average of # of days above 30C per month.
#       We first count # of days above 30C per month
#       and then average over months.
write.csv( x = convert_weather_monthly(data=tmax.mun, weather="tmax", operation="above30-notconsecutive"),
           file = "./mmp_data/crude_above30-tmax_monthly_mx-mun_1980-2017.csv", row.names = FALSE)


# 4. CRUDE TMAX: number of CONSECUTIVE days > 30
## 4.1 MMP
# Data: Yearly average of # of CONSECUTIVE days above 30C per month.
#       We first count # of CONSECUTIVE days above 30C per month
#       and then average over months.
write.csv( x = convert_weather_monthly(data=tmax.mmp, weather="tmax", operation="above30-consecutive"),
           file = "./mmp_data/crude_above30-tmax_monthly-consecutive_mmp_1980-2017.csv", row.names = FALSE)

## 4.2 MUN
# Data: Yearly average of # of CONSECUTIVE days above 30C per month.
#       We first count # of CONSECUTIVE days above 30C per month
#       and then average over months.
write.csv( x = crude_weather_yearly(data=tmax.mun, weather="tmax", operation="above30-consecutive"),
           file = "./mmp_data/crude_above30-tmax_monthly-consecutive_mun_1980-2017.csv", row.names = FALSE)
