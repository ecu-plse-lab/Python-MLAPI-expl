#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import pairwise_distances_argmin
from scipy import stats
import seaborn as sns

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# See what's inside of the data.

# In[ ]:


data = pd.read_csv('/kaggle/input/coronavirusdataset/patient.csv')
data.info()
data.head(20)
data.groupby(['state']).groups.keys()


# Cleaning up data. Raw data is missing too much detail....
# 
# 93% of region data is null.<br/>
# 99% of group data is null.<br/>
# 98% of infection_reason data is null.<br/>

# In[ ]:


data = data[data['birth_year'].notna()]
data = data[data['sex'].notna()]
data = data[data['group'].notna()]
data = data[data['state'].notna()]

data[data.region == 'region'] = 'unknown'
data[data.group == 'group'] = 'unknown'


# switch sex to numeric male -> 1, female -> 2
data["sex"].replace({"male": "1", "female": "2"}, inplace=True)

# ... weill 98% is missing. :( 
data["infection_reason"].replace({'contact with patient': 1, 'pilgrimage to Israel' : 2, 'visit to Daegu': 3}, inplace=True)
data["state"].replace({'isolated': 1, 'released' : 2, 'deceased': 3}, inplace=True)

data.sex = data.sex.astype(int)
data.birth_year = data.birth_year.astype(int)
data.state = data.state.astype(int)

print(data)
data.info()


# In[ ]:


print(data)


# Pretty much no corr between features. Nothing to do with this other than just showing charts for data distribution...

# In[ ]:


plt.figure(figsize=(14,10))
data = data.drop(['id', 'infection_reason'], axis=1)
#data = data.drop(['id', 'disease', 'infection_order', 'infected_by'], axis=1)

cor = data.corr()
print(cor)
sns.heatmap(cor, annot=True, cmap=plt.cm.Reds)
plt.show()
