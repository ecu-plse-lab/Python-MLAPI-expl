#!/usr/bin/env python
# coding: utf-8

# **I will be using the Aotizhongxin dataset (the first dataset among the ones I have uploaded) in this kernel for analysis. I will print the outputs of only the first 5 entries for all arrays and lists else you guys have to scroll through a lot to reach the next cell and it also takes a lot of time to commit. If you want to print all the entries, you can fork this kernel and just run a loop until the length of the array or list and print all entries. **

# In[ ]:


import pandas as pd
import numpy as np
import seaborn as sns;
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from numpy import array
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras import optimizers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


# In[ ]:


# loading the data into the dataframe
df = pd.read_csv('/kaggle/input/air-quality-of-cities-in-china/PRSA_Data_20130301-20170228/PRSA_Data_Aotizhongxin_20130301-20170228.csv')
print(df)


# In[ ]:


# viewing info about the columns
df.info();


# In[ ]:


#viewing few rows from the top
df.head()


# In[ ]:


#number of rows and columns in the dataset
print(df.shape)


# In[ ]:


#statistical information about columns
print(df.describe())


# In[ ]:


#checking how many null values are in each column
df.isnull().sum()


# In[ ]:


# dropping all the rows with NaN values
df = df.dropna()


# Now that we have dropped all null values, there should be no rows with NaN values. Let's check using the below command and as we can see, there are 0 null values in each column.

# In[ ]:


df.isnull().sum()


# In[ ]:


#defining training and testing data
x_train = df[:24865]
y_train = x_train['PM2.5']
x_test = df[24865:31898]
y_test = x_test['PM2.5']
print(y_test)


# There are many pollutants. Let's first try to predict PM2.5 concentration values. Let the years 2016 and 2017 be the testing set. As you can see below, these 2 years account for 20.06% of the data (test set)

# In[ ]:


df.loc[24865:31898].count() / df.shape[0] * 100


# In[ ]:


#Normalize training data
train_norm = x_train['PM2.5'] 
train_norm_arr = np.asarray(train_norm)
train_norm = np.reshape(train_norm_arr, (-1, 1))
scaler = MinMaxScaler(feature_range=(0, 1))
train_norm = scaler.fit_transform(train_norm)


# Even after normalization and scaing, null values are possible (many people disregard this). Let's check if any null values are present.

# In[ ]:


count = 0
for i in range(len(train_norm)):
    if train_norm[i] == 0:
        count = count +1
print('Number of null values in train_norm = ', count)


# It says 0 because after running the below cell, I ran the above cell. I had to this because I forgot to add a print statement. There were 291 null values and we had to get rid of this. Else, it's gonna be a problem while training.

# In[ ]:


#removing null values 
train_norm = train_norm[train_norm!=0]


# In[ ]:


test_norm = x_test['PM2.5']
test_norm_arr = np.asarray(test_norm)
test_norm = np.reshape(test_norm_arr, (-1, 1))
scaler = MinMaxScaler(feature_range=(0, 1))
test_norm = scaler.fit_transform(test_norm)


# Let's repeat the same procedure for test_norm.

# In[ ]:


count = 0
for i in range(len(test_norm)):
    if test_norm[i] == 0:
        count = count + 1 
print('Number of null values in test_norm = ', count)


# There are 86 null values and we have to get rid of them as below.

# In[ ]:


test_norm = test_norm[test_norm != 0]


# Since this is a time seris data, we should be predicting the values after looking at a set of values rather than just a single value like we usually do. This takes into account the correlation between the data points and the timestamps. Because the neighbours should be considered for how the values change over time. Let's define a function to do this.

# The below function called split_sequence splits the sequence into sets of n values. This n is given as n_steps (step_size). For example, if n=3, we split the sequence in groups of 3. We create 2 empty lists and append the split sequences.

# In[ ]:


def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return array(X),array(y)


# Here the number of features = 1 as we will be predicting a single value. Let's reshape the split sequences into the format of number of rows, number of columns. (shape[0], shape[1]). In the output, we can see that groups of 3 since n_steps = 3 have been obtained.

# In[ ]:


n_steps = 3
X_split_train, y_split_train = split_sequence(train_norm, n_steps)
n_features = 1
X_split_train = X_split_train.reshape((X_split_train.shape[0], X_split_train.shape[1], n_features))
for i in range(1):
    print(X_split_train)


# You can see below that, we predict the value for the first 3 values, then consider that output as one of the 3 values in the next set.
# For example, we preedict 0.1 first, then we take that 0.1 as input in the second set and so on.

# In[ ]:


X_split_test, y_split_test = split_sequence(test_norm, n_steps)
for i in range(5):
    print(X_split_test[i], y_split_test[i])
n_features = 1
X_split_test = X_split_test.reshape((X_split_test.shape[0], X_split_test.shape[1], n_features))


# Let's define our neural network (LSTM: Long Short Term Memory). Let's add 50 nodes in our first layer with a ReLU (Rectified linear unit) activation. Their shape will be step size, number of features. Then we will add, a dense layer with one node for the output.

# We can try out different optimizers to see which minimizes loss and maximizes accuracy. Stochastic gradient descent (SGD), Adam, AdaBoost, RMSProp are few of them. lr = learning rate, decay = by how much to decay the learning rate, momentum = how much should the gradient descent be accelerated to dampen oscillations, nesterov = whether to use nesterov momentum. Nesterov has stronger convergence for convex functions. And then we compile using MSE (mean squared loss) as our loss function.

