# Climate Change and Migration

This repository contains `R` code for the Cornell-based project on climate change and migration. This code extract climate change data and combine it with survey information from MMP (Mexican Migration Project). 

The key variable upon which data merging relies is the geocode for Mexican localities. Climate change data contains: 18 different variable for human footprint (in 1993 and 2009) and daily climate measures for precipitation, minimum temperature, and maximum temperature (from 1980 to 2017).

---

We provide information for the task performed by each file. Importantly, these files assume that climate change data have been downloaded and stored in specific local paths. 

- `master.R`: 
  * This is the master file that calls all the other files.
  * It contains all libraries and all paths that are used for the data extraction and storage.

- `mx_shapefile_construction.R`: 
  * It uses shapefiles for each Mexican state (taken from INEGI) and construct a Mexican shapefile that contains all urban and rural localities in great detail. 
  * It includes all blocks (i.e. manzanas) from urban areas. 
  * It assumes that `.zip` files were already downloaded and stored locally.

- `subset_polygons_mx_hf.R`: 
  * It reads human footprint files (in `.tif` format) and construct a multi raster object. These files contain human footprints from all over the world in a 1km x 1km grid. 
  * It loops over all `.zip` files and extract spatial information from the state-level Mexican shapefiles (not block-level, as in `mx_shapefile_construction.R`).
  * Finally, it extracts human footprint information for all Mexican states and stores it a local folder named `state_level_footprints` as separate files (one for each state). 
  
- `extract_geocode_mx_sh.R`: 
  * It extracts MMP geocodes (the code assumes that MMP data exists).
  * It creates geocodes for all Mexican localities combining entity (i.e. state), municipality, and locality codes.
  * It checks whether all MMP geocodes exists in geocodes from Mexican shapefiles (block-level). **UPDATE: there are 4 missing geocodes that need to be recovered** (please change or remove when this is done).
  
- `hf2MMP.R`: 
  *
  * 
