from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from sklearn.metrics import average_precision_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"


# load data
filename = path_data + "/ind161_train_set.csv"
tr = pd.read_csv(filename, dtype="str")
tr = tr.sort_values(by=["persnum", "year"])

tr.loc[ tr.persnum=="100013" ,["persnum", "year", "migf"]].head(20)

################################################################################
###   V A R I A B L E   C R E A T I O N
################################################################################

# create DEPENDENT VARIABLE:
#         - based on person-year (persnum-year) observation
#         - keep individual history up to first migration,
#               then drop the rest of person-year observations

# remove all observation that has not mirated between 2019 and 1985
idx_logical = ( (tr.usyr1 >= "1985") & (tr.usyr1 <= "2019") ) | (tr.usyr1 == '8888')
tr = tr.loc[ idx_logical.values, :  ]


# remove all observations whose "year" > "usyr1"
idx_logical =  tr.year <= tr.usyr1
tr = tr.loc[idx_logical, ]

# create first migration variable
tr = tr.assign(first_mig = np.where(tr["usyr1"]=='8888', 0, 1) )

tr[["persnum", "year", "usyr1", "first_mig", "mxmig", "primary", "secondary", "bank"]].head(35)

# load PRCP, TMAX, TMIN
weather = ["prcp", "tmax", "tmin"]
for item in weather:
    filename = path_data + "/" + item + "_yearly_dev-norm_1980-2017.csv"
    weather_mmp = pd.read_csv(filename, dtype="str")
    # append to training dataset
    tr = pd.merge(tr, weather_mmp, how="left", on="geocode")
    break

#####################################################################
# V A R I A B L E S   (R E L A B E L)
#####################################################################

####  S O C I O  -  D E M O G R A P H I C S
################################################
# sex: female/male
tr = tr.assign(sex = pd.get_dummies(tr.sex).female)
# if there is primary school
tr = tr.assign(primary = pd.get_dummies(tr.primary).yes)
# if there is secondary school
tr = tr.assign(secondary = pd.get_dummies(tr.secondary).yes)
# mexican migration
tr = tr.assign(mxmig = pd.get_dummies(tr.mxmig).yes)
# age
tr = tr.assign(age = tr.age.astype(int))
# age squared
tr = tr.assign(age2 = tr.age**2)
# total migrants in household
tr = tr.assign(totmighh = tr.totmighh.astype(int))
# number of rooms in household
tr = tr.assign(troom = tr.troom.astype(int))
# wether hh owns a business
tr = tr.assign(tbuscat = pd.get_dummies(tr.tbuscat).yes)
# prevalenve of migration in the community
tr = tr.assign(dprev = tr.dprev.astype(float))
# value of land (log)
tr = tr.assign(lnvland_nr = tr.lnvland_nr.astype(float))
# share of main working in agriculture
tr = tr.assign(agrim = tr.agrim.astype(float))
# share of people earning twice minimum wage
tr = tr.assign(minx2 = tr.minx2.astype(float))
# metropolitan status
tr[["metropolitan", "rancho", "small urban", "town"]] = pd.get_dummies(tr.metrocat)
# population size (lnpop)
tr = tr.assign(lnpop = tr.lnpop.astype(float))
# ejido
tr = tr.assign(ejido = pd.get_dummies(tr.ejido).yes)
# bank
tr = tr.assign(bank = pd.get_dummies(tr.bank).yes)
# visaaccs
tr = tr.assign(visaaccs = tr.visaaccs.astype(float))
# infrate: inflation per year
tr = tr.assign(infrate = tr.infrate.astype(float))
# mxminwag: minimum wage
tr = tr.assign(mxminwag = tr.mxminwag.astype(float))
# mxunemp: unemployment
tr = tr.assign(mxunemp = tr.mxunemp.astype(float))
# usavwage: USA average wage for low skill labor
tr = tr.assign(usavwage = tr.usavwage.astype(float))
# log trade mexico-USA
tr = tr.assign(lntrade = tr.lntrade.astype(float))
# distance to US (log)
tr = tr.assign(logdist = tr.logdist.astype(float))

####  W E A T H E R   I N F O
################################################
# deviation from norm: 1980 lag
tr = tr.assign(prcp_1980 = tr["prcp-1980"].astype(float))
# deviation from norm: 1983 lag
tr = tr.assign(prcp_1983 = tr["prcp-1983"].astype(float))


#####################################################################
#  S E L E C T   F E A T U R E S
#####################################################################
features_sociodem = ["primary", "secondary", "mxmig", "age", "age2", "sex",
                     "totmighh", "troom", "tbuscat", "dprev", "lnvland_nr",
                     "agrim", "minx2", "metropolitan", "rancho", "small urban", "town",
                     "lnpop", "ejido", "bank", "visaaccs", "infrate", "mxminwag",
                     "mxunemp", "usavwage", "lntrade" ]

features_prcp = ["prcp_1980", "prcp_1983"]

features_all = features_sociodem + features_prcp

tr_subset = tr.dropna(axis=0, how="any")


#####################################################################
# B U I L D   R A N D O M   F O R E S T
#####################################################################
# target vector
y = np.array(tr_subset.first_mig)
# features
X_socio = np.array(tr_subset.loc[:,features_sociodem])

# train and test sets
X_socio_train, X_socio_test, y_socio_train, y_socio_test = train_test_split(X_socio, y, test_size=0.25, random_state=200)

X_all = np.array(tr_subset.loc[:,features_all])

# train and test sets
X_all_train, X_all_test, y_all_train, y_all_test = train_test_split(X_all, y, test_size=0.25, random_state=200)


#  R A N D O M   F O R E S T
###################################
# O N L Y   S O C I O  -  D E M O G R A P H I C S
rf_socio = RandomForestClassifier(n_estimators=100, criterion="entropy")
rf_socio.fit(X_socio_train, y_socio_train)

# accuracy prediciton
pred_train_socio = rf_socio.predict(X_socio_train)
pred_test_socio = rf_socio.predict(X_socio_test)

# probabilities
probs_socio = rf_socio.predict_proba(X_socio_test)
# keep probabilities for the positive outcome only
probs_socio = probs_socio[:,1]

precision_socio, recall_socio, thresholds_socio = precision_recall_curve(y_test, probs_socio)
# calculate F1 score
f1_socio = f1_score(y_test, pred_test_socio)
# calculate precision-recall AUC
auc_socio = auc(recall_socio, precision_socio)
fpr, tpr, thresholds =  roc_curve(y_test, pred_test_socio)


# Feature importance in predictive capacity
importances_socio = rf_socio.feature_importances_
std = np.std([tree.feature_importances_ for tree in rf_socio.estimators_], axis=0)
indices_socio = np.argsort(importances_socio)[::-1]
features_sorted_socio = [features_sociodem[x] for x in indices]

for f in range(X_socio.shape[1]):
    print("%d. feature %d (%f)" % (f + 1, indices[f], importances_socio[indices[f]]))

# Plot the feature importances of the forest
plt.figure()
plt.title("Feature Importances (Socio-demographics only)")
plt.bar(range(X_socio.shape[1]), importances_socio[indices_socio],
       color="r", yerr=std[indices_socio], align="center", orientation="vertical")
plt.xticks(range(X_socio.shape[1]), features_sorted_socio, rotation=90)
plt.xlim([-1, X_socio.shape[1]])
fig_name = path_git + "/results/rf_features_importance_socio_only.png"
plt.savefig(fig_name, bbox_inches='tight')



# P R C P   1 9 8 0 / 1 9 8 3    A N D    S O C I O  -  D E M O G R A P H I C S
rf_all = RandomForestClassifier(n_estimators=100, criterion="entropy")
rf_all.fit(X_all_train, y_all_train)

# accuracy prediciton
pred_train_all = rf_all.predict(X_all_train)
pred_test_all = rf_all.predict(X_all_test)

# probabilities
probs_all = rf_all.predict_proba(X_all_test)
# keep probabilities for the positive outcome only
probs_all = probs_all[:,1]

precision_all, recall_all, thresholds_all = precision_recall_curve(y_test, probs_all)
# calculate F1 score
f1_all = f1_score(y_test, pred_test_all)
# calculate precision-recall AUC
auc_all = auc(recall_all, precision_all)
fpr, tpr, thresholds =  roc_curve(y_test, pred_test_all)
# plot no skill
plt.figure()
plt.title("Precision-Recall Curve")
# plot the precision-recall curve for the model
plt.plot(recall_all, precision_all, marker='.', color="r", label="Random Forest with prcp lags")
plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.legend()

fig_name = path_git + "/results/recall-precision_curve.png"
plt.savefig(fig_name, bbox_inches='tight')



###  I M P O R T A N C E S
# Feature importance in predictive capacity
importances_all = rf_all.feature_importances_
std = np.std([tree.feature_importances_ for tree in rf_all.estimators_], axis=0)
indices_all = np.argsort(importances_all)[::-1]
features_sorted_all = [features_all[x] for x in indices_all]

for f in range(X_all.shape[1]):
    print("%d. feature %d (%f)" % (f + 1, indices_all[f], importances_all[indices_all[f]]))


# Plot the feature importances of the forest
plt.figure()
plt.title("Feature Importances (Socio-demographics + Precipitation)")
plt.bar(range(X_all.shape[1]), importances_all[indices_all],
       color="r", yerr=std[indices_all], align="center", orientation="vertical")
plt.xticks(range(X_all.shape[1]), features_sorted_all, rotation=90)
plt.xlim([-1, X_all.shape[1]])
fig_name = path_git + "/results/rf_features_importance_socio_prcp.png"
plt.savefig(fig_name, bbox_inches='tight')
