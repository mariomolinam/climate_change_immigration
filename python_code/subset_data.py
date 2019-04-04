import pandas as pd
import sys, os
sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code")
import functions as func


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

# load data
filename = "ind161_w_env.csv"
full_path = path_data + '/' + filename
d = pd.read_csv(full_path, dtype="str")

# select columns and save as csv file
subset = func.select_columns(d)
subset.to_csv(path_data + "/ind161_w_env-subset.csv", index=False)
del d, subset # remove d from environment


# load subset data
filename = path_data + "/ind161_w_env-subset.csv"
all = pd.read_csv(filename, dtype="str")
all = all.sort_values(by=["persnum", "year"])

# list with weather files
weather_data = [ x for x in os.listdir(path_data)
                        if x.startswith("crude")
                        or x.startswith("norm")
                        or x.startswith("warm") ]

# restrain data to
sub_all = func.select_data(all)
# correct info for some migrants
sub_all = func.correct_migrants(sub_all)
# keep only 5 person-year observations
sub_all = func.keep_five_person_year(sub_all)
# attach weather information
mmp_data_weather = func.attach_weather_by_geocode(sub_all, weather_data)

mmp_data_weather = func.relabel_variables(mmp_data_weather)

# create training and test set
func.create_test_set(mmp_data_weather)
