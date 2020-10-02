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


from sklearn import datasets
wine = datasets.load_wine()
dir(wine)


# In[ ]:


df = pd.DataFrame(wine.data, columns = wine.feature_names)
df.head()


# In[ ]:


df['target'] = wine.target
df.head()


# In[ ]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(wine.data, wine.target, test_size = 0.25)


# In[ ]:


from sklearn.naive_bayes import GaussianNB, MultinomialNB
model_gaussian = GaussianNB()
model_gaussian.fit(X_test, y_test)
model_gaussian.score(X_test, y_test)


# In[ ]:


model_multinomial = MultinomialNB()
model_multinomial.fit(X_train, y_train)
model_multinomial.score(X_test, y_test)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:



