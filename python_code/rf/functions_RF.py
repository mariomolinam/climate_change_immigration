# -*- coding: utf-8 -*-
import csv, random, os, re, gc
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, cross_val_score, cross_val_predict
from sklearn.metrics import make_scorer
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, matthews_corrcoef, average_precision_score



def get_features(file):
    """
    Input:
        - a pandas dataframe
        - a string (file name)

    Task: Create list of sociodemographic features

    Return: a dictionary with time constant, time varying, and weather variables.
    """
    # TIME CONSTANT (INDIVIDUAL-LEVEL)
    features_sociodem_constant = [
        # "migf",      # whether migrant or not (regardless of year of first migration)
        "primary",   # if there is a school
        "secondary", # if there is a secondary school
        "sex",
        "totmighh",  # total number of prior U.S. migrants in the household (up until that year)
        "tbuscat",   # whether hh owns a business
        "troom",     # number of rooms in properties household owns
        # "metropolitan",  # from metrocat
        "rancho",          # from metrocat
        "small urban",     # from metrocat
        "town",            # from metrocat
        "lnvland_nr",# log(value of land) — excluding that bought by remittances
        "ejido",     # collective land system (0/1)
        "logdist"    # distance of community to the U.S.
    ]

    # TIME VARYING (INDIVIDUAL-LEVEL)
    features_sociodem_varying = [
          "age",
          "age2",
          "mxmig",     # whether they migrated in mexico until this year
          "visaaccs",  # visa accessibility to the U.S. in year
          "infrate",   # inflation in Mexico in year
          "mxminwag",  # min wage in mexico in year
          "mxunemp",   # unemployment in Mexico
          "usavwage",  # U.S. average wages for low-skill work in year
          "lntrade"    # log of trade between MX-U.S.d
    ]

    # COMMUNITY-LEVEL VARIABLES
    features_community = [
        "dprev_0",   # prevalence of migration in community (share of people who
                     # have ever migrated to the U.S. up until that year). Dprev is
                     # time-varying but it is highly correlated over time (r > 0.98)
        "lnpop",     # log of population size in community
        "bank",      # in community
        "agrim",     # TIME VARYING (CHANGE) # share of men working in agriculture in community
        "minx2"      # share of people earning twice the minimum wage or more
    ]

    # STATE and YEAR indicators
    state_year = [
        "state_10",
        "state_11",
        "state_12",
        "state_13",
        "state_14",
        "state_15",
        "state_16",
        "state_17",
        "state_18",
        "state_19",
        "state_2",
        "state_20",
        "state_21",
        "state_22",
        "state_24",
        "state_27",
        "state_25",
        "state_29",
        "state_30",
        "state_31",
        "state_32",
        "state_6",
        "state_8",
        "year_1990",
        "year_1991",
        "year_1992",
        "year_1993",
        "year_1994",
        "year_1995",
        "year_1996",
        "year_1997",
        "year_1998",
        "year_1999",
        "year_2000",
        'year_2001',
        'year_2002',
        "year_2003",
        "year_2004",
        "year_2005",
        "year_2006",
        "year_2007",
        "year_2008",
        "year_2009",
        "year_2010",
        "year_2011",
        "year_2012",
        "year_2013",
        "year_2014",
        'year_2015',
        "year_2016"
    ]

    # WEATHER VARIABLES and KEYS
    features_weather = [
         "tmin_cum_2sd",
         "warmest_night",
         "extremely_wet_longterm99th",
         "spell_dry_prcp",
         "coldest_day",
         "max_5day_cons",
         # "norm_deviation_longterm_cats",
         "perc_cold_nights",
         "prcp_minimum_yearly",
         "perc_warmest_nights",
         "norm_percent_short-term_tmax",
         "total_frost_days",
         "norm_deviation_longterm",
         # "norm_deviation_short-term_cats_tmax",
         "gdd",
         "prcp_total_wet_days",
         "spell_cold_tmin",
         "perc_change_prcp",
         "spell_wet_prcp",
         "norm_deviation_short-term_tmax",
         "prcp_low_cum",
         "hdd",
         "norm_percent_short-term_prcp",
         "tmax_cum_2sd",
         "prcp_total_heavy",
         "crude_above30-tmax_yearly-consecutive",
         "spell_warm_tmax",
         "warmest_day",
         "norm_deviation_short-term_prcp",
         "perc_cold_days",
         "prcp_maximum_yearly",
         # "norm_deviation_short-term_cats_prcp",
         # "norm_deviation_longterm_cats_(-1,1)",
         "norm_deviation_longterm_cats_(-2,-1]",
         'norm_deviation_longterm_cats_[1,2)',
         # 'norm_deviation_short-term_cats_tmax_(-1,1)',
         "norm_deviation_short-term_cats_tmax_>=2",
         'norm_deviation_short-term_cats_tmax_[1,2)',
         # 'norm_deviation_short-term_cats_prcp_(-1,1)',
         "norm_deviation_short-term_cats_prcp_[1,2)"
    ]

    # rename weather variables
    # features_weather = { weather_keys[x]: [ features_weather[x] + '_' + str(i) for i in range(5) ] for x in range(len(features_weather)) }
    features_weather = [ x + '_' + str(i) for i in range(5) for x in features_weather ]
    # rename time_varying variables
    # features_sociodem_varying = [ name + "_" + str(i) for i in range(0) for name in features_sociodem_varying ]
    features_sociodem_varying = [ name + "_0" for name in features_sociodem_varying ]
    features_sociodem = { "individual_level": features_sociodem_constant + features_sociodem_varying,
                          "community_level": features_community,
                          "state_year": state_year,
                          "weather_vars": features_weather }
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
    n_estimators = [int(x) for x in np.linspace(start = 125, stop = 1500, num = 12)]
    # Number of features to consider at every split
    # max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(5, 40, num = 8)]
    max_depth.append(None)

    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
                   'max_depth': max_depth
                   }
    return random_grid


