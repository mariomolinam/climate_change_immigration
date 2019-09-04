# Load Mexican map with states only
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
cat('Done!', '\n')

# Load PRCP raw data
setwd(path.shapefiles)
climate = fread("./mmp_data/crude_raw_prcp_monthly-average_mmp_1980-2017.csv")
# column names
climate_names = colnames(climate)[-c(1,2)]

# obtain columns that correspond to decades
decade_vals = substr(gsub("^.*?-", "", climate_names), 3, 3)
decade_names = c("1980-1989", "1990-1999", "2000-2016")

for(d in 1:length(unique(decade_vals)[1:3])){
  # get values for the decade
  d_char = unique(decade_vals)[d]
  if(d==3) dec = climate_names[decade_vals == d_char | decade_vals == "1"] else  dec = climate_names[decade_vals == d_char]

  # get means for the decade for each state  
  climate_decade_means = cbind( state = climate$state,climate=rowMeans(climate[,dec,with=FALSE]))
  
  # aggregate by state (since there are several localities in one state)
  climate_decade_means_by_state = aggregate(climate_decade_means[,"climate"], by=list(climate_decade_means[,"state"]), mean)
  colnames(climate_decade_means_by_state) = c("state", decade_names[d])
  
  # add values to raster
  mx.ent@data = merge(mx.ent@data, climate_decade_means_by_state, by.x="CVE_ENT", by.y="state", all.x=TRUE)
}


#### P R E C I P I T A T I O N 
##############################################################

### P L O T   M A P   O V E R   T I M E


assign_class = function(x, qtls){
  if( length(x) > 2 ) stop("You're using a dataframe with more than 2 columns...This isn't going to work!")
  state = as.numeric(as.character(x[1]))
  val = as.numeric(x[2])
  quantiles = qtls[qtls[,"state"] == state,]
  if(is.na(val)){
    class = "No data"
  } else if(val >= quantiles["0%"] & val < quantiles["25%"]){
    class = "1st Quartile"
  } else if(val >= quantiles["25%"] & val < quantiles["50%"]){
    class = "2nd Quartile"
  } else if(val >= quantiles["50%"] & val < quantiles["75%"]){
    class = "3rd Quartile"
  } else if(val >= quantiles["75%"] & val <= quantiles["100%"]){
    class = "4th Quartile"
  }
  return(class)
}

# aggregate by STATE
state_average = aggregate(climate[,3:458], by=list(climate$state), mean)
colnames(state_average)[1] = "state"

# MONTHS
months = c("Jan", "Feb", "Mar", "Apr", "May","Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dec")


for(m in 1:length(months)){
  # Load Mexican map with states only
  setwd(path.shapefiles)
  cat('\n', 'Reading Mexican shapefiles...', '\n')
  mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
  mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
  cat('Done!', '\n')
  
  
  # get right months across years  
  col_month = colnames(climate)[grepl(tolower(months[m]), colnames(climate))]
  # get data
  d = state_average[,c("state", col_month)]
  
  seq_cols = seq(2,39,5)[-8]
  five_years_names = c()
  for(i in 1:length(seq_cols)){
    col1 = seq_cols[i]
    col2 = seq_cols[i] + 4
    if(i==7) col2=39
    start = gsub("\\D","", colnames(d[,c(col1:col2)]))[1]
    end = gsub("\\D","", colnames(d[,c(col1:col2)]))[length(col1:col2)]
    col_name = paste0(start,"-",end)
    five_years_names[i] = col_name
    # update d and colname
    d = cbind(d, rowMeans(d[,c(col1:col2)]))
    colnames(d)[ncol(d)] = col_name
  }
  
  # add to Mexico's shapefile 
  mx.ent@data = merge(mx.ent@data, d[,c("state",five_years_names)], by.x="CVE_ENT", by.y="state", all.x=TRUE, suffixes=c("",""))
  
  # define quantile within state to assign appropriate colors
  state_val_quantile = t(apply(d[,2:39], 1, quantile))
  state_val_quantile = cbind(state=d$state, state_val_quantile)
  class_names = c("No data", "1st Quartile", "2nd Quartile", "3rd Quartile", "4th Quartile")
  
  setwd(path.git)
  file_name = paste0("./results/prcp_raw_map_",tolower(months[m]),".tiff")
  bitmap(file_name, height=7, width=20,units="in",type="tiff24nc",res=150)
  
  # DEFINE PAR
  par(mfrow=c(2,4), mai = c(0.2,0.2,0.2,0.2))
      
  
  for(y in 1:length(five_years_names)){
    
    # assign values to classes
    year_name = five_years_names[y]
    class = apply(mx.ent@data[,c("CVE_ENT",year_name)], 1, function(x) assign_class(x, state_val_quantile))
    
    # COLORS
    ncolors = 9
    colors_pal = brewer.pal(ncolors,"Blues")[seq(1,9,2)]
    names(colors_pal) = class_names
    class_color = colors_pal[match(class, names(colors_pal))]
  
    # PLOT
    plot(mx.ent[,year_name], col=class_color)
    
    # title = paste0("Mexican Migration to the US (", t,")")
    title = paste(months[m], year_name)
    text(2500000, 2400000, title, font=2, cex=1.4)
    legend(3200000, 2200000, legend=names(colors_pal),
           fill=colors_pal, cex=1.2, bty="n", border="white")
  
  }
  # close figure
  dev.off()
  
}


###  H O V M O E L L E R    P L O T 
##################################################
# y = 1980:2016
y = 1:456
plot(1:nrow(climate), seq(min(y),max(y),length.out=nrow(climate)), 
     axes=FALSE, xlab="",ylab="",type="n", main="Monthly precipitation in Mexico (1980-2017)")

for(row in 1:nrow(climate)){
  vals = round( climate[row,climate_names,with=FALSE] )
  vals = as.vector(unlist(vals))
  x = rep(row,length(y))
  
  pal = colorRampPalette(brewer.pal(9, "Blues"))(max(vals)-min(vals))
  
  cols = pal[vals-min(vals)]
  points(x, y, bg=cols, col="white", pch=22, cex=1)
  
}
# Axes
# x-axis
axis(1, tick=TRUE, at=1:nrow(climate), labels=climate$state, cex.axis=0.3, las=2)
x_axis_id = match( unique(climate$state), climate$state )
abline(v=x_axis_id, col="black", lty=1, lwd=0.8)

# y-axis
axis(2, tick=TRUE, at=seq(min(y), max(y), 12), labels = 1980:2017, las=1, cex.axis=0.6)
abline(h=seq(min(y), max(y), 12), col="black", lty=1, lwd=0.8)


dev.off()



#### T E M P E R A T U R E
##############################################################

setwd(path.shapefiles)
temp = fread("./mmp_data/crude_raw-tmax_monthly-average_mmp_1980-2017.csv")
# column names
temp_names = colnames(temp)[-c(1,2)]


### P L O T   M A P   O V E R   T I M E

assign_class = function(x, qtls){
  if( length(x) > 2 ) stop("You're using a dataframe with more than 2 columns...This isn't going to work!")
  state = as.numeric(as.character(x[1]))
  val = as.numeric(x[2])
  quantiles = qtls[qtls[,"state"] == state,]
  if(is.na(val)){
    class = "No data"
  } else if(val >= quantiles["0%"] & val < quantiles["25%"]){
    class = "1st Quartile"
  } else if(val >= quantiles["25%"] & val < quantiles["50%"]){
    class = "2nd Quartile"
  } else if(val >= quantiles["50%"] & val < quantiles["75%"]){
    class = "3rd Quartile"
  } else if(val >= quantiles["75%"] & val <= quantiles["100%"]){
    class = "4th Quartile"
  }
  return(class)
}

# aggregate by STATE
state_average = aggregate(temp[,3:458], by=list(temp$state), mean)
colnames(state_average)[1] = "state"

# MONTHS
months = c("Jan", "Feb", "Mar", "Apr", "May","Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dec")


