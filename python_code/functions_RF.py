# -*- coding: utf-8 -*-
import csv, random, os, re, gc
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import f1_score
from sklearn.metrics import average_precision_score


def get_features(file):
    """
    Input:
        - a pandas dataframe
        - a string (file name)

    Task: Create list of sociodemographic features

    Return: a dictionary with time constant, time varying, and weather variables.
    """
    # TIME CONSTANT
    features_sociodem_constant = [
        # "migf",      # whether migrant or not (regardless of year of first migration)
        "primary",   # if there is a school
        "secondary", # if there is a secondary school
        "sex",
        "totmighh",  # total number of prior U.S. migrants in the household (up until that year)
        "tbuscat",   # whether hh owns a business
        "troom",     # number of rooms in properties household owns
        # "metropolitan",
        "rancho",
        "small urban",
        "town",
        "lnvland_nr",# log(value of land) — excluding that bought by remittances
        "agrim",     # TIME VARYING (CHANGE) # share of men working in agriculture in community
        "bank",      # in community
        "lnpop",     # log of population size in community
        "ejido",     # collective land system (0/1)
        "minx2",      # share of people earning twice the minimum wage or more
        "logdist"    # distance of community to the U.S.
    ]
    # TIME VARYING
    features_sociodem_varying = [
          "age",
          "age2",
          "mxmig",     # whether they migrated in mexico until this year
          "dprev",     # prevalence of migration in community (share of people who have ever migrated to the U.S. up until that year)
          "visaaccs",  # visa accessibility to the U.S. in year
          "infrate",   # inflation in Mexico in year
          "mxminwag",  # min wage in mexico in year
          "mxunemp",   # unemployment in Mexico
          "usavwage",  # U.S. average wages for low-skill work in year
          "lntrade"    # log of trade between MX-U.S.d
    ]
    # WEATHER VARIABLES and KEYS
    weather_vars = [
         'crude_raw_prcp_monthly-average',
         'crude_raw-tmax_monthly-average',
         'crude_above30-tmax_monthly-average',
         'norm_deviation_longterm',
         'norm_percent_short-term_tmax',
         'norm_percent_short-term_prcp',
         'norm_deviation_short-term_tmax',
         'norm_deviation_short-term_prcp',
         'warm_spell_tmax',
    ]
    weather_keys = [ 'crude_raw_prcp',
                     'crude_raw_tmax',
                     'crude_above30_tmax',
                     'norm_dev_long',
                     'norm_perc_short_tmax',
                     'norm_perc_short_prcp',
                     'norm_dev_short_tmax',
                     'norm_dev_short_prcp',
                     'warm_spell']
    if "long_aug" in file:
        weather_vars = { weather_keys[x]: weather_vars[x] for x in range(len(weather_vars)) }
        features_sociodem = { "time_constant": features_sociodem_constant,
                              "time_varying": features_sociodem_varying,
                              "weather_vars": weather_vars }
    elif "long_noaug" in file:
        # rename weather variables
        weather_vars = { weather_keys[x]: [ weather_vars[x] + '_lag_t' + str(i) for i in range(5) ] for x in range(len(weather_vars)) }
        features_sociodem = { "time_constant": features_sociodem_constant,
                              "time_varying": features_sociodem_varying,
                              "weather_vars": weather_vars }
    else:
        # rename weather variables
        weather_vars = { weather_keys[x]: [ weather_vars[x] + '_' + str(i) for i in range(5) ] for x in range(len(weather_vars)) }
        # rename time_varying variables
        features_sociodem_varying = [ name + "_" + str(i) for i in range(5) for name in features_sociodem_varying ]
        features_sociodem = { "time_constant": features_sociodem_constant,
                              "time_varying": features_sociodem_varying,
                              "weather_vars": weather_vars }
    return features_sociodem


