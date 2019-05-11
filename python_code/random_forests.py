import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code")
import functions_RF as func_rf
import plots_RF as plots


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"


filename = path_data + "/" + "ind161_train_set_LONG.csv"
mmp_data_weather = pd.read_csv(filename)

#####################################################################
#  S E L E C T   F E A T U R E S
#####################################################################

first_migration = func_rf.sociodemographics_features()[0]
features_sociodem = func_rf.sociodemographics_features()[1:]
features_weather = func_rf.weather_features()
weather_names = sorted( features_weather.keys() ) + ['sociodemographics only']

# build ROC curve: save values here
np_array_fpr = {}
rf_output_dict = {}
lr_output_dict = {}
y_test_list  = []
y_train_list = []

for i in range(len(weather_names)):
    print "\nSet: " + str(i)
    if i == 9:
        features_all = features_sociodem
    else:
        features_all = features_sociodem + features_weather[weather_names[i]]
    # remove missin values
    tr = mmp_data_weather.loc[:,[first_migration] + features_all]
    tr_subset = tr.dropna(axis=0, how="any")
    #####################################################################
    # B U I L D   R A N D O M   F O R E S T
    #####################################################################
    # target vector
    y = np.array(tr_subset.migf)
    # features
    X = np.array(tr_subset.loc[:,features_all ])
    # train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=200)
    #  R A N D O M   F O R E S T
    ###################################
    # run multiple Random Forest
    rf_output = func_rf.multiple_RF(X_train, y_train, X_test, y_test)
    lr_output = func_rf.logistic_regression_stat(X_train, y_train, X_test, y_test)
    #
    features_set = "set_" + str(i)
    roc_values = func_rf.ROC_curve_values(rf_output, y_test, model=0)
    val_fpr, val_tpr, val_auc = roc_values
    # save values from RF models
    np_array_fpr[features_set] = [val_fpr, val_tpr, val_auc]
    rf_output_dict[features_set] = rf_output
    lr_output_dict[features_set] = lr_output
    y_test_list.append(y_test)
    y_train_list.append(y_train)


# ROC curve and test under different ratio costs.
plots.ROC_curve(np_array_fpr, weather_names)


# y_test_list = get_y_test()
# y_train_list = get_y_test()
plots.ROC_sensitivity(rf_output_dict, y_test_list, weather_names)

# Confusion Matrices: train and test set
plots.confusion_matrices(rf_output_dict, y_train_list, y_test_list)




###  I M P O R T A N C E S
# Feature importance in predictive capacity
importances_all = rf_output_dict['set_1'][0].feature_importances_
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
