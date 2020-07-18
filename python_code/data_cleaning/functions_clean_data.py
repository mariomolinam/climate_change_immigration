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


def select_data(mmp_data, data_structure):
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

    # FILTER 2: REMOVE all observations for which:
    #           - data_structure != 'long_aug':
    #                  there is information after the
    #                  year of migration (usyr1 > year)
    #           - data_structure == 'long_aug':
    #                   there is information after the three years of
    #                   year of migration (usyr1 > (year-2)). This allows for
    #                   +2/-2 years around year of migration.
    #
    # This filter does NOT affect non-migrants

    if data_structure != "long_aug":
        cond = mmp_data.year <= mmp_data.usyr1
        mmp_data = mmp_data.loc[ cond , ]
    else:
        # allow for 2 extra years after migration year.
        year = mmp_data.year.astype(int) - 2
        year = year.astype(str)
        cond = year <= mmp_data.usyr1
        mmp_data = mmp_data.loc[ cond , ]

# FILTER 3: remove all observations (MIGRANTS and NON-MIGRANTS) that
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
    check_mig = subset.migf.sum(level=0)
    check_mig_idx = check_mig.apply(lambda x: "1" not in x).to_numpy().nonzero()[0]
    subset_idx_persnum = check_mig.iloc[check_mig_idx].index.get_level_values(0)

    # obtain highest year within selected migrants
    t = subset.loc[list(subset_idx_persnum),:].groupby(level=0).apply(
          lambda grp: grp.index.get_level_values("year").max() )

    # set multiIndex: "persnum", "year"
    mmp_data_multi = mmp_data.set_index(["persnum", "year"])
    # loop through all persnum indices and max year and recode

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
        # if there are more than 5 rows, then ramdoly choose the starting year.
        if resp.shape[0] > 5:
            idx_range = range(resp.shape[0])[4:]
            random_idx = int(np.random.choice(idx_range, size=1))
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

    mmp_data.sort_index(level=["persnum","year"], ascending=False, inplace=True)

    print("Keeping up to 5 years per person. Please wait...")
    # for migrants select the past 5 years if they exist
    mmp_data_five = mmp_data.groupby(level=0).apply(lambda x: select_five_year_points(x))
    print("Done!")

    mmp_data_five.reset_index(level=0, drop=True, inplace=True)

    return mmp_data_five


def add_migrant_info(mmp_data, data_structure):
    """
    Input: mmp_data: pandas dataframe (mmp)

    Task:
        - Add 1 in migf variable for past info of migrants.
        (i.e. rows that represent past info of migrants)
    """

    if data_structure == 'long_aug':
        mmp_data.loc[ mmp_data.usyr1 != '8888', "migf" ] = "1"

    return mmp_data


def attach_weather_5_year_lags(mmp_data, w_data, data_structure):
    """
    Input:  mmp_data: pandas dataframe (mmp).
            w_data: list of strs (with name of weather file).

    Task:
            1. reset mmp_data indices.
            2. read w_data file.
            3. get weather name variable (using name of file)
            4. loop through range(5) to create 5 lag variables (including lag 0)
            5. get lag variable using shift function
            6. transform weather_data from wide to long format
            7. merge mmp_data_weather with weather_long long format.

    Return: pandas dataframe - merged mmp_data with weather info in long format
    """
    # reset index mmp_data to geocode and year because weather varies by community
    mmp_data_weather = mmp_data.reset_index()

    for w in w_data:
        # read weather data
        filename = path_data + "/" + w
        weather = pd.read_csv(filename, dtype="str")
        weather.drop('state', axis=1, inplace=True) # drop state column
        # weather variable name
        weather_name = re.sub("mmp.+", "", w)[:-1]

        # long format with no augmentation: lags are needed
        if data_structure == "long_noaug":
            # loop for lags
            for y in range(5):
                # column name
                lag_name = "lag_t" + str(y)
                weather_lag_name = weather_name + '_' + lag_name
                # get lag of weather
                weather_lag = weather.loc[:,weather.columns[1:]].shift(y, axis=1)
                weather_lag = weather_lag.assign(geocode=weather.geocode)
                # from wide format to long format
                weather_long = pd.melt( weather_lag,
                                        id_vars="geocode",
                                        var_name="year",
                                        value_name=weather_lag_name )

                # remove weather name from year variable
                weather_long["year"].replace( regex=True,
                                              inplace=True,
                                              to_replace=r'\D',
                                              value=r'')
                # set index: geocode and year
                # weather_long.set_index(["geocode", "year"], inplace=True)
                # merge
                mmp_data_weather = pd.merge( mmp_data_weather,
                                             weather_long,
                                             how="left",
                                             on=["geocode", "year"])

        # works for:
        #       long format with augmentation
        #       wide format (lags needed)
        else:
        # elif data_structure == "long_aug":
            # column name
            # lag_name = "lag_t" + str(y)
            # weather_lag_name = weather_name + '_' + lag_name
            # get lag of weather
            # weather_lag = weather.loc[:,weather.columns[1:]].shift(y, axis=1)
            # weather_lag = weather_lag.assign(geocode=weather.geocode)
            # from wide format to long format
            weather_long = pd.melt( weather,
                                    id_vars="geocode",
                                    var_name="year",
                                    value_name=weather_name )

            # remove weather name from year variable
            weather_long["year"].replace( regex=True,
                                          inplace=True,
                                          to_replace=r'\D',
                                          value=r'')
            # set index: geocode and year
            # weather_long.set_index(["geocode", "year"], inplace=True)
            # merge
            mmp_data_weather = pd.merge( mmp_data_weather,
                                         weather_long,
                                         how="left",
                                         on=["geocode", "year"])


    return mmp_data_weather


