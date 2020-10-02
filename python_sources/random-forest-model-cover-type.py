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


train_data = pd.read_csv('/kaggle/input/learn-together/train.csv')


# In[ ]:


train_data.head()


# In[ ]:


import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report,confusion_matrix


# In[ ]:


X = train_data.drop('Cover_Type',axis=1)
y = train_data['Cover_Type']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)


# In[ ]:


dtree = DecisionTreeClassifier()


# In[ ]:


dtree.fit(X_train,y_train)


# In[ ]:


predictions = dtree.predict(X_test)


# In[ ]:


# Evaluation of Decision tree 
print(classification_report(y_test,predictions))


# In[ ]:


print(confusion_matrix(y_test,predictions))

Training Random Forest 
# In[ ]:


rfc = RandomForestClassifier(n_estimators=500)


# In[ ]:


rfc.fit(X_train,y_train)


# In[ ]:


predictions = rfc.predict(X_test)


# In[ ]:


print(classification_report(y_test,predictions))


# In[ ]:


print(confusion_matrix(y_test,predictions))


# In[ ]:



