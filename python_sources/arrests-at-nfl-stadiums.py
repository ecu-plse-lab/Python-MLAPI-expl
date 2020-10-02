#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# ## Questions to Answer From Washignton Post
# Which stadiums had the most arrests? The least?
# Are arrests more likely when the home team lost a game? 
# Does the score correlate with number of arrests? (For example, if the game ended in a narrow loss for the home team, does this correlate with more arrests?)
# Are there any stadiums with consistent arrest rates, regardless of how the game ended?
# 
# ### Some Additional Questions I Have
# On certain days (Thursday vs Sunday vs Monday)
# Did the arrest rates change year to year?
# 

# To start the analysis, I'm going to import the data, I'll import both the arrests and notes.

# In[ ]:


arrestsTotal = pd.read_csv('../input/nfl-arrests/arrests.csv')
notes = pd.read_csv('../input/nfl-arrests/notes.csv')


# **I'll start by doing basic data analysis to learn more about the dataset. I like to see the first 5 rows, then I'll look at the last five rows, to see what the data looks like.

# In[ ]:


arrestsTotal.head()


# In[ ]:


arrestsTotal.tail()


# **Finally I'll get a random sample of 10 rows

# In[ ]:


arrestsTotal.sample(10)


# **Get the data shape**

# In[ ]:


arrestsTotal.shape


# Now let's check the datatypes of the dataset.

# In[ ]:


print(arrestsTotal.dtypes)


# To get even more information about the columns, use the .info() method.

# In[ ]:


arrestsTotal.info()


# **I'll take a look at the Notes dataset.

# In[ ]:


notes.head()


# **After looking at the notes dataset, it's just extra information about the original dataset so I will disregard it unless I have a question. One thing to note is that some of the teams did not provide as much data (Ex: Baltimore, Buffalo)**

# **Now I will run describe on the dataset, which will return basic statistics about the data. 
# From this list, I see the mean number of arrests is 6.56, but the highest is 69 arrests! I'm wondering about that!
# Looking at the arrests column, the mean is 6, but the standard deviation is 9, and the range of arrests go from 0 to 69. 50% of the number of arrests are 3 or lower, and 75% are 8 or lower. So there is obviously at least one major outlier.**

# In[ ]:


arrestsTotal.describe()


# **So I would like to get started by looking at a histogram of some columns, starting with week number.**
# **There are some dips with fewer arrests during the middle of the season versus the most at the end and at the start of the season.**

# In[ ]:


week = arrestsTotal['week_num']
week.hist()


# **Finally I'll look at arrests histogram to see what that data looks like.**

# In[ ]:


arrestNo=arrestsTotal['arrests']
arrestNo.hist()


# **So from the above histogram, it's clear that 0 arrests is the most common value, but I do see there is a long tail, almost reaching 70! I'd like to quickly get a count of arrests over 8, which represents the top 25% of the data values for arrests (the describe section above), so 227 rows are returned.**

# In[ ]:


arrestsTotal[arrestsTotal['arrests'].gt(8)]


# **I want to see the highest end of the arrests to see what that tells me, so I selected 50 and above. When Pittsburgh is the home team there were 52 and 56 arrests. There are two instances where the highest number of arrests, 69, occured. Both times were when Oakland played at San Diego!**
# 

# In[ ]:


arrestsTotal[arrestsTotal['arrests'].gt(50)]


# **While it's intersting to see the pattern with the highest number of arrests, that's only 4 data points. So now I want to see how the data looks for cases where the number of arrests are greater than 30.**

# In[ ]:


over30 = arrestsTotal[arrestsTotal['arrests'].gt(30)]
arrestsTotal[arrestsTotal['arrests'].gt(30)]


# **I see a lot of entries for New York and San Diego, so next I'll examine the stadiums that have over 30 arrests in more detail.**

# In[ ]:


over30.groupby([ 'home_team', 'arrests']).count()


# **Now I'll start with the first question: Which stadiums had the most arrests? The least?
# To solve this I'll look the data for the home team.
# And again, given the data, the team with the most arrests is San Diego. However, if you count the stadium, the Jets and Giants play at the same stadium, so Giants Stadium has the most arrests. Detroit has the least - with zero arrests.**

# In[ ]:


homeStadiumArrests = arrestsTotal.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)
print(homeStadiumArrests)


# **The next question is are arrests more likely when the home team lost a game? To analyze this, I've made a new column to arrestsCopy that holds the result of home score - away score, so if the number is negative, then the home team lost.**

# In[ ]:


arrestsCopy = arrestsTotal
arrestsCopy['resultScore']=arrestsCopy.apply(lambda row: row.home_score - 
                                  (row.away_score), axis = 1) 


# **Now breakout the games where the home team lost and where the home team won**
# **And finally where there are ties**

