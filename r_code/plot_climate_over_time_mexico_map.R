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


##############################################################
### P L O T 


setwd(path.git)
bitmap("./results/prcp_raw_map_over_time.tiff", height=5, width=9,units="in",type="tiff24nc",res=150)

y = 1980:2016
plot(1:nrow(climate), seq(1980,2016,length.out=nrow(climate)), 
     axes=FALSE, xlab="",ylab="",type="n", main="Prcp in Mexico (1980-2016)")

for(row in 1:nrow(climate)){
  vals = round( climate[row,climate_names,with=FALSE] )
  vals = as.vector(unlist(vals))
  x = rep(row,length(y))
  
  pal = colorRampPalette(brewer.pal(9, "Blues"))(max(vals)-min(vals))
  
  cols = pal[vals-min(vals)]
  points(x, y, bg=cols, col="white", pch=22, cex=1.8)
  
}
# Axes
axis(1, tick=TRUE, at=1:143, cex.axis=0.6, las=2)
axis(2, tick=TRUE, at=1980:2016, las=1, cex.axis=0.6)

dev.off()