def weather_features():
    """
    Input: None

    Task: create a selection of weather features.
            Different measures are keys of a dict, and values
            are a list with variable names.

    Return: a dictionary
    """

    features_weather = { "crude_raw_prcp": ['crude_raw_prcp_monthly-average_lag_t0',
                                            'crude_raw_prcp_monthly-average_lag_t1',
                                            'crude_raw_prcp_monthly-average_lag_t2',
                                            'crude_raw_prcp_monthly-average_lag_t3',
                                            'crude_raw_prcp_monthly-average_lag_t4'],

                        "crude_raw_tmax": [ 'crude_raw-tmax_monthly-average_lag_t0',
                                            'crude_raw-tmax_monthly-average_lag_t1',
                                            'crude_raw-tmax_monthly-average_lag_t2',
                                            'crude_raw-tmax_monthly-average_lag_t3',
                                            'crude_raw-tmax_monthly-average_lag_t4'],

                        "crude_above30_tmax": [ 'crude_above30-tmax_monthly-average_lag_t0',
                                                'crude_above30-tmax_monthly-average_lag_t1',
                                                'crude_above30-tmax_monthly-average_lag_t2',
                                                'crude_above30-tmax_monthly-average_lag_t3',
                                                'crude_above30-tmax_monthly-average_lag_t4' ],

                        "norm_dev_long": [  'norm_deviation_longterm_lag_t0',
                                            'norm_deviation_longterm_lag_t1',
                                            'norm_deviation_longterm_lag_t2',
                                            'norm_deviation_longterm_lag_t3',
                                            'norm_deviation_longterm_lag_t4' ],

                        "norm_perc_short_tmax": [ 'norm_percent_short-term_tmax_lag_t0',
                                                  'norm_percent_short-term_tmax_lag_t1',
                                                  'norm_percent_short-term_tmax_lag_t2',
                                                  'norm_percent_short-term_tmax_lag_t3',
                                                  'norm_percent_short-term_tmax_lag_t4' ],

                        "norm_perc_short_prcp": [ 'norm_percent_short-term_prcp_lag_t0',
                                                  'norm_percent_short-term_prcp_lag_t1',
                                                  'norm_percent_short-term_prcp_lag_t2',
                                                  'norm_percent_short-term_prcp_lag_t3',
                                                  'norm_percent_short-term_prcp_lag_t4' ],

                        "norm_dev_short_tmax": [ 'norm_deviation_short-term_tmax_lag_t0',
                                                 'norm_deviation_short-term_tmax_lag_t1',
                                                 'norm_deviation_short-term_tmax_lag_t2',
                                                 'norm_deviation_short-term_tmax_lag_t3',
                                                 'norm_deviation_short-term_tmax_lag_t4' ],

                        "norm_dev_short_prcp": [ 'norm_deviation_short-term_prcp_lag_t0',
                                                 'norm_deviation_short-term_prcp_lag_t1',
                                                 'norm_deviation_short-term_prcp_lag_t2',
                                                 'norm_deviation_short-term_prcp_lag_t3',
                                                 'norm_deviation_short-term_prcp_lag_t4' ],

                        "warm_spell": [ 'warm_spell_tmax_lag_t0',
                                        'warm_spell_tmax_lag_t1',
                                        'warm_spell_tmax_lag_t2',
                                        'warm_spell_tmax_lag_t3',
                                        'warm_spell_tmax_lag_t4' ]
                        }

    return features_weather


def set_params_grid_search():
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start = 500, stop = 1500, num = 21)]
    # Number of features to consider at every split
    # max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(5, 40, num = 8)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    # min_samples_split = [2, 5, 10]
    # Minimum number of samples required at each leaf node
    # min_samples_leaf = [1, 2, 4]
    # Method of selecting samples for training each tree
    # bootstrap = [True]
    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
                   # 'max_features': max_features,
                   'max_depth': max_depth,
                   # 'min_samples_split': min_samples_split,
                   # 'min_samples_leaf': min_samples_leaf,
                   # 'bootstrap': bootstrap
                   }
    return random_grid


def random_forest_stat(X_train, y_train, weight):
    """
    Input:  Paramaters for Random Forest:

            X_train, y_train, X_test, y_test: numpy arrays
            weights: dict

    Task: run random forest and predict:
            - using train data (X_train)
            - using test data (Y_test)
            -

    Return: dictionary
    """
    # set parameters for grid search
    random_grid = set_params_grid_search()
    # build random forest classifier
    rf = RandomForestClassifier( criterion = "entropy",
                                 bootstrap = True,
                                 # n_estimators = 800,
                                 # max_depth = 12,
                                 class_weight = weight
                                )
    # determine search grid to find best paramaters using cross-validation (10 folds)
    rf_grid = RandomizedSearchCV( estimator = rf,
                                  param_distributions = random_grid,
                                  scoring = "balanced_accuracy", # accounts for imbalance in data
                                  n_jobs = 10, # number of cores (-1 to use them all)
                                  n_iter = 20,
                                  cv = 3,
                                  refit = True,
                                  verbose = 2
                                  # random_state=466
                                  )
    # rf_grid = GridSearchCV( estimator = rf,
    #                        param_grid = random_grid,
    #                        scoring = "balanced_accuracy", # accounts for imbalance in data
    #                        n_jobs = -1,
    #                        # n_iter=15,
    #                        cv = 5,
    #                        refit = True,
    #                        verbose=2
    #                        )
    print('.'*60)
    print("\tEstimating a random forest with randomized grid search...\n")
    # rf_random.fit(X_train, y_train)
    # rf_random.best_params_
    rf_grid.fit(X_train, y_train)
    print("\n\tDone!\n\n")
    print('.'*60)
    return rf_grid


def multiple_RF(X_train, y_train):
    """
    Input: Paramaters for Random Forest:
            X_train, y_train, X_test, y_test: numpy arrays

    Task: create class weights and run random forest

    Return: A list of dictionaries, where each dictionary
            contains output for random forest.
    """
    # define class weights
    weights = [ "balanced_subsample",               # ratio:  49/1 (approx)
                # {0:0.01, 1: 1000},                   # ratio:  100000/1
                {0:0.01, 1: 1000000}               # ratio:  100000000/1
                # {0:0.01, 1: 10000000},              # ratio:  1000000000/1
                # {0:0.01, 1: 100000000}              # ratio:  10000000000/1
                ]
    # loop through all weights
    save_outputs = list()
    for w in weights:
        output = random_forest_stat(X_train, y_train, w)
        save_outputs.append(output)
    return save_outputs


def logistic_regression_stat(X_train, y_train):
        """
        Input:  Paramaters for Logistic Regression:

                X_train, y_train, X_test, y_test: numpy arrays
                weights: dict

        Task: run logistic regression and predict:
                - using train data (X_train)
                - using test data (Y_test)

        Return: dictionary
        """
        # random_grid = set_params_grid_search()
        lr = LogisticRegression( penalty = "none",
                                 fit_intercept = True,
                                 intercept_scaling = 1,
                                 class_weight = None,
                                 solver = "saga", # optimization algorithm
                                 max_iter = 500
                              )
        #
        print('.'*60)
        print("\tEstimating a logistic regression..\n")
        output = lr.fit(X_train, y_train)
        print("\n\tDone!\n\n")
        print('.'*60)
        return output


def run_RF(file_names, data_structure):
    # number of models
    no_models = 10  # includes: LogisticRegression and RF with sociodemographics only (+2)
            #           RF with 9 different climate change variables (+9)

    # define type of file
    for file in file_names:
        if data_structure in file:
            f = file
            break

    # LOAD DATA
    mmp_data_weather = pd.read_csv(f)

    #####################################################################
    #  S E L E C T   F E A T U R E S
    #####################################################################
    first_migration = ["migf"]
    all_features = get_features(f)
    # time-constant varaibles
    features_time_constant = all_features['time_constant']
    # time-varying variables
    features_time_varying = all_features['time_varying']
    # weather measures
    features_weather = all_features['weather_vars']
    # get weather names
    weather_names = ['sociodemographics only'] + sorted( features_weather.keys() )
    # weather_var = weather_names[i]
    # set features for models
    features = features_time_constant + features_time_varying

    # STORE VALUES HERE
    MODEL_OUTPUT = {}
    for i in range(no_models):
        # define names (to be used when STORING values)
        features_set = "set_" + str(i) + "_" + data_structure
        # add dict to MODEL_OUTPUT
        MODEL_OUTPUT[i] = {}

        # add weather_variables when needed
        if i > 0:
            if not isinstance(features_weather[weather_names[i]], list):
                weather_vars = [ features_weather[weather_names[i]] ]
            else:
                weather_vars = features_weather[weather_names[i]]
            # create features list
            features = features + weather_vars

        # remove missing values
        tr = mmp_data_weather.loc[:, first_migration + features]
        tr_subset = tr.dropna(axis=0, how="any")

        print("\nVariable number: " + str(weather_names[i]))
        print("\tFile: " + f )
        print("\tData subset shape:" + str(tr_subset.shape) + "\n")

        #####################################################################
        # B U I L D   M O D E L S
        #####################################################################

        # C R E A T E   V A R I A B L E S
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
        rf_output = multiple_RF(X_train, y_train)

        # L O G I S T I C   R E G R E S S I O N
        ###################################
        lr_output = logistic_regression_stat(X_train, y_train)

        # S T O R E   O U T P U T
        MODEL_OUTPUT[features_set] = {"rf": rf_output, "lr": lr_output, "y_test": y_test, "X_test": X_test}
        # MODEL_OUTPUT[i].update( {data_structure[f]: {"y_test": y_test, "X_test": X_test} } )

    return MODEL_OUTPUT


def unpack_gridSearch(output_list):
    best_models = {}
    for model in range(len(output_list)):
        best_models[model] = {}
        for data_str in output_list[model]:
            best_models[model].update({data_str: []})
            for w in range(len(output_list[model][data_str]['rf'])):
                best_models[model][data_str].append(output_list[model][data_str]['rf'][w].best_estimator_)
    return best_models


def ROC_curve_values(best_models, y_test):
    roc_models = []
    for model in best_models:
        # accuracy prediciton
        pred_train = model.predict(X_train)
        pred_test = model.predict(X_test)
        pred_probs = model.predict_proba(X_test) # probabilities
        # ROC curve
        fpr, tpr, _ = roc_curve(y_test, pred_probs[:,1])
        auc_value = auc(fpr, tpr)
        roc_models.append([fpr, tpr, auc_value])
    return roc_models


def rf_outputs(rf):
    # accuracy prediciton
    pred_train = rf.predict(X_train)
    pred_test = rf.predict(X_test)
    pred_probs = rf.predict_proba(X_test) # probabilities
    # dict for output
    output = { "pred_prob": pred_probs[:,1],
               "pred_test": pred_test,
               "pred_train": pred_train,
               "rf_model": rf
             }

    return output



def get_y_test():
    # save y_test
    y_test_list = []
    for i in range(len(weather_names)):
        features_all = features_sociodem + features_weather[weather_names[i]]
        # remove missin values
        tr = mmp_data_weather.loc[:,[first_miragtion] + features_all]
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
        # save y_test
        y_test_list.append(y_test)
    return y_test_list