# In[ ]:


homeStadiumLose = arrestsCopy[arrestsCopy['resultScore'].lt(0)]
homeStatiumWin = arrestsCopy[arrestsCopy['resultScore'].gt(0)]
homeStadiumTie = arrestsCopy[arrestsCopy['resultScore'].eq(0)]


# **Now to find the total arrests for each category**

# In[ ]:


loss = homeStadiumLose.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)

win = homeStatiumWin.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)
tie = homeStadiumTie.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)


# **Let's try printing the top 10 of each**

# In[ ]:


print(loss[:10])
print(win[:10])
print(tie[:10])


# **Just looking at the results, it doesn't seem overwhelmingly evident, so let's make a visualization, but ignoring
# ties since there are only 4 ties**
# **It seems some stadiums will have slightly more arrests if they lose (San Diego, Giants Stadium, Pittsburgh) whereas 
# other stadiums will have more arrests (in some cases many more arrests) if they win (Green Bay, New England, Arizona and Denver)**
# **San Francisco looks the closest for wins or losses (but still has about 70 more arrests when there are wins).

# In[ ]:


ax = loss.sort_values(by='arrests', ascending=0)[:10].plot(kind='line', figsize=(10, 10), color='red', stacked=False, rot=90)
win.sort_values(by='arrests', ascending=0)[:10].plot(ax=ax, kind='line', color='green', stacked=False, rot=90)

ax.legend(["loss", "win"])


# **Next I will look at close games versus larger deficits, so close will be 6 or less points, not close will be 24 or more points, 
# This is arbitrary but I'll just start there.**

# In[ ]:


close =  arrestsCopy[arrestsCopy['resultScore'].between(-6, 6, inclusive=True)]
notClose = arrestsCopy[arrestsCopy['resultScore'].le(-24) | arrestsCopy['resultScore'].gt(24)]
                                                                        
closeGraph = close.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)
notCloseGraph = notClose.groupby(['home_team']).agg({'arrests': 'sum'}).sort_values(by='arrests', ascending=False)


# **Now let's graph the results, which are very clear! Close games lead to more arrests when graphing the top 10, especially for the stadiums with the most arrests.**

# In[ ]:


ax = closeGraph.sort_values(by='arrests', ascending=0)[:10].plot(kind='line', figsize=(10, 10), color='green', stacked=False, rot=90)
notCloseGraph.sort_values(by='arrests', ascending=0)[:10].plot(ax=ax, kind='line', color='red', stacked=False, rot=90)

ax.legend(["close", "not close"])


# **To determine if day of the week influences arrests, let's compare them, really it's unfair to compare Sunday, since most games are played then, but Monday and Thursday are comparable since there is usually only one game each. Saturday is usually for playoffs and the numbers bear that out.**

# In[ ]:


monArrests = len([x for x in arrestsTotal['day_of_week'] if 'Monday' in x])
thursArrests = len([x for x in arrestsTotal['day_of_week'] if 'Thursday' in x])
satArrests = len([x for x in arrestsTotal['day_of_week'] if 'Saturday' in x])
sunArrests = len([x for x in arrestsTotal['day_of_week'] if 'Sunday' in x])
print('The number of Monday arrests are: ' + str(monArrests))
print('The number of Thursday arrests are: ' + str(thursArrests))
print('The number of Saturday arrests are: ' + str(satArrests))
print('The number of Sunday arrests are: ' + str(sunArrests))


# **Now let's look at year over year for all teams to see if there is a trend, which it turns out there are the same number approximately 200.**

# In[ ]:


yr2011 = arrestsTotal[arrestsTotal.season == 2011].count()
yr2012 = arrestsTotal[arrestsTotal.season == 2012].count()
yr2013 = arrestsTotal[arrestsTotal.season == 2013].count()
yr2014 = arrestsTotal[arrestsTotal.season == 2014].count()
yr2015 = arrestsTotal[arrestsTotal.season == 2015].count()
print(yr2011['season'])
print(yr2012['season'])
print(yr2013['season'])
print(yr2014['season'])
print(yr2015['season'])


# **Summary**
# 
# **Most Arrests**
# The top five stadiums had the most arrests: San Diego, NY Giants, NY Jets, Pittsburgh, and Oakland. 
# 
# **Wins vs Losses**
# The top five stadiums for number of arrests when the team won the game: NY Giants, San Diego, Oakland, NY Jets, and Pittsburgh.
# The top five stadiums for number of arrests when the team lost the game: Sand Diego, NY Jets, Pittsburgh, NY Giants, and San Francisco.
# Close games had more arrests than close games. 
# 
# **Most Arrests in a Game**
# Two Oakland at San Diego had the highest number of arrests at 69 for each game. 