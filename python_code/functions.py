# -*- coding: utf-8 -*-
import csv, random, os, re, gc
import pandas as pd
import numpy as np

# paths
path_data = "/home/mario/Documents/environment_data/mmp_data"
path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"


def select_columns(data):
    """
        Input: pandas dataframe.

        Task: select columns of dataframe and subset.

        Return: pandas dataframe.
    """
    # define columns
    cols = [
            "commun",    # community ID
            "hhnum",     # household ID
            "persnum",   # person ID
            "year",      # year within person
            "geocode",
            # "occur_5", # 5 occupational categories (not time-varying; based on survey year)
            "usyr1",     # first year of migration
            "migf",
            "age",
            "sex",
            "mxmig",     # whether they migrated in mexico until this year
            "primary",   # if there is a school
            "secondary", # if there is a secondary school

            "totmighh",  # total number of prior U.S. migrants in the household (up until that year)
            "tbuscat",   # whether hh owns a business
            "troom",     # number of rooms in properties household owns
            "lnvland_nr",# log(value of land) — excluding that bought by remittances
            "dprev",     # prevalence of migration in community (share of people who have ever migrated to the U.S. up until that year)
            "agrim",     # share of men working in agriculture in community
            "minx2",     # share of people earning twice the minimum wage or more
            "metrocat",  # metropolitan status of community
            "ejido",     # collective land system (0/1)
            "lnpop",     # log of population size in community
            "bank",      # in community
            "visaaccs",  # visa accessibility to the U.S. in year
            "infrate",   # inflation in Mexico in year
            "mxminwag",  # min wage in mexico in year
            "mxunemp",   # unemployment in Mexico
            "usavwage",  # U.S. average wages for low-skill work in year
            "lntrade",   # log of trade between MX-U.S.
            "logdist"    # distance of community to the U.S.
            ]
    # define subset
    subset = data[cols]

    return subset


