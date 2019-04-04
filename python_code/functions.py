import csv, random
import pandas as pd
import gc

# Create training, validation, and test sets

# path
path_data = "/home/mario/Documents/environment_data/mmp_data"
filename = "ind161_w_env.csv"
full_path = path_data + '/' + filename

# load data
d = pd.read_csv(full_path, dtype="str")


def select_columns(data):
    """
        Input: pandas dataframe.
        Task: select columns of dataframe and subset.

        Return: pandas dataframe.
    """
    # define columns
    cols = [
            "commun", # community ID
            "hhnum",  # household ID
            "persnum", # person ID
            "year",    # year within person
            "geocode",
            # "occur_5", # 5 occupational categories (not time-varying; based on survey year)
            "usyr1", # first year of migration
            "migf",
            "age",
            "sex",
            "mxmig", # whether they migrated in mexico until this year
            "primary", # if there is a school
            "secondary", # if there is a secondary school

            "totmighh", # total number of prior U.S. migrants in the household (up until that year)
            "tbuscat", # whether hh owns a business
            "troom", # number of rooms in properties household owns
            "lnvland_nr", # log(value of land) — excluding that bought by remittances
            "dprev", # prevalence of migration in community (share of people who have ever migrated to the U.S. up until that year)
            "agrim", # share of men working in agriculture in community
            "minx2", # share of people earning twice the minimum wage or more
            "metrocat", # metropolitan status of community
            "ejido", # collective land system (0/1)
            "lnpop", # log of population size in community
            "bank",  # in community
            "visaaccs", # visa accessibility to the U.S. in year
            "infrate",  # inflation in Mexico in year
            "mxminwag", # min wage in mexico in year
            "mxunemp", # unemployment in Mexico
            "usavwage", # U.S. average wages for low-skill work in year
            "lntrade",  # log of trade between MX-U.S.
            "logdist" # distance of community to the U.S.
            ]
    # define subset
    subset = data[cols]
    return subset

# select columns and save as csv file
subset = select_columns(d)
subset.to_csv(path_data + "/ind161_w_env-subset.csv", index=False)



def create_test_set(data, seed=50):
    # get unique users
    users = subset.persnum.unique()
    N_total = int(len(users) * 0.25)
    random.seed(seed)
    users_sub = random.sample(users, N_total)
    data_test = data.loc[ data.persnum.isin(users_sub) ,:]
    data_train = data.loc[ ~ data.persnum.isin(users_sub),: ]
    # test set
    file_test = "/ind161_test_set-DONOTUSE.csv"
    data_test.to_csv(path_data + file_test)
    # train set
    file_train = "/ind161_train_set.csv"
    data_train.to_csv(path_data + file_train, index=False)
    # message
    message = "Test and train sets created!"
    return message

# run functions
create_test_set(subset)

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
