# Climate Change and Migration

This repository contains `R` code for the Cornell-based project on climate change and migration. This code extract climate change data and combine it with survey information from MMP (Mexican Migration Project). 

The key variable upon which data merging relies is the geocode for Mexican localities. Climate change data contains: 18 different variable for human footprint (in 1993 and 2009) and daily climate measures for precipitation, minimum temperature, and maximum temperature (from 1980 to 2017).

---

We provide information for the task performed by each file. Importantly, these files assume that that climate change data have been downloaded and stored in specific local paths. 

- `master.R`: 

⋅⋅ -This is the master file that calls all the other files. ⋅⋅
⋅⋅ -It contains all libraries and all paths that are used for the data extraction and storage. ⋅⋅

- `mx_shapefile_construction.R`: It uses shapefiles for each Mexican state (taken from INEGI) and construct a Mexican shapefile that contains all urban and rural localities in great detail. It includes all blocks (i.e. manzanas) from urban areas. It assumes that `.zip` files were already downloaded and stored locally.

- `subset_polygons_mx_hf.R`: It reads human footprint files (in `.tif` format) and construct a multi raster. Then 
