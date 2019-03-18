library(plyr)
library(foreign)
library(data.table)

path.mmp = "/home/mario/Documents/environment_data/mmp_data/ind161_w_env.csv"
path.environs = "/home/mario/Documents/environment_data/mmp_data/environs.dta"
path.git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

# data
mmp = fread(path.mmp)
env = read.dta(path.environs)

# rain 
months = c("jan", "feb", "mar", "apr", 
           "may", "jun", "jul", "ago", 
           "sep", "oct", "nov", "dec")
rain.year = paste0("rai", 60:90)
rain.6090 = as.vector( sapply(months, function(x) paste0(x, rain.year)) )

# define state-level norm rain between 1960 and 1990
# state ids
mmp.states = as.numeric(names(table(mmp$state)))
state.names = c("Aguascalientes", "Baja California del Norte", "Baja California del Sur", 
                "Campeche", "Coahuila","Colima","Chiapas","Chihuahua", "Mexico City",
                "Durango", "Guanajuato","Guerrero","Hidalgo","Jalisco",
                "México","Michoacán","Morelos","Nayarit","Nuevo Leon", 
                "Oaxaca","Puebla","Querétaro","Quintana Roo","San Luis Potosí", 
                "Sinaloa","Sonora","Tabasco","Tamaulipas","Tlaxcala",
                "Veracruz", "Yucatán", "Zacatecas")


state.names.sub = state.names[mmp.states] # state names subset
# rain norm
state.rain.norm = rowMeans(env[mmp.states,rain.6090])
# rain standard deviation
state.rain.sd = apply(env[mmp.states,rain.6090], 1, sd)
# deviation from the norm over time
state.dev.mean = env[mmp.states,rain.6090] - state.rain.norm


# create plot for rain
setwd(path.git)
jpeg('./results/prcp_mmp_1960-1990.jpeg', height = 7000, width = 5500, res=450, pointsize=22)
par(mfrow=c(6,4), mar=c(1.5,3.1,1,0.5))
for(state in 1:dim(state.dev.mean)[1]){
  time = 1:dim(state.dev.mean)[2]
  y = state.dev.mean[state,] 
  
  # create plot frame
  plot(time, y, type='n',  ylim = c(-250,1000), las=1, ylab = "", xlab="", axes=FALSE)
  
  # add points
  points(time, y, pch=20, col="#302B54", cex=0.2)
  
  # add horizontal lines
  sd1 = state.rain.sd[state] # 1 standard deviation
  abline(h=0, lty=1, lwd=0.5, col="black") # at zero
  abline(h=c(-sd1,sd1), col="red", lty=2, lwd=0.5) # within 1 sd
  abline(h=c(-2*sd1,2*sd1), col="red", lty=3, lwd=0.3) # within 2 sd
  
  # axes
  axis(1, at=seq(1,dim(state.dev.mean)[2], 48), labels=seq(1960,1990, 4), cex.axis=0.42, tick=FALSE, line=-1.2)
  rug(seq(1,dim(state.dev.mean)[2], 48), ticksize = 0.03)
  axis(2, at=seq(-200,1000, 200), cex.axis=0.45, las=1)
  
  # box
  box()
  
  # margin text
  mtext("Rain (mm/month)", side=2, line=2, cex=0.5)
  # mtext("Time", side=1, line=2, cex=0.6)
  mtext(state.names.sub[state], side=3, cex=0.5)
  
  # legend
  legend(270, 950, legend=c("1 sd", "2 sd"), col="red", lty=c(2,3), bty="n", cex = 0.5, lwd=c(0.5,0.3))
}
dev.off()
