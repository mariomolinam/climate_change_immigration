#!/usr/bin/python
# add python_code folder as directory to search for modules
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("python_code"), ".")))

# Create datasets
import data_cleaning.subset_data

# Run Random Forests
import random_forests


#
if __name__ == '__main__':
    print("Running random forests...")
