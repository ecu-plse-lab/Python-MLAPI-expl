#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

9# Any results you write to the current directory are saved as output.


# In[ ]:


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plot
get_ipython().run_line_magic('matplotlib', 'inline')
from numba import jit, cuda


# In[ ]:


os.getcwd()


# In[ ]:


train = train=pd.read_csv("/kaggle/input/liverpool-ion-switching/train.csv")


# In[ ]:


train.shape


# In[ ]:


train.info()


# In[ ]:


train.isnull()


# In[ ]:


train.head(6)


# In[ ]:


test = pd.read_csv('/kaggle/input/liverpool-ion-switching/test.csv')


# In[ ]:


test.shape


# In[ ]:


test.info()


# In[ ]:


test.head(6)


# In[ ]:


test['time'] = (test['time'] - 500).round(4)


# In[ ]:


test.head()


# In[ ]:


train['signal'].describe()


# In[ ]:


def add_batch(data, batch_size):
    c = 'batch_' + str(batch_size)
    data[c] = 0
    ci = data.columns.get_loc(c)
    n = int(data.shape[0] / batch_size)
    print('Batch size:', batch_size, 'Column name:', c, 'Number of batches:', n)
    for i in range(0, n):
        data.iloc[i * batch_size: batch_size * (i + 1), ci] = i


# In[ ]:


for batch_size in [500000, 400000, 200000,100000]:
    add_batch(train, batch_size)
    add_batch(test, batch_size)


# In[ ]:


train.head()


# In[ ]:


original_batch_column = 'batch_500000'

batch_columns = [c for c in train.columns if c.startswith('batch')]
batch_columns


# In[ ]:


batch_6 = train[train[original_batch_column] == 6]


# In[ ]:



def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.        
    """
    start_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
#        else:
#            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
    
    return df


train = reduce_mem_usage(train)
test = reduce_mem_usage(test)


# In[ ]:


def add_stats(data, batch_column, column):
    
    # mean,std: one value per batch
    stats = {}
    group = data.groupby(batch_column)[column]
    stats['mean']   = group.mean()
    stats['median'] = group.median()
    stats['max']    = group.max()
    stats['min']    = group.min()
    stats['std']    = group.std()
    
    c = column + '_' + batch_column
    
    # apply it to batches
    for key in stats:
        data[c + '_' + key] = data[batch_column].map(stats[key].to_dict())
    
    # range
    data[c + '_range'] = data[c + '_max'] - data[c + '_min']
    data[c + '_max_to_min_ratio'] = data[c + '_max'] / data[c + '_min']


# In[ ]:


for batch_column in batch_columns:
    if batch_column == original_batch_column:
        continue
    
    add_stats(train, batch_column, 'signal')
    # add_stats(train, batch_column, 'open_channels')
    
    add_stats(test, batch_column, 'signal')


# In[ ]:


train.head()


# In[ ]:


def add_shifted_signal(data, shift):
    for batch in data[original_batch_column].unique():
        m = data[original_batch_column] == batch
        new_feature = 'shifted_signal_'
        if shift > 0:
            shifted_signal = np.concatenate((np.zeros(shift), data.loc[m, 'signal'].values[:-shift]))
            new_feature += str(shift)
        else:
            t = -shift
            shifted_signal = np.concatenate((data.loc[m, 'signal'].values[t:], np.zeros(t)))
            new_feature += 'minus_' + str(t)
        data.loc[m, new_feature] = shifted_signal


# In[ ]:


add_shifted_signal(train, -1)
add_shifted_signal(test, -1)


# In[ ]:


add_shifted_signal(train, 1)
add_shifted_signal(test, 1)


# In[ ]:


train.head()


# In[ ]:


exclude_columns = ['time', 'signal', 'open_channels'] + batch_columns


# In[ ]:


def add_signal_minus(data, exclude_columns):
    for column in [c for c in data.columns if c not in exclude_columns]:
        data['signal_minus_' + column] = data['signal'] - data[column]


# In[ ]:


add_signal_minus(train, exclude_columns)
add_signal_minus(test, exclude_columns)


# In[ ]:


train.head()
#batch_columns


# In[ ]:


# groups = train['batch'].copy()

y_train = train['open_channels'].copy()
x_train = train.drop(['time', 'open_channels'] + batch_columns, axis=1)

x_test = test.drop(['time'] + batch_columns, axis=1)


# In[ ]:


list(x_train.columns)


# In[ ]:


del train
del test


# In[ ]:


set(x_train.columns) ^ set(x_test.columns)


# In[ ]:


from sklearn.preprocessing import StandardScaler
x_train = x_train.values
x_test = x_test.values


# In[ ]:


from sklearn.model_selection import train_test_split


# In[ ]:


X_train, X_test, Y_train, Y_test = train_test_split(x_train,y_train,test_size=0.20)


# In[ ]:


from sklearn.neighbors import KNeighborsRegressor


# In[ ]:


error_rate = []
# Will take some time
for i in range(1,20):
    print('training for k=',i)
    knn = KNeighborsRegressor(n_neighbors=i,weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski')
    knn.fit(X_train,Y_train)
    pred_i = knn.predict(X_test)
    error_rate.append(np.mean(pred_i-Y_test)**2)


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import matplotlib.pyplot as plt


# In[ ]:


plt.figure(figsize=(10,6))
plt.plot(range(1,20),error_rate,color='blue', linestyle='dashed', marker='o',
         markerfacecolor='red', markersize=10)
plt.title('Error Rate vs. K Value')
plt.xlabel('K')
plt.ylabel('Error Rate')


# In[ ]:


np.round(pred_i)


# In[ ]:


knn = KNeighborsRegressor(n_neighbors=4,weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski')
knn.fit(X_train,Y_train)
pred_i = knn.predict(x_test)


# In[ ]:


y_pred = np.round(pred_i)


# In[ ]:


submission = pd.read_csv('/kaggle/input/liverpool-ion-switching/sample_submission.csv')
submission['open_channels'] = pd.Series(y_pred, dtype='int32')
submission['open_channels']=submission['open_channels'].astype('int')
submission.to_csv('submission_by_sanjoy.csv', index=False, float_format='%.4f')
submission.head(10)


# In[ ]:



