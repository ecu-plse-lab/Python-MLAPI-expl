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


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# In[ ]:


data = pd.read_csv('/kaggle/input/rossmann-store-sales/train.csv')
store= pd.read_csv('/kaggle/input/rossmann-store-sales/store.csv')
test= pd.read_csv('/kaggle/input/rossmann-store-sales/test.csv')


# In[ ]:


print(data.shape)
print(store.shape)


# In[ ]:


data.head()


# ****Granularity - One big brand has various number of branches and each rows is the data of that branch day wise****

# In[ ]:


store.head()


# ****Granularity - Here it is the metadata of the branches with respect to promotional events events conducted overall****

# In[ ]:


data.info()
# data.dtypes


# In[ ]:


data.describe(include='object')


# In[ ]:


data.describe()[['Sales','Customers']]


# In[ ]:


data.describe()[['Sales','Customers']].loc['mean']


# In[ ]:


data.describe()[['Sales','Customers']].loc['min']


# In[ ]:


data.describe()[['Sales','Customers']].loc['max']


# In[ ]:


data.Store.nunique()


# In[ ]:


data.head()
data.Store.value_counts().head(50).plot.bar()


# In[ ]:


data.Store.value_counts().tail(50).plot.bar()


# In[ ]:


data.Store.value_counts()


# ****Store - It is categorical column hence min and max must not be done. we do value counts to check if every category has same amount of data********

# In[ ]:


data.DayOfWeek.value_counts()


# In[ ]:


data.Open.value_counts()


# In[ ]:


data.Promo.value_counts()


# In[ ]:


data['Date']=pd.to_datetime(data['Date'],format='%Y-%m-%d')
store_id= data.Store.unique()[0]
print(store_id)
store_rows=data[data['Store']==store_id]
print(store_rows.shape)
# store_rows.resample('1D',on='Date')['Sales'].sum().plot.line(figsize=(14,4))


# In[ ]:


# store_rows[store_rows['Sales']==0]


# In[ ]:


test['Date']=pd.to_datetime(test['Date'],format='%Y-%m-%d')
store_test_rows = test[test['Store']==store_id]
store_test_rows['Date'].min(),store_test_rows['Date'].max()

store_test_rows
# In[ ]:


store_rows['Sales'].plot.hist()
# it is slightly skewed.


# In[ ]:


data['Sales'].plot.hist()
# it is slightly skewed.


# In[ ]:


store.head()


# In[ ]:


# store.isna.sum()


# In[ ]:


store_id=store[store['Store']==1].T


# In[ ]:


store[~store['Promo2SinceYear'].isna()].iloc[0]


# In[ ]:


# Method1
store = pd.read_csv('/kaggle/input/rossmann-store-sales/store.csv')
store['Promo2SinceWeek']= store['Promo2SinceWeek'].fillna(0)
store['Promo2SinceYear']= store['Promo2SinceYear'].fillna(store['Promo2SinceYear'].mode().iloc[0])
store['PromoInterval']= store['PromoInterval'].fillna(store['PromoInterval'].mode().iloc[0]) 

store['CompetitionDistance']=store['CompetitionDistance'].fillna(store['CompetitionDistance'].max())
store['CompetitionOpenSinceMonth']= store['CompetitionOpenSinceMonth'].fillna(store['CompetitionOpenSinceMonth'].mode().iloc[0])
store['CompetitionOpenSinceYear']= store['CompetitionOpenSinceYear'].fillna(store['CompetitionOpenSinceYear'].mode().iloc[0])
store.isna().sum()
      


# In[ ]:


data_merged = data.merge(store, on='Store',how='left')
print(data.shape)
print(data_merged.shape)
print(data_merged.isna().sum().sum()) #to cross check if there are any missing values


# In[ ]:


# encoding
# 3 categorical column,1 date column, rest are numerical
# data_merged.dtypes
data_merged['day']=data_merged['Date'].dt.day
data_merged['month']=data_merged['Date'].dt.month
data_merged['year']=data_merged['Date'].dt.year
#data_merged['dayofweek']=data_merged['Date'].dt.strftime('%a')


# In[ ]:


# Decision tress - label encoding should be used.
# regression - one hot encoding must be used.


# In[ ]:


# data_merged.dtypes
# StateHoliday,StoreType,Assortment,PromoInterval
data_merged['StateHoliday'].unique()
# for creating dummy variables - label encoding is used
data_merged['StateHoliday']=data_merged['StateHoliday'].map({'0':0,0:0,'a':1,'b':2,'c':3})
data_merged['StateHoliday']=data_merged['StateHoliday'].astype(int)
data_merged


# In[ ]:


# encoding assorted
data_merged['Assortment']
# for creating dummy variables - label encoding is used
data_merged['Assortment']=data_merged['Assortment'].map({'a':1,'b':2,'c':3})
data_merged['Assortment']=data_merged['Assortment'].astype(int)
data_merged


