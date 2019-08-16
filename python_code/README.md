# Python Code

This repository contains `python` code for the Cornell-based project on climate change and migration. This code builds a primary dataset that combines MMP data with climate data, and then subsets the data into training/validation and test.

Our weather data starts in 1980 until 2017 and our data construction ensures that we have at least 5  

we construct our primary dataset by removing all information that takes place before 1980.   

We use 3 forms of data structure:
  1) **person-year structure WITHOUT augmentation (long format)**: each observation is person-year and the dependent variable is coded 1 at the year level, i.e., for the year of actual migration. For migrants, we keep the year of migration along with the 4 previous years
  2) **person-year structure WITH augmentation (long format)**: each observation is person-year and the dependent variable is coded 1 at the year level, i.e., for the year of actual migration.
  3) **person structure (wide format)**: each observation is person, the dependent variable is coded 1 if person is a migrant, and time-varying information is added as features.


We provide information for the task performed by each file. Importantly, these files assume that climate change data have been downloaded, stored in specific local paths, and measures of climate change have already been created.

- `functions_RF.py`:
  * This file contains functions that implement a random forest model.

- `functions_clean_data.py`:
  * This file contains all functions that clean data and provide specific data structures.
