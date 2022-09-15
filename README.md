# Climate Change and Migration Project


This repository contains `R` and `python` code for my project on climate change and migration in collaboration with Nancy Chau (Cornell University), Amanda D. Rodewald (Cornell University) and Filiz Garip (Princeton University). 

We wrote an article together using this code, which was published at the Journal of Ethnic and Migration Studies in 2022 ([link to the article](https://doi.org/10.1080/1369183X.2022.2100549)).

The code extracts weather data and creates weather measures used for the analyses. It also combines it with survey information from MMP (Mexican Migration Project), and run random-forests models to predict migration. The code for each programming language is stored in separate folders (`r_code` and `python_code`). A third folder `results` stores the results that appeared on the paper (figures and tables).

**NOTE**: There is a lot of code in this repository! Although I tried to create master files (`00-master.R` and `run.py`) that help reproduce the results step by step and added comments to explain what almost all the code does, it may be difficult to navigate all the files. Please reach out if you have a hard time trying to understand some parts of the code structure. 

## Code

### R code

The `R` code does several operations needed before running the random-forests models for the analysis. In particular:
- It processes Mexico's shapefiles. 
- It creates weather information using data from Dayment
- It computes weather measures described on the paper and it creates files with these variables that will be used with the MMP data using `python` code.
- It creates figure 2 on the paper.

### Python code
The `python` code runs random forests using `scikit-learn`. In particular, 
- It manipulates the data containing the MMP survey and Daymet weather measures and prepares the data for the analysis.
- It creates figures 3, 4, and 5 on the paper.
- It gives the results presented in tables 2 and 3 on the paper.


## Data

### Mexican Shapefiles
Data for Mexico's map can be downloaded here: https://www.inegi.org.mx/app/mapas/. This project uses the "Marco Geoestaditico, febrero 2018", and it can be accessed using [this link](https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463526636_s.zip). (**NOTE**: If you click on this link, you will start downloading the Mexican shapefiles (~3Gb) right away.)

### Dayment
Daily climate measures for precipitation, minimum temperature, and maximum temperature (from 1980 to 2017) are taken from NASA Dayment and you can access the data [here](https://daymet.ornl.gov/)). To download the raster files for North America, you need to create an account first.

### Mexican Migration Project
You need to get access to the restricted data from the [Mexican Migration Project](https://mmp.opr.princeton.edu/), which includes geocodes for the communities available in the MMP data.
