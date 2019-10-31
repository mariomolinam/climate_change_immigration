# R Code

This repository contains `R` code for the Cornell-based project on climate change and migration. This code extract climate change data and combine it with survey information from MMP (Mexican Migration Project).

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
  * It checks whether all MMP geocodes exists in geocodes from Mexican shapefiles (block-level). **UPDATE: there are 4 missing geocodes that need to be recovered (please change or remove when this is done)**.

- `hf2MMP.R`:
  * It loops through all MMP geocodes and extract human footprint information for each locality from folder `state_level_footprints/`.
  * At each iteration, it extracts values using weights, so that a fraction of the grid value is considered when only a portion of the polygon overlaps the grid.
  * Each geocode generally contains many blocks and it therefore saves this information in a `.rds` file.
  * Lastly, it computes a weighted average that is then assigned to the MMP gecode.
  * It creates a new MMP file `mmp_w_footprint.csv`.

- `prcp_mx.R`:
  *

- `create_weather_data_for_ML_models.R`:
  * This file creates 9 measures of climate change using weather stressors:
      1. raw precipitation.
      2. raw max temperature.
      3. rax max temperature: number of days > 30 degrees (Celcius).
      4. norm deviation for precipitation: LONG-term norm between 1960-1979.
      5. norm deviation for precipitation: SHORT-term norm between 1980-1984.
      6. norm deviation for max temperature: SHORT-term norm between 1980-1984.
      7. norm percentage for precipitation: SHORT-term norm between 1980-1984.
      8. norm percentage for max temperature: SHORT-term norm between 1980-1984.
      9. warm spells: number of times there are 6 consecutive days with temperature higher than SHORT-norm 1980-1984.
  * It relies on function contained in the file `functions_weather_data_for_ML_models.R`.

-