def random_forest_stat(X_train, y_train, task, params=None):
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

    if task == "search":
        # build random forest classifier
        rf = RandomForestClassifier( criterion = "entropy",
                                     bootstrap = True,
                                     class_weight = "balanced_subsample"
                                    )
        # determine
        scoring_params = { 'Matthews_score': make_scorer(matthews_corrcoef), # use make_scorer to compute Matthews corr
                           'f1': 'f1',
                           'AUC': 'roc_auc',
                           'balanced_accuracy':'balanced_accuracy'}

        # determine search grid to find best paramaters using cross-validation (5 folds)
        rf_grid = RandomizedSearchCV( estimator = rf,
                                      param_distributions = random_grid,
                                      scoring = scoring_params, # accounts for imbalance in data
                                      n_jobs = -1, # number of cores (-1 to use them all)
                                      n_iter = 30,
                                      cv = 5,
                                      refit = False,
                                      verbose = 2,
                                      return_train_score = True
                                      # random_state=466
                                      )
        print('.'*60)
        print("\tEstimating a random forest with randomized grid search...\n")
        # run random forests
        rf_grid.fit(X_train, y_train)

        print("\n\tDone!\n\n")
        print('.'*60)
    else:
        # fit best random forest after search over many hyperparameters
        rf_grid = RandomForestClassifier( n_estimators = params["n_estimators"],
                                     max_depth = params["max_depth"],
                                     criterion = "entropy",
                                     bootstrap = False,
                                     class_weight = "balanced_subsample",
                                     n_jobs = -1
                                    )
        # fit
        rf_grid.fit(X_train, y_train)

    return rf_grid


def logistic_regression_stat(X_train, y_train):
    """
    Input:  Paramaters for Logistic Regression:

            X_train, y_train: numpy arrays
            weights: dict

    Task: run logistic regression and predict:
            - using train data (X_train)
            - using test data (Y_test)

    Returns: dictionary
    """
    lr = LogisticRegression(
                             # penalty = "none",
                             fit_intercept = True,
                             intercept_scaling = 1,
                             C = 1, # sets regularization
                             class_weight = "balanced",
                             solver = "lbfgs", # optimization algorithm
                             n_jobs = -1,
                             max_iter = 100000
                          )
    #
    print('.'*60)
    print("\tEstimating a logistic regression..\n")
    output = lr.fit(X_train, y_train)
    print("\n\tDone!\n\n")
    print('.'*60)
    return output


