import pandas as pd
from define_paths import *
import data_cleaning.functions_clean_data as func

# # load data
# filename = "ind161_w_env.csv"
# full_path = path_data + '/' + filename
# d = pd.read_csv(full_path, dtype="str")
#
# ############################################
# # select columns and save as csv file
# subset = func.select_columns(d)
# subset.to_csv(path_data + "/ind161_w_env-subset.csv", index=False)
# del d, subset # remove d from environment

############################################
# load subset data
filename = path_data + "/ind161_w_env-subset.csv"
all = pd.read_csv(filename, dtype="str")
all = all.sort_values(by=["persnum", "year"])

# list with weather files
weather_data = [ x for x in os.listdir(path_data)
                        if x.startswith("crude")
                        or x.startswith("norm")
                        or x.startswith("warm") ]


############################################
# Create 3 different data structures
data_struc_keys = ['long_noaug', 'long_aug', 'wide']

# Create data structuresbased on keys from data_struc_keys
func.create_data_structures(all, data_struc_keys, weather_data)
