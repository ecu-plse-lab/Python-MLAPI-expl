#!/usr/bin/env python
# coding: utf-8

# 

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from bokeh.charts import Donut, show, output_file
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.


# In[ ]:


vg_df = pd.read_csv('../input/Video_Games_Sales_as_at_22_Dec_2016.csv')
vg_df.head()


# In[ ]:


platform = vg_df.Platform
print("Data Lenth: ",len(platform))
vg_df.Platform.unique()


# In[ ]:



