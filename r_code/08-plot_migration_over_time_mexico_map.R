
# Load Mexican map with states only
setwd(path.shapefiles)
cat('\n', 'Reading Mexican shapefiles...', '\n')
mx.ent = readOGR("mexican_shapefiles/.", layer='mx_ent')
mx.ent@data = mx.ent@data[,c("CVE_ENT", "NOMGEO")]
cat('Done!', '\n')


# Load MMP data
mmp = fread("mmp_data/ind161_w_env-subset.csv")

# create state ID variable
mmp[,"state_id"] =  sapply( as.character(mmp$geocode), function(x) if(nchar(x)==9) substr(x, 1, 2) else paste0("0",substr(x, 1, 1)))

###########################################
### M I G R A N T S   B Y   T I M E
mmp[,"time_mig"] = NA
mmp[,"time_mig"] = ifelse( mmp$usyr1 >= 1900 &mmp$usyr1 <=1979, "1900-1979",
                           ifelse( mmp$usyr1 >= 1980 &mmp$usyr1 <=1989, "1980-1989",  
                                   ifelse(mmp$usyr1 >= 1990 &mmp$usyr1 <=1999, "1990-1999", 
                                          ifelse(mmp$usyr1 >= 2000 &mmp$usyr1 <=2019, "2000-2016", "no_migration"))))

###########################################
### P L O T   M I G R A N T S  ( A L L)

setwd(path.git)
bitmap("./results/migration_map_1900-2016.tiff", height=6, width=6,units="in",type="tiff24nc",res=200)

# assign absolute values to class (number are arbitrarily decided)
class_names = c("No data","1-500", "501-1000", "> 1000")
assign_class = function(x){
  if(is.na(x)){
    class = "No data"
  } else if(x > 0 & x <= 500){
    class = "1-500"
  } else if(x >500 & x <= 1000){
    class = "501-1000"
  } else if(x > 1000){
    class = "> 1000"
  }
  return(class)
}

### NUMBER OF MIGRANTS
# get number of migrants per state
n_mig = aggregate(mmp$migf, by=list(mmp$state_id), sum)
colnames(n_mig) = c("state_id", "n_mig")

# get proportion of migrants per state
n_ind_state = aggregate(mmp$persnum, by=list(mmp$state_id), function(x) length(unique(x)) )
prop_mig = data.frame(n_mig[,1], round(n_mig[,2]/n_ind_state[,2],2))
colnames(prop_mig) = c("state_id", "prop_mig")

# merge n_mig to mx.ent data
mx.ent@data = merge(mx.ent@data, n_mig, by.x="CVE_ENT", by.y="state_id", all.x=TRUE)
# mx.ent[is.na(mx.ent$n_mig),"n_mig"] = 0 # replace NA values

### PLOT

# colcode = findColours(class, colors_pal)

# PLOT
ncolors = length(class_names)
colors_pal = brewer.pal(ncolors,"Blues")
names(colors_pal) = class_names
# assign values to classes
class = sapply(mx.ent@data[,"n_mig"], assign_class)
class_color = colors_pal[match(class, names(colors_pal))]


plot(mx.ent[,"n_mig"], col=class_color)
par("usr") # get coordinates
text(2500000, 2500000, "Mexican Migration to the US (1900-2016)", font=2, cex=1.2)
legend(3200000, 2200000, legend=names(colors_pal),
       fill=colors_pal, cex=0.7, bty="n")

dev.off()


####################################################################
### P L O T   M I G R A N T S  (B Y   T I M E)

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
    } else if(x==0.0){
      class = "0.0"
    } else if(x > 0 & x <= 0.33){
      class = "0.0-0.33"
    } else if(x > 0.33 & x <= 0.66){
      class = "0.34-0.66"
    } else if(x > 0.66){
      class = "> 0.66"
    }
  }
  return(class)
}

# for loop
N_TIMES = names(table(mmp[,"time_mig"]))[-length(names(table(mmp[,"time_mig"])))]

# define 2x2 grid for plotting
setwd(path.git)
# opar = par(mfrow=c(2,2), mar=c(bottom=0,left=1,top=2,right=1))
# opar$mar = c(1,1,1,1)
for(t in N_TIMES){
  
  # get number of migrants per state
  n_mig = aggregate(mmp[mmp$time_mig==t,"migf"], 
                    by=list(mmp[mmp$time_mig==t,state_id]), 
                    function(x) sum(x))
  colnames(n_mig) = c("state_id", paste0("n_mig_",t))
  
  # get proportion of migrants per state
  # n_ind_state = aggregate( mmp[,"persnum"], 
  #                          by=list(mmp[,state_id]), 
  #                          function(x) length(unique(x)) )
  # 
  # mig_merge = merge(n_mig,n_ind_state,by.x="state_id",by.y="Group.1")
  # 
  # prop_mig = data.frame( n_mig[,1], round(mig_merge[,2]/mig_merge[,3],2) )
  # colnames(prop_mig) = c("state_id", paste0("prop_mig_",t))
  
  # for(j in 1:2){
   # if(j==1) {
     mig = n_mig
     in_name = "abs"
     legend_title = "Number of Migrants"
     class_names = c("No data", "0", "1-100", "101-500", "> 500")
     # merge n_mig to mx.ent data
     mx.ent@data = merge(mx.ent@data, mig, by.x="CVE_ENT", by.y="state_id", all.x=TRUE)
   # } else{
   #   mig = prop_mig
   #   in_name = "prop"
   #   class_names = c("No data", "0.0", "0.0-0.33", "0.34-0.66", "> 0.66")
   #   legend_title = "Proportion of Migrants"
   #   # merge n_mig to mx.ent data
   #   mx.ent@data = merge(mx.ent@data, mig, by.x="CVE_ENT", by.y="state_id", all.x=TRUE)
   # }
    # figure name
    fig_name = paste0("./results/migration_map_", t,"_", in_name, ".tiff")
    bitmap(fig_name, height=7, width=8,units="in",type="tiff24nc",res=200)
    
    # assign values to classes
    class = sapply(mx.ent@data[,colnames(mig)[2]], function(x) assign_class(x,in_name))
    
    # PLOT
    ncolors = 9
    colors_pal = brewer.pal(ncolors,"Greens")[c(3,5,7,9)]
    names(colors_pal) = class_names[-1]
    class_color = colors_pal[match(class, names(colors_pal))]
    
    par(bg="black")
    plot(mx.ent[,colnames(mig)[2]], col=class_color, border="white")
    plot(mx.ent[as.numeric(which(is.na(class_color))),colnames(mig)[2]], col="white", density=30, border="white",add=TRUE)
    
    # par("usr") # get coordinates
    # title = paste0("Mexican Migration to the US (", t,")")
    title = t
    text(2500000, 2400000, title, font=2, cex=1.2, col="white")
    legend(3200000, 2200000, legend=names(colors_pal),
           fill=colors_pal, cex=0.9, bty="n", border="white", 
           text.col = "white", title=legend_title)
    
    # kill bitmap()
    dev.off()
  # }
}

# title of figure
# mtext("Mexican Migration to the US (1900-2016)", side=3, outer=TRUE, line=-3, font=2, cex=1.3)



