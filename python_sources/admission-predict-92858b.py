#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression,LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import math


# In[ ]:


for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
        
Data = pd.read_csv('/kaggle/input/graduate-admissions/Admission_Predict.csv')
Data


# In[ ]:


# Remove the spaces and replace spaces with '_'
Data.columns=Data.columns.str.strip().str.replace(' ','_')
Data


# In[ ]:


Data=Data.drop(['Serial_No.'],axis=1)
Data


# In[ ]:


# Is there any null values in the dataset
Data.isnull().sum()


# In[ ]:


# boxplot will check th outlier in the dataset
plt.figure(figsize=(9,9))
Data.boxplot()
plt.tight_layout()


# In[ ]:


# Process of removing the outlier
Q1=Data.quantile(0.25)
Q2=Data.quantile(0.75)

Q3=Q2-Q1

Data=Data[~((Data < (Q1-1.5*Q3)) | (Data > (Q2+1.5*Q3))).any(axis=1)]
Data


# In[ ]:


plt.figure(figsize=(9,9))
Data.boxplot()


# In[ ]:


# We can check the skewness whether dataset is normally distrubuted or not
# here we are checing the predictive variable
sns.distplot(Data.Chance_of_Admit)


# In[ ]:


# With the following code we can back our dataset in the noraml distrubution
Data.Chance_of_Admit=np.power(Data.Chance_of_Admit,2)

sns.distplot(Data.Chance_of_Admit)


# In[ ]:


Data


# In[ ]:


# Statistical information about datset
Data.describe()


# In[ ]:


# Correlation tells us the strength and relationship between variables
Data.corr(method='pearson')


# In[ ]:


sns.pairplot(Data)


# In[ ]:


# Independent variable
x=Data.iloc[:,[0,1,5]]
x


# In[ ]:


# Dependent variable
y=Data.iloc[:,[-1]]
y


# In[ ]:


# We are training and testing our model
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.3,random_state=10)


# In[ ]:


reg=LinearRegression()
reg.fit(x_train,y_train)
reg.intercept_


# In[ ]:


# We are predicting our test data
y_pred=reg.predict(x_test)


# In[ ]:


# Trying to predict the Chance_of_Admit
reg.predict([[337,118,9.65]])


# In[ ]:


# Model accuracy
r2_score(y_test,y_pred)


# In[ ]:


y_pred.shape


# In[ ]:


# Mean square error
Actual=y.head(119)
MSE=mean_squared_error(y_test,y_pred)
MSE


# In[ ]:


# Root mean square error
RMSE=math.sqrt(MSE)
RMSE


# In[ ]:



