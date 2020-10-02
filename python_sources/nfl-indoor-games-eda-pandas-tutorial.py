#!/usr/bin/env python
# coding: utf-8

# Hello! I created this notebook to look at how playing indoors affects the total points scored in a NFL game while also giving a tutorial on basic Python functions. 
# 
# There has been a theory that has been around the NFL for a long time that playing indoors leads to higher-scoring games. There have been a number of potential reasons that have been thrown around to support this, but ultimately, this theory has mostly just been considered a myth. In this notebook, we will explore the numbers and see if there is any real correlation or at least any pattern in indoor games.
# 
# Start by running the first cell below:

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


# #  Starting Up
# For this analysis, load in the spreadspoke_scores.csv dataset. The other ones will not be needed for now.

# In[ ]:


#create a dataset called 'games' with the 'spreadspoke_scores.csv file'
games = pd.read_csv('/kaggle/input/nfl-scores-and-betting-data/spreadspoke_scores.csv')


# First, print out the last twenty lines of the file in order to become familiar with the different columns and information in the table. Use the .tail() function to print out the final twenty rows of the file. 
# 
# **What .tail() does:**
# 
# .tail is a function that will print out the bottom of the table; it will default to the last 5 lines, but putting a number, x, in the parentheses will have it print out the final x rows.

# In[ ]:


#print out the final 20 rows of dataset 'games' using the .tail() function.
games.tail(20)


# As you can see, this file contains game information from the regular season and playoffs. For this analysis, we will be only looking at games from the last decade, 2010-2019. 
# 
# Create a new dataset conditionally selecting only games from the 2010s. Verify that you did this correctly by using the .head() function and making sure the first game listed is the New Orleans Saints vs. Minnesota Vikings on 09/09/2010.
# 
# **Conditional Selection**
# 
# Conditional selection is an effect way to select only certain rows from a large dataset. It is particularly useful to create datasets with only the pieces of information you want. In this case, create a new dataset and set it equal to the 'games' dataset and then a conditional statement that is only true for games from 2010-2019
# 
# **What .head() does:**
# 
# The .head() function works very similarly to the .tail function, but instead of printing out the bottom of the table, it will print the top of the table. Therefore, it's default is set to printing out the first five lines, but putting a number, x, in the parentheses will have it print out the first x rows.

# In[ ]:


#new dataset named 'games_2010s' to hold all games from 2010-2019. The data is populated by adding the correct games from the 'games' dataset
games_2010s = games[ games.schedule_season > 2009]

#print out the first five games of the years 2010-2019
games_2010s.head()


# # 2010-2019 Game Analysis 
# Use the method .shape[] to see how many NFL games were played in the last decade.
# 
# **What .shape[] does:**
# 
# .shape[] is a method that will return the number of rows and columns in the dataset. Without any inputs, it will print out the number of rows followed by number of columns. If you input 0, it will just print out the number of rows and if you input 1, it will print out the number of columns.

# In[ ]:


#print out the number of rows in the dataset 'games_2010'
games_2010s.shape[0]


# Of these 2670 games, let's see how many were played in a dome versus being played in a typical outdoor field. Use the .groupby() function to separate the data based on the weather_detail column because it contains information about whether a game was played in a dome.
# 
# Once you have done the .groupby() function, use .size() to print out the count of games in domes.
# 
# **What .groupby() does:**
# 
# .groupby() is a very useful function to organize the data in groups that you want to analyze. For this exercise, input the name of the column that holds the data that you want to group the rows by.
# 
# **What .size() does:**
# 
# .size() is a convenient way to count the frequency of a specific piece of data when combined with .groupby(). In this example, .size() will print out each unique value that is in the weather_detail column and the number of occurrences.

# In[ ]:


#create groups based on the 'weather_detail' column and counts the number of rows with that value in the column.'
games_2010s.groupby('weather_detail').size()


# This shows that there were 627 games played in regular domes and 56 in open-roof domes in the last decade. This combines for 683 games played in domes. (Note: For the purposes of this study, we will categorize regular domes and open-roof domes as the same becasue the roofs are only open when weather will not affect the game.)

# Next, let's see the average points per game in dome games. First, we will have to add a new column that has the combined total points per game. Do this by adding the home score and away score and adding the result to a new column for each row called 'total points'.

# In[ ]:


#creates a new column called total points and appends the total points scored by the home and away teams of each game.
games_2010s['total_points'] = games_2010s.score_home + games_2010s.score_away


