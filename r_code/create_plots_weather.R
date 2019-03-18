#######################################################
############################## H U M A N   F O O T P R I N T 
#######################################################

# MMP Mexican localities
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.loc = readOGR(".", layer='mx_localities')

# create geocode by combining STATE (ENT), MUNICIPALITY (MUN), and LOCALITY (LOC) .
handle.geocode = function(x){
  rows = c("CVE_ENT", "CVE_MUN", "CVE_LOC")
  if(sum(is.na(x[rows])) == 0) paste0( x[rows][1], x[rows][2], x[rows][3] )
  else x["CVEGEO"]
}
cat('\n', 'Creating geocode...', '\n')
mx.loc@data[,'geocode'] = apply(mx.loc@data, 1, function(x) handle.geocode(x)) 

cat('Done!', '\n')

# Mexican localities - coordinates
# mx.loc.coor = as.data.frame(coordinates(mx.loc))
# mx.loc.coor[,'geocode'] = mx.loc@data[,'geocode']
# mx.loc.agg = aggregate(mx.loc.coor[,1:2], by=list(mx.loc.coor$geocode), mean)

# 
states.in.border = c('02','26','08','05','19','28')
test = mx.loc[mx.loc$CVE_ENT %in% states.in.border,]
plot(test, border='gray98')


test.proj = spTransform(test, proj4string(raster_layers))
test.proj.coor = coordinates(test.proj)
val.cells = cellFromXY(raster_layers, test.proj.coor)

values = as.data.frame( raster_layers[[1]][val.cells] )
test.proj@data[,'Built1994'] = values

values = as.data.frame( raster_layers[[2]][val.cells] )
test.proj@data[,'Built2009'] = values

png('test.png', width=3000, height = 1800, res=100)
par(mfrow=c(1,2))
# my.palette <- brewer.pal(n = 2, name = "OrRd")
spplot(test.proj[p,], zcol='Built1994', col.regions=heat.colors(10))
plot(test.proj['Built2009'], border='gray98', col=c('brown1', 'brown'))
dev.off()




# Human footprint Index
setwd( path.shapefiles )
hf.mmp = read.csv("mmp_w_footprint.csv")

# hfp = colnames(hf.mmp)[grep("HFP", colnames(hf.mmp))]
hfp = colnames(hf.mmp)[12:dim(hf.mmp)[2]]
hfp = hfp[-grep('_int', hfp)]
hfp = hfp[-c(15,16)]
#hfp = sub("_+.*", "", hfp)

# hfp data
d = hf.mmp[,hfp]
d = d[-which(is.na(d[,1])),]
names = c("Built","Croplands","HFP index", "Nighttime Lights", "Nav Water", "Pasture", "Population Dens")
years = list(c(1994,2009),c(1992,2005),c(1993,2009),c(1994,2009),c(1994,2009),c(1993,2009),c(1990,2010))

png('./results/mmp_density_change.png', width = 2000, height = 1000, res=160)
par(mfrow=c(2,4), oma = c(0, 0, 3, 0))
val.odd = seq(1,14,2)
for(i in 1:length(val.odd)){
  c = val.odd[i]
  vec.1 = d[!is.na(d[,c]),c] 
  vec.2 = d[!is.na(d[,c]),c+1] 
  dens.1 = density(vec.1)
  dens.2 = density(vec.2)
  # x = dens.1$x; y = dens.1$
  # hist(vec.1, col='red')
  # hist(vec.2, col='blue', add=TRUE)
  # 
  ymax = 0.22
  if(i==3){ymax=0.04} else if(i==6){ymax=1.0}
  
  plot(dens.1, type='n', bty="n", main = names[i], xaxt="n", yaxt="n", ylim=c(0,ymax))
  lines(dens.1, col='#302B54')
  lines(dens.2, col='#2B60DE')
  
  axis(1, seq(floor(min(dens.1$x)),ceiling(max(dens.1$x)),5) )
  axis(2, round(seq(0,ymax, length.out = 5),2), las=1)
  
  legend(max(dens.1$x)*0.7, ymax*0.95, legend=years[[i]],
         col=c('#302B54', '#2B60DE'), lty=c('solid','solid'), 
         lwd=c(1,1), box.lty=0, cex=0.8)
}
mtext('MMP Localities - Density Distribution for Human Footprints (1993-2009)', outer = TRUE, cex=1)
dev.off()


#######################################################
##############################  C L I M A T E 
#######################################################

######################### PRECIPITATION
##  FIGURES
setwd( path.shapefiles )
prcp.mmp = as.data.frame(fread("mmp_w_prcp.csv"))

# Yearly Figure: yearly cumulative precipitation
png("./results/prcp_trends_cumulative_year.png", height=3000, width=2000, res=130)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))
years = as.character(1980:2017)
for(j in years){
  specific.years = colnames(prcp.mmp)[grep(j, colnames(prcp.mmp))]
  d = t( apply(prcp.mmp[,specific.years], 1, cumsum) )
  
  # take the mean values of each month
  prcp.summary = apply(d,2,function(x) quantile(x, probs=c(0.05,0.25,0.5,0.75,0.95)))
  
  main.name = paste("Year", j)
  
  # creat main plot with median value (50%)
  plot(prcp.summary[3,], main = main.name, type="l", ylim=c(0,2000), 
       xlab='Days', ylab='Cumulative Precipation (mm/day)', 
       bty="n", col="#302B54", xaxt="n", yaxt="n", lwd=2)
  
  # add interquartile and top/bottom 5%
  lines(prcp.summary[2,], lty='dashed', lwd=1, col='#2B60DE')
  lines(prcp.summary[4,], lty='dashed', lwd=1, col='#2B60DE')
  lines(prcp.summary[1,], lty='dotted', lwd=0.5, col='#2B60DE')
  lines(prcp.summary[5,], lty='dotted', lwd=0.5, col='#2B60DE')
  
  # add axes labels
  axis(1, at=seq(0,dim(prcp.summary)[2], 30), cex.axis=0.6)
  axis(2, at=seq(0,2000,200), cex.axis=0.6, las=1)
  
  # add legend
  legend(20, 2000, legend=c('2nd quartile', '1st/3rd quartile', 'bottom/top 5%'),
         col=c('#302B54', '#2B60DE', '#2B60DE'), lty=c('solid','dashed','dotted'), 
         lwd=c(2,1,0.5), box.lty=0, cex=0.8)
}
mtext('MMP Localities - Cumulative Precipitation 1980-2017 (quartiles)', outer = TRUE, cex=2)
dev.off()


# Yearly Figure: daily precipitation
png("./results/prcp_trends_daily.png", height=2700, width=1900, res=120)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))
years = as.character(1980:2017)

for(j in years) {
  # select data for subset of years
  specific.years = colnames(prcp.mmp)[grep(j, colnames(prcp.mmp))]
  d = prcp.mmp[,specific.years]
  
  # get mean and median
  prcp.mean.daily = apply( d, 2, mean)
  prcp.median.daily = apply( d, 2, median)
  
  main.name = paste("Year", j)
  # creat main plot with mean
  plot(prcp.mean.daily, main = main.name, type="h", ylim=c(0,20), 
       xlab='Days', ylab='Cumulative Precipation (mm/day)', 
       bty="n", col="#39B7CD", xaxt="n", yaxt="n", lwd=0.8)
  # add median
  lines(prcp.median.daily, type="h", lty="dashed", lwd=0.5, col="#302B54")
  
  # add axes labels
  axis(1, at=seq(0,length(prcp.summary), 30), cex.axis=0.6)
  axis(2, at=seq(0,20,5), cex.axis=0.6, las=1)
  
  # add legend
  legend(30, 20, legend=c('Mean','Median'),
         col=c('#39B7CD','#302B54'), lty=c('solid','dashed'),
         lwd=c(0.8,0.5), box.lty=0, cex=0.8)
  
}
mtext('MMP Localities - Daily Precipitation 1980-2017', outer = TRUE, cex=2)
dev.off()


######################### MAX TEMPERATURE
##  FIGURES
setwd( path.shapefiles )
tmax.mmp = as.data.frame(fread("mmp_w_tmax.csv"))

# Yearly Figure: cumulative number of days above 30 degrees
png("./results/tmax_trends_cumulative_year.png", height=3000, width=2000, res=130)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))

years = as.character(1980:2017)
for(j in years){
  specific.years = colnames(tmax.mmp)[grep(j, colnames(tmax.mmp))]
  # values higher than 30 Celcius degrees
  d = t( apply(tmax.mmp[,specific.years], 1, function(x) x > 30) )
  d = t( apply(d, 1, cumsum ) )
  
  # take the mean values of each day
  tmax.summary = apply(d,2,function(x) quantile(x, probs=c(0.25,0.5,0.75)))
  
  main.name = paste("Year", j)
  # creat main plot with median value (50%)
  plot(tmax.summary[2,], main = main.name, type="l", ylim=c(0,200), 
       xlab='Days', ylab='# of Days above 30° (Celcius)', 
       bty="n", col="#CC0000", xaxt="n", yaxt="n", lwd=2)
  
  # add interquartile and top/bottom 5%
  lines(tmax.summary[1,], lty='dashed', lwd=1, col="#B33B24")
  lines(tmax.summary[3,], lty='dashed', lwd=1, col="#B33B24")
  
  # add axes labels
  axis(1, at=seq(0,dim(tmax.summary)[2], 30), cex.axis=0.6)
  axis(2, at=seq(0,200,50), cex.axis=0.7, las=1)
  
  # add legend
  legend(20, 200, legend=c('2nd quartile', '1st/3rd quartile'),
         col=c('#CC0000', '#B33B24'), lty=c('solid','dashed'),
         lwd=c(2,1), box.lty=0, cex=0.8)
}
mtext('MMP Localities - Cumulative # of Hot Days 1980-2017 (quartiles)', outer = TRUE, cex=2)
dev.off()


# Yearly Figure: daily deviation from 30 degrees
png("./results/tmax_trends_daily.png", height=3500, width=2700, res=150)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))
years = as.character(1980:2017)

for(j in years) {
  # select data for subset of years
  specific.years = colnames(tmax.mmp)[grep(j, colnames(tmax.mmp))]
  # values higher than 30 Celcius degrees
  d = tmax.mmp[,specific.years] - 30
  
  # get mean and median
  tmax.mean.daily = apply( d, 2, mean)
  tmax.median.daily = apply( d, 2, median)
  
  main.name = paste("Year", j)
  # creat main plot with mean
  plot(tmax.mean.daily, main = main.name, type="n", ylim=c(-15,5), 
       xlab='Days', ylab='Daily Deviation from 30°', 
       bty="n", xaxt="n", yaxt="n")
  # add mean 
  lines(tmax.mean.daily, type="h", lty="solid", lwd=1, col="#E8AC41")
  # add median
  lines(tmax.median.daily, type="h", lty="solid", lwd=0.5, col="#CC0000")
  
  # add axes labels
  axis(1, at=seq(0,length(tmax.mean.daily), 30), cex.axis=0.6)
  axis(2, at=seq(-15,5,5), cex.axis=0.6, las=1)
  
  # add legend
  legend(90, -7, legend=c('Mean','Median'),
         col=c('#E8AC41','#CC0000'), lty=c('solid','solid'),
         lwd=c(1,0.5), box.lty=0, cex=0.8)
  
}
mtext('MMP Localities - Daily Deviation from 30° 1980-2017 (Max. Temp.)', outer = TRUE, cex=2)
dev.off()


######################### MIN TEMPERATURE
##  FIGURES
setwd( path.shapefiles )
tmin.mmp = as.data.frame(fread("mmp_w_tmin.csv"))


# Yearly Figure: cumulaive number of days below 5 degrees.
png("./results/tmin_trends_cumulative_year.png", height=3000, width=2000, res=130)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))

years = as.character(1980:2017)
for(j in years){
  specific.years = colnames(tmin.mmp)[grep(j, colnames(tmin.mmp))]
  
  d = t( apply(tmin.mmp[,specific.years], 1, function(x) x < 10) )
  d = t( apply(d, 1, cumsum ) )
  
  
  # take the mean values of each day
  tmin.summary = apply(d,2,function(x) quantile(x, probs=c(0.25,0.5,0.75)))
  
  main.name = paste("Year", j)
  # creat main plot with median value (50%)
  plot(tmin.summary[2,], main = main.name, type="l", ylim=c(0,180), 
       xlab='Days', ylab='# of Days below 10° (Celcius)', 
       bty="n", col="#302B54", xaxt="n", yaxt="n", lwd=2)
  
  # add interquartile and top/bottom 5%
  lines(tmin.summary[1,], lty='dashed', lwd=1, col="#2B60DE")
  lines(tmin.summary[3,], lty='dashed', lwd=1, col="#2B60DE")
  
  # add axes labels
  axis(1, at=seq(0,dim(tmax.summary)[2], 30), cex.axis=0.6)
  axis(2, at=seq(0,180,20), cex.axis=0.7, las=1)
  
  # add legend
  legend(20, 180, legend=c('2nd quartile', '1st/3rd quartile'),
         col=c('#302B54', '#2B60DE'), lty=c('solid','dashed'),
         lwd=c(2,1), box.lty=0, cex=0.8)
}
mtext('MMP Localities - Cumulative number of cold days 1980-2017 (quartiles)', outer = TRUE, cex=2)
dev.off()


# Yearly Figure: daily deviation from 30 degrees
png("./results/tmin_trends_daily.png", height=3500, width=2700, res=150)
par(mfrow=c(8,5), oma = c(0, 0, 3, 0))
years = as.character(1980:2017)

for(j in years) {
  # select data for subset of years
  specific.years = colnames(tmin.mmp)[grep(j, colnames(tmin.mmp))]
  # values lower than 5 Celcius degrees
  d = tmin.mmp[,specific.years] - 10
  
  # get mean and median
  tmin.mean.daily = apply( d, 2, mean)
  tmin.median.daily = apply( d, 2, median)
  
  main.name = paste("Year", j)
  # creat main plot with mean
  plot(tmin.mean.daily, main = main.name, type="n", ylim=c(-7,7), 
       xlab='Days', ylab='Daily Deviation from 10°', 
       bty="n", xaxt="n", yaxt="n")
  # add mean 
  lines(tmin.mean.daily, type="h", lty="solid", lwd=1, col="#2B60DE")
  # add median
  lines(tmin.median.daily, type="h", lty="solid", lwd=0.5, col="#302B54")
  
  # add axes labels
  axis(1, at=seq(0,length(tmin.mean.daily), 30), cex.axis=0.6)
  axis(2, at=seq(-5,7,1), cex.axis=0.6, las=1)
  
  # add legend
  legend(10, 7, legend=c('Mean','Median'),
         col=c('#2B60DE','#302B54'), lty=c('solid','solid'),
         lwd=c(1,0.5), box.lty=0, cex=0.8)
  
}
mtext('MMP Localities - Daily Deviation from 10° 1980-2017 (Minimum Temperature)', outer = TRUE, cex=2)
dev.off()

