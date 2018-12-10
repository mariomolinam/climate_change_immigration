

setwd("/home/mario/Documents/environment_data/mexican_shapefiles/mmp_prcp")

mx.geo = readRDS("geo_010030084.rds")
prcp.names = names(mx.geo[[1]][[1]])[grep("_weighted", names(mx.geo[[1]][[1]]) )]


max(mx.geo[[1]][[1]]@data[20,prcp.names])

pal = colorRampPalette(c("snow", "dodgerblue4"))

# all month lengths
month.len= c(1, cumsum( c(31,28,31,30,31,30,31,31,30,31,30,31) ))
month.name = c("January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", 
               "December")
# list with monthly data
prcp = list()
for( m in 2:(length(month.len)) ){
  (subsetting = month.len[m-1] : month.len[m])
  prcp[[m-1]] = mx.geo[[1]][[1]]@data[,prcp.names[subsetting] ]
}
# take the mean values of each month
prcp.summary = lapply(prcp, function(x) apply(x,1,mean) )
min.max = round( unique(unlist(prcp.summary)), 1 )



colors.blue = pal(7)
years=seq(1980,2017,1)
png("prcp_geo.png", height=2000, width=2000, res=60)
par(mfrow=c(8,6))
for(j in c(1,10,20,38)){
  prcp.names = names(mx.geo[[j]][[1]])[grep("_weighted", names(mx.geo[[j]][[1]]) )]
  prcp = list()
  for( m in 2:(length(month.len)) ){
    (subsetting = month.len[m-1] : month.len[m])
    prcp[[m-1]] = mx.geo[[j]][[1]]@data[,prcp.names[subsetting] ]
  }
  # take the mean values of each month
  prcp.summary = lapply(prcp, function(x) apply(x,1,mean) )
  
  for(i in 1:length(prcp.summary)){
    main.name = paste(month.name[i], paste0('(', years[j],')'))
    plot(mx.geo[[j]][[1]], col=colors.blue[ceiling(prcp.summary[[i]])], main = main.name)
  }
}
dev.off()


png("prcp_trends_daily.png", height=1700, width=2500, res=80)
par(mfrow=c(8,12))
for(j in c(1,5,10,15,20,25,30,38)) {
  prcp.names = names(mx.geo[[j]][[1]])[grep("_weighted", names(mx.geo[[j]][[1]]) )]
  prcp = list()
  for( m in 2:(length(month.len)) ){
    (subsetting = month.len[m-1] : month.len[m])
    prcp[[m-1]] = mx.geo[[j]][[1]]@data[,prcp.names[subsetting] ]
  }
  # take the mean values of each month
  prcp.summary = lapply(prcp, function(x) apply(x,2,mean) )
  
  for(i in 1:length(prcp.summary)){
    main.name = paste(month.name[i], paste0('(', years[j],')'))
    x = prcp.summary[[i]]
    plot(x, main = main.name, type='l', ylim=c(0,30), xlab='Days', ylab='Cumulative Precipation (daily)', 
         bty="n", col="red", xaxt="n", yaxt="n")
    axis(1, at=1:length(x))
    axis(2, at=seq(0,30,5), cex.axis=0.7)
    
  }
}
dev.off()


png("prcp_trends_cumulative_month.png", height=2000, width=2500, res=90)
par(mfrow=c(8,12))
for(j in c(1,5,10,15,20,25,30,38)) {
  prcp.names = names(mx.geo[[j]][[1]])[grep("_weighted", names(mx.geo[[j]][[1]]) )]
  prcp = list()
  for( m in 2:(length(month.len)) ){
    (subsetting = month.len[m-1] : month.len[m])
    prcp[[m-1]] = mx.geo[[j]][[1]]@data[,prcp.names[subsetting] ]
  }
  # take the mean values of each month
  prcp.summary = lapply(prcp, function(x) apply(x,2,mean) )
  
  for(i in 1:length(prcp.summary)){
    main.name = paste(month.name[i], paste0('(', years[j],')'))
    x = prcp.summary[[i]]
    plot(cumsum(x), main = main.name, type='l', ylim=c(0,210), xlab='Days', ylab='Cumulative Precipation (daily)', 
         bty="n", col="red", xaxt="n", yaxt="n")
    axis(1, at=1:length(x))
    axis(2, at=seq(0,210,25), cex.axis=0.7)
    
  }
}
dev.off()



png("prcp_trends_cumulative_year.png", height=1500, width=900, res=70)
par(mfrow=c(8,5))
for(j in 1:38){
  prcp.names = names(mx.geo[[j]][[1]])[grep("_weighted", names(mx.geo[[j]][[1]]) )]
  prcp = mx.geo[[j]][[1]]@data[,prcp.names ]
  
  # take the mean values of each month
  prcp.summary = apply(prcp,2,mean)
  
  main.name = paste('Year', years[j])
  plot(cumsum(prcp.summary), main = main.name, type="l", ylim=c(0,850), 
       xlab='Days', ylab='Cumulative Precipation (daily)', 
       bty="n", col="red", xaxt="n", yaxt="n")
  
  axis(1, at=seq(0,length(prcp), 30), cex.axis=0.7)
  axis(2, at=seq(0,850,100), cex.axis=0.7)
  
}
dev.off()




