# -*- coding: utf-8 -*-
import csv, random, os, re, gc
import pandas as pd
import numpy as np
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
        "agrim",     # share of men working in agriculture in community
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
        weather_vars = { weather_keys[x]: [ weather_vars[x] + '_t' + str(i) for i in range(5) ] for x in range(len(weather_vars)) }

        features_sociodem = { "time_constant": features_sociodem_constant,
                              "time_varying": features_sociodem_varying,
                              "weather_vars": weather_vars }
    else:
        # rename weather variables
        weather_vars = { weather_keys[x]: [ weather_vars[x] + '_t' + str(i) for i in range(5) ] for x in range(len(weather_vars)) }

        # rename time_varying variables
        features_sociodem_varying = [ name + "_t" + str(i) for i in range(5) for name in features_sociodem_varying ]

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


def set_params_random_search():
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 200)]
    # Number of features to consider at every split
    # max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(5, 200, num = 50)]
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


def multiple_RF(X_train, y_train, X_test, y_test):
    """
    Input: Paramaters for Random Forest:
            X_train, y_train, X_test, y_test: numpy arrays

    Task: create class weights and run random forest

    Return: A list of dictionaries, where each dictionary
            contains output for random forest.
    """
    # define class weights
    weights = [ "balanced",              # ratio:  49/1 (approx)
                {0:0.01, 1: 1000},       # ratio:  100000/1
                {0:0.01, 1: 1000000},    # ratio:  100000000/1
                {0:0.01, 1: 10000000},   # ratio:  1000000000/1
                {0:0.01, 1: 100000000}   # ratio:  10000000000/1
                ]
    # loop through all weights
    save_outputs = list()
    for w in weights:
        output = random_forest_stat(X_train, y_train, X_test, y_test, w)
        save_outputs.append(output)
    return save_outputs
    #

def random_forest_stat(X_train, y_train, X_test, y_test, weight):
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
    random_grid = set_params_random_search()
    rf = RandomForestClassifier( criterion = "entropy",
                                 bootstrap = True,
                                # n_estimators = 1000,
                                # max_depth = 30,
                                # class_weight = weight
                                )
    # determine search grid to find best paramaters using cross-validation (10 folds)
    rf_random = RandomizedSearchCV( estimator = rf,
                              param_distributions = random_grid,
                              n_iter=50,
                              cv = 5,
                              verbose=2,
                              random_state=466,
                              n_jobs = -1)

    print("\tEstimating a random forest with randomized grid search...")

    rf_random.fit(X_train, y_train)

    print("\tDone!\n")

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


def logistic_regression_stat(X_train, y_train, X_test, y_test):
        """
        Input:  Paramaters for Logistic Regression:

                X_train, y_train, X_test, y_test: numpy arrays
                weights: dict

        Task: run logistic regression and predict:
                - using train data (X_train)
                - using test data (Y_test)

        Return: dictionary
        """

        # random_grid = set_params_random_search()
        lr = LogisticRegression( penalty="l2",
                                 C=1e42,
                                 n_jobs = 5 )
        # determine search grid to find best paramaters using cross-validation (10 folds)
        # lr_random = RandomizedSearchCV( estimator = lr,
        #                           param_distributions = random_grid,
        #                           n_iter=40,
        #                           cv = 5,
        #                           verbose=2,
        #                           n_jobs = -1)
        print("\tEstimating a logistic regression...")
        lr.fit(X_train, y_train)
        print("\tDone!")
        # accuracy prediciton
        pred_train = lr.predict(X_train)
        pred_test = lr.predict(X_test)
        pred_probs = lr.predict_proba(X_test) # probabilities
        # dict for output
        output = { "pred_prob": pred_probs[:,1],
                   "pred_test": pred_test,
                   "pred_train": pred_train,
                   "lr_model": lr
                 }
        return output


def ROC_curve_values(rf_output, y_test, model):
    fpr, tpr, _ = roc_curve(y_test, rf_output[model]["pred_prob"])
    auc_value = auc(fpr, tpr)
    return [fpr, tpr, auc_value]


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
