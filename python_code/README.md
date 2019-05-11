# Python Code

This repository contains `python` code for the Cornell-based project on climate change and migration. This code builds a primary dataset that combines MMP data with climate data, and then subsets the data into training/validation and test.

Our weather data starts in 1980 until 2017. Therefore, we construct our primary dataset by removing all observations whose year of migration is 1985 (for migrants) or whose year of survey is 1985   

We use 3 forms of data structure:
..* *person-year stucture WITHOUT augmentation (long format)*: each observation is person-year and the dependent variable is coded 1 at the year level, i.e., for the year of actual migration. For migrants, we keep the year of migration along with the 4 previous years
..* *person-year stucture WITH augmentation (long format)*: each observation is person-year and the dependent variable is coded 1 at the year level, i.e., for the year of actual migration.
..* *person stucture (wide format)*: each observation is person, the dependent variable is coded 1 if person is a migrant, and time-varying information is added as features.


We provide information for the task performed by each file. Importantly, these files assume that climate change data have been downloaded and stored in specific local paths.

- `master.R`:
  * This is the master file that calls all the other files.
  * It contains all libraries and all paths that are used for the data extraction and storage.