# Now that we have the total points for each game, you can check whether dome games lead to higher points per game. You could group by the weather_detail column again, but it would be much easier if there was a column that just told us whether it was an indoor or outdoor game. Well luckily with what you've learned so far, you can create another column that will do just that!
# 
# Create a function called 'indoor_outdoor_test' that will return 'Indoors' or 'Outdoors' based on what the value in the weather_detail column is.

# In[ ]:


#create the function and apply it to dataframes.

def indoor_outdoor_test(df):
    
#use if statement to conditionally select rows that have 'DOME' or 'DOME (Open Roof) to return 'Indoors'
    
    if df['weather_detail'] == 'DOME':
        return 'Indoors'
    elif df['weather_detail'] == 'DOME (Open Roof)':
        return 'Indoors'
    
#every other row should return 'Outdoors'
    
    else:
        return 'Outdoors'

#create a new column for the dataset 'games_2010s' and apply the indoor_outdoor_test function to the dataset.
games_2010s['indoor_outdoor'] = games_2010s.apply(indoor_outdoor_test, axis=1)


# Now that each game has been categorized to dome or outdoors, calculate the average points scored per game for each You can use .mean() to obtain the mean of the indoor games and outdoor games. You can visualize this data by using .plot and then selecting whichever type of chart you choose. In this case, a bar chart would be the simplest way to observe differences.
# 
# **What .mean() does:**
# 
# .mean() simply calculates the mean of a specific set of data.
# 
# **What .plot does:**
# 
# .plot is a function that will create a chart with whatever data you select. You need to put something like .bar() or .line() to indicate what kind of chart you want to produce.

# In[ ]:


#create vertical bar chart of average total points per game based on indoor and outdoor games
games_2010s.groupby('indoor_outdoor').total_points.mean().plot.bar()


# Before drawing any conclusions from just looking at the mean, take a look at the medians of each category as well. You can use .median() the same way you used .mean(). Also, instead of doing .bar(), try doing .barh() to see how the chart is different!
# 
# **What .median() does:**
# 
# .median() calculates the median of a specific set of data.

# In[ ]:


#create horizontal bar chart of average total points per game based on indoor and outdoor games
games_2010s.groupby('indoor_outdoor').total_points.median().plot.barh()


# Even though this shows that there is a slight increase between the total points scored in dome games rather than outdoor games, we should look at more data to see if there are other distinct differences between indoor and outdoor games.
# 
# # 2019 New Orleans Saints Analysis
# 
# One way to do this would be to analyze how a team whose home stadium is a dome and see if they score more points at home rather than away. For this study's sake, let's analyze the 2019 games of the New Orleans Saints who play their home games in the famous Superdome. 
# 
# Create two new datasets, one having all of the Saints' home games from 2019 and the other all of their away games of 2019. Then, print out the home games in descending order of total points scored using the sort_values method.
# 
# Hint: You will need to create an intermeidary dataset in case the Saints made it to the Super Bowl and played in a neutral site game (they didn't)!
# 
# **What .sort_values does:**
# 
# You can use .sort_values to organize the rows in ascending or descending order based on a specific column.

# In[ ]:


#create a dataset that just contains the games from the 2019 season
games_2019 = games_2010s[ games_2010s.schedule_season == 2019]

#create a dataset that removes the Super Bowl from the dataset due to its being played on a neutral site game
regular_season = games_2019[ games_2019.stadium_neutral == False]

#create separate datasets that hold the Saints' home games and away games
NOS_2019_home = regular_season[ regular_season.team_home == 'New Orleans Saints']
NOS_2019_away = regular_season[ regular_season.team_away == 'New Orleans Saints']

#print out the Saints' home games in order of highest to lowest point total
NOS_2019_home.sort_values('total_points', ascending=False)


# Now, print out the away games in ascending order of total points scored.

# In[ ]:


NOS_2019_away.sort_values('total_points', ascending=True)


# Because there don't seem to be any huge outliers, we can just use the mean to determine analyze the points per game data for the Saints last season.

# In[ ]:


NOS_2019_home.total_points.mean()


# In[ ]:


NOS_2019_away.total_points.mean()


# # Conclusion
# Both analyses show that there is a small increase in total points scored in indoor games rather than outdoor games; aggregate data from the last decade and a deeper look at the 2019 New Orleans Saints both indicate that playing indoors could lead to higher scoring games. However, it is much too early to draw any significant conclusions. A much more in-depth analysis with more advanced statistics would help to reveal whether there is a true correlation. 