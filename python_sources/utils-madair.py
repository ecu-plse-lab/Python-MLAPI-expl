# data handling imports
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# sklearn
from sklearn.preprocessing import StandardScaler


# %% Normalizacion
def normalize_data_alt(data, training_size):
    '''
    Normalizing the data by mean-centering the data.
    output within the training set have std = 1 and mean = 0
    '''    
    training_data = data[:training_size]
    
    mean = training_data.mean(axis=0)
    std = training_data.std(axis=0)
    
    def _center_data(data, mean, std):
        return (data - mean) / std
    
    data = _center_data(data, mean, std)
    
    return (data, mean, std)


# %% [code]
def normalize_data_sklearn(data, training_size):
    '''
    Normalizing the data by mean-centering the data.
    output within the training set have std = 1 and mean = 0
    '''    
    training_data = data[:training_size]
    training_data = np.reshape(training_data, (training_data.shape[0], 1))
    
    scaler = StandardScaler()
    scaler.fit(training_data)
    
    data = scaler.transform(np.reshape(data, (data.shape[0], 1)))
    
    return (data[:,0], scaler)

# %% [markdown]
# ## Creaci�n de las secuencias

# %% [code]
def _get_chunk(data, seq_len, steps):  
    """
    data should be pd.DataFrame()
    """

    n_seqs = len(data) - (seq_len + steps - 1)  # - 1 cz python list are 0 indexed
    
    chunk_X, chunk_Y = [], []
    for i in range(n_seqs):
        chunk_X.append(data[i:i+seq_len])
        chunk_Y.append(data[i+seq_len+steps - 1]) # - 1 cz python list are 0 indexed
    chunk_X = np.array(chunk_X)
    chunk_Y = np.array(chunk_Y)

    return chunk_X, chunk_Y


def train_test_validation_split(data, test_prop, validation_prop, seq_len, steps):
    """
    This just splits data to training, testing and validation parts
    """
    
    ntrn1 = round(len(data) * (1 - test_prop)) # get size for train set (including validation set)
    ntrn2 = round(ntrn1 * (1 - validation_prop)) # get size for pure train set (without validation set)

    train_set = data[:ntrn2]
    val_set = data[ntrn2:ntrn1]
    test_set = data[ntrn1:]
    
    X_train, y_train = _get_chunk(train_set, seq_len, steps)
    X_val, y_val = _get_chunk(val_set, seq_len, steps)
    X_test, y_test = _get_chunk(test_set, seq_len, steps)

    return (X_train, y_train), (X_test, y_test), (X_val, y_val)


def train_test_split(data, test_prop, seq_len, steps):
    """
    This just splits data to training, testing and validation parts
    """
    
    ntrn1 = round(len(data) * (1 - test_prop)) # get size for train set

    train_set = data[:ntrn1]
    test_set = data[ntrn1:]
    
    X_train, y_train = _get_chunk(train_set, seq_len, steps)
    X_test, y_test = _get_chunk(test_set, seq_len, steps)

    return (X_train, y_train), (X_test, y_test)


# ## Versi�n mejorada que permite un dataframe como entrada donde puede haber columnas que correspondan 
#      con datasets auxiliares y en los output sets usa su valor en $X_{steps}$

def train_test_validation_split_df(df, test_prop, validation_prop, seq_len, steps):
    """
    This splits a dataframe to training, testing and validation parts in sequences of length `seq_len`
 and using `steps` as the prediction value for y and to get the value also for the auxiliar sets.
 
   :param DataFrame df: pandas DataFrame with at least one column called `data`, which will be sequenced,
      plus optional columns of aux data.
   :return a dict with:
       - X: sequence of length: `seq_len`
       - y: target for that sequence (in a `steps` distance)
       - DataFrame with other columns: aux data corresponding to that sequence (in a `steps` distance)
    """
    
    assert('data' in df.columns)
    
    # 1.  split all data in dataframe in three sets
    ntrn1 = round(len(df) * (1 - test_prop)) # get size for train set (including validation set)
    ntrn2 = round(ntrn1 * (1 - validation_prop)) # get size for pure train set (without validation set)

    train_set = df[:ntrn2]
    val_set = df[ntrn2:ntrn1]
    test_set = df[ntrn1:]
    
    # 2. Convert base data for every set in supervised learning input -> X and y
    X_train, y_train = _get_chunk(train_set['data'].values, seq_len, steps)
    X_val, y_val = _get_chunk(val_set['data'].values, seq_len, steps)
    X_test, y_test = _get_chunk(test_set['data'].values, seq_len, steps)
    

    aux_dfs = []
    
    # 3.  create auxiliar dataframe with the rest of the data and shift it to the time of prediction
    for set_it in [train_set, val_set, test_set]:
        aux_df = set_it.loc[:, set_it.columns != 'data']
        offset = seq_len + steps - 1 # offset aux data to the predicted data plus - 1 cz python list are 0 indexed
        aux_df = aux_df.slice_shift(-offset) # left shift
        aux_dfs.append(aux_df.copy(deep=False))
    
    train = {'X': X_train, 'y': y_train, 'aux': aux_dfs[0]}
    val   = {'X': X_val, 'y': y_val, 'aux': aux_dfs[1]}
    test  = {'X': X_test, 'y': y_test, 'aux': aux_dfs[2]}
    
    return train, test, val


# ## Partir datasets auxiliares en train, test y val para el momento actual.

# %% [code]
def datasets_split(data, training_size, validating_size, testing_size, seq_len, steps):
    
    seq_margin = seq_len+(steps - 1)
    
    train = data[:training_size]
    head_val = training_size+seq_margin  # we have skip the first window_width before to grab val inputs because they are missed in the sequence creation for (train, val, test) sets
    val = data[head_val:head_val+validating_size]
    head_test = head_val+validating_size+seq_margin
    test = data[head_test:head_test+testing_size]
    return train, val, test


# %% [code]
# Alternative method
def datasets_split_alt(data, test_prop, validation_prop, training_size, seq_len, steps):
    
    seq_margin = seq_len+(steps - 1)
    
    no_test = round(len(data) * (1 - test_prop))
    no_test_data = data[:no_test]
    train = no_test_data[:training_size]
    val_pointer = round(len(no_test_data) * validation_prop)
    val = no_test_data[-val_pointer:-seq_margin]
    test = data[no_test:-seq_margin]
    return train, val, test




#### %%% Tests %%% ####

'''
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python

# built-in imports
import sys
import os

# Carga de datos

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.

# set input dirname
input_dir = os.path.join('/kaggle/input', 'seleccion-datos-aire-primavera-2019-24-estacione')


# 1. Cargar datos
df24 = pd.read_csv(os.path.join(input_dir, 'pre_24est-feb-may_2019+date.csv'), index_col = 0)
#df.head()

#df.info()

# Preparaci�n de los datos de entrada al modelo

## Definici�n de variables para la preparaci�n de datos

step_forecasting = 24
window_width = 23
test_prop = 0.1
validation_prop = 0.1

df1 = df24[df24['estacion'] == 4].copy(deep=True)

df1 = df1.rename(columns = {'NO2': 'data'})
train, test, val = train_test_validation_split_df(df1, test_prop, validation_prop,
                                                        window_width, step_forecasting)

'''