def run_RF(file, model_type):

    # LOAD DATA
    mmp_data_weather = pd.read_csv(file)

    #####################################################################
    #  S E L E C T   F E A T U R E S
    #####################################################################

    # Define variables for different levels
    first_migration = ["migf"]
    # all features contains all features to be used in the models
    # with no interactions
    all_features = get_features(file)
    models = ['model_a', 'model_b', 'model_c', 'model_d']
    list_features = ['individual_level', 'weather_vars', 'state_year', 'community_level']

    # run models for each specification
    MODEL_OUTPUT = {}
    for i in range(len(all_features)):
        print("Specification: ", list_features[i])

        # define features to be included
        set_of_features = list_features[ :i+1 ]
        features = []
        for x in range(i+1):
            features += all_features[set_of_features[x]]


        # remove missing values
        tr = mmp_data_weather.loc[:, first_migration + features]
        tr_subset = tr.dropna(axis=0, how="any")

        # Check there are no missing values taht haven't been dealt with
        if tr.shape[0] == tr_subset.shape[0]:
            print("\tAll is looking good...onwards!")
        else:
            print("\tProbably need to deal with missing values...")
            break

        #####################################################################
        # B U I L D   M O D E L S
        #####################################################################

        # C R E A T E   V A R I A B L E S
        ###################################
        # target vector
        y_train = np.array(tr_subset.migf)
        # features
        X_train = np.array(tr_subset.loc[:,features ])
        # train and validation sets (validation sets will be set in the Grid search for out-of-sample performance)
        # X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=200)

        if model_type == "rf":
            #  R A N D O M   F O R E S T
            ###################################
            # run Grid Search of Random Forest
            output = random_forest_stat(X_train, y_train, task="search")

            # S T O R E   O U T P U T
            MODEL_OUTPUT[models[i]] = {  model_type: output,
                                         "X_train":X_train,
                                         "y_train":y_train
                                         }
        else:
            # L O G I S T I C   R E G R E S S I O N
            ###################################
            output = logistic_regression_stat(X_train, y_train)

            # S T O R E   O U T P U T
            MODEL_OUTPUT[models[i]] = {  model_type: output,
                                         "X_train":X_train,
                                         "y_train":y_train
                                         }
            # estimate only model specification with individual-level params
            break

    return MODEL_OUTPUT


def ROC_curve_values(output_list, test_values, model_type):
    roc_models = {}
    if model_type == "rf":
        for key, value in output_list.items():
            X_test = test_values[key]["X_test"]
            y_test = test_values[key]["y_test"]
            roc_models[key] = {}
            # get best estimator with balanced weights
            # best_model = output_list[key]['rf'][0].best_estimator_
            best_model = output_list[key]['best_model_retrained']
            pred_test = best_model.predict(X_test)
            pred_probs = best_model.predict_proba(X_test) # probabilities
            # ROC curve
            fpr, tpr, _ = roc_curve(y_test, pred_probs[:,1])
            auc_value = auc(fpr, tpr)
            # roc_models.append([fpr, tpr, auc_value])
            # update dictionary
            roc_models[key].update({"fpr":fpr, "tpr":tpr, "auc_value":auc_value})
    else:
        for key, value in output_list.items():
            count += 1
            print(count)
            # accuracy prediciton
            pred_train = value['lr'].predict( value["X_train"] )
            pred_test = value['lr'].predict(value["X_test"])
            pred_probs = value['lr'].predict_proba(value["X_test"]) # probabilities
            # ROC curve
            fpr, tpr, _ = roc_curve(value["y_test"], pred_probs[:,1])
            auc_value = auc(fpr, tpr)
            # roc_models.append([fpr, tpr, auc_value])
            # update dictionary
            roc_models[key] = { "fpr":fpr, "tpr":tpr, "auc_value":auc_value,
                                "pred_test":pred_test, "pred_train":pred_train, "pred_probs":pred_probs[:,1] }
    return roc_models


def get_test_values(FILE_TEST, rf):
    # load file
    mmp_weather_test = pd.read_csv(FILE_TEST)

    # remove column with row IDs (inplace)
    if "Unnamed: 0" in mmp_weather_test.columns:
        mmp_weather_test.drop("Unnamed: 0", axis="columns", inplace=True)

    # Define variables for different levels
    first_migration = ["migf"]

    # all features contains all features to be used in the models
    all_features = get_features(FILE_TEST)

    # test on each specific datat structure
    list_features = ['individual_level', 'weather_vars', 'state_year', 'community_level']
    models = ['model_a', 'model_b', 'model_c', 'model_d']

    # STORE VALUES OF TEST SET
    values = dict()
    for m in range(len(rf.keys())):
        set_of_features = list_features[ :m+1 ]

        features = []
        for x in range(m+1): features += all_features[set_of_features[x]]

        # remove missing values
        test = mmp_weather_test.loc[:, first_migration + features]
        test_subset = test.dropna(axis=0, how="any")

        # Check there are no missing values taht haven't been dealt with
        if test.shape[0] == test_subset.shape[0]:
            print("All is looking good...onwards!")
        else:
            print("...You need to deal with missing values first!")
            break

        # C R E A T E   V A R I A B L E S
        ###################################
        # target vector and features
        y_test = np.array(test_subset.migf)
        X_test = np.array(test_subset.loc[:,features ])

        values[models[m]] = {"X_test": X_test, "y_test": y_test, "features": features}

    return values


