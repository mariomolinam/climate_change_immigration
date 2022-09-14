# -*- coding: utf-8 -*-
import csv, random, os, re, gc
from define_paths import *
import pandas as pd
import numpy as np


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
            "logdist",   # distance of community to the U.S.
            "visaaccs",  # visa accessibility to the U.S. in year
            "infrate",   # inflation in Mexico in year
            "mxminwag",  # min wage in mexico in year
            "mxunemp",   # unemployment in Mexico
            "usavwage",  # U.S. average wages for low-skill work in year
            "lntrade"    # log of trade between MX-U.S.

            ]
    # define subset
    subset = data[cols]

    return subset


def select_data(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task: filter data based on relevant migration information:
            1. People who migrated on or after 1985
            2. Info provided after year of 1st migration (usyr1)
            3. People with info only after 1980 (migrants or non-migrants).

    Return: subset of pandas dataframe
    """

    # FILTER 1: GET all MIGRANTS who migrated on or after 1985
    mmp_data = mmp_data.loc[ mmp_data.usyr1 >= "1985" , ]

    cond = mmp_data.year <= mmp_data.usyr1
    mmp_data = mmp_data.loc[ cond , ]

    # FILTER 2: remove all observations (MIGRANTS and NON-MIGRANTS) that
    #           have entries before our first year with weather
    #           information (1980).
    mmp_data = mmp_data.loc[ mmp_data.year >= "1980" , ]

    return mmp_data


def correct_migrants(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task: Correct for migrants who have a valid year listed in
            year of migration ("usyr1"!=8888) but have a year earlier
            listed in survey ("year").

    Return: pandas dataframe
    """

    # get only migrants
    subset = mmp_data.loc[ mmp_data.usyr1 != "8888", : ]

    # set multiIndex: "persnum", "year"
    subset.set_index(["persnum", "year"], inplace=True)

    # check migrants with all 0 in "migf" and then obtain indices for persnum'
    check_mig = subset.migf.sum(level=0) # produce a string with year-migration sequence (0s and 1s)
    subset_idx_persnum = check_mig[check_mig.apply(lambda x: "1" not in x)].index


    # obtain highest year within selected migrants
    t = subset.loc[subset_idx_persnum,:].groupby(level=0).apply(
          lambda grp: grp.index.get_level_values("year").max() )

    # set multiIndex: "persnum", "year"
    mmp_data_multi = mmp_data.set_index(["persnum", "year"]).sort_index()
    # use zip to combine persnum and year and .loc to search for those cases
    mmp_data_multi.loc[ list(zip(t.index, t)) , "migf"] = "1"

    rep = mmp_data_multi.loc[(t.index, slice(None)), "usyr1"].groupby(level=['persnum']).size()
    new_vals = t.repeat(rep.values)
    mmp_data_multi.loc[(t.index, slice(None)), "usyr1"] = new_vals.values

    return mmp_data_multi


def select_five_year_points(resp):
    """
    Input: pands dataframe (mmp) from function groupby (used in function keep_five_person_year())

    Task:
        - It selects 5 rows from dataframe coming from groupby function using
        level=0 (i.e. persnum from MMP survey).
        - It distinguishes from non-migrants and migrants, such that if
        respondent is non-migrant, then the year from which non-migrant history will
        considered is randomly chosen, and then it selects the past 5 years from this
        starting point. If migrant, then it selects the first 5 rows. Rows are ordered by year.

    Return: pandas dataframe (mmp)
    """

    # check if non-migrant or miragtn
    if sum(resp.usyr1.isin(['8888'])) > 0:
        # if there are more than 5 rows, then randomly choose the starting year.
        max_year = resp.index.get_level_values('year')[0]
        if resp.shape[0] > 5 and int(max_year) > 1989 :
            # set range from the fifth time point on
            idx_range = range(resp.shape[0])[4:]
            # set seed for random choice
            rng = np.random.default_rng(100)
            random_idx = int(rng.choice(idx_range, size=1))
            idx_random_range = range(random_idx-4, random_idx+1)
            # print(idx_random_range)
            output = resp.iloc[idx_random_range,:]
        else:
            output = resp.iloc[:5,:]
    else:
        output = resp.iloc[:5,:]

    return output


def keep_five_person_year(mmp_data):
    """
    Input: pandas dataframe (mmp)

    Task:
        - Keep the 5 most recent years per person

    Return: a pandas dataframe (mmp)
    """

    # sort index: persnum (ascending) and year (descending)
    mmp_data.sort_index(level=["persnum","year"], ascending=[True,False], inplace=True)

    # count observations with at least 5 years and exlude them.
    obs_counter = mmp_data.count(level=0).iloc[:,0]
    obs_idx = obs_counter[obs_counter < 5].index
    less_than_five = mmp_data.index.get_level_values(0).isin(obs_idx)
    mmp_data_sub = mmp_data[~ less_than_five]

    print("Keeping up to 5 years per person. Please wait...")

    # for migrants select the past 5 years if they exist
    mmp_data_five = mmp_data_sub.groupby(level=0).apply(lambda x: select_five_year_points(x))
    print("Done!")

    mmp_data_five.reset_index(level=0, drop=True, inplace=True)

    return mmp_data_five


def attach_weather_5_year_lags(mmp_data, w_data):
    """
    Input:  mmp_data: pandas dataframe (mmp).
            w_data: list of strs (with name of weather file).

    Task:
            1. reset mmp_data indices.
            2. read w_data file.
            3. get weather name variable (using name of file)
            4. transform weather_data from wide to long format
            5. merge mmp_data_weather with weather_long long format.

    Return:
        - pandas dataframe - merged mmp_data with weather info in long format
    """
    # reset index mmp_data to geocode and year because weather varies by community
    mmp_data_weather = mmp_data.reset_index()

    for w in w_data:
        # read weather data
        filename = path_data + "/" + w
        weather = pd.read_csv(filename, dtype="str")
        # if "state" in weather.columns:
        weather.drop('state', axis=1, inplace=True) # drop state column

        # weather variable name
        weather_name = re.sub("mmp.+", "", w)[:-1]

        # from wide format to long format
        weather_long = pd.melt( weather,id_vars="geocode",var_name="year",value_name=weather_name )

        # remove weather name from year variable: it matches four consecutive digits
        # in a string
        weather_long["year"] = weather_long['year'].str.extract(r'(\d{4})')
        # weather_long["year"].replace( regex=True,inplace=True,to_replace=r'\D', value=r'')

        # merge
        mmp_data_weather = pd.merge( mmp_data_weather,weather_long,how="left",on=["geocode", "year"])
        # print(mmp_data_weather.shape)

    return mmp_data_weather


def create_test_set(data, seed=50):
    """
    Input:
        - data: pandas dataframe
        - seed: an integer

    Task:
        - It creates training and test sets (75% and 25%, respectively).
        - Since migration is a rare event, it stratifies the sample
        by prevalence of the event.

    Return:
        - It saves test and training sets as two separate csv files.
        - It returns a message saying whether this operation was successful.
    """

    # NON-MIGRANTS
    # unique users
    non_migrants = data.loc[data.usyr1 == "8888","persnum"].unique()
    N_total_nonmigrants = int(non_migrants.shape[0] * 0.25)
    random.seed(seed)    # seed the random generator
    non_migrants_sub = random.sample( list(non_migrants), N_total_nonmigrants)

    # MIGRANTS
    migrants = data.loc[data.usyr1 != "8888","persnum"].unique()
    N_total_migrants = int(migrants.shape[0] * 0.25)
    random.seed(seed+2)  # seed the random generator
    migrants_sub = random.sample( list(migrants), N_total_migrants)

    # build test and training sets
    data_test = data.loc[ data.persnum.isin(non_migrants_sub) | data.persnum.isin(migrants_sub) ,:]
    data_train = data.loc[ ~ ( data.persnum.isin(non_migrants_sub) |  data.persnum.isin(migrants_sub) ),: ]

    # save test set
    file_test = "/ind161_test_set_wide.csv"
    # train set
    file_train = "/ind161_train_set_wide.csv"

    # save test set
    data_test.to_csv(path_data + file_test)
    # save training set
    data_train.to_csv(path_data + file_train, index=False)

    return "Test and train sets created!"


def structure_wide(mmp_data):
    """
    Input: pandas dataframe

    Task:
        - Transform from long format to wide format

    Return: pandas dataframe
    """

    # define time-varying and time-constant variables
    time_varying = [
        "year",
        "age",
        "mxmig",     # whether they migrated in mexico until this year
        "dprev",     # prevalence of migration in community (share of people who have ever
                     # migrated to the U.S. up until that year)
        "visaaccs",  # visa accessibility to the U.S. in year
        "infrate",   # inflation in Mexico in year
        "mxminwag",  # min wage in mexico in year
        "mxunemp",   # unemployment in Mexico
        "usavwage",  # U.S. average wages for low-skill work in year
        "lntrade"    # log of trade between MX-U.S.
    ]

    time_constant = [
        "geocode",
        "commun",    # community ID
        "hhnum",     # household ID
        # "persnum",   # person ID
        "sex",
        "totmighh",  # total number of prior U.S. migrants in the household (up until that year)
        "primary",   # if there is a school
        "secondary", # if there is a secondary school
        "tbuscat",   # whether hh owns a business
        "troom",     # number of rooms in properties household owns
        "migf",      # whether migrant or not (regardless of year of first migration)
        "usyr1",     # first year of migration
        "lnvland_nr",# log(value of land) — excluding that bought by remittances
        "bank",      # in community
        "lnpop",     # log of population size in community
        "ejido",     # collective land system (0/1)
        "metrocat",  # metropolitan status of community
        "agrim",     # share of men working in agriculture in community
        "minx2",      # share of people earning twice the minimum wage or more
        "logdist"    # distance of community to the U.S.
    ]

    logdist_idx = list(mmp_data.columns).index("logdist")
    weather_vars = list(mmp_data.columns[logdist_idx+1:])

    # add column that indexes years: from 1 to 5 regardless of actual year.
    # This would allow to compare observations, say, between 2002-2007 and 1983-1987.
    year_max = mmp_data.groupby(mmp_data.persnum).apply(lambda grp: grp.year.max())
    year_max.name = "year_max"
    year_max = year_max.reset_index()

    # merge (left outer join)
    mmp_data = mmp_data.merge(year_max, how='left', on='persnum')
    # take diff and set temporal lags
    year_diff = mmp_data.year_max.astype(int) - mmp_data.year.astype(int)
    mmp_data = mmp_data.assign(year_diff=year_diff.astype(str).values)

    # reshape from LONG to WIDE and keep time-varying columns only
    mmp_data_pivoted = mmp_data.pivot(index="persnum", columns="year_diff")

    # get time-VARYING variables
    mmp_data_varying = mmp_data_pivoted[time_varying + weather_vars]
    mmp_data_varying.columns = mmp_data_varying.columns.remove_unused_levels()
    # rename time-VARYING INDICES
    mmp_data_varying.columns = [ i if len(j) == 0 else i + '_' + j for i, j in mmp_data_varying.columns ]
    mmp_data_varying.reset_index(inplace=True)

    # get time-CONSTANT variables
    mmp_data_constant = mmp_data_pivoted[time_constant]
    mmp_data_constant.columns = mmp_data_constant.columns.remove_unused_levels()

    # remove second level for time_constant (allc constant values are repeated from 0 to 4)
    mmp_data_constant = mmp_data_constant.loc[ :, (mmp_data_constant.columns.get_level_values(0), '0') ]
    mmp_data_constant.columns = mmp_data_constant.columns.droplevel(level=1)
    mmp_data_constant.reset_index(inplace=True)


    # merge time-constant and time-varying variables
    mmp_data = mmp_data_constant.merge(mmp_data_varying, on="persnum")

    return mmp_data


def relabel_variables(data):
    """
    Input: pandas dataframe (mmp data).

    Task: Relabel variables.
            - Some factors variables are transformed into dummies.
            - Other variables are transformed from str to float or int.
            - Weather variables are transformed to float.

    Return: pandas dataframe.
    """

    ####  S O C I O  -  D E M O G R A P H I C S
    ################################################
    # TIME CONSTANT
    data = data.assign( sex = pd.get_dummies(data.sex).female,           # sex: female/male
                        primary = pd.get_dummies(data.primary).yes,      # if there is primary school
                        secondary = pd.get_dummies(data.secondary).yes,  # if there is secondary school
                        totmighh = data.totmighh.astype(int),            # total migrants in household
                        troom = data.troom.astype(int),                  # number of rooms in household
                        tbuscat = pd.get_dummies(data.tbuscat).yes,      # wether hh owns a business
                        lnvland_nr = data.lnvland_nr.astype(float),      # value of land (log)
                        agrim = data.agrim.astype(float),                # share of main working in agriculture
                        minx2 = data.minx2.astype(float),                # share of people earning twice minimum wage
                        lnpop = data.lnpop.astype(float),                # population size (lnpop)
                        ejido = pd.get_dummies(data.ejido).yes,          # ejido
                        bank = pd.get_dummies(data.bank).yes,            # bank
                        logdist = data.logdist.astype(float) )           # distance to US (log)



    # metropolitan status: keep only 3 categories (metropolitan is reference)
    data[["rancho", "small urban", "town"]] = pd.get_dummies(data.metrocat).loc[:,
                                                                        ["rancho", "small urban", "town"]]

    # STATE dummies
    state_dummies = pd.get_dummies(data.state).iloc[:,1:]
    state_labels =  ["state_" + str(x) for x in list(state_dummies.columns)]
    data[state_labels] = state_dummies

    # TIME-VARYING variables
    time_varying = [ "age",
                     "mxmig",
                     "dprev",
                     "visaaccs",
                     "infrate",
                     "mxminwag",
                     "mxunemp",
                     "usavwage",
                     "lntrade"
                    ]
    time_varying = { x: [x + '_' + str(i) for i in range(5)] for x in time_varying }

    # age
    data.loc[:,time_varying["age"]] = data.loc[:,time_varying["age"]].astype(float)

    # age squared
    age2 = ["age2_" + str(i) for i in range(5)]
    data[age2] = data.loc[:,time_varying["age"]].astype(float)**2

    # mexican migration
    data[ time_varying["mxmig"] ] = pd.get_dummies(data.loc[:,time_varying["mxmig"]]).iloc[:,list(range(1,11,2))]

    # YEAR dummies
    year_dummies = pd.get_dummies(data.year_0).iloc[:,1:]
    year_labels =  ["year_" + str(x) for x in list(year_dummies.columns)]
    data[year_labels] = year_dummies

    rest = ["dprev","visaaccs","infrate","mxminwag","mxunemp","usavwage","lntrade"]
    for i in rest:
        data[time_varying[i]] = data.loc[:,time_varying[i]].astype(float)

    ####  W E A T H E R
    ################################################
    # Numerical weather measures
    weather_measures_num = [ "tmin_cum_2sd",
                            "warmest_night",
                            "extremely_wet_longterm99th",
                            "spell_dry_prcp",
                            "prcp_total_yearly_average",
                            "coldest_day",
                            "max_5day_cons",
                            "perc_cold_nights",
                            "prcp_minimum_yearly",
                            "perc_warmest_nights",
                            "norm_percent_short-term_tmax",
                            "total_frost_days",
                            "norm_deviation_longterm",
                            "gdd",
                            "prcp_total_wet_days",
                            "spell_cold_tmin",
                            "perc_change_prcp",
                            "spell_wet_prcp",
                            "norm_deviation_short-term_tmax",
                            "prcp_low_cum",
                            "crude_raw-tmax_yearly-average",
                            "hdd",
                            "norm_percent_short-term_prcp",
                            "tmax_cum_2sd",
                            "prcp_total_heavy",
                            "crude_above30-tmax_yearly-consecutive",
                            "spell_warm_tmax",
                            "warmest_day",
                            "norm_deviation_short-term_prcp",
                            "perc_cold_days",
                            "crude_above30-tmax_yearly-average",
                            "prcp_average_yearly_average",
                            "prcp_maximum_yearly"
                            ]

    weather_measures_num = [ x + '_' + str(i) for i in range(5) for x in weather_measures_num]

    data.loc[:,weather_measures_num] = data.loc[:,weather_measures_num].astype(float)

    # Categorical weather measures
    weather_measures_cat = [ "norm_deviation_longterm_cats",
                             "norm_deviation_short-term_cats_tmax",
                             "norm_deviation_short-term_cats_prcp"
                            ]
    # Add dummy columns for categeorical variables, including lags
    for w in weather_measures_cat:
        for i in range(5):
            var_name = w + "_" + str(i)
            dum_cats = pd.get_dummies(data[var_name])
            dum_cats_cols = [ w + "_" + x + "_" + str(i) for x in dum_cats.columns ]
            data[ dum_cats_cols[1:] ] = dum_cats.iloc[:,1:]
            # drop columns used to create dummy columns
            data = data.drop([var_name], axis=1)

    return data


def NA_values(mmp_data_weather):

    mmp_data_weather.set_index(["persnum", "year"], inplace=True)

    # drop missing values
    sub_all_noNA = mmp_data_weather.dropna(axis=0, how="any")

    # logical values for persnum obs > 1
    just_one = sub_all_noNA.groupby(level=0).count().iloc[:,0]
    # get persnum indices
    obs_idx = just_one[just_one > 1].index
    # use persnum indices to map persnum in sub_all_noNA
    more_than_one = sub_all_noNA.index.get_level_values(0).isin(obs_idx)
    # subset sub_all_noNA so that all obs have at least 2 time points
    sub_all_noNA = sub_all_noNA[more_than_one]

    # reset row indices
    sub_all_noNA.reset_index(inplace=True)

    return sub_all_noNA


def number_of_lags(mmp_data_weather, lag_number):

    # set persnum and year as multilevel index
    mmp_data_weather.set_index(["persnum", "year"], inplace=True)

    # count how many time-person obs are
    counter = mmp_data_weather.groupby(level=0).count().iloc[:,0]

    # choose obs that have person-year obs >= lag_number
    obs_idx = counter[counter >= lag_number].index
    obs_logical = mmp_data_weather.index.get_level_values(0).isin(obs_idx)

    # subset mmp_data_weather
    mmp_data_weather = mmp_data_weather[obs_logical]

    # reset row indices
    mmp_data_weather.reset_index(inplace=True)

    return mmp_data_weather


def add_mx_state(mmp_weather):
    state = mmp_weather.loc[:,"geocode"].apply(lambda x: x[0:2] if len(x) == 9 else x[0:1])
    mmp_weather["state"] = state
    return mmp_weather


def create_data_structures(data, weather_data):

    print("\tCreating data structures. This may take some time...\n")

    # restrain data to years around 1980
    sub_all = select_data( data )

    # correct info for some migrants
    sub_all = correct_migrants( sub_all )

    # keep only 5 person-year observations
    sub_all = keep_five_person_year( sub_all )

    # relabel migf=1 for past info of migrants.
    # sub_all has 100,572 unique observations:
    #    sub_all.index.get_level_values('persnum').unique().shape

    # attach weather information
    mmp_data_weather = attach_weather_5_year_lags( sub_all, weather_data )

    # deal with missing data on some of the lags (less lags return more observations)
    mmp_data_weather = NA_values( mmp_data_weather )

    # determine number of lags to be used for data analysis
    mmp_data_weather = number_of_lags( mmp_data_weather, lag_number=5 )

    # WIDE format
    mmp_data_weather = structure_wide( mmp_data_weather )

    # add state
    mmp_data_weather = add_mx_state( mmp_data_weather )

    # relabel all variables
    mmp_data_weather = relabel_variables( mmp_data_weather)

    # training and test set
    create_test_set(data=mmp_data_weather)

    print("Done!\n")
