# Climate Change and Migration

This repository contains `R` and `python` code for the Cornell-based project on climate change and migration. All this code extracts climate change data, combine it with survey information from MMP (Mexican Migration Project), and run machine learning models to predict migration. Code in each programming language is stored in a separate folder (`r_code` and `python_code`) and a third folder includes results (in `results`), which stores results using both `R` and `python`.

The key variable upon which data merging relies is the geocode for Mexican localities. Climate change data contains: 18 different variable for human footprint (in 1993 and 2009) -taken from the human footprint project (<a href="https://wcshumanfootprint.org/" target="_blank">click here</a>)- and daily climate measures for precipitation, minimum temperature, and maximum temperature (from 1980 to 2017) - taken NASA Dayment ([click here](https://daymet.ornl.gov/)).
