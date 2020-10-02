#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.



# In[ ]:


df_train = pd.read_csv("../input/train.csv")
df_test = pd.read_csv("../input/test.csv")


# In[ ]:


df_train.time.describe()


# In[ ]:


df_test.time.describe()


# In[ ]:


range_train = df_train.time.max() - df_train.time.min()
print(range_train)

range_test = df_test.time.max() - df_test.time.min()
print(range_test)

range = range_train + range_test
print(range)


# In[ ]:


# number of days of data if time is given in seconds - 11 days is too small?
range  / (60 * 60 * 24)


# In[ ]:


# number of days of data if time is given in minutes - This almost two years - OK?
range  / (60 * 24)


# In[ ]:



