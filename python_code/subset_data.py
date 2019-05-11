import pandas as pd
import sys, os
sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code")
import functions_clean_data as func


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

# load data
filename = "ind161_w_env.csv"
full_path = path_data + '/' + filename
d = pd.read_csv(full_path, dtype="str")

############################################
# select columns and save as csv file
subset = func.select_columns(d)
subset.to_csv(path_data + "/ind161_w_env-subset.csv", index=False)
del d, subset # remove d from environment

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
data_struc = ['long_noaug', 'long_aug', 'wide']

for entry in data_struc:

    # restrain data to years around 1980
    sub_all = func.select_data(all, data_structure = entry)

    # correct info for some migrants
    sub_all = func.correct_migrants(sub_all)

    # keep only 5 person-year observations
    sub_all = func.keep_five_person_year(sub_all)

    # relabel migf=1 for past info of migrants
    sub_all = func.add_migrant_info(sub_all, data_structure = entry)

    # attach weather information
    mmp_data_weather = func.attach_weather_5_year_lags(sub_all, weather_data)

    # relabel all variables
    mmp_data_weather = func.relabel_variables(mmp_data_weather)

    # LONG FORMAT: create training and test set in LONG format
    func.create_test_set(data=mmp_data_weather, data_structure=entry)

    # WIDE FORMAT: create training and test set in WIDE format