for(m in 1:length(months)){
  # Load Mexican map with states only
  setwd(path.shapefiles)
  cat('\n', 'Reading Mexican shapefiles...', '\n')
  mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
  mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
  cat('Done!', '\n')
  
  
  # get right months across years  
  col_month = colnames(temp)[grepl(tolower(months[m]), colnames(temp))]
  
  # get data
  d = state_average[,c("state", col_month)]
  
  seq_cols = seq(2,39,5)[-8]
  five_years_names = c()
  for(i in 1:length(seq_cols)){
    col1 = seq_cols[i]
    col2 = seq_cols[i] + 4
    if(i==7) col2=39
    start = gsub("\\D","", colnames(d[,c(col1:col2)]))[1]
    end = gsub("\\D","", colnames(d[,c(col1:col2)]))[length(col1:col2)]
    col_name = paste0(start,"-",end)
    five_years_names[i] = col_name
    # update d and colname
    d = cbind(d, rowMeans(d[,c(col1:col2)]))
    colnames(d)[ncol(d)] = col_name
  }
  
  # add to Mexico's shapefile 
  mx.ent@data = merge(mx.ent@data, d[,c("state",five_years_names)], by.x="CVE_ENT", by.y="state", all.x=TRUE, suffixes=c("",""))
  
  # define quantile within state to assign appropriate colors
  state_val_quantile = t(apply(d[,2:39], 1, quantile))
  state_val_quantile = cbind(state=d$state, state_val_quantile)
  class_names = c("No data", "1st Quartile", "2nd Quartile", "3rd Quartile", "4th Quartile")
  
  setwd(path.git)
  file_name = paste0("./results/tmax_raw_map_",tolower(months[m]),".tiff")
  bitmap(file_name, height=7, width=20,units="in",type="tiff24nc",res=150)
  
  # DEFINE PAR
  par(mfrow=c(2,4), mai = c(0.2,0.2,0.2,0.2))
  
  
  for(y in 1:length(five_years_names)){
    
    # assign values to classes
    year_name = five_years_names[y]
    class = apply(mx.ent@data[,c("CVE_ENT",year_name)], 1, function(x) assign_class(x, state_val_quantile))
    
    # COLORS
    ncolors = 9
    colors_pal = brewer.pal(ncolors,"Reds")[seq(1,9,2)]
    names(colors_pal) = class_names
    class_color = colors_pal[match(class, names(colors_pal))]
    
    # PLOT
    plot(mx.ent[,year_name], col=class_color)
    
    # title = paste0("Mexican Migration to the US (", t,")")
    title = paste(months[m], year_name)
    text(2500000, 2400000, title, font=2, cex=1.4)
    legend(3200000, 2200000, legend=names(colors_pal),
           fill=colors_pal, cex=1.2, bty="n", border="white")
    
  }
  # close figure
  dev.off()
  
}


###  H O V M O E L L E R    P L O T 
##################################################
setwd(path.git)
bitmap("./results/tmax_raw_map_over_time.tiff", height=60, width=50,units="in",type="tiff24nc",res=150)

# y = 1980:2016
y = 1:456
plot(1:nrow(temp), seq(min(y),max(y),length.out=nrow(temp)), 
     axes=FALSE, xlab="",ylab="",type="n", main="Monthly max temperature in Mexico (1980-2017)")

for(row in 1:nrow(temp)){
  vals = round( temp[row,temp_names,with=FALSE] )
  vals = as.vector(unlist(vals))
  x = rep(row,length(y))
  
  pal = colorRampPalette(brewer.pal(5, "Reds"))(max(vals)-min(vals))
  
  cols = pal[vals-min(vals)]
  points(x, y, bg=cols, col="white", pch=22, cex=1)
  
}

# Axes

# x-axis
axis(1, tick=TRUE, at=1:nrow(temp), labels=temp$state, cex.axis=0.3, las=2)
x_axis_id = match( unique(temp$state), temp$state )
abline(v=x_axis_id, col="black", lty=1, lwd=0.8)

# y-axis
axis(2, tick=TRUE, at=seq(min(y), max(y), 12), labels = 1980:2017, las=1, cex.axis=0.6)
abline(h=seq(min(y), max(y), 12), col="black", lty=1, lwd=0.8)


dev.off()


