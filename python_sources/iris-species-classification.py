#!/usr/bin/env python
# coding: utf-8

# # Welcome!
# 
# * Studied about Machine Learning but don't know where to start using it from?<br>
# * Or you know the concepts but don't know how to implement them?<br>
# * Or are you a beginner in the field of Machine Learning and code tutorials or books are of too high a level for you that they start demotivating you?<br>
# If so, you are at the right place, becuase I have written this notebook keeping in view all the difficulties I have faced as a beginner (Python is not even my primary language, still I could make it ;) so why can't you?)

# This tutorial is meant for beginners who have at least some basic theoretical knowledge of fundamental Machine Learning concepts and are looking to implement them practically. We will use the famous Iris Dataset to predict the specie of an Iris flower, given its petal length, petal width, sepal length and sepal width.

# We will import 2 Python libraries: Numpy and Pandas as they will be used everywhere in our code
# 
# **Note:** One thing I want to make clear at the start of this tutorial is - you **DO NOT** have to remember the code (which initially I used to think is necessary) to proceed further; understanding what is happening and how, is sufficient. Just look what libraries we will use and the parameters in the functions. This will come automatically to you as you keep practicing (Believe me, by the time you will write code for your 4th model, you would be knowing most of the things already)

# In[ ]:


import numpy as np
import pandas as pd


# # Loading Data

# Scikit Learn includes Iris Dataset by default, so we do not need to download the dataset explicitly

# In[ ]:


from sklearn.datasets import load_iris

#Make an object of the dataset for further use
iris_data = load_iris()


# Let's see what this dataset contains...

# In[ ]:


iris_data


# Well, it doesn't seems to be much readable, but atleast we got to know that the dataset is in the form of a Python dictionary.
# 
# Let's see the keys (or column names, if you can imagine it in the form of a table, with keys as column names and values as column data corresponding to each key)

# In[ ]:


iris_data.keys()


# So, basically the dataset contains 6 fields.<br>First, let's see what the DESCR (description) contains.

# In[ ]:


iris_data.DESCR


# That's some messed up text and it's very difficult to read and understand.<br>Why not try it with print() function?

# In[ ]:


print(iris_data.DESCR)


# Now it makes much more sense (Read the description once, in case you thought it would be fine skipping it:))
# 
# We should now look at the features and target

# In[ ]:


print("Feature names: ",iris_data.feature_names)
print("Target names: ",iris_data.target_names)


# Let's look at the actual data itself!

# In[ ]:


iris_data.data


# It is more convenient to work on **Pandas Dataframe** than on numpy arrays, so we will convert the data and target arrays to a Pandas Dataframe

# In[ ]:


df = pd.DataFrame(data=np.c_[iris_data.data, iris_data.target],
                 columns= iris_data.feature_names + ['target'])


# Done that! But how do we know if it was  actually converted or not?
# 
# We can check that by printing some rows of the dataframe.

# In[ ]:


df.head(5)


# This looks good and well organised.
# 
# **Note:** in target column (or Series, as to say in terms of Pandas), a value of 0 represents 'setosa'. Similarly, a value of 1 represents 'versicolor' and value of 2 represent 'viginica'
# 
# 
# Let's look at the shape of this dataframe. It should have a total of 150 rows and 5 columns as it was stated in the Description

# In[ ]:


df.shape


# # Visualizing the Data
# 
# Before starting to train our model, we should have a clear understanding of our data. We should compare and contrast different independent variables (called as features) with the dependent variable (called as target variable) in order to find relationship between them.
# 
# One way to know about the relationships among different variables in our dataset is to plot graphs and compare them visually. We will now plot matrix of graphs that can help us understand the data

# In[ ]:


#these libraries will help us in plotting graph
import matplotlib as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns


# Let's first define our feature and target variables.<br>
# For the sake of simplicity, currently I am taking all 4 independent variables as features.

# In[ ]:


features = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
target = 'target'


# In[ ]:


sns.pairplot(df, hue="target")
# help(sns.pairplot)


# From these graphs, it can be clearly observed Iris flowers with small sepals and petals are Iris-Setosa (with target = 0 and in blue color).
# 
# We can also infer that Iris-Virginica's (target = 2 and in green color) petal length and width are greater than those of Iris-Versicolor (target = 1 and in orange color)

