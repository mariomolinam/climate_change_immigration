from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

# paths
path_data = "/home/mario/Documents/environment_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

# sets
sets = { "training": "/mmp_training_set.csv",
         "validation": "/mmp_validation_set.csv",
         "test": "/mmp_test_set-DO-NOT-USE.csv" }

#  V A R I A B L E   S E L E C T I O N
socio_demo = [
               "sex",
               "age",
               "marstat", # marital status
               "occ",     # occupation at the time of survey
               "hhincome" # household head income or wages
              ]
health = [
            "kgs",     # weight
            "health"   # health at age 14
            "healthy"  # health at time of survey
        ]


# D E P E N D E N T   V A R I A B L E
# fix
tr.loc[ tr.usyr1=="usyr1","usyr1"] = np.nan
tr.usyr1 = tr["usyr1"].astype(float)
# Migration equals 1 if first mgration to US took place, regardless of when it happened
tr = tr.assign(first_migration = 0)
tr.loc[ tr.usyr1.isnull() , "first_migration"] = np.nan
tr.loc[ tr.usyr1.notnull() & ( (tr.usyr1 >= 1900) & (tr.usyr1 <= 2019) ) , "first_migration"] = 1





#  R A N D O M   F O R E S T
data_training = path_data + sets["training"]
tr = pd.read_csv(data_training, dtype="str")
header = list(tr.columns)

"mig" in tr.columns
tr["migf"].value_counts(dropna=False)
