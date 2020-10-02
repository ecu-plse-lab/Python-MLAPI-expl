#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt 
import seaborn as sns

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# In[ ]:


#Importing the datasets
df_train = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-3/train.csv')
df_test = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-3/test.csv')
df_sub = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-3/test.csv')


# In[ ]:


df_train.info()


# In[ ]:


df_test.info()


# In[ ]:


df_sub.info()


# In[ ]:


df_train.shape, df_test.shape, df_sub.shape


# In[ ]:


df_train.head()


# Now lets preprosses the data

# In[ ]:


import datetime
df_train['Date'] = pd.to_datetime(df_train['Date'], infer_datetime_format=True)
df_test['Date'] = pd.to_datetime(df_test['Date'], infer_datetime_format=True)
df_train.loc[:, 'Date'] = df_train.Date.dt.strftime("%m%d")
df_train["Date"]  = df_train["Date"].astype(int)
df_test.loc[:, 'Date'] = df_test.Date.dt.strftime("%m%d")
df_test["Date"]  = df_test["Date"].astype(int)


# In[ ]:


df_train['ConfirmedCases'] = df_train['ConfirmedCases'].apply(int)
df_train['Fatalities'] = df_train['Fatalities'].apply(int)


# In[ ]:


df_train['Province_State'] = df_train['Province_State'].fillna('unknown')
df_test['Province_State'] = df_test['Province_State'].fillna('unknown')


# In[ ]:


import xgboost as xgb
from xgboost import XGBRegressor


# In[ ]:


features = ['Date']
submission = pd.DataFrame(columns=['ForecastId', 'ConfirmedCases', 'Fatalities'])

from tqdm import tqdm
for i in tqdm(df_train.Country_Region.unique()):
    c_train = df_train[df_train['Country_Region'] == i]
    c_test = df_test[df_test['Country_Region'] == i]
    for j in c_train.Province_State.unique():
        p_train = c_train[c_train['Province_State'] == j]
        p_test = c_test[c_test['Province_State'] == j]
        x_train = p_train[features]
        y_train_cc = p_train['ConfirmedCases']
        y_train_ft = p_train['Fatalities']
        model = xgb.XGBRegressor(n_estimators=1000)
        model.fit(x_train, y_train_cc)
        #Confirmed Cases Prediction
        y_pred_cc = model.predict(p_test[features])
        model.fit(x_train, y_train_ft)
        #Fatalities Prediction
        y_pred_ft = model.predict(p_test[features])
        
        p_test['ConfirmedCases'] = y_pred_cc
        p_test['Fatalities'] = y_pred_ft
        submission = pd.concat([submission, p_test[['ForecastId', 'ConfirmedCases', 'Fatalities']]], axis=0)


# In[ ]:


submission.to_csv('submission.csv', index=False)
