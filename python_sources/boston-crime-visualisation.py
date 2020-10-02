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

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.


# **I do most of the visualisation with Tableau/Other tools and import the image to Kernels here as it is easier and visually pleasing**

# In[ ]:


data = pd.read_csv(r'../input/crime.csv',encoding='latin-1')
data.head()


# **Shooting Incident as a Percent of Total**

# In[ ]:


data_shooting = data[data.SHOOTING == 'Y']
data_shooting.head()


# In[ ]:


print(len(data_shooting)/len(data)*100)
print(len(data_shooting))
print(len(data))


# Hmm Only 0.32% of reported incidents were involved the shooting Column which is about 1055. Might be that all shooting incident are exaggerated by Media to create the Fear.

# **Let's Analyze the Non-Shooting Incidents First**

# In[ ]:


data_non_shooting = data[data.SHOOTING != 'Y']
data_non_shooting.head()


# **Let's Check The Safest District - (Meaning the Area with Least Reported Incidents)**

# In[ ]:


data_non_shooting['DISTRICT'].value_counts()


# **Among the given District A15 Seems to be the safest**

# <a href="http://imgbox.com/yAlQv2PY" target="_blank"><img src="https://images2.imgbox.com/2c/67/yAlQv2PY_o.png" alt="image host"/></a>

# **Visualisation of Major Offense Group not involved in the shooting incidents**

# In[ ]:


df = pd.DataFrame(data_non_shooting['OFFENSE_CODE_GROUP'].value_counts())
from IPython.display import display
pd.options.display.max_rows = 30
#display(df)
#df.to_csv('MajorOffenseNonShooting.csv')
print(df)


# <a href="http://imgbox.com/YZwoppTm" target="_blank"><img src="https://images2.imgbox.com/7b/b4/YZwoppTm_o.png" alt="image host"/></a>

# **Let's check the period and timings when most incidents occur**

# In[ ]:


data_non_shooting['HOUR'].value_counts()


# <a href="http://imgbox.com/jQjLNMUh" target="_blank"><img src="https://images2.imgbox.com/87/02/jQjLNMUh_o.png" alt="image host"/></a>

# I have Categorised the Data from 12pm to 2am as midnight and till  6am as early morning and upto10 am as morning and till 2pm as as noon and till 5 pm as evening and till 8 pm as night and till 11 pm as Late Night.
# **Hmm.. Unlike the Chart below on Shooting Incidents the conditions are totally reversed here where the frequency is higher at Morning, Noon and Evening attributing to almost 56% of Non Shooting Incidents**

# **Lets Visualize the Major Offense groups which leads to a shooting incident**

# In[ ]:


#I do my visualisation either in Tableau or locally and just paste the image in Kernels sometimes.It is easy this way
data[data.SHOOTING=='Y']['OFFENSE_CODE_GROUP'].value_counts()


# <a href="http://imgbox.com/fQ9AO3XM" target="_blank"><img src="https://images2.imgbox.com/38/b4/fQ9AO3XM_o.png" alt="image host"/></a>

#  **Hmm It seems like 51% of the shooting incident is categaorised as Aggravated Assault.  It is good to note that only 12% shooting cases have been categorised as a homicide.
#  Also it shows dangerous a cops job can be as  7% of all shooting incident are related to an arrest warrant**
# 

# **Let's check the period and timings when most shootings occur**

# In[ ]:


data_shooting['HOUR'].value_counts()


# <a href="http://imgbox.com/YYbJcxGE" target="_blank"><img src="https://images2.imgbox.com/4d/63/YYbJcxGE_o.png" alt="image host"/></a>

# I have Categorised the Data from 10pm to 2am as midnight and till  6am as early morning and upto10 am as morning and till 2pm as as noon and till 6 pm as evening and till 10 pm as night
# **It is evident that most shooting occurs at evening ,night and midnight contributing to 78% of the occurences. Now lets move on to the most dangerous Days of the week(Weekend vs Weekday)**

# In[ ]:


data_shooting['DAY_OF_WEEK'].value_counts()


# <a href="http://imgbox.com/jfWFjGSq" target="_blank"><img src="https://images2.imgbox.com/92/3d/jfWFjGSq_o.png" alt="image host"/></a>

# **Well It seems only saturday seems like an off-day. Other days seems to have an equal frequency of shooting. Time to check out the months**

# In[ ]:


data_shooting['MONTH'].value_counts()


# **Shooting Comparison by Months**
# <a href="http://imgbox.com/0OCOBAOh" target="_blank"><img src="https://images2.imgbox.com/c8/04/0OCOBAOh_o.png" alt="image host"/></a>

# In[ ]:



