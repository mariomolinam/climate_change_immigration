
# Load Mexican map with states only
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
cat('Done!', '\n')


# Load MMP data (subset of columns)
# mmp = fread("mmp_data/ind161_w_env-subset.csv")
mmp = fread("mmp_data/ind161_w_env.csv")

# create state ID variable
mmp[,"state_id"] =  sapply( as.character(mmp$geocode), function(x) if(nchar(x)==9) substr(x, 1, 2) else paste0("0",substr(x, 1, 1)))

###########################################
### M I G R A N T S   B Y   T I M E
mmp[,"time_mig"] = NA
mmp[,"time_mig"] = ifelse( mmp$usyr1 >= 1900 &mmp$usyr1 <=1979, "1900-1979",
                           ifelse( mmp$usyr1 >= 1980 &mmp$usyr1 <=1989, "1980-1989",  
                                   ifelse(mmp$usyr1 >= 1990 &mmp$usyr1 <=1999, "1990-1999", 
                                          ifelse(mmp$usyr1 >= 2000 &mmp$usyr1 <=2019, "2000-2016", "no_migration"))))


##################################
###  F I G U R E   1
##################################

# Load Mexican map with states only
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
cat('Done!', '\n')


# class names to color states 
assign_class = function(x,mig){
  if(mig=="abs"){
    if(is.na(x)){
      class = "No data"
    } else if(x==0){
      class = "0"
    } else if(x > 1 & x <= 100){
      class = "1-100"
    } else if(x >100 & x <= 500){
      class = "101-500"
    } else if(x > 500){
      class = "> 500"
    } 
  } else{
    if(is.na(x)){
      class = "No data"
    } else if(x >= 0 & x <= 5 ){
      class = "0%-5%"
    } else if(x > 5 & x <= 10 ){
      class = "6%-10%"
    } else if(x > 10 & x <= 15 ){
      class = "10%-15%"
    } else if(x > 15 & x <= 20 ){
      class = "15%-20%"
    } else if(x > 20 ){
      class = "> 20%"
    }
  }
  return(class)
}

# for loop
# N_TIMES = names(table(mmp[,"time_mig"]))[-length(names(table(mmp[,"time_mig"])))]
N_TIMES = names(table(mmp[,"time_mig"]))[-length(names(table(mmp[,"time_mig"])))][2:4]

# define 2x2 grid for plotting
setwd(path.git)

fig_name = paste0("./results/figure1.tiff")
bitmap(fig_name, height=5, width=12,units="in",type="tiff24nc",res=170)

opar = par(mfrow=c(1,3), mar=c(bottom=0,left=1,top=2,right=1))
opar$mar = c(1,1,1,1)


for(t in N_TIMES){
  
  # get number of migrants per state
  # n_mig = aggregate(mmp[mmp$time_mig==t,"migf"], 
  #                   by=list(mmp[mmp$time_mig==t,state_id]), 
  #                   function(x) sum(x))
  # colnames(n_mig) = c("state_id", paste0("n_mig_",t))
  
  # get prevalence of migration in community-year ("prev")
  chunk = mmp[mmp$time_mig==t,c("commun", "persnum","prev","year", "state_id")]
  # reduce data to only years given in time_mig
  years = as.numeric(strsplit(t,"-")[[1]])
  chunk = chunk[chunk$year>=years[1] & chunk$year<=years[2],]
  
  # reduce observations that are redundant (get unique values by state, year, comuna)
  p_mig_unique = aggregate(chunk$prev, 
                    by=list(chunk$state_id, chunk$year, chunk$commun), 
                    function(x) unique(x))
  
  # aggregate by state and year first
  p_mig_year = aggregate(p_mig_unique$x,
                     by=list(p_mig_unique[,1], p_mig_unique[,2]), 
                     function(x) mean(x))
  # aggregate by state over years
  p_mig_state = aggregate(p_mig_year$x,
                         by=list(p_mig_year[,1]), 
                         function(x) mean(x))
  
  colnames(p_mig_state) = c("state_id", paste0("n_mig_",t))
  
   mig = p_mig_state
   in_name = "prev"
   legend_title = "Number of Migrants"
   class_names = c("No data", "0%-5%", "5%-10%", "10%-15%", "15%-20%", "> 20%")
   # merge n_mig to mx.ent data
   mx.ent@data = merge(mx.ent@data, mig, by.x="CVE_ENT", by.y="state_id", all.x=TRUE)

  # assign values to classes
  class = sapply(mx.ent@data[,colnames(mig)[2]], function(x) assign_class(x,in_name))
  
  # PLOT
  ncolors = 9
  colors_pal = brewer.pal(ncolors,"Greens")[c(2,3,5,7,9)]
  names(colors_pal) = class_names[-1]
  class_color = colors_pal[match(class, names(colors_pal))]
  
  # BACKGROUND = WHITE
  par(bg="white", mar = c(bottom=0, left=0, top=0, right=0) )
  plot(mx.ent[,colnames(mig)[2]], col=class_color, border="black")
  plot(mx.ent[as.numeric(which(is.na(class_color))),colnames(mig)[2]], col="black", density=30, border="black",add=TRUE)

  title = t
  text(2500000, 2500000, title, font=2, cex=2.7, col="black")
  legend(3200000, 2200000, legend=names(colors_pal),
         fill=colors_pal, cex=2.5, bty="n", border="white", 
         text.col = "black")
  
}
dev.off()



