# -*- coding: utf-8 -*-
import csv, random, os, re, gc
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import auc
from sklearn.metrics import average_precision_score
import matplotlib.pyplot as plt
import sys
# sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code")
# import functions_RF as func_rf


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/migration_climate_change/climate_change_immigration"

def ROC_curve(roc_values):
    legend_values = {"model_a": ["Individual-level variables", "-"],
                     "model_b": ["  + Weather variables", "--"],
                     "model_c": ["  + State-Year variables", "-."],
                     "model_d": ["  + Community-level variables", ":"]}
        # plot no skill and black background
    plt.figure(figsize=(12,7), dpi=120)
    plt.axes(facecolor="w")
    # plt.style.use("ggplot")
    plt.title("ROC Curve - Random Forests (test set)")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="#403e3e", linewidth=2)
    # add fpr and tpr
    colors = [  "red", "darkorange", "olivedrab","royalblue"]
    counter = 0
    for key in sorted(roc_values):
        values = roc_values[key]
        fpr, tpr, auc_value = values["fpr"], values["tpr"], values["auc_value"]
        # true positive rate against false positive rate
        label_legend = legend_values[key][0]
        plt.plot(fpr,tpr, linestyle=legend_values[key][1], color="#403e3e", label=label_legend, linewidth=2)
        counter += 1
    # define grid color and linewidth
    plt.grid(color="gray", linewidth=0.1)
    # add a box around plot
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["axes.linewidth"] = 1
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc=(0.59,0.21), frameon=True, fontsize=13, facecolor='w')
    # plt.show()
    fig_name = path_git + "/results/figure3.png"
    plt.savefig(fig_name, bbox_inches='tight')



def map_features(features_list):
    # Feature importance in predictive capacity
    features_sorted_all_labels = {
                "sex": "Male",
                "age2_0": "Age squared",
                "age_0": "Age",
                "bank": "Bank in community",
                "totmighh": "Migrants in hh",
                "lntrade_0":  "Ln(MX-US) trade",
                "logdist": "Ln(distance to border)",
                "troom": "No. of rooms owned",
                "usavwage_0": "Average US wage",
                "infrate_0": "MX inflation rate",
                "mxunemp_0": "MX unemployment rate",
                "visaaccs_0": "Visa accessibility",
                "lnvland_nr": "Log(land value)",
                "mxminwag_0": "MX min wage",
                "rancho": "Community = rancho",
                'tbuscat':  "Owns business",
                "town": "Community = town",
                "small urban": "Community = small urban",
                "secondary": "Middle school in community",
                "mxmig_0": "Migrated in MX?",
                "primary": "Primary school in community",
                "ejido": "Communal land in community",
                "gdd_0": "Growing degree day (lag 0)",
                "gdd_1": "Growing degree day (lag 1)",
                "gdd_2": "Growing degree day (lag 2)",
                "gdd_3": "Growing degree day (lag 3)",
                "gdd_4": "Growing degree day (lag 4)",
                "warmest_day_0": "Warmest day (lag 0)",
                "warmest_day_1": "Warmest day (lag 1)",
                "warmest_night_0": "Warmest night (lag 0)",
                "warmest_night_1": "Warmest night (lag 1)",
                "warmest_night_2": "Warmest night (lag 2)",
                "coldest_day_0": "Coldest day (lag 0)",
                "coldest_day_1": "Coldest day (lag 1)",
                "spell_warm_tmax_1": "Tmax Spell warm",
                "spell_dry_prcp_4": "Precipitation Spell dry (lag 4)",
                "year_2013": "Year 2013",
                "year_2011": "Year 2011",
                "norm_deviation_short-term_tmax_3": "T max short-term dev",
                "minx2": "% earning 2x min wage",
                "dprev_0": "Prevalence of migration",
                "lnpop": "Ln(Population size)",
                "agrim": "% of men in agriculture",
                "state_30": "Veracruz State"
                }
    map_feat = [features_sorted_all_labels[ name ] for name in features_list]
    return(map_feat)



def feature_importance_plot(final_models_rf, test_values):
    models_all = ["model_" + i for i in 'abcd']
    models_names = ["Model (" + i + ")" for i in 'abcd']
    collect_features = []

    # FIGURE: IMPORTANCES
    fig, axs = plt.subplots(2, 2, figsize=(14,9))
    axes = [x[i] for x in axs.tolist() for i in range(len(x))]
    plt.style.use("ggplot")

    for m in range(len(models_all)):
        # importances_all = models_output_rf[models_all[m]]['rf'][0].best_estimator_.feature_importances_
        best_rf = final_models_rf[models_all[m]]['best_model_retrained']
        importances_all = best_rf.feature_importances_
        # std_importances = np.std([tree.feature_importances_ for tree in best_rf.estimators_], axis=0)
        # std = np.std([tree.feature_importances_ for tree in rf_all.estimators_], axis=0)
        indices_all = np.argsort(importances_all)[::-1][:21]
        features_all = test_values[models_all[m]]['features']
        feature_names = {features_all[i]: importances_all[i] for i in indices_all}
        # Rescale variable importances relative to the 21 top variables in performance
        normalizer = sum(feature_names.values())
        for key, value in feature_names.items():
            feature_names[key] = value/normalizer
        # get values
        y_values = list(range(len(feature_names)))[::-1]
        x_values = list(feature_names.values())
        # x_values_std = list(feature_names_std.values())
        # collect features
        collect_features += collect_features + list(feature_names.keys())
        # map feature names
        feature_names_labels = map_features(feature_names.keys())
        # set axis
        ax = axes[m]
        ax.set_facecolor("white")
        if m==1 or m==3:
            # X-axis
            ax.set_xticks(np.arange(0,0.22, 0.04)[::-1])
            ax.set_xlim([0.22, 0])
            ax.set_yticklabels([]) # Hide the left y-axis tick-labels
            ax.set_yticks([]) # Hide the left y-axis ticks
            # create twin y-axis
            ax1 = ax.twinx()
            # ax1.set_facecolor("white")
            ax1.barh( y_values, x_values, color="gray")
            # ticks and values
            ax1.set_yticks(y_values)
            ax1.set_yticklabels( feature_names_labels, fontsize=11)
            # title
            ax1.set_title(models_names[m])
            # ax.tick_params(axis='y')
            ax1.set_ylim([-1, len(feature_names)])
            if m==3: ax.set_xlabel("Cumulative Predictive Power")
        else:
            # X-axis
            ax.set_xticks(np.arange(0,0.22, 0.04))
            ax.set_xlim([0, 0.22])
            # ticks and values
            ax.set_yticks(y_values)
            ax.set_yticklabels( feature_names_labels, fontsize=11)
            ax.barh( y_values, x_values,color="gray")
            # title
            ax.set_title(models_names[m])
            # ax.tick_params(axis='y')
            ax.set_ylim([-1, len(feature_names)])
            if m==2: ax.set_xlabel("Cumulative Predictive Power")

    plt.subplots_adjust(wspace=0.1, hspace=0.15)
    # plt.show()
    fig_name = path_git + "/results/figure4.png"
    plt.savefig(fig_name, bbox_inches='tight', dpi=120)
    plt.clf()



def feature_importance_permutation_plot(perm_features, test_values):

    models_names = ["Model (" + i + ")" for i in 'abcd']
    # FIGURE: IMPORTANCES
    fig, axs = plt.subplots(2, 2, figsize=(14,9))
    axes = [x[i] for x in axs.tolist() for i in range(len(x))]
    plt.style.use("ggplot")
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["axes.linewidth"] = 1

    for m in range(len(perm_features.keys())):
        # models and their features
        models_all = list(perm_features.keys())
        feature_names = test_values[models_all[m]]['features']
        # permutation results for model
        perm_model = perm_features[models_all[m]]
        # top 15 vars in terms of their AUC contribution
        final_idx = len(feature_names)
        top_vars_idx = perm_model.importances_mean.argsort()[final_idx-15:final_idx]
        # get values
        y_values = list(range(15)) #[::-1]
        x_values = perm_model.importances[top_vars_idx]
        feature_names_labels = map_features( [feature_names[x] for x in top_vars_idx])
        # set axis
        ax = axes[m]
        ax.set_facecolor("white")
        if m==1 or m==3:
            ax.set_xticks(np.arange(0,0.11, 0.02)[::-1])
            ax.set_xlim([0.11, -0.003])
            ax.set_yticklabels([]) # Hide the left y-axis tick-labels
            ax.set_yticks([]) # Hide the left y-axis ticks
            # invert values
            ax1 = ax.twinx()
            # title
            ax1.boxplot( x_values.T, vert=False, showfliers=False, labels=feature_names_labels,
                        positions=y_values, # boxprops = dict(linewidth=2, color='#403e3e'),
                        medianprops = dict(linestyle='-.', linewidth=1.5, color='#403e3e'))
            ax1.set_yticks(y_values)
            ax1.set_yticklabels( feature_names_labels, fontsize=11)
            # title
            ax1.set_title(models_names[m])
            ax1.set_ylim([-1, 15])
            # add x-axis label
            if m==3: ax.set_xlabel("Decrease in AUC score")
        else:
            ax.set_xticks(np.arange(0,0.11, 0.02))
            ax.set_xlim([-0.003, 0.11])
            # ticks and values
            ax.set_yticks(y_values)
            ax.set_yticklabels( feature_names_labels, fontsize=11)
            ax.boxplot( x_values.T, vert=False, showfliers=False, labels=feature_names_labels,
                        positions=y_values, # boxprops = dict(linewidth=2, color='#403e3e'),
                        medianprops = dict(linestyle='-.', linewidth=1.5, color='#403e3e'))
            ax.set_title(models_names[m])
            # ax.tick_params(axis='y')
            ax.set_ylim([-1, 15])
            if m==2: ax.set_xlabel("Decrease in AUC score")

    plt.subplots_adjust(wspace=0.1, hspace=0.15)
    # plt.show()
    fig_name = path_git + "/results/figure5.png"
    plt.savefig(fig_name, bbox_inches='tight', dpi=120)
    plt.clf()
