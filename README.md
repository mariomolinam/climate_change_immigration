# Climate Change and Migration Project


This repository contains `R` and `python` code for the Cornell-based project on climate change and migration. All this code extracts climate change data, combine it with survey information from MMP (Mexican Migration Project), and run machine learning models to predict migration. 

Code in each programming language is stored in a separate folder (`r_code` and `python_code`). A third folder `results` includes results, which stores figures and tables produced using both `R` and `python`.

## Code

### R code
The `R` code does several operations needed before running random forests for the analysis. In particular:
- It processes Mexico's shapefiles. 
- It creates weather information using data from Dayment
- It computes weather measures described on the paper and it creates files with these variables that will be used with the MMP data using `python` code.

### Python code
The `python` code runs the random forests using `scikit-learn`.


## Data

### Mexican Shapefiles
Data for Mexico's map can be downloaded here: https://www.inegi.org.mx/app/mapas/. This project uses the "Marco Geoestaditico, febrero 2018", and it can be accessed using [this link](https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463526636_s.zip). (**NOTE**: If you click on this link, you will start downloading the Mexican shapefiles (~3Gb) right away.)

### Dayment
Daily climate measures for precipitation, minimum temperature, and maximum temperature (from 1980 to 2017) are taken from NASA Dayment and you can access the data [here](https://daymet.ornl.gov/)). To download the raster files for North America, you need to create an account first.

### Mexican Migration Project
You need to get access to the restricted data from the [Mexican Migration Project](https://mmp.opr.princeton.edu/), which includes geocodes for the communities available in the MMP data.