# In[ ]:


data_merged['StoreType'].unique()
data_merged['StoreType']=data_merged['StoreType'].map({'a':1,'b':2,'c':3,'d':4})
data_merged['StoreType']=data_merged['StoreType'].astype(int)
data_merged


# In[ ]:


data_merged['PromoInterval'].unique()
map_promo = {'Jan,Apr,Jul,Oct':1,'Feb,May,Aug,Nov':2,'Mar,Jun,Sept,Dec':3}
data_merged['PromoInterval']=data_merged['PromoInterval'].map(map_promo)
data_merged


# In[ ]:


# Train and validate Split
features= data_merged.columns.drop(['Sales','Date'])
from sklearn.model_selection import train_test_split
train_x,validate_x,train_y,validate_y = train_test_split(data_merged[features],np.log(data_merged['Sales']+1),test_size=0.2,random_state=1)
train_x.shape,validate_x.shape,train_y.shape,validate_y.shape


# In[ ]:


# from sklearn.tree import DecisionTreeRegressor

# model_dt = DecisionTreeRegressor(max_depth=20,random_state=1).fit(train_x,train_y)
# validate_y_pred = model_dt.predict(validate_x)

from sklearn.tree import DecisionTreeRegressor
model_dt=DecisionTreeRegressor(max_depth=10,random_state=1).fit(train_x,train_y)
validate_y_pred=model_dt.predict(validate_x)


# In[ ]:


get_ipython().system('pip install pydotplus')


# In[ ]:


def draw_tree(model, columns):
    import pydotplus
    from sklearn.externals.six import StringIO
    from IPython.display import Image
    import os
    from sklearn import tree
    
    graphviz_path = 'C:\Program Files (x86)\Graphviz2.38/bin/'
    os.environ["PATH"] += os.pathsep + graphviz_path

    dot_data = StringIO()
    tree.export_graphviz(model,
                         out_file=dot_data,
                         feature_names=columns)
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
    return Image(graph.create_png())


# In[ ]:


draw_tree(model_dt,features)


# In[ ]:


validate_y_pred = model_dt.predict(validate_x)
from sklearn.metrics import mean_squared_error
validate_y_inv = np.exp(validate_y) - 1
validate_y_pred_inv = np.exp(validate_y_pred) - 1
np.sqrt(mean_squared_error(validate_y_inv , validate_y_pred_inv))


# # steps done in the current ml data
# 
# * summary stats
# * understand your data
# * data preprocessing
#  --missing value imputation
#  --transformation
#  --scaling
#  --encoding
# * model fitting'
# * model summary
# * Prediction
# * Evaluation

# In[ ]:


# submitting the train on test data set


# In[ ]:


model_dt.feature_importances_


# In[ ]:


import matplotlib.pyplot as plt
plt.figure(figsize=(10,5))
plt.barh(features,model_dt.feature_importances_)
pd.Series(model_dt.feature_importances_,index=features)


# In[ ]:


stores_avg_cust = data.groupby(['Store'])[['Customers']].mean().reset_index().astype(int)
test_1 = test.merge(stores_avg_cust,on='Store',how='left')
test.shape,test_1.shape
test_merged = test_1.merge(store,on='Store',how='inner')
test_merged['Open']=test_merged['Open'].fillna(1)
test_merged['Date']=pd.to_datetime(test_merged["Date"],format='%Y-%m-%d')
test_merged['day']=test_merged['Date'].dt.day
test_merged['month']=test_merged['Date'].dt.month
test_merged['year']=test_merged['Date'].dt.year
test_merged['StateHoliday']=test_merged['StateHoliday'].map({'0':0,'a':1})
test_merged['StateHoliday']=test_merged['StateHoliday'].astype(int)
test_merged['Assortment']=test_merged['Assortment'].map({'a':1,'b':2,'c':3})
test_merged['Assortment']=test_merged['Assortment'].astype(int)
test_merged['StoreType']=test_merged['StoreType'].map({'a':1,'b':2,'c':3,'d':4})
test_merged['StoreType']=test_merged['StoreType'].astype(int)
map_promo = {'Jan,Apr,Jul,Oct':1,'Feb,May,Aug,Nov':2,'Mar,Jun,Sept,Dec':3}
test_merged['PromoInterval']=test_merged['PromoInterval'].map(map_promo)


# In[ ]:


test_merged


# In[ ]:


test_pred = model_dt.predict(test_merged[features])
test_pred_inv = np.exp(test_pred) - 1


# In[ ]:


submission = pd.read_csv('/kaggle/input/rossmann-store-sales/sample_submission.csv')
submission_predicted = pd.DataFrame({'Id':test['Id'],'Sales':test_pred_inv})
submission_predicted.to_csv('submission.csv',index=False)
submission_predicted.head()


# In[ ]:





# In[ ]:



