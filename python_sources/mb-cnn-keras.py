#!/usr/bin/env python
# coding: utf-8

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


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('reload_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
import warnings
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings(action='ignore')


# In[ ]:


# matplotlib configuration
plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['image.interpolation'] = 'spline16'

# numpy setup
np.set_printoptions(precision=2)
np.random.seed(0)


# In[ ]:


import pandas as pd
train_data = pd.read_csv("/kaggle/input/digit-recognizer/train.csv")
test_data = pd.read_csv("/kaggle/input/digit-recognizer/test.csv")

print('Training data shape:    ', train_data.shape)
print('Testing data shape:  ', test_data.shape)


# In[ ]:


Y_train = train_data["label"]
# # Drop 'label' column
X_train = train_data.drop(labels = ["label"],axis = 1) 


# In[ ]:


# Reshape image in 3 dimensions (height = 28px, width = 28px , canal = 1)
X_train = X_train.values.reshape(-1,28,28,1)
X_test = test_data.values.reshape(-1,28,28,1)
print('Training data shape:    ', X_train.shape)
print('Training labels shape:  ', X_test.shape)


# In[ ]:


from keras.utils.np_utils import to_categorical # convert to one-hot-encoding
# Encode labels to one hot vectors (ex : 2 -> [0,0,1,0,0,0,0,0,0,0])
Y_train = to_categorical(Y_train, num_classes = 10)
 


# In[ ]:


from sklearn.model_selection import train_test_split
# Split the train and the validation set for the fitting
X_train, X_test, Y_train, Y_test = train_test_split(X_train, Y_train, test_size = 0.1, random_state=2)


# In[ ]:


print('X_train data shape:  ', X_train.shape)
print('Y_train data shape:    ', Y_train.shape)

print('X_test data shape:  ', X_test.shape)
print('Y_test data shape:  ', Y_test.shape)


# In[ ]:


import seaborn as sns

def plot_sample(X, y, idx=None, annot=False, shape=(28, 28)):
    if idx is None:
        idx = np.random.randint(0, X.shape[0] + 1)
        
    x = X[idx].reshape(shape)
    
    figsize = (shape[0] // 2, shape[1] // 2)
    plt.figure(figsize=figsize)
    sns.heatmap(x, annot=annot, cmap=plt.cm.Greys, cbar=False)
    plt.title(y[idx])
    plt.xticks([])
    plt.yticks([])
    plt.show()

plot_sample(X_train, Y_train, annot=True, idx=None)


# ### Preprocessing: normalization

# - In this dataset, every pixel has a value in `[0, 1]`, so there is no need for feature scaling.
# - But still we need to subtract the mean. 
# 
# Note that the mean vector is computed only from training data and subtracted from all data.

# In[ ]:


# compute mean vector from training data
mu = np.mean(X_train, axis=0)

X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)

# remove mean vector from all data
X_train -= mu
X_test  -= mu


# In[ ]:


plt.figure(figsize=(4, 4))
plt.imshow(mu.reshape(28, 28), interpolation='nearest', cmap=plt.cm.Greys)
plt.xticks([])
plt.yticks([])
plt.title("Mean value of features")
plt.show()


# In[ ]:


from keras.layers import BatchNormalization
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D

model = Sequential()

model.add(Conv2D(filters = 16, kernel_size = (3, 3), activation='relu',
                 input_shape = (28, 28, 1)))
model.add(BatchNormalization())
model.add(Conv2D(filters = 16, kernel_size = (3, 3), activation='relu'))
model.add(BatchNormalization())
#model.add(Conv2D(filters = 16, kernel_size = (3, 3), activation='relu'))
#model.add(BatchNormalization())
model.add(MaxPool2D(strides=(2,2)))
model.add(Dropout(0.25))

model.add(Conv2D(filters = 32, kernel_size = (3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(Conv2D(filters = 32, kernel_size = (3, 3), activation='relu'))
model.add(BatchNormalization())
#model.add(Conv2D(filters = 32, kernel_size = (3, 3), activation='relu'))
#model.add(BatchNormalization())
model.add(MaxPool2D(strides=(2,2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(10, activation='softmax'))


# In[ ]:


from keras.preprocessing.image import ImageDataGenerator
datagen = ImageDataGenerator(zoom_range = 0.1,
                            height_shift_range = 0.1,
                            width_shift_range = 0.1,
                            rotation_range = 10)


# In[ ]:


model.summary()


# In[ ]:


import tensorflow as tf
from tensorflow import keras
model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer =keras.optimizers.Adadelta(),
              metrics= ['accuracy'])


# In[ ]:



model.fit(X_train, Y_train,
         batch_size =128,
         epochs = 5,
         verbose =1,
         validation_data =(X_test,Y_test)
         )


# In[ ]:


#Evaluation for Score Test Data
scoreForTest = model.evaluate(X_test, Y_test, verbose=0)

#Evaluation for Score Train Data
scoreForTrain = model.evaluate(X_train, Y_train, verbose=0)

print('Test Score:', scoreForTest[0])
print('Test Accuracy:', scoreForTest[1] )
print('---------')
print('Train Score:', scoreForTrain[0])
print('Train Accuracy:', scoreForTrain[1] )


# In[ ]:


# defining labels 
activities = ('Test Score', 'Test Accuracy', 'Trian Score', 'Trian Accuracy')
  
# portion covered by each label 
slices = [scoreForTest[0], scoreForTest[1], scoreForTrain[0], scoreForTrain[1]] 
  
# color for each label 
colors = ['r', 'y', 'g', 'b'] 
  
# plotting the pie chart 
plt.pie(slices, labels = activities, colors=colors,  
        startangle=90, shadow = True, explode = (0, 0, 0.1, 0), 
        radius = 1.2, autopct = '%1.1f%%') 
  
# plotting legend 
plt.legend() 
  
# showing the plot 
plt.show() 


# In[ ]:



