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
from sklearn.metrics import average_precision_score
import matplotlib.pyplot as plt
import sys
# sys.path.insert(0, "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration/python_code")
# import functions_RF as func_rf


# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

def ROC_curve(roc_values, weather_names):
    # plot no skill
    plt.figure(figsize=(15,8))
    plt.title("ROC Curve - Weights 1:100000000")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="black")
    # add fpr and tpr
    colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
    counter = 0
    for key, values in roc_values.items():
        fpr, tpr, auc = values[1]["fpr"], values[1]["tpr"], values[1]["auc_value"]
        # true positive rate against false positive rate
        label_legend = weather_names[counter] + " - (AUC: " + str(round(auc, 3)) + ")"
        plt.plot(fpr,tpr, linestyle='-', color=colors[counter], label=label_legend)
        counter += 1

    # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc='lower right', frameon=False, fontsize=10)
    # plt.show()
    fig_name = path_git + "/results/ROC_curve_weights_ratio_1_100000000.png"
    plt.savefig(fig_name, bbox_inches='tight')


def ROC_sensitivity(rf_output_dict, y_test_list, weather_names):
    # plot no skill
    plt.figure()
    plt.title("ROC Curve with different cost ratios")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="black")
    colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
    for key, value in rf_output_dict.items():
        rf_output = rf_output_dict[key]
        key_int = [int(s) for s in list(key) if s.isdigit()][0]
        # build arrays
        fpr_array = np.array([0])
        tpr_array = np.array([0])
        for i in range(len(rf_output)):
            # true positive rate against false positive rate
            fpr, tpr, _ =  roc_curve(y_test_list[key_int], rf_output[i]["pred_test"])
            fpr_array = np.append(fpr_array, fpr[1])
            tpr_array = np.append(tpr_array, tpr[1])
        # add 1
        fpr_array = np.append(fpr_array, [1])
        tpr_array = np.append(tpr_array, [1])
        plt.plot(fpr_array, tpr_array, marker='x', color=colors[key_int], label=weather_names[key_int])
    # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc='lower right', frameon=False, fontsize=10)
    # plt.show()
    fig_name = path_git + "/results/ROC_sensitivity.png"
    plt.savefig(fig_name, bbox_inches='tight')


def confusion_matrices(rf_output_dict, y_train_list, y_test_list):
    filename = path_git + '/results/confusion_matrices.csv'
    with open(filename, 'w+') as f:
        for i in range(len(rf_output_dict)):
            y_train = y_train_list[i]
            y_test = y_test_list[i]
            for j in range(len(rf_output_dict["set_"+str(i)])):
                # training data
                y_pred = rf_output_dict["set_"+str(i)][j]['pred_train']
                cm = pd.DataFrame( confusion_matrix( y_train, y_pred ) )
                # test data
                y_pred = rf_output_dict["set_"+str(i)][j]['pred_test']
                cm = cm.append( pd.DataFrame( confusion_matrix( y_test, y_pred ) ) )
                # h = "Test set" + " - " + "model " + str(i+1)
                cm.to_csv(filename, mode='a', index=["True = 0", "True = 1"], header=["Pred = 0", "Pred = 1"])


def ROCcurve_models(rf_output_dict, y_test_list, model):
    # plot no skill
    plt.figure()
    plt.title("ROC Curve with cost ratio: 1,000,000,000:1")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="black")
    colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
    for i in range(len(rf_output_dict)):
        roc_values = ROC_curve_values(rf_output_dict["set_"+str(i)], y_test_list[i], model)
        val_fpr, val_tpr, val_auc = roc_values
        label_legend = weather_names[i] + " - (AUC: " + str(round(val_auc, 3)) + ")"
        plt.plot(val_fpr,val_tpr, linestyle='-', color=colors[i], label=label_legend)

    # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc='lower right', frameon=False, fontsize=10)
    # plt.show()
    fig_name = path_git + "/results/ROC_curve_model_4.png"
    plt.savefig(fig_name, bbox_inches='tight')
