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

# Any results you write to the current directory are saved as output.


# In[ ]:


df_train_identity = pd.read_csv("/kaggle/input/ieee-fraud-detection/train_identity.csv")
df_test_identity = pd.read_csv("/kaggle/input/ieee-fraud-detection/test_identity.csv")
df_test_transaction = pd.read_csv("/kaggle/input/ieee-fraud-detection/test_transaction.csv")
df_sample_submission = pd.read_csv("/kaggle/input/ieee-fraud-detection/sample_submission.csv")
df_train_transaction = pd.read_csv("/kaggle/input/ieee-fraud-detection/train_transaction.csv")


# In[ ]:


df_train_identity.info()
df_train_transaction.info()


# In[ ]:


X = df_train_transaction.sort_values('TransactionDT').drop(['isFraud', 'TransactionDT', 'TransactionID'], axis=1)
y = df_train_transaction.sort_values('TransactionDT')['isFraud']


# In[ ]:


df_sample_submission['isFraud'] = [0.01]*len(df_sample_submission)
df_sample_submission.to_csv('0.01_model.csv', index = False)


# In[ ]:



