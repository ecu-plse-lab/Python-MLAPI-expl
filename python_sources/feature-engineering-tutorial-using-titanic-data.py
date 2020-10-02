#!/usr/bin/env python
# coding: utf-8

# How to represent raw data into nice features that machine can easily learn from is very important second step of machine learning. (The first step is definitely collecting data with good quality) 
# 
# As we are using **Math** to build models most of the time, representing features with reasonable numeric values is the way to go. However, some of the raw data in real life are not like this.   
# 
# **Categorical Features** 
# 
# Categorical Features are the features whose values are from a finite and discrete set of possible values. For example, the feature 'Sex' in our Titanic data set only has two possible values: 'male' or 'female'. These are not numeric and thus can't not directly used. Moreover, though some categorical features are numeric values, we still need to improve the representation. For example, the feature 'Pclass' in our Titanic data set only has three possible values: '1', '2' or '3'. These are numeric but it is bad pratice to directly use them. 'Pclass' is Ticket class, where	'1' means 1st class or the best class, and '2' means 2nd or the middle class ,and '3' means 3rd or the worest class. That is equally reasonable to use '3' for the best class,  and '1' for the worest.
# 
# 
# 
# 
# **Feature Engineering** 
# 
# Feature Engineering is transforming raw data into feature vectors.
# 
# In this tutorial, I will demonstrate feature engieering using the Titanic data set step by step.
# 
# 

# In[ ]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# Let's load the data and display how the data table looks like.

# In[ ]:


train_data = pd.read_csv("/kaggle/input/titanic/train.csv")
train_data.head()


# In[ ]:


test_data = pd.read_csv("/kaggle/input/titanic/test.csv")
test_data.head()


# In[ ]:



