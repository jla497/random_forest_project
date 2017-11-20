import pandas as pd
import numpy as np
import copy

def process(dataset_file):
    """
    Process the given hockey dataset so that it can be consumed by the Random Forest.

    @param dataset_file - filepath to hockey dataset.

    @return preprocessed data.

    """
    print("Processing the data using Hockey Dataset Preprocessor...")

    test_data_x = None
    test_data_y = None
    train_data_x = None
    train_data_y = None

    """
    with open(dataset_file) as file_stream:
       None

    How about we use pandas?

    """
    df = pd.read_csv(dataset_file)
    #shuffle dataset
    np.random.seed(7)
    df = df.reindex(np.random.permutation(df.index))
    df = df.reset_index(drop=True)

    class_name = "GP_greater_than_0"

    ##Seperate into training and test set
    #Training from yrs 2004, 2005, 2006
    df_train = df.loc[(df['DraftYear'] == 2004) |
                            (df['DraftYear'] == 2005) |
                            (df['DraftYear'] == 2006)]

    df_test = df.loc[(df['DraftYear'] == 2007)]

    list_of_dropped_vars = ["id","PlayerName","DraftYear","Country",
                          "Overall","sum_7yr_TOI","sum_7yr_GP"]

    #Drop columns as given on course website, returns new dataset
    df_train = df_train.drop(list_of_dropped_vars, axis=1)
    df_test = df_test.drop(list_of_dropped_vars, axis=1)

    #%% Pre process data

    #Training and test Data
    x_train = df_train.drop([class_name], axis=1)
    x_test = df_test.drop([class_name], axis=1)

    #add boolean terms for catagories
    x_train, col_list_train = dummy(x_train)
    x_test, col_list_test = dummy(x_test)

    #add interaction terms for all i, j: xi*xj
    #train_data_x = interactions(x_train)
    #test_data_x = interactions(x_test)

    #Normalize
    x_train = standardize(x_train, col_list_train)
    x_test = standardize(x_test, col_list_test)

    """  target value for training and testing dataset"""
    t_train = df_train[class_name]
    t_test = df_test[class_name]

    #Insert w0 term for weight vector matrix
    x_train.insert(0, 'w0', np.ones(len(x_train), dtype=np.int))
    x_test.insert(0, 'w0', np.ones(len(x_test), dtype=np.int))

    #%%
    # Data matrix, with column of ones at end.
    train_data_x = x_train.values
    test_data_x = x_test.values
    # Target values, 0 for no, 1 for yes.
    train_data_y = t_train.map(dict(yes=1, no=0)).values
    test_data_y = t_test.map(dict(yes=1, no=0)).values

    return train_data_x, train_data_y, test_data_x, test_data_y

def dummy(ndata):
    #create boolean variables for discrete variables
    data = copy.deepcopy(ndata)
    s = '_'
    bool_columns = []
    j = 0
    tmp = np.zeros(len(data))
    for column in data:
        #create unqie variable for discrete catagories
        if data[column].dtype == 'O':
            a = data[column].unique()
            for i in range(a.size):
                k = 0
                for row in data.iterrows():
                    if row[1][column] == a[i]:
                        tmp[k] = int(1)
                    else:
                        tmp[k] = int(0)
                    k += 1 #row index
                data.insert(j+1, s.join((column,a[i])), tmp)
                bool_columns.append(s.join((column,a[i])))
            data = data.drop([column], axis=1)

        j += 1 #column index

    return data, bool_columns

def interactions(ndata):
    pass

def standardize(ndata, bool_columns):
    #standardize continuous ignoring boolean created variables
    data = copy.deepcopy(ndata)

    for column in data:
        #create unqie variable for discrete catagories
        if any(column != t for t in bool_columns):
            x = data[column].values
            mean = np.mean(x)
            std = np.std(x)
            data[column] = (data[column]-mean)/std

    return data
