#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# # NOTE: The above was automatically generated by Kaggle when I generated this notebook.  It tells us where Kaggle stores our training and test data.

# # *I'm including the Kaggle Data Description here as an accessible reminder of what we should expect to see in the data.*
# ## Kaggle Data Description
# 
# * In this competition, you will be predicting the probability [0, 1] of a binary target column.
# 
# * The data contains binary features (bin_*), nominal features (nom_*), ordinal features (ord_*) as well as (potentially cyclical) day (of the week) and month features. The string ordinal features ord_{3-5} are lexically ordered according to string.ascii_letters.

# In[ ]:


# Let's Inspect what is going on in the csv file by printing out the first 10 rows.
# You can't load and manipulate data if you're not familiar with its contents, so this is always the first step.
import csv
csv_file = open('/kaggle/input/cat-in-the-dat/train.csv')
csv_reader = csv.reader(csv_file)
for _ in range(10):
    row = next(csv_reader)
    print(row)
csv_file.close()


# ### Notice that csv_reader returns each row as a list of strings, we need to know this when it comes time to actually parse/convert the data. We can see the first row tells us the names of each column, subsequent rows are actual data. Let's read in the column names and first row.

# In[ ]:


csv_file = open('/kaggle/input/cat-in-the-dat/train.csv')
csv_reader = csv.reader(csv_file)
header = next(csv_reader)
row = next(csv_reader)
csv_file.close()

num_columns = len(header)
# print out name and value and type of data
for c in range(num_columns):
    col = header[c]
    value = row[c]
    print('======================')
    print('column name: {}'.format(col))
    print('value: {}'.format(value))
    # I'm printing out the type of the value here to emphasize that it csv loads everything as a string
    # and that we'll have to convert it to the correct data format later if we want to feed this data
    # into any algorithms.
    print('type: {}'.format(type(value)))  


# # Next Steps
# 
# The big picture overview of this challenge is that most machine learning classifiers need numbers are inputs, but data doesn't always come as numbers.  And it turns out it makes a difference how you convert the data into numbers.  So this challenge is about exploring different ways of converting the same data into numbers to find the best way of doing so.  This can be broken into four steps:
# 1. Load data into a pandas dataframe (without converting them into numbers).
# 2. Convert data in your pandas dataframe to numbers.
# 3. Feed your converted data to a machine learning classifier and see its test accuracy.
# 4. Modify step 2 and try 3 again to see how your classification performance changes.
# 
# **The most important part of data science is keeping a good record of the different things you tried and their outcomes.**
# 
# ## CSV Data --> Pandas DataFrame
# * This requires reading each row and parsing each column based on the type of column.
#   * The example row we printed above shows that `bin_*` columns can be coded in various ways: some are 0/1, some are `Y/N`, some are `T/F`. You will have to write a function that converts all binary values to python's True/False, regardless of what format it comes in.
#   * Similarly you need to write conversion functions for the rest of the different column types:
#     * nominal (which is like binary, except instead of only taking two values (True/False), it can take a range of values.)
#       * A challenge here is that depending on the specific column, you don't know the range of values it can take until you look through all the unique values in the dataset. Once you do have all the data loaded, `numpy` and `pandas.DataFrame` have `unique()` functions that tell you the unique values in a column or matrix - this should come in handy.
#     * ordinal (which is like nominal except there is an ordering to the values these variables can take)
#     * day/month: which is tricky because December (12th month) is closer to January (1st month) than it is to October (10th month) even though 12 is closer to 10 than it is to 1.
# * Each row in the data has a binary `target` column, which is used when you're training or evaluating the machine learning classifier.  This tells what "class" this row belongs to.
# 
#     
# ## Converting Panda Values To Numbers
# * This is where you get to try different things.
#   * Should binary values be converted to numbers as 0,1 or -0.5, 0.5?  Does it make a difference at all?  Does it make a difference for some classifiers but not others?
#   * If you convert a nominal category as `0, 1, 2`, should you convert a ordinal category also as `0, 1, 2` or would this confuse your classifier into thinking that the order of your nominal values matters just as much as the order of your ordinal values?
# * The output of this step should yield two numpy arrays that can plug very easily into classifier algorithms.
#   * `X`: This should have the shape: `[number_of_rows, number_of_columns`] and contain all of your rows and columns excluding the `target` column.
#   * `Y`: This should have the shape `[number_of_rows]` and this should contain the value of `target` for each row.  **Please Note:** Depending on the classifier you are using, this might need to have shape `[number_of_rows, 1]` or `[number_of_rows, 2]`.
# * You need to run these first two steps for both the training csv file and test csv file, so that ultimately you have: `X_train`, `Y_train`, `X_test`, `Y_test`
# 
# ## Train and Evaluate Classifiers
# From the previous steps you should have something that plugs neatly into this kind of template (try different classifiers of course).
# ```
# from sklearn.linear_model import LogisticRegression
# # This is your training step
# clf = LogisticRegression(random_state=0).fit(X_train, Y_train)
# clf.score(X_test, Y_test)
# ```
# 
# ## Record and reflect on what you tried in step 2 and the accuracy you got in step 3.  Form a hypothesis on a modification to step 2 that might improve or change your results and repeat the whole process.
# 
# Data science is really about using the scientific method to learn about your data and how it interacts with the algorithms you feed it into.  Even "experiments" where we get low classification accuracy are useful - learning about what does not work is still informative!

# # Begin Working Area

# # Experiments
# 1. Hypothesis: Using sin(days) only, not sin(days) cos(days), will lead to worse accuracy using Logistic Regression.
# - Result: Test Accuracy using sin(days): 78.% Test accuracy using sin and cos (days): 88%
# 2. Question: what is the effect of removing order information from ordinal columns?
# 
# 3. Question: which single column, on its own, gives us the highest accuracy?
# - nom_1: Test accuracy 30%
# - nom_2: Test accuracy 31%
# 

# In[ ]:


# use easy import
df_train=pd.read_csv('../input/cat-in-the-dat/train.csv')
print(df_train.head())


# In[ ]:


ordinal_columns = {}
for c in df_train.columns:
    if 'ord' in c:
        ordinal_columns[c] = df_train[c].unique()
from pprint import pprint
pprint(ordinal_columns)


# In[ ]:


df_train.keys()


# In[ ]:


import matplotlib.pyplot as plt
days = np.array(range(1,13))

print(np.sin(days), np.cos(days))

plt.scatter(np.sin(days), np.cos(days))