def performance_test_set(rf, test_values):
    # STORE VALUES OF TEST SET
    values = dict()
    for m in rf.keys():
        X_test = test_values[m]["X_test"]
        y_test = test_values[m]["y_test"]
        # Test on random forest
        rf_model = rf[m]
        # choose best estimator
        # rf_best = rf_model['rf'][r].best_estimator_
        rf_best = rf_model['best_model_retrained']
        # rf_best = rf_model['lr'] # FOR LOGISTIC REGRESSION
        # prediction using TEST set
        pred_test = rf_best.predict(X_test)
        # pred_probs using validation set
        pred_probs = rf_best.predict_proba(X_test)
        fpr, tpr, _ = roc_curve(y_test, pred_probs[:,1])
        # AUC
        auc_value = auc(fpr, tpr)
        # F1 Score
        f1_ = f1_score(y_test, pred_test)
        # Matthews Correlation
        mcc = matthews_corrcoef(y_test, pred_test)
        values[m] = [auc_value, f1_, mcc]
    return values


def eval_performance_rf(rf):
    # store values
    performance_vals = {}
    for m in rf.keys():
        print(m)
        # cross-validation results
        if isinstance(rf[m]['rf'], list):
            cv_results = rf[m]['rf'][0].cv_results_
        else:
            cv_results = rf[m]['rf'].cv_results_
        # F1 score
        f1 = cv_results["mean_test_f1"]
        f1_sorted = np.argsort(f1)[::-1][:3]
        # AUC score
        auc = cv_results["mean_test_AUC"]
        auc_sorted = np.argsort(auc)[::-1][:3]
        # Matthews score
        matt = cv_results["mean_test_Matthews_score"]
        matt_sorted = np.argsort(matt)[::-1][:3]

        # votes for best models
        all_best = np.concatenate((f1_sorted, auc_sorted, matt_sorted), axis=None)
        all_best = np.unique(all_best)

        all_best_votes = {}
        for entry in all_best:
            all_best_votes[entry] = 0
            auc_vote = np.where(auc_sorted==entry)[0]
            if auc_vote.shape[0] > 0:
                all_best_votes[entry] += auc_vote + 1
            else: # add 4 if model doesn't show up
                all_best_votes[entry] += 4
            f1_vote = np.where(f1_sorted==entry)[0]
            if f1_vote.shape[0] > 0:
                all_best_votes[entry] += f1_vote + 1
            else:
                all_best_votes[entry] += 4
            matt_vote = np.where(matt_sorted==entry)[0]
            if matt_vote.shape[0] > 0:
                all_best_votes[entry] += matt_vote + 1
            else:
                all_best_votes[entry] += 4

        # choose the best model based on the minimum value
        # (minimum possible score is 3)
        best_model = min(all_best_votes.items(), key = lambda k: k[1])[0]

        # best parameters
        params_best = cv_results["params"][best_model]

        # Refit model using all data (training set + validation set)
        best_output = random_forest_stat(rf[m]["X_train"], rf[m]["y_train"], task="best", params=params_best)

        # store in the dict
        performance_vals[m] = { "auc-f1_rank_best": [auc_sorted[0] if auc_sorted[0]==f1_sorted[0] else auc_sorted[1]],
                                "auc_vals_best3": auc[auc_sorted],
                                "f1_vals_best3": f1[f1_sorted],
                                "Matthews_vals_best3": matt[matt_sorted],
                                "params_best": params_best,
                                "best_model_retrained": best_output}
    return performance_vals


def perm_importance(final_models_rf, test_values):
    models = list(final_models_rf.keys())
    perm_store = {}
    for m in range(len(models)):
        print(models[m])
        X_test = test_values[models[m]]["X_test"]
        y_test = test_values[models[m]]["y_test"]
        perm = permutation_importance( final_models_rf[models[m]]["best_model_retrained"],
                                    X_test,
                                    y_test,
                                    n_repeats = 20, n_jobs = -1, scoring="roc_auc")
        perm_store[models[m]] = perm
    return perm_store
