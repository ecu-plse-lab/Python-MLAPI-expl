#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pylab as plt

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory
data = pd.read_csv('../input/train.csv')



from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.


# In[ ]:


print(data.columns.values)


# In[ ]:


plt.scatter(data['row_id'],data['y'])


# In[ ]:


plt.show()


# In[ ]:


plt.scatter(data['x'],data['y'])


# In[ ]:


meanByPlace = data.groupby(['place_id']).mean()


# In[ ]:


print(meanByPlace.shape)


# In[ ]:


plt.scatter(meanByPlace.x,meanByPlace.y)


# In[ ]:


meanByP
