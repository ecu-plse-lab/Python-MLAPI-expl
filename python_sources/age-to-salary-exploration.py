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


df = pd.read_csv('../input/WA_Fn-UseC_-HR-Employee-Attrition.csv')


# In[ ]:


for job in set(df.JobRole):
    agesalary = []
    for i in range(df['Age'].min(), df['Age'].max() + 1):
        agesalary.append([i, df[(df['Age'] == i) & (df['JobRole'] == job)]['MonthlyIncome'].median()])
    agesalary = pd.DataFrame(agesalary, columns=['Age '+job, 'Median Salary'])
    agesalary = agesalary.dropna().reset_index(drop=True)
    agesalary.plot(x='Age '+job, y='Median Salary', title=job)
