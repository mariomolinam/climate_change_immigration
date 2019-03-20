from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"


# load data
filename = path_data + "/ind161_train_set.csv"
tr = pd.read_csv(filename, dtype="str")
tr = tr.sort_values(by=["persnum", "year"])

################################################################################
###   V A R I A B L E   C R E A T I O N
################################################################################

# create DEPENDENT VARIABLE:
#         - based on person-year (persnum-year) observation
#         - keep individual history up to first migration,
#               then drop the rest of person-year observations

# remove all observation that has no valid value in usyr1
idx_logical = ( (tr.usyr1 >= "1900") & (tr.usyr1 <= "2019") ) | (tr.usyr1 == '8888')
tr = tr.loc[ idx_logical, :  ]

# remove all observations whose "year" > "usyr1"
idx_logical =  tr.year <= tr.usyr1 
tr = tr.loc[idx_logical, ]

# create first migration variable
tr = tr.assign(first_mig = np.where(tr["usyr1"]=='8888', 0, 1) )

tr[["persnum", "year", "usyr1", "first_mig"]].head(50)



# load PRCP, TMAX, TMIN

weather = ["prcp", "tmax", "tmin"]
for item in weather:
    filename = path_data + "/mmp_data/" + item + "_monthly_dev-norm_1980-2017.csv"
    weather_mmp = pd.read_csv(filename, dtype="str")
    # append to training dataset
    tr = pd.merge(tr, weather_mmp, how="left", on="geocode")
    break



# D E P E N D E N T   V A R I A B L E
# fix

tr_subset = tr.loc[:,["first_migration", "sex", "marstat"]]
tr_subset.marstat[ (tr.marstat > '6') ] = np.nan

tr_subset = tr_subset.dropna(axis=0, how="any")
tr_subset = tr_subset.assign(female=pd.get_dummies(tr.sex).female)
tr_subset[["Never married", "Married", "Consensual union", "Widowed", "Divorced", "Separated"]] = pd.get_dummies(tr_subset.marstat)

# target vector
y = np.array(tr_subset.first_migration)
# features
X = np.array(tr_subset.loc[:,["female", "Never married", "Married", "Consensual union", "Widowed", "Divorced", "Separated"]])

# train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=200)

#  R A N D O M   F O R E S T
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

# accuracy prediciton
accuracy_score(y_train, rf.predict(X_train))
accuracy_score(y_test, rf.predict(X_test))


"mig" in tr.columns
tr["migf"].value_counts(dropna=False)
