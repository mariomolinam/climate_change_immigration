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

### DEFINE FILE NAMES
# Training
file_names_train = [ path_data + "/" + x for x in os.listdir(path_data) if "train_set_wide" in x]
f_train = file_names_train[0] # wide train data
# Test
file_names_test = sorted([ path_data + "/" + x for x in os.listdir(path_data) if "test_set_wide" in x])
f_test = file_names_test[0] # wide train data


# RUN RANDOM FORESTS (this will take a while...)
#############################################

# SAVE RANDOM FORESTS (RF) models
if "rf_models.pickle" not in os.listdir(path_data):
    with open(path_data+"/rf_models.pickle","wb") as f:
        # Run random forest
        models_output_rf = func_rf.run_RF(f_train, model_type="rf")
        pickle.dump(models_output_rf, f, protocol=pickle.HIGHEST_PROTOCOL)
else: # LOAD rf models
    with open(path_data+"/rf_models.pickle","rb") as f:
        models_output_rf = pickle.load(f)

f.close() # close file


# RUN LOGISTIC REGRESSION
#############################################
# SAVE LOGISTIC REGRESSION (LR) models using pickle.dump
if "lr_models.pickle" not in os.listdir(path_data):
    with open(path_data+"/lr_models.pickle","wb") as f:
        # Run logistic regression using baseline model only (model a)
        models_output_lr = func_rf.run_RF(f_train, model_type="lr")
        pickle.dump(models_output_lr, f, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open(path_data+"/lr_models.pickle","rb") as f:
        models_output_lr = pickle.load(f)

f.close() # close file


################################
###   T A B L E   3  (values)
################################

# VALIDATION SET
# Random Forest
final_models_rf = func_rf.eval_performance_rf(models_output_rf)

# TEST SET for Random Forest AND Logistic Regression
#############################################
# Random Forest
test_values_rf = func_rf.get_test_values(f_test, models_output_rf)
performance_TEST_set_rf = func_rf.performance_test_set(final_models_rf, test_values_rf)

# Logistic Regression
test_values_lr = func_rf.get_test_values(f_test, models_output_lr)
performance_TEST_set_lr = func_rf.performance_test_set(models_output_lr, test_values_lr)


################################
###   F I G U R E   3
################################
# Calculate ROC values for each model
roc_values_rf = func_rf.ROC_curve_values(final_models_rf, test_values_rf,model_type="rf")

# ROC curve and test under different ratio costs.
plots.ROC_curve(roc_values_rf)


################################
###   F I G U R E   4
################################
# plot feature importance for all models
plots.feature_importance_plot(final_models_rf, test_values_rf)


################################
###   F I G U R E   5
################################

# Permutation tests
if "rf_perm_tests.pickle" not in os.listdir(path_data):
    with open(path_data+"/rf_perm_tests.pickle","wb") as f:
        # Run permutation tests for feature importance
        perm_features = func_rf.perm_importance(final_models_rf, test_values_rf)
        pickle.dump(perm_features, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close() # close file
else:
    with open(path_data+"/rf_perm_tests.pickle","rb") as f:
        perm_features = pickle.load(f)

# Plot results from permutation tests
plots.feature_importance_permutation_plot(perm_features, test_values_rf)
