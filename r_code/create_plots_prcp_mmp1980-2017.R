library(foreign)
library(data.table)

path.mmp = "/home/mario/Documents/environment_data/mmp_data/"
path.git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"
path.shapefiles = "/home/mario/Documents/environment_data/mexican_shapefiles/"

###########################################################################
######################### P R E C I P I T A T I O N
setwd( path.shapefiles )
prcp.mmp = as.data.frame(fread("mmp_w_prcp.csv"))
setwd(path.mmp)
env = read.dta("environs.dta")

# time range
years = as.character(1980:2017)

# E N V I R O N S   D A T A
# rain at state level. data coming environs.dta
months = c( "jan", "feb", "mar", "apr", 
            "may", "jun", "jul", "ago", 
            "sep", "oct", "nov", "dec" )
rain.year = paste0("rai", 60:79)
rain.6079 = as.vector( sapply(months, function(x) paste0(x, rain.year)) )

# get only state names that appear in mmp data
mmp.state.names = sapply( prcp.mmp$geocode, function(x) {
                  if(nchar(x) == 8) st = substr(x, start = 1, stop = 1) else st = substr(x, start = 1, stop = 2)
                  return(as.numeric(st))
                } )
prcp.mmp[,"state"] = mmp.state.names
mmp.state.names = unique(mmp.state.names)


# rain monthly norm at state level (1960-1979)
state.rain.norm.monthly = rowMeans(env[mmp.state.names,rain.6079]) # get monthly means
state.rain.norm.monthly = as.data.frame(state.rain.norm.monthly)
colnames(state.rain.norm.monthly) = "norm_monthly"
state.rain.norm.monthly[,"state"] = rownames(state.rain.norm.monthly) 

# rain yearly norm at state level (1960-1979)
state.rain.norm.yearly = c()
for(y in rain.year){
  idx = grep(y, names(env))
  state.rain.yearly = rowSums(env[mmp.state.names,idx]) # get yearly means 
  state.rain.norm.yearly = cbind(state.rain.norm.yearly, as.matrix(state.rain.yearly) )
}
state.rain.norm.yearly = as.data.frame( rowMeans(state.rain.norm.yearly) )
colnames(state.rain.norm.yearly) = "norm_yearly"
state.rain.norm.yearly[,"state"] = rownames(state.rain.norm.yearly) 


# merge prcp.mmp with prcp state norm by using state ID
prcp.mmp = merge(prcp.mmp, state.rain.norm.monthly, by="state")
prcp.mmp = merge(prcp.mmp, state.rain.norm.yearly, by="state")


# P R C P   D A T A
ncol = ncol(prcp.mmp) - 1 # last column is "state.rain.norm.monthly"
nmonths = list() 
months = c(31,28,31,30,31,30,31,31, 30,31,30,31)
for(y in 1:length(years)) {
  if(y==1) nmonths[[y]] = cumsum(c(1,months)) else nmonths[[y]] =  cumsum( c( (365*(y-1)+1), (months)) )    # c( (365*(y-1)+1),(365*y) ) 
}

# prcp mmp monthly
prcp.mmp.monthly = prcp.mmp[,c("geocode", "state")]
prcp.mmp.yearly = prcp.mmp[,c("geocode", "state")]

prcp.data.prel = prcp.mmp[,3:ncol]

for(y in 1:length(nmonths) ){
  month = nmonths[[y]]
  for(m in 2:length(month)){
    range.month = (month[m-1]):(month[m]-1)
    sum.monthly = rowSums(prcp.data.prel[,range.month])
    # monthly sum
    prcp.mmp.monthly = cbind( prcp.mmp.monthly, sum.monthly )   
  }
  # build yearly measures of prcp 
  range.year = (month[1]) : (month[13]-1)
  sum.yearly = rowSums(prcp.data.prel[,range.year])
  prcp.mmp.yearly = cbind(prcp.mmp.yearly, sum.yearly)
}


# calculate the monthly/yearly average (monthly prcp state norm) of prcp across communities
lastcol.month = ncol(prcp.mmp.monthly)
lastcol.year = ncol(prcp.mmp.yearly)
# monthly deviation at community level (1980-2017) from the state mean (1960-1979)
dev.community.monthly = prcp.mmp.monthly[,3:lastcol.month] - prcp.mmp[,"norm_monthly"]
dev.community.yearly = prcp.mmp.yearly[,3:lastcol.year] - prcp.mmp[,"norm_yearly"]
# standard deviation of communities (1980-2017) from state-level mean  
sd.prcp.state.monthly = sqrt( rowMeans( (dev.community.monthly)^2 )  )
sd.prcp.state.yearly = sqrt( rowMeans( (dev.community.yearly)^2 )  )
# 
community.dev.mean.monthly = cbind( prcp.mmp.monthly[,"geocode"], dev.community.monthly)
community.dev.mean.yearly = cbind( prcp.mmp.yearly[,"geocode"], dev.community.yearly)

# add column names
months = c("jan", "feb", "mar", "apr", 
           "may", "jun", "jul", "ago", 
           "sep", "oct", "nov", "dec")
year.month = c()
for(y in years) year.month = c(year.month, paste0(months, "-", y))
year.month = paste0("prcp-",year.month)
# for monthly data
colnames(community.dev.mean.monthly) = c("geocode", year.month)
# for yearly data
colnames(community.dev.mean.yearly) = c("geocode", paste0("prcp-",years))

# save community-level monthly/yearly norm deviation between 1980 and 2017
setwd(path.mmp)
write.csv(community.dev.mean.monthly, "prcp_monthly_dev-norm_1980-2017.csv", row.names = FALSE)
write.csv(community.dev.mean.yearly, "prcp_yearly_dev-norm_1980-2017.csv", row.names = FALSE)

############################################################################
######  P L O T   
# create plot for rain
setwd(path.git)
jpeg('./results/prcp_mmp_yearly_1980-2017.jpeg', height = 10000, width = 12500, res=400, pointsize=22)
par(mfrow=c(12,12), mar=c(1.5,3.1,1,0.5))
nrow = nrow(community.dev.mean.yearly)
ncol = ncol(community.dev.mean.yearly)
for(comm in 1:nrow){
  time = 1:(ncol-1)
  y = community.dev.mean.yearly[comm,2:ncol] 
  print(max(y))
  
  # create plot frame
  plot(time, y, type='n',  ylim = c(-2000,2000), las=1, ylab = "", xlab="", axes=FALSE)
  
  # add points
  points(time, y, pch=20, col="#302B54", cex=0.7)
  
  # add horizontal lines
  sd1 = sd.prcp.state.yearly[comm] # 1 standard deviation
  abline(h=0, lty=1, lwd=0.5, col="black") # at zero
  abline(h=c(-sd1,sd1), col="red", lty=2, lwd=0.5) # within 1 sd
  abline(h=c(-2*sd1,2*sd1), col="red", lty=3, lwd=0.3) # within 2 sd
  
  # axes
  axis(1, at=seq(1,ncol-1, 1), labels=seq(1980,2017, 1), cex.axis=0.3, tick=FALSE, line=-1.2)
  rug(seq(1,ncol-1, 1), ticksize = 0.03)
  axis(2, at=seq(-2000,2000, 400), cex.axis=0.45, las=1)
  
  # box
  box()
  
  # margin text
  mtext("Rain (mm/year)", side=2, line=2, cex=0.5)
  # mtext("Time", side=1, line=2, cex=0.6)
  mtext(paste0("Community #", comm), side=3, cex=0.5)
  
  # legend
  legend(26, 1450, legend=c("1 sd", "2 sd"), col="red", lty=c(2,3), bty="n", cex = 0.3, lwd=c(0.5,0.3))
}
dev.off()
