import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
from define_paths import *
# ADD PATH AND LOAD CUSTOMIZED FUNCTIONS
sys.path.insert(0, path_git)
import rf.functions_RF as func_rf
import rf.plots_RF as plots


############################################################################################

# DEFINE FILE NAMES
file_names = sorted([ path_data + "/" + x for x in os.listdir(path_data) if "train" in x])

# TYPES OF DATA STRUCTURE
data_structure = sorted(["long_aug", "wide", "long_noaug"])
weather_names = [ 'sociodemographics only',
                  'crude_above30_tmax',
                  'crude_raw_prcp',
                  'crude_raw_tmax',
                  'norm_dev_long',
                  'norm_dev_short_prcp',
                  'norm_dev_short_tmax',
                  'norm_perc_short_prcp',
                  'norm_perc_short_tmax',
                  'warm_spell' ]

# RUN RANDOM FORESTS (this will take a while...)
#############################################

# It runs 10 models for 3 different data structures using a Randomized grid search with Cross-validation.
# It also includes different weight schemes for each model.
models_output_rf = func_rf.run_RF(file_names, data_structure = "wide", model_type="rf")
# use pickle to save RF
with open(path_data+"/rf_models.pickle","wb") as f:
    pickle.dump(models_output_rf, f, protocol=pickle.HIGHEST_PROTOCOL)

# Extract best models from RF grid search
rf_best = func_rf.unpack_gridSearch(models_output_rf)

# Calculate ROC values for each model
roc_values_rf = ROC_curve_values(models_output_rf, model_type="rf", best_models=rf_best)

# Calculate precision and recall scores for each model
precision_recall = precision_recall_values(models_output_rf, model_type="rf", best_models=rf_best)


# RUN LOGISTIC REGRESSION
#############################################
models_output_lr = func_rf.run_RF(file_names, data_structure = "wide", model_type="lr")
# use pickle to save Logistic Regressions
with open(path_data+"/lr_models.pickle","wb") as f:
    pickle.dump(models_output_lr, f, protocol=pickle.HIGHEST_PROTOCOL)


# Calculate ROC values for each model
roc_values_lr = ROC_curve_values(output_list=models_output_lr, model_type="lr")




# P L O T
#############################################
# ROC curve and test under different ratio costs.
plots.ROC_curve(roc_values, weather_names)




# U R B A N   V S    R U R A L
#############################################
idx_rural_urban = idx_rural_urban(file_names, data_structure = "wide")



# precision-recall curve PLOT



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