# In[ ]:


# define model
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model.add(Dense(1))
#sgd = optimizers.SGD(lr=0.001, decay=1e-5, momentum=1.0, nesterov=False)
sgd = optimizers.SGD(lr=0.01, decay=1e-5, momentum=0.9, nesterov=True) #good
#keras.optimizers.RMSprop(learning_rate=0.01, rho=0.9)
keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)
model.compile(optimizer='sgd', loss='mse', metrics=['accuracy'])


# In[ ]:


# fit model
hist = model.fit(X_split_train, y_split_train, validation_data=(X_split_test, y_split_test), epochs=10, verbose = 1)


# In[ ]:


print(hist.history.keys())


# Let's make our predictions using model.predict.

# In[ ]:


yhat = model.predict(X_split_test)
for i in range(5):
    print(yhat[i])


# In[ ]:


mse = mean_squared_error(y_split_test, yhat)
print('MSE: %.5f' % mse)


# Below, I have plotted the actual true values (first plot) and preedicted values (second plot). One can visually see that the distribution is almost the same. This says that our predictions are very accurate.

# In[ ]:


plt.plot(yhat)


# In[ ]:


plt.plot(y_split_test)


# In[ ]:


_, train_acc = model.evaluate(X_split_train, y_split_train, verbose=0)
_, test_acc = model.evaluate(X_split_test, y_split_test, verbose=0)
print('Train: %.6f, Test: %.5f' % (train_acc, test_acc))


# In[ ]:


# summarize history for accuracy
plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


# Above, accuracy increase a lot in the last few epochs. Below, the loss gradually decrease. These are positive signs that our model is doing very good.

# In[ ]:


# summarize history for loss
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


# Until now, we just ran our model for prediction of a single pollutant. We have 6 pollutants in our dataset and can make predictions for all of them. So, I have made a function which can be used to predict the other pollutants rather than having to write the code again and again. I have commented the function calls. You can fork this kernel to uncomment and predit the other pollutants (Coz it would take up a lot of space and time).

# In[ ]:


def compute(var):
    train_norm = x_train[var] 
    train_norm_arr = np.asarray(train_norm)
    train_norm = np.reshape(train_norm_arr, (-1, 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_norm = scaler.fit_transform(train_norm)

    test_norm = x_test[var]
    test_norm_arr = np.asarray(test_norm)
    test_norm = np.reshape(test_norm_arr, (-1, 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    test_norm = scaler.fit_transform(test_norm)

    X_split_train, y_split_train = split_sequence(train_norm, n_steps)
    X_split_train = X_split_train.reshape((X_split_train.shape[0], X_split_train.shape[1], n_features))

    X_split_test, y_split_test = split_sequence(test_norm, n_steps)
    X_split_test = X_split_test.reshape((X_split_test.shape[0], X_split_test.shape[1], n_features))

    hist = model.fit(X_split_train, y_split_train, validation_data=(X_split_test, y_split_test), epochs=10, verbose = 1)

    yhat = model.predict(X_split_test)

    mse = mean_squared_error(y_split_test, yhat)
    print(mse)
    
    plt.plot(hist.history['accuracy'])
    plt.plot(hist.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    
# compute('PM2.5')
# compute('PM10')
# compute('SO2')
# compute('NO2')
# compute('CO')
# compute('O3')


# Below, we will do a lot of visualizations to understand our data using various scatterplots, jointplots, pairplots, heatmap and correlation. 

# In[ ]:


#jointplot for PM2.5 concentration and PM10 concentration
sns.jointplot(x=df['PM2.5'], y=df['PM10'], data = df)


# The above plot gives us the idea that these two conentrations are positively correlated with very few outliers.

# In[ ]:


#finding correlation
corrmat = df.corr()
fig, ax = plt.subplots(figsize=(11,11))

#Heatmap
sns.heatmap(corrmat)


# In[ ]:


#To generate pairplots for all features.
g = sns.pairplot(df)


# In[ ]:


#density plots
df.plot(kind='density', subplots=True, layout=(4,4), sharex=False, figsize=(10,10))
plt.show()


# In[ ]:


#scatter plots
df.plot.scatter(x='PM2.5', y='PM10', c='DarkBlue')


# In[ ]:


plt.scatter(y_split_test, yhat)


# In[ ]:


df.plot.scatter(x='PM10', y='SO2', c='DarkBlue')


# In[ ]:


df.plot.scatter(x='SO2', y='NO2', c='DarkBlue')


# In[ ]:


df.plot.scatter(x='NO2', y='CO', c='DarkBlue')


# In[ ]:


df.plot.scatter(x='CO', y='O3', c='DarkBlue')


# Heatmap is a very useful visualization tool to know how much each feature is correlated. 
# vmax = max value of the heatmap
# fmt = number of decimal places upto which the value is shown
# square = do you want the heatmap to be square shaped
# linewidth = width of the lines in the heatmap
# annot = should the boxes be labelled with the value

# In[ ]:


correlations = df.corr()
fig, ax = plt.subplots(figsize=(15,15))
sns.heatmap(correlations, vmax=1.0, center=0, fmt='.2f', square=True, linewidths=.5, annot=True, cbar_kws={"shrink": .70})
plt.show();


# **Don't forget to upvote if you learnt and enjoyed this notebook as much as I did and share this kernel with your friends!!! Bye.**