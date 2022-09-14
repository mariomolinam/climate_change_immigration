import pandas as pd
from define_paths import *
import data_cleaning.functions_clean_data as func


############################################
# load subset data
filename = path_data + "/ind161_w_env-subset.csv"
all = pd.read_csv(filename, dtype="str")
all = all.sort_values(by=["persnum", "year"])

# list with weather files
weather_data = [ x for x in os.listdir(path_data)
                        if x.startswith("prcp")            # 1. raw prcp & 7. multiple days
                        or x.startswith("crude")           # 2. raw tmax
                        or x.startswith("norm_deviation")  # 3. long-term & 4. short-term norms
                        or x.startswith("extremely")       # 3. long-term norm
                        or x.startswith("norm_percent")    # 4. short-term norm
                        or x.startswith("spell")           # 5. spells
                        or x.startswith("warmest")         # 6. single days
                        or x.startswith("coldest")         # 6. single days
                        or x.startswith("max")             # 7. multiple days
                        or x.startswith("total")           # 7. multiple days
                        or x.startswith("tmax")            # 7. multiple days
                        or x.startswith("tmin")            # 7. multiple days
                        or x.startswith("perc")            # 8. percentage-based
                        or x.startswith("gdd")             # 9. growing
                        or x.startswith("hdd")             # 9. growing
                        ]
weather_data = [x for x in weather_data if "mun" not in x]


############################################

# Create data structures based on keys from data_struc_keys
func.create_data_structures(all, weather_data)
