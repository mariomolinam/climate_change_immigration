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
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"

def ROC_curve(roc_values, weather_names):
    # plot no skill and black background
    plt.figure(figsize=(15,8))
    plt.style.use("dark_background")
    plt.title("ROC Curve - Balanced Weights")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="white")
    # add fpr and tpr
    colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
    counter = 0
    for key in sorted(roc_values):
        values = roc_values[key]
        fpr, tpr, auc = values[0]["fpr"], values[0]["tpr"], values[0]["auc_value"]
        # true positive rate against false positive rate
        label_legend = weather_names[counter] + " - (AUC: " + str(round(auc, 3)) + ")"
        plt.plot(fpr,tpr, linestyle='-', color=colors[counter], label=label_legend)
        counter += 1

    # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc='lower right', frameon=False, fontsize=10)
    # plt.show()
    fig_name = path_git + "/results/ROC_curve_balanced_weights.png"
    plt.savefig(fig_name, bbox_inches='tight')



def ROC_curve_rural_urban(roc_values, weather_names, idx_rural_urban, output_list):

    metrocat = ["rancho","small_urban","town","metro"]

    for loc in range(len(metrocat)):
        name_fig = metrocat[loc]
        # plot no skill
        plt.figure(figsize=(15,8))
        plt.style.use("dark_background")
        plt.title("ROC Curve (RF - " + name_fig + ") " + "- Balanced weights")
        # plot the 45 degrees lines
        plt.plot([0, 1], [0, 1], linestyle='--', color="white")
        # add fpr and tpr
        colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                    "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
        counter = 0
        for key in sorted(roc_values):
            # idx
            idx = idx_rural_urban[key]["test_"+name_fig]
            pred_probs = rf_best[key][0].predict_proba(models_output[key]["X_test"]) # probabilities
            fpr, tpr, _ = roc_curve(models_output[key]["y_test"][idx], pred_probs[:,1][idx])
            auc_value = auc(fpr, tpr)
            # true positive rate against false positive rate
            label_legend = weather_names[counter] + " - (AUC: " + str(round(auc_value, 3)) + ")"
            plt.plot(fpr,tpr, linestyle='-', color=colors[counter], label=label_legend)
            counter += 1
        # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc='lower right', frameon=False, fontsize=10)
        # plt.show()
        fig_name = path_git + "/results/ROC_curve_" + name_fig+ ".png"
        plt.savefig(fig_name, bbox_inches='tight')
        plt.close()



def recall_precision_curve(precision_recall_values, weather_names):
    # plot no skill
    plt.figure(figsize=(15,8))
    plt.title("Precision-Recall Curve (RF) - Balanced weights")
    # plot the 45 degrees lines
    plt.plot([0, 1], [0, 1], linestyle='--', color="black")
    # add fpr and tpr
    colors = [  "red", "maroon", "darkgoldenrod", "olivedrab", "blue",
                "indigo", "darkorange", "cyan", "dodgerblue", "lawngreen"]
    counter = 0
    for key, values in precision_recall_values.items():
        prec, rec = values[0]["precision"], values[0]["recall"]
        # true positive rate against false positive rate
        label_legend = weather_names[counter] # + " - (AUC: " + str(round(auc, 3)) + ")"
        plt.plot(prec,rec, linestyle='-', color=colors[counter], label=label_legend)
        counter += 1

    # plt.plot(recall_socio, precision_socio, marker='.', color="b", label="Random Forest without prcp lags")
    plt.xlabel("Precision")
    plt.ylabel("Recall")
    plt.legend(loc='lower right', frameon=False, fontsize=10)
    # plt.show()
    fig_name = path_git + "/results/precision_recall_curve_rf.png"
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