def select_data(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task: filter data based on relevant migration information:
            1. People who migrated in or after 1985
            2. Info provided after year of 1st migration (usyr1)

    Return: subset of pandas dataframe
    """
    # FILTER 1: get all migrants who migrated in or after 1985
    mmp_data = mmp_data.loc[ mmp_data.usyr1 >= "1985" , ]

    # FILTER 2: remove all observations for which there is information
    #           after the year of migration (usyr1 > year)
    mmp_data = mmp_data.loc[ mmp_data.year <= mmp_data.usyr1 , ]

    # FILTER 3: remove all observations that have observations before
    #           our first year with weather information (1980)
    mmp_data = mmp_data.loc[ mmp_data.year >= "1980" , ]

    return mmp_data


def correct_migrants(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task: Correct for migrants who have a valid year listed in
            "usyr1" but have a year earlier listed in survey

    Return: pandas dataframe
    """

    # get only migrants
    subset = mmp_data.loc[ mmp_data.usyr1 != "8888", : ]

    # set multiIndex: "persnum", "year"
    mmp_data_multi = mmp_data.set_index(["persnum", "year"])
    subset.set_index(["persnum", "year"], inplace=True)

    # check migrants with all 0 in "migf" and then obtain indices for persnum
    check_mig = subset.migf.sum(level=0)
    check_mig_idx = check_mig.apply(lambda x: "1" not in x).nonzero()[0]
    subset_idx_persnum = check_mig.iloc[check_mig_idx].index.get_level_values(0)

    # obtain highest year within selected migrants
    t = subset.loc[list(subset_idx_persnum),:].groupby(level=0).apply(
          lambda grp: grp.index.get_level_values("year").max() )

    # loop through all persnum indices and max year and recode
    for x in range(t.shape[0]):
        mmp_data_multi.loc[(t.index[x], t[x]), "migf"] = "1"
        mmp_data_multi.loc[t.index[x], "usyr1"] = t[x]

    return mmp_data_multi


def keep_five_person_year(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task: Keep the 5 most recent years per person

    Return: a pandas dataframe (mmp)
    """

    mmp_data.sort_index(level=["persnum","year"], ascending=False, inplace=True)

    print("Keeping up to 5 years per person. Please wait...")
    mmp_data_five = mmp_data.groupby(level=0).apply(lambda x: x.iloc[:5,:])
    print("Done!")

    mmp_data_five.reset_index(level=0, drop=True, inplace=True)

    return mmp_data_five


def attach_weather_by_geocode(mmp_data, w_data):
    """
    Input:  mmp_data: pandas dataframe (mmp).
            w_data: list of strs (with name of weather file).

    Task:   First, reset mmp_data indices.
            Second, read w_data file.
            Third, get weather name variable (e.g. prcp, tmax)
            Fourth, transform weather_data from wide to long format
            Fifth, merge mmp_data with weather long format.

    Return: pandas dataframe: merged mmp_data with weather info in long format
    """
    # reset index mmp_data to geocode and year because weather varies by community
    mmp_data_weather = mmp_data.reset_index()

    # mmp_data.set_index(["geocode", "year"], inplace=True)
    for w in w_data:
        # read weather data
        filename = path_data + "/" + w
        weather = pd.read_csv(filename, dtype="str")
        weather.drop('state', axis=1, inplace=True) # drop state column
        # weather variable name
        weather_name = re.sub("\d+", "", weather.iloc[:,3].name)[:-1]
        # from wide format to long format
        weather_long = pd.melt(weather, id_vars="geocode", var_name="year",value_name=weather_name)
        # remove weather name from year variable
        weather_long["year"].replace(regex=True,inplace=True,to_replace=r'\D',value=r'')
        # set index: geocode and year
        # weather_long.set_index(["geocode", "year"], inplace=True)
        # merge
        mmp_data_weather = pd.merge(mmp_data_weather, weather_long, how="inner", on=["geocode", "year"])

    return mmp_data_weather


def create_test_set(data, seed=50):

    # NON-MIGRANTS
    # unique users
    non_migrants = data.loc[data.usyr1 == "8888","persnum"].unique()
    N_total_nonmigrants = int(non_migrants.shape[0] * 0.25)
    random.seed(seed)
    non_migrants_sub = random.sample(non_migrants, N_total_nonmigrants)

    # MIGRANTS
    migrants = data.loc[data.usyr1 != "8888","persnum"].unique()
    N_total_migrants = int(migrants.shape[0] * 0.25)
    random.seed(seed+2)
    migrants_sub = random.sample(migrants, N_total_migrants)

    # build test and training sets
    data_test = data.loc[ data.persnum.isin(non_migrants_sub) | data.persnum.isin(migrants_sub) ,:]
    data_train = data.loc[ ~ ( data.persnum.isin(non_migrants_sub) |  data.persnum.isin(migrants_sub) ),: ]
    # save test set
    file_test = "/ind161_test_set.csv"
    data_test.to_csv(path_data + file_test)
    # train set
    file_train = "/ind161_train_set.csv"
    data_train.to_csv(path_data + file_train, index=False)
    # message
    message = "Test and train sets created!"
    return message

def relabel_variables(data):
    ####  S O C I O  -  D E M O G R A P H I C S
    ################################################
    data = data.assign( sex = pd.get_dummies(data.sex).female,           # sex: female/male
                        primary = pd.get_dummies(data.primary).yes,      # if there is primary school
                        secondary = pd.get_dummies(data.secondary).yes,  # if there is secondary school
                        mxmig = pd.get_dummies(data.mxmig).yes,          # mexican migration
                        age = data.age.astype(int),                      # age
                        age2 = data.age.astype(int)**2,                  # age squared
                        totmighh = data.totmighh.astype(int),            # total migrants in household
                        troom = data.troom.astype(int),                  # number of rooms in household
                        tbuscat = pd.get_dummies(data.tbuscat).yes,      # wether hh owns a business
                        dprev = data.dprev.astype(float),                # prevalenve of migration in the community
                        lnvland_nr = data.lnvland_nr.astype(float),      # value of land (log)
                        agrim = data.agrim.astype(float),                # share of main working in agriculture
                        minx2 = data.minx2.astype(float),                # share of people earning twice minimum wage
                        lnpop = data.lnpop.astype(float),                # population size (lnpop)
                        ejido = pd.get_dummies(data.ejido).yes,          # ejido
                        bank = pd.get_dummies(data.bank).yes,            # bank
                        visaaccs = data.visaaccs.astype(float),          # visaaccs
                        infrate = data.infrate.astype(float),            # infrate: inflation per year
                        mxminwag = data.mxminwag.astype(float),          # mxminwag: minimum wage
                        mxunemp = data.mxunemp.astype(float),            # mxunemp: unemployment
                        usavwage = data.usavwage.astype(float),          # usavwage: USA average wage for low skill labor
                        lntrade = data.lntrade.astype(float),            # log trade mexico-USA
                        logdist = data.logdist.astype(float) )           # distance to US (log)

    # metropolitan status: keep only 3 categories
    data[["rancho", "small urban", "town"]] = pd.get_dummies(data.metrocat).loc[:,
                                                                        ["rancho", "small urban", "town"]]

    ####  W E A T H E R
    ################################################
    weather_measures = ['prcp_x', 'tmax_x', 'norm_%-tmax', 'prcp_y', 'spell-tmax', 'tmax_y', 'tmax', 'norm_%-prcp', 'prcp']
    data.loc[:,weather_measures] = data.loc[:,weather_measures].astype(float)

    return data



#
#
# # read file and count number of rows
# def row_counter(path):
#     # read in chunks of 1,000
#     mmp = pd.read_csv(path, chunksize=10000)
#     Nrows = 0
#     for line in mmp:
#         Nrows += line.shape[0]
#     return Nrows
#
#
# # Define N for training, validation, and test set
# def N_for_sets(row_counter):
#     # get total number of rows
#     Nrows = row_counter(full_path)
#     prop = [0.5, 0.25, 0.25]
#     # Create training, validation, and test set
#     N_training = round(Nrows*prop[0])
#     N_validation = round(Nrows*prop[1])
#     N_test = round(Nrows*prop[2]) + 1 # add last row
#     # check numbers add up...
#     if(N_training + N_validation + N_test == Nrows):
#         print("Success!")
#         N_sets = { "N_training": N_training,
#                    "N_validation": N_validation,
#                    "N_test": N_test,
#                    "N_rows_total": Nrows}
#         return N_sets
#     else:
#         print("Numbers don't add up...")
#         return None
#
#
# N_sets = N_for_sets(row_counter)
#
#
# # create ids for training, validation, and test sets
# def create_sets_idx(N_sets, seed = 300):
#     # get all possible idx rows
#     Nrows = N_sets["N_rows_total"]
#     range_total = range(0, Nrows)
#     # TRAINING SET
#     # get ids for training_set
#     random.seed(seed) # set random seed
#     training_set_idx = random.sample(range_total, N_sets["N_training"])
#     # get ids that are left
#     range_left = set(range_total) - set(training_set_idx)
#     # VALIDATION SET
#     random.seed(seed) # set random seed
#     validation_set_idx = random.sample(range_left, N_sets["N_validation"])
#     # TEST SET
#     # it's defined by ids that are left
#     range_left = set(range_left) - set(validation_set_idx)
#     test_set_idx = list(range_left)
#     # output all sets
#     sets_idx = { "training_idx": training_set_idx,
#                  "validation_idx": validation_set_idx,
#                  "test_idx": test_set_idx }
#     return sets_idx
#
#
# # Create training, validation, and test sets
# def create_sets_files(create_sets_idx):
#     # get sets idx
#     sets_idx = create_sets_idx(N_sets)
#     header_original = list(pd.read_csv(full_path, nrows=1).columns)
#     # path to save data
#     path = "/home/mario/Documents/environment_data"
#     # loop through all sets
#     for key in sets_idx:
#         if key == "training_idx":
#             print("     Creating training set...")
#             filename = path + '/mmp_training_set.csv'
#             # skip validation and test
#             skip = set(sets_idx["validation_idx"]).union(set(sets_idx["test_idx"]))
#             skip = sorted(skip) # sort ids
#             mmp_piece = pd.read_csv(full_path, dtype="str", chunksize=10000, skiprows = skip, header=None)
#             for chunk in mmp_piece:
#                 chunk.to_csv(filename, mode="a", header=header_original)
#         elif key == "validation_idx":
#             print("     Creating validation set...")
#             filename = path + '/mmp_validation_set.csv'
#             # skip validation and test
#             skip = set(sets_idx["training_idx"]).union(set(sets_idx["test_idx"]))
#             skip = sorted(skip) # sort ids
#             mmp_piece = pd.read_csv(full_path, dtype="str", chunksize=10000, skiprows = skip, header=None)
#             for chunk in mmp_piece:
#                 chunk.to_csv(filename, mode="a", header=header_original)
#         else:
#             print("     Creating test set...")
#             filename = path + '/mmp_test_set.csv'
#             # skip validation and test
#             skip = set(sets_idx["validation_idx"]).union(set(sets_idx["training_idx"]))
#             skip = sorted(skip) # sort ids
#             mmp_piece = pd.read_csv(full_path, dtype="str", chunksize=10000, skiprows = skip, header=None)
#             for chunk in mmp_piece:
#                 chunk.to_csv(filename, mode="a", header=header_original)
#     # return message
#     message = "All files successfully created!"
#     return message
#
# # Create training, validation, and test sets
# create_sets_files(create_sets_idx)
