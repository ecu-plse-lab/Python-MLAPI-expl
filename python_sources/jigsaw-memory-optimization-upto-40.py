#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# In[ ]:


TextFileReader = pd.read_csv("../input/train.csv", chunksize=1000,low_memory=True)  # the number of rows per chunk

dfList = []
for df in TextFileReader:
    dfList.append(df)

train = pd.concat(dfList)
#########################################################
TextFileReader = pd.read_csv("../input/train.csv", chunksize=1000,low_memory=True)  # the number of rows per chunk

dfList_test = []
for df in TextFileReader:
    dfList_test.append(df)

test = pd.concat(dfList_test)
#########################################################
sub = pd.read_csv("../input/sample_submission.csv")


# In[ ]:


def memory_usage(df):
    return(round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2))


# In[ ]:


memory_usage(train)


# In[ ]:


train.memory_usage(deep=True) / 1024 ** 2


# In[ ]:


train.head()


# In[ ]:


# Rating is taking 111 MB 
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
train['rating']=le.fit_transform(train['rating'])


# In[ ]:


# There is no use of created date
train = train.drop('created_date',axis=1)


# ## Reduceing Size of int or float
# 
# code taken from https://www.kaggle.com/arjanso/reducing-dataframe-memory-size-by-65

# In[ ]:


def reduce_mem_usage(props):
    start_mem_usg = props.memory_usage().sum() / 1024**2 
    print("Memory usage of properties dataframe is :",start_mem_usg," MB")
    NAlist = [] # Keeps track of columns that have missing values filled in. 
    for col in props.columns:
        if props[col].dtype != object:  # Exclude strings
            
            # Print current column type
            print("******************************")
            print("Column: ",col)
            print("dtype before: ",props[col].dtype)
            
            # make variables for Int, max and min
            IsInt = False
            mx = props[col].max()
            mn = props[col].min()
            
            # Integer does not support NA, therefore, NA needs to be filled
            if not np.isfinite(props[col]).all(): 
                NAlist.append(col)
                props[col].fillna(mn-1,inplace=True)  
                   
            # test if column can be converted to an integer
            asint = props[col].fillna(0).astype(np.int64)
            result = (props[col] - asint)
            result = result.sum()
            if result > -0.01 and result < 0.01:
                IsInt = True

            
            # Make Integer/unsigned Integer datatypes
            if IsInt:
                if mn >= 0:
                    if mx < 255:
                        props[col] = props[col].astype(np.uint8)
                    elif mx < 65535:
                        props[col] = props[col].astype(np.uint16)
                    elif mx < 4294967295:
                        props[col] = props[col].astype(np.uint32)
                    else:
                        props[col] = props[col].astype(np.uint64)
                else:
                    if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
                        props[col] = props[col].astype(np.int8)
                    elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
                        props[col] = props[col].astype(np.int16)
                    elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
                        props[col] = props[col].astype(np.int32)
                    elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
                        props[col] = props[col].astype(np.int64)    
            
            # Make float datatypes 32 bit
            else:
                props[col] = props[col].astype(np.float32)
            
            # Print new column type
            print("dtype after: ",props[col].dtype)
            print("******************************")
    
    # Print final result
    print("___MEMORY USAGE AFTER COMPLETION:___")
    mem_usg = props.memory_usage().sum() / 1024**2 
    print("Memory usage is: ",mem_usg," MB")
    print("This is ",100*mem_usg/start_mem_usg,"% of the initial size")
    #return props, NAlist


# In[ ]:


reduce_mem_usage(train)


# ## This is 40% reduction in size

# In[ ]:


memory_usage(train)


# In[ ]:


memory_usage(test)


# In[ ]:


test.head()


# In[ ]:


le = LabelEncoder()
test['rating']=le.fit_transform(test['rating'])


# In[ ]:


test.memory_usage(deep=True) / 1024 ** 2


# In[ ]:


test = test.drop('created_date',axis=1)


# In[ ]:


reduce_mem_usage(test)


# In[ ]:


memory_usage(test)


# In[ ]:


train.to_csv('train_optimized.csv',index=False)


# In[ ]:


test.to_csv('test_optimized.csv',index=False)
