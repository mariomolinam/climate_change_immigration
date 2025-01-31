# Python Code

This code builds the primary dataset used for the analyses on the paper. It also subsets the data into training (75%) and test sets (25%) and runs random-forests models with different specifications, as reported on the paper.

The `run.py` file provides a basic rubric to structure the files and the `define_paths.py` file defines the paths used for the analysis. If you try to reproduce the results on the paper, make sure that you have the right paths.

The `data_cleaning` folder contains code the creates the main dataset used for analyses. Within this folder, the file `functions_clean_data.py` specifies functions used to subset the original dataset.

The `rf` folder contains the code that runs random forests. The code uses scikit-learn for the analysis. Within this folder, the file `functions_RF.py` creates functions that help with the analysis of the data and the file `plots_RF.py` contains code to create figures 3, 4, and 5 on the paper. 
