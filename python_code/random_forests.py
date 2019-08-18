import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys, os, socket
import functions_RF as func_rf
import plots_RF as plots


# DEFINE PATHS depending on hostname server
hostname = socket.gethostname()
if hostname == 'molina':
    path_data = "/home/mario/Documents/environment_data/mmp_data"
    path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"
    sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code") # local
elif hostname == 'sdl3':
    path_git = "/home/mm2535/documents/climate_change_immigration"
    path_data = "/home/mm2535/data/climate_change"
    sys.path.insert(0, "/home/mm2535/documents/climate_change_immigration/python_code") # sdl3
elif hostname == 'sdl1':
    path_git = "/home/mm2535/documents/climate_change_immigration"
    path_data = "/home/mm2535/documents/data/climate_change"        # sdl1
    sys.path.insert(0, "/home/mm2535/documents/climate_change_immigration/python_code") # sdl1


# DEFINE FILE NAMES
file_names = [ path_data + "/" + x for x in os.listdir(path_data) if "train" in x]
f = file_names[0]
# TYPES OF DATA STRUCTURE
data_structure = ["long_aug", "wide", "long_noaug"]


# RUN RANDOM FORESTS (this wil take a while...)
#           It run 10 models for 3 different data structures using a Randomized grid search with Cross-validation.
#           It also includes different weight schemes for each model.
models_output = func_rf.run_RF(file_names, data_structure)


























# np_array_fpr = {}
#
# rf_output_dict = {}
# lr_output_dict = {}
#
# y_test_list  = []
# y_train_list = []



        # O U T P U T S
        ###################################

        # Extract best models
        rf_best = unpack_gridSearch(rf_output)
        lr_best = lr_output

        # ROC values
        roc_values = ROC_curve_values(rf_best, y_test)
        val_fpr, val_tpr, val_auc = roc_values

        # save values from RF models
        np_array_fpr[features_set] = [val_fpr, val_tpr, val_auc]
        rf_output_dict[features_set] = rf_output
        lr_output_dict[features_set] = lr_output
        y_test_list.append(y_test)
        y_train_list.append(y_train)












for f in file_names:
    # load data
    mmp_data_weather = pd.read_csv(f)

    #####################################################################
    #  S E L E C T   F E A T U R E S
    #####################################################################
    first_migration = ["migf"]
    all_features = func_rf.get_features(f)
    features_time_constant = all_features['time_constant']
    features_time_varying = all_features['time_varying']
    features_weather = all_features['weather_vars']

    weather_names = ['sociodemographics only'] + sorted( features_weather.keys() )

    # build ROC curve: save values here
    np_array_fpr = {}
    rf_output_dict = {}
    lr_output_dict = {}
    y_test_list  = []
    y_train_list = []

    for i in range(len(weather_names)):
        print "\nSet: " + str(i)
        if i == 0:
            features = features_time_constant + features_time_varying
        else:
            features = features_time_constant + features_time_varying + features_weather[weather_names[i]]

        # remove missing values
        tr = mmp_data_weather.loc[:, first_migration + features]
        tr_subset = tr.dropna(axis=0, how="any")

        #####################################################################
        # B U I L D   R A N D O M   F O R E S T
        #####################################################################

        # CREATE VARIABLES
        ###################################
        # target vector
        y = np.array(tr_subset.migf)
        # features
        X = np.array(tr_subset.loc[:,features ])
        # train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=200)

        #  R A N D O M   F O R E S T
        ###################################
        # run Grid Search of Random Forest
        rf_output = func_rf.multiple_RF(X_train, y_train, X_test, y_test)

        # lr_output = func_rf.logistic_regression_stat(X_train, y_train, X_test, y_test)
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