# # Train-Test Data Split
# 
# Before we finally move on to train our model and start predicting, we need to ensure that we should have some data through which we can validate our model. A model, if trained and tested on the same data, may give very high accuracy for the in-sample data (data on which it was trained), since it *knows* what the output should be. But this model may (and surely it will, in most cases) give very low accuracy for out of sample data.
# 
# It is usually good to have 70-80% of data for training and rest for testing.
# 
# We will use train_test_split from scikit learn to split our data into training and testing sets.<br>
# By default, it splits data in the ratio of 3:1 (75% training and 25% test).

# In[ ]:


X_data = df[features]
y_data = df[target]
print(X_data)
print(y_data)


# In[ ]:


from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(X_data, y_data, random_state=0)


# Let's check the number of entries in each set.

# In[ ]:


print(X_train.shape)
print(X_val.shape)
print(y_train.shape)
print(y_val.shape)


# # Train the Model
# Ok, we are finally here. We will now train our Model!!
# 
# But wait, how should we choose which model will be good?
# 
# * We have some data with corresponding result to look at and we are going to train model which will learn from this data, so this is a Supervised Learning problem.
# * Also, we know that we need to predict the specie of Iris flower, which can be either 0 (Setosa), 1 (Versicolor) or 2 (Virginica), i.e. we need to classify the flower in one of the 3 categories. So this is a Classification problem.
# * For classification of data, we can use either Decision Tree or Random Forest or KNN (K-Nearest Neighbors) or Naive Bayes Model. Which one should we pick here?
# * One way is that that we can try each one of these and finally choose the one which gives the best result. We can do that here since we have a very small dataset, but this method may take a lot of time for training and validation when we have a huge dataset and that might make it practically impossible to implement.
# * Therefore, we will meticulously choose one of the above models. In the graphs plotted earlier, we can clearly observe that the species are clustered in some range of values. So, if we have a point on graph representing the properties of a flower, we can look around for other points with similar properties and corresponding specie and can predict the specie of this point based on the results of our observations.
# * This is exactly what a KNN algorithm does.
# 
# Hence, we will use KNN model (KNeighborsClassifier) to train our data.

# In[ ]:


from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=1)


# Since, we know the clusters of species are well separated from each other, we can just look at the nearest neighbor and predict the specie. But this won't be the case with most of the practical problems. We will have to find the optimum number of neighbors(k) we should look before making any prediction.
# 
# To find the best value of the number of neighbours(k), we can try running a loop for all values of k and select that value for which we get the highest accuracy. But, when we have huge dataset, we cannot practically train a model, predict and measure accuracy for each and every possible value of k as this might take a very very long time to complete. If the target values occur in cluster, it is sensible to observe only some of its neighbors to predict its value. Therefore we can run a loop from k=1 to say k=20 approx. (higher limit depends on the distribution of data) and do as stated above.

# You can try uncommenting and running the below code to see how accuracy changes with change in value of k. Notice the fluctuations in accuracy for k=27 to k=33.

# In[ ]:


# from sklearn.metrics import accuracy_score
# best_k, max_acc=0,0
# for k in range(1, 112):
#     knn = KNeighborsClassifier(n_neighbors=k)
#     knn.fit(X_train, y_train)
#     pred = knn.predict(X_val)
#     acc = accuracy_score(y_val, pred)
#     print(k, acc)
#     if acc > max_acc:
#         max_acc = acc
#         best_k = k
# knn = KNeighborsClassifier(n_neighbors=best_k)


# We should now fit our model and predict the target value for X_val.

# In[ ]:


knn.fit(X_train, y_train)


# In[ ]:


pred = knn.predict(X_val)


# We can measure the accuracy of our model using the accracy_score from sklearn.metrics 

# In[ ]:


from sklearn.metrics import accuracy_score
accuracy_score(y_val, pred)


# Wohoo! We got an accuracy of 97%. That's really good!
# 
# **Note:** We don't have any explicit test dataset (i.e. for which we do not already have target values) here to use our model and predict target value. Otherwise, after performing the validation and getting a good accuracy, we must train our data on whole dataset, i.e. on X_data (X_train+X_val) and y_data (y_train+y_val), else we will lose a part of our precious data in the form of validation data.
# 
# Uncomment the following code and run to train our model on whole available data.
# You can try testing it on some hypothetical data of your own.

# In[ ]:


# knn.fit(X_data, y_data)


# I hope you enjoyed and learned something<br>
# Keep practicing!