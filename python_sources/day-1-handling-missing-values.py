#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import libraries
import pandas as pd 
import numpy as np

# load data
nfl_data = pd.read_csv("../input/nflplaybyplay2009to2016/NFL Play by Play 2009-2017 (v4).csv")
sf_permits = pd.read_csv('../input/building-permit-applications-data/Building_Permits.csv')

# set seed for reproducibility
np.random.seed(0)


# The first thing to do is to take a look at original datasets. In this case, I'm looking to see if I see any missing values, which will be represented with NaN or None.

# In[ ]:


# look at a few rows of the nfl_data flie. I can see a handful of missing 
# data already!
nfl_data.sample(5)


# In[ ]:


# look at any missing data at a couple rows from the sf_permits 
sf_permits.sample(5)


# ** See how many missing data points we have**
# 
# Let's see how many we have missing data points in each column.

# In[ ]:


# get the number of missing data points per column
missing_values_count_nfl = nfl_data.isnull().sum()
missing_values_count_sf = sf_permits.isnull().sum()

# look at the missing points in the first ten columns
missing_values_count_nfl[0:10]
missing_values_count_sf[0:10]


# That seems like a lot! It might be helpful to see what percentage of the values  in our dataset were missing to give us a better sense of the scale of this problem

# In[ ]:


# how many total missing values do we have?
total_cells_nfl = np.product (nfl_data.shape)
total_missing_nfl = missing_value_count.sum()

# percent of nfl data that is missing
(total_missing_nfl/total_cells_nfl)*100


# In[ ]:


total_cells_sf = np.product(sf_permits.shape)
total_missing_sf = missing_values_count_sf.sum()

# percent of sf data that is missing
(total_missing_sf/total_cells_sf)*100


# ** Figure out why the data is missing **
# 
# This is the point at which we get into the part of data science that I like to call " data intution", by which I mean " really looking at your data and trying to figure out why it is the way it is and how that will affect your analysis". It can be a frustrating part of data science, especially if you're newer to the field and don;t have a lot of experience. One of the most important question you can ask yourself to help figure this out is this:
# 
# *** Is this value missing because it wasn't recorded or because it doesn't exist? ***
# 
# If a value is missing because it doesn't exist then it doesn't make sense to try and guess what it might be. These values you probabally  try to guess what it might have been based on the other values in that column and row.
# 
# 
# 

# In[ ]:


# look at the missing points in the first ten columns
nfl_data['TimeSecs'].head(10)


# In[ ]:


sf_permits['Zipcode'].head(10)


# Zipcode doesn't record while Street Number Suffix doesn't exit because it was almost empty.
# 

# ** Drop missing values **
# 
# If you're in a hurry or don't have a reason to figure out why your values are missing, one option you have is to just remove any rows or columns that contain missing values. (it is note recommended for import projects.)
# 
# If you're sure you want to drop rows with missing values, pandas does a handy function, dropna( ) to help you do this. Let's try it out on NFL dataset

# In[ ]:


# remove all the rows that contain a missing value
nfl_data.dropna()


# It looks like it's removed all our data because every row has at least one missing value.

# In[ ]:


# remove all columns with at least one missing value
columns_with_na_dropped = nfl_data.dropna(axis = 1)
columns_with_na_dropped.head()


# In[ ]:


# just how much data did we lost?
print('COlumns in original dataset : %d \n' % nfl_data.shape[1])
print('COlumns with na dropped: %d' % columns_with_na_dropped.shape[1])


# In[ ]:


sf_columns_with_na_dropped = sf_permits.dropna(axis = 1)
sf_columns_with_na_dropped.head()


# In[ ]:


# how many data did we lose in sf_permits?
print('Columns in original sf_permits dataset: %d\n' % sf_permits.shape[1])
print('Columns in na dropped sf_permits dataset: %d\n' % sf_columns_with_na_dropped.shape[1])


# ** Filling in missing values automatically **

# In[ ]:


# Get a small subset of the NFL dataset
subset_nfl_data =nfl_data.loc[:,'EPA':'Season'].head()
subset_nfl_data


# In[ ]:


# replace all NA'S with 0
subset_nfl_data.fillna(0)


# In[ ]:


# replace all NA's the value that comes directly after it in the same column,then replace 
# all the remaining na's with 0
subset_nfl_data.fillna(method = 'bfill',axis=0).fillna(0)
sf_permits.fillna(method='bfill', axis = 0).fillna(0)
