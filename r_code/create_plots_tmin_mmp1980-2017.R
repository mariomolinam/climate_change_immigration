library(foreign)
library(data.table)

path.mmp = "/home/mario/Documents/environment_data/mmp_data/"
path.git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"
path.shapefiles = "/home/mario/Documents/environment_data/mexican_shapefiles/"

###########################################################################
######################### P R E C I P I T A T I O N
###  FIGURES
setwd( path.shapefiles )
tmin.mmp = as.data.frame(fread("mmp_w_tmin.csv"))

# time range
years = as.character(1980:2017)

# norm (average) between 01/01/1980 - 12/31/2017
ncol = dim(tmin.mmp)[2]
nmonths = list() 
months = c(31,28,31,30,31,30,31,31, 30,31,30,31)
for(y in 1:length(years)) {
  if(y==1) nmonths[[y]] = cumsum(c(1,months)) else nmonths[[y]] =  cumsum( c( (365*(y-1)+1), (months)) )    # c( (365*(y-1)+1),(365*y) ) 
}

tmin.mmp.monthly = tmin.mmp[,"geocode"]

for(y in 1:length(nmonths) ){
  month = nmonths[[y]]
  for(m in 2:length(month)){
    range = (month[m-1]):(month[m]-1); range
    sum.monthly = as.matrix( apply(tmin.mmp[,2:ncol][,range], 1, mean) )
    tmin.mmp.monthly = cbind( tmin.mmp.monthly, sum.monthly )   
  }
}

# calculate the monthly average (monthly norm) of prcp across communities
ncol = dim(tmin.mmp.monthly)[2]
norm.community = rowMeans( tmin.mmp.monthly[,2:ncol] )
sd.prcp.community = apply(tmin.mmp.monthly[,2:ncol], 1, sd)
dev.community = tmin.mmp.monthly[,2:ncol] - norm.community
community.dev.mean = cbind(tmin.mmp.monthly[,1], dev.community)
# add column names
months = c("jan", "feb", "mar", "apr", 
           "may", "jun", "jul", "ago", 
           "sep", "oct", "nov", "dec")
year.month = c()
for(y in years) year.month = c(year.month, paste0(months, "-", y))
year.month = paste0("tmin-",year.month)

colnames(community.dev.mean) = c("geocode", year.month)

# save community-level norm deviation between 1980 and 2017
setwd(path.mmp)
write.csv(community.dev.mean, "tmin_monthly_dev-norm_1980-2017.csv", row.names = FALSE)

# create plot for rain
setwd(path.git)
jpeg('./results/tmin_mmp_1980-2017.jpeg', height = 10000, width = 12500, res=400, pointsize=22)
par(mfrow=c(12,12), mar=c(1.5,3.1,1,0.5))
nrow = dim(community.dev.mean)[1]
for(comm in 1:nrow){
  time = 1:(ncol-1)
  y = community.dev.mean[comm,2:ncol] 
  print(max(y))
  
  # create plot frame
  plot(time, y, type='n',  ylim = c(-20,20), las=1, ylab = "", xlab="", axes=FALSE)
  
  # add points
  points(time, y, pch=20, col="#302B54", cex=0.2)
  
  # add horizontal lines
  sd1 = sd.prcp.community[comm] # 1 standard deviation
  abline(h=0, lty=1, lwd=0.5, col="black") # at zero
  abline(h=c(-sd1,sd1), col="red", lty=2, lwd=0.5) # within 1 sd
  abline(h=c(-2*sd1,2*sd1), col="red", lty=3, lwd=0.3) # within 2 sd
  
  # axes
  axis(1, at=seq(1,ncol-1, 24), labels=seq(1980,2017, 2), cex.axis=0.3, tick=FALSE, line=-1.2)
  rug(seq(1,ncol-1, 24), ticksize = 0.03)
  axis(2, at=seq(-20,20, 5), cex.axis=0.45, las=1)
  
  # box
  box()
  
  # margin text
  mtext("Temp (°C)", side=2, line=2, cex=0.5)
  # mtext("Time", side=1, line=2, cex=0.6)
  mtext(paste0("Community #", comm), side=3, cex=0.5)
  
  # legend
  legend(350, 20, legend=c("1 sd", "2 sd"), col="red", lty=c(2,3), bty="n", cex = 0.3, lwd=c(0.5,0.3))
}
dev.off()
