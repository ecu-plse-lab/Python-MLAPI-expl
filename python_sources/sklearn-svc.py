#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np 
import pandas as pd 
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC

import os
print(os.listdir("../input"))


# In[ ]:


data = pd.read_csv("../input/pima_data.csv")
array = data.values
X = array[:,0:8]
Y = array[:,8]
kfold = KFold(n_splits=10,random_state=2)
model = SVC()
result = cross_val_score(model,X,Y,cv=kfold)
print("result:",result.mean())


# In[ ]:



