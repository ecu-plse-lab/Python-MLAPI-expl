#!/usr/bin/env python
# coding: utf-8

# # Introduction
# 
# In this dataset I tried to predict target.
# 
# 1. [Entering and Cleaning Data](#1)
# 1. [Train Test Split](#2)
# 1. [Initialize Weights and Bias](#3)
# 1. [Sigmoid Function](#4)
# 1. [Forward Backward Propagation](#5)
# 1. [Update Part](#6)
# 1. [Prediction Part](#7)
# 1. [Logistic Regression](#8)
# 1. [Logistic Regression with Sklearn](#9)
# 

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


# <a id="1"></a><br>
# # Entering and Cleaning Data

# In[ ]:


df=pd.read_csv("/kaggle/input/heart-disease-uci/heart.csv")


# In[ ]:


df.head()


# In[ ]:


df.info()


# In[ ]:


x_data=df.drop(["target"],axis=1)
    
x=((x_data-np.min(x_data))/(np.max(x_data)-np.min(x_data))).values


# In[ ]:


y=df.target.values


# <a id="2"></a><br>
# # Train Test Split

# In[ ]:


from sklearn.model_selection import train_test_split

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)

x_train=x_train.T
x_test=x_test.T
y_train=y_train.T
y_test=y_test.T

print("x train shape: ",x_train.shape)
print("x test shape: ",x_test.shape)
print("y train shape: ",y_train.shape)
print("y test shape: ",y_test.shape)


# <a id="3"></a><br>
# # Initialize Weights and Bias

# In[ ]:


def initialize_weights_and_bias(dimension):
    w=np.full((dimension,1),0.01)
    b=0.0
    return w,b


# <a id="4"></a><br>
# # Sigmoid Function

# In[ ]:


def sigmoid(z):
    y_head=1/(1+np.exp(-z))
    return y_head


# <a id="5"></a><br>
# # Forward Backward Propagation

# In[ ]:


def forward_backward_propagation(w,b,x_train,y_train):
    # forward propagation
    z=np.dot(w.T,x_train)+b
    y_head = sigmoid(z)
    loss= -y_train*np.log(y_head)-(1-y_train)*np.log(1-y_head)
    cost = (np.sum(loss))/x_train.shape[1]
    
    # backward propagation
    derivative_weight= (np.dot(x_train,((y_head-y_train).T)))/x_train.shape[1]
    derivative_bias=np.sum(y_head-y_train)/x_train.shape[1]
    gradients={"derivative_weight":derivative_weight,"derivative_bias": derivative_bias}
    return cost,gradients


# <a id="6"></a><br>
# # Update Part

# In[ ]:


def update(w,b,x_train,y_train,learning_rate,number_of_iteration):
    cost_list=[]
    cost_list2=[]
    index=[]
    
    for i in range(number_of_iteration):
        
        cost,gradients=forward_backward_propagation(w,b,x_train,y_train)
        cost_list.append(cost)
        
        w=w- learning_rate*gradients["derivative_weight"]
        
        b= b - learning_rate*gradients["derivative_bias"]
        
        if i%10 == 0:
            cost_list2.append(cost)
            index.append(i)
            print("cost after iteration {}:{}".format(i,cost))
            
    parameters={"weight":w,"bias":b}
    plt.plot(index,cost_list2)
    plt.xticks(index,rotation = "vertical")
    plt.xlabel("Number of iteration")
    plt.ylabel("Cost")
    plt.show()
    
    return parameters,gradients,cost_list


# <a id="7"></a><br>
# # Prediction Part

# In[ ]:


def predict(w,b,x_test):
    z=sigmoid(np.dot(w.T,x_test)+b)
    
    Y_prediction=np.zeros((1,x_test.shape[1]))
    
    for i in range(z.shape[1]):
        if z[0,i]<=0.5:
            Y_prediction[0,i]=0
        else:
            Y_prediction[0,i]=1
    
    return Y_prediction


# <a id="8"></a><br>
# # Logistic Regression

# In[ ]:


def logistic_regression(x_train,y_train,x_test,y_test,learning_rate,num_iterations):
    dimension=x_train.shape[0]
    w,b = initialize_weights_and_bias(dimension)
    
    parameters,gradients,cost_list = update(w,b,x_train,y_train,learning_rate,num_iterations)
    
    y_prediction_test= predict(parameters["weight"],parameters["bias"],x_test)
    
    print("test accuracy: {} %".format(100- np.mean(np.abs(y_prediction_test- y_test))*100))


# In[ ]:


logistic_regression(x_train,y_train,x_test,y_test,learning_rate=2,num_iterations=120)


# <a id="9"></a><br>
# # Logistic Regresion with Sklearn

# In[ ]:


from sklearn.linear_model import LogisticRegression

lr=LogisticRegression()

lr.fit(x_train.T,y_train.T)

print("test accuracy {} %".format(lr.score(x_test.T,y_test.T)*100))