def create_test_set(data, data_structure, seed=50):
    """
    Input:
        - data: pandas dataframe
        - data_structure: a string
        - seed: an integer

    Task:
        - It creates training and test sets. Since migration is a rare event,
        it stratifies the sample by prevalence of the event. More specifically,
        it saves as test set 25% of non-migrants AND 25% of migrants.

    Return:
        - It saves test and training sets as two separate csv files.
        - It returns a message saying whether this operation was successful.
    """

    # NON-MIGRANTS
    # unique users
    non_migrants = data.loc[data.usyr1 == "8888","persnum"].unique()
    N_total_nonmigrants = int(non_migrants.shape[0] * 0.25)
    random.seed(seed)
    non_migrants_sub = random.sample( list(non_migrants), N_total_nonmigrants)

    # MIGRANTS
    migrants = data.loc[data.usyr1 != "8888","persnum"].unique()
    N_total_migrants = int(migrants.shape[0] * 0.25)
    random.seed(seed+2)
    migrants_sub = random.sample( list(migrants), N_total_migrants)

    # build test and training sets
    data_test = data.loc[ data.persnum.isin(non_migrants_sub) | data.persnum.isin(migrants_sub) ,:]
    data_train = data.loc[ ~ ( data.persnum.isin(non_migrants_sub) |  data.persnum.isin(migrants_sub) ),: ]

    # save test set
    file_test = "/ind161_test_set_" + data_structure + ".csv"
    # train set
    file_train = "/ind161_train_set_" + data_structure + ".csv"

    # save test set
    data_test.to_csv(path_data + file_test)
    # save training set
    data_train.to_csv(path_data + file_train, index=False)

    # message
    message = "Test and train sets created!"
    return message


def structure_wide_or_long(mmp_data, data_structure):
    """
    Input: pandas dataframe

    Task:
        - Transform from long format to wide format

    Return: pandas dataframe
    """

    ###################################
    # NEEDS IMPLEMENTATION:
    #   - transform long format to wide
    #
    # DELETE WHEN COMPLETED
    ###################################
    if data_structure == "wide":

        # define time-varying and time-constant variables
        time_varying = [
            "year",
            "age",
            "mxmig",     # whether they migrated in mexico until this year
            "dprev",     # prevalence of migration in community (share of people who have ever migrated to the U.S. up until that year)
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

        weather_vars = [ 'crude_raw_prcp_monthly-average',
                         'crude_raw-tmax_monthly-average',
                         'norm_percent_short-term_tmax',
                         'norm_deviation_longterm',
                         'warm_spell_tmax',
                         'crude_above30-tmax_monthly-average',
                         'norm_deviation_short-term_tmax',
                         'norm_percent_short-term_prcp',
                         'norm_deviation_short-term_prcp']

        # reset index mmp_data: persnum and year levels
        # mmp_data.reset_index(level=[0,1], inplace=True)

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

        # remove second level for time_constant
        mmp_data_constant = mmp_data_constant.loc[ :, (mmp_data_constant.columns.get_level_values(0), '0') ]
        mmp_data_constant.columns = mmp_data_constant.columns.droplevel(level=1)
        mmp_data_constant.reset_index(inplace=True)


        # merge time-constant and time-varying variables
        mmp_data = mmp_data_constant.merge(mmp_data_varying, on="persnum")

    return mmp_data


def relabel_variables(data, data_structure):
    """
    Input: pandas dataframe (mmp data).

    Task: Relabel variables.
            - Some factors variables are transformed inot dummies.
            - Other variables are transformed from str to float or int.
            - Weather variables are transformed to float.

    Return: pandas dataframe.
    """
    if data_structure == 'long_noaug':

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
        weather_measures = [ 'crude_raw_prcp_monthly-average_lag_t0',
                             'crude_raw_prcp_monthly-average_lag_t1',
                             'crude_raw_prcp_monthly-average_lag_t2',
                             'crude_raw_prcp_monthly-average_lag_t3',
                             'crude_raw_prcp_monthly-average_lag_t4',
                             'crude_raw-tmax_monthly-average_lag_t0',
                             'crude_raw-tmax_monthly-average_lag_t1',
                             'crude_raw-tmax_monthly-average_lag_t2',
                             'crude_raw-tmax_monthly-average_lag_t3',
                             'crude_raw-tmax_monthly-average_lag_t4',
                             'norm_percent_short-term_tmax_lag_t0',
                             'norm_percent_short-term_tmax_lag_t1',
                             'norm_percent_short-term_tmax_lag_t2',
                             'norm_percent_short-term_tmax_lag_t3',
                             'norm_percent_short-term_tmax_lag_t4',
                             'norm_deviation_longterm_lag_t0',
                             'norm_deviation_longterm_lag_t1',
                             'norm_deviation_longterm_lag_t2',
                             'norm_deviation_longterm_lag_t3',
                             'norm_deviation_longterm_lag_t4',
                             'warm_spell_tmax_lag_t0',
                             'warm_spell_tmax_lag_t1',
                             'warm_spell_tmax_lag_t2',
                             'warm_spell_tmax_lag_t3',
                             'warm_spell_tmax_lag_t4',
                             'crude_above30-tmax_monthly-average_lag_t0',
                             'crude_above30-tmax_monthly-average_lag_t1',
                             'crude_above30-tmax_monthly-average_lag_t2',
                             'crude_above30-tmax_monthly-average_lag_t3',
                             'crude_above30-tmax_monthly-average_lag_t4',
                             'norm_deviation_short-term_tmax_lag_t0',
                             'norm_deviation_short-term_tmax_lag_t1',
                             'norm_deviation_short-term_tmax_lag_t2',
                             'norm_deviation_short-term_tmax_lag_t3',
                             'norm_deviation_short-term_tmax_lag_t4',
                             'norm_percent_short-term_prcp_lag_t0',
                             'norm_percent_short-term_prcp_lag_t1',
                             'norm_percent_short-term_prcp_lag_t2',
                             'norm_percent_short-term_prcp_lag_t3',
                             'norm_percent_short-term_prcp_lag_t4',
                             'norm_deviation_short-term_prcp_lag_t0',
                             'norm_deviation_short-term_prcp_lag_t1',
                             'norm_deviation_short-term_prcp_lag_t2',
                             'norm_deviation_short-term_prcp_lag_t3',
                             'norm_deviation_short-term_prcp_lag_t4' ]

        data.loc[:,weather_measures] = data.loc[:,weather_measures].astype(float)

    elif data_structure == 'long_aug':

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
        weather_measures = [ 'crude_raw_prcp_monthly-average',
                             'crude_raw-tmax_monthly-average',
                             'norm_percent_short-term_tmax',
                             'norm_deviation_longterm',
                             'warm_spell_tmax',
                             'crude_above30-tmax_monthly-average',
                             'norm_deviation_short-term_tmax',
                             'norm_percent_short-term_prcp',
                             'norm_deviation_short-term_prcp'
                            ]

        data.loc[:,weather_measures] = data.loc[:,weather_measures].astype(float)


    elif data_structure == 'wide':
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



        # metropolitan status: keep only 3 categories
        data[["rancho", "small urban", "town"]] = pd.get_dummies(data.metrocat).loc[:,
                                                                            ["rancho", "small urban", "town"]]

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


        rest = ["dprev","visaaccs","infrate","mxminwag","mxunemp","usavwage","lntrade"]
        for i in rest:
            data[time_varying[i]] = data.loc[:,time_varying[i]].astype(float)

        ####  W E A T H E R
        ################################################
        weather_measures = [ 'crude_raw_prcp_monthly-average',
                             'crude_raw-tmax_monthly-average',
                             'norm_percent_short-term_tmax',
                             'norm_deviation_longterm',
                             'warm_spell_tmax',
                             'crude_above30-tmax_monthly-average',
                             'norm_deviation_short-term_tmax',
                             'norm_percent_short-term_prcp',
                             'norm_deviation_short-term_prcp'
                            ]

        weather_measures = [ x + '_' + str(i) for i in range(5) for x in weather_measures]

        data.loc[:,weather_measures] = data.loc[:,weather_measures].astype(float)


    return data


def create_data_structures(data, data_struc_keys, weather_data):

    print("\tCreating data structures. This may take some time...\n")

    for entry in data_struc_keys:

        print("entry:", entry)

        # restrain data to years around 1980
        sub_all = select_data( data,
                                    data_structure = entry )

        # correct info for some migrants
        sub_all = correct_migrants( sub_all )

        # keep only 5 person-year observations
        sub_all = keep_five_person_year( sub_all )

        # relabel migf=1 for past info of migrants
        sub_all = add_migrant_info( sub_all,
                                         data_structure = entry )

        # attach weather information
        mmp_data_weather = attach_weather_5_year_lags( sub_all,
                                                            weather_data,
                                                            data_structure = entry)

        # LONG OR WIDE format
        mmp_data_weather = structure_wide_or_long( mmp_data_weather,
                                                        data_structure = entry )

        # relabel all variables
        mmp_data_weather = relabel_variables( mmp_data_weather,
                                                   data_structure = entry )

        # training and test set
        create_test_set(data=mmp_data_weather, data_structure=entry)

        print("Done!\n")




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
