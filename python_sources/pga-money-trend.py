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


PGA = pd.read_csv('../input/pga-tour-20102018-data/PGA_Data_Historical.csv')


# In[ ]:


PGA_Money = PGA[PGA['Variable']=='Total Money (Official and Unofficial) - (MONEY)']


# In[ ]:


PGA_Money


# In[ ]:


PGA_Money = PGA_Money.drop(['Statistic','Variable'],axis=1)


# In[ ]:


PGA_Money['Value']=PGA_Money['Value'].str.replace('\s+|,|\$', '')


# In[ ]:


PGA_Money['Value']= PGA_Money['Value'].astype(float)


# In[ ]:


import seaborn as sn


# In[ ]:


sn.jointplot(x='Season', y='Value', data=PGA_Money, kind ='reg', ratio=5, color='green', space=0.2,height =10)


# In[ ]:


PGA_Money.loc[PGA_Money['Value'].idxmax()]
