#!/usr/bin/env python
# coding: utf-8

# This kernel is done with sone editing in this kernel  [cifar10_cnn](https://www.kaggle.com/lianglirong/cifar10-cnn-by-keras)"
# 
# in version_3 we use adam as an optimizer and another small editing and use 40 epoch  with 64 batch size to avoiad overfitting

# In[ ]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from keras.datasets import cifar10

import os
import tarfile
import sys
import pickle
print(os.listdir("../input/cifar10/"))

import keras
from keras import backend   as K
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense,Conv2D,Flatten,Dropout,MaxPooling2D,Activation, BatchNormalization
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
# Any results you write to the current directory are saved as output.


# In[ ]:


from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())


# In[ ]:


def load_batch(fpath, label_key='labels'):
    """Internal utility for parsing CIFAR data.

    # Arguments
        fpath: path the file to parse.
        label_key: key for label data in the retrieve
            dictionary.

    # Returns
        A tuple `(data, labels)`.
    """
    with open(fpath, 'rb') as f:
        if sys.version_info < (3,):
            d = pickle.load(f)
        else:
            d = pickle.load(f, encoding='bytes')
            # decode utf8
            d_decoded = {}
            for k, v in d.items():
                d_decoded[k.decode('utf8')] = v
            d = d_decoded
    data = d['data']
    labels = d[label_key]

    data = data.reshape(data.shape[0], 3, 32, 32)
    return data, labels


# In[ ]:


train_num = 50000
train_x = np.zeros(shape=(train_num,3,32,32))
train_y = np.zeros(shape=(train_num))

test_num = 10000
test_x = np.zeros(shape=(test_num,3,32,32))
test_y = np.zeros(shape=(test_num))


# In[ ]:


def load_data():
    for i in range(1,6):
        begin = (i-1)*10000
        end = i*10000
        train_x[begin:end,:,:,:],train_y[begin:end] = load_batch("../input/cifar10/data_batch_"+str(i))
    
    test_x[:],test_y[:] = load_batch("../input/cifar10/test_batch")


# In[ ]:


load_data()


# In[ ]:


test_y[1:10]


# In[ ]:


train_x[1]


# In[ ]:


if K.image_data_format() == 'channels_last':
    print("channels_last")
    test_x = test_x.transpose(0, 2, 3, 1)
    train_x = train_x.transpose(0, 2, 3, 1)
else:
    print("channels_first")


# In[ ]:


train_x.shape


# In[ ]:


train_y.shape


# In[ ]:


train_y[0:10]


# In[ ]:


test_x.shape


# In[ ]:


test_y.shape


# ### we should zero-center and normalize data first

# In[ ]:


# zero-center 
train_x -= np.mean(train_x, axis = 0)
test_x -= np.mean(test_x, axis = 0)


# In[ ]:


# Normalization
train_x /= np.std(train_x, axis = 0)
test_x /= np.std(test_x, axis = 0)


# In[ ]:


train_x[2][2][3]


# In[ ]:


train_y = to_categorical(train_y,10)
test_y = to_categorical(test_y,10)


# In[ ]:


train_y[1:5]


# In[ ]:


train_y.shape


# In[ ]:


model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=train_x.shape[1:]))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.3))
model.add(Dense(10))
model.add(BatchNormalization())
model.add(Activation('softmax'))

# initiate RMSprop optimizer
opt = keras.optimizers.Adam(lr=0.0001)

# Let's train the model using RMSprop
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])


# In[ ]:


batch_size = 64
epochs = 40


# In[ ]:


history = model.fit(train_x,train_y,batch_size,epochs,validation_data=(test_x,test_y),shuffle=True)


# In[ ]:


history.history


# In[ ]:


fig = plt.plot(history.history["acc"],label = "train", color='green')
plt.plot(history.history["val_acc"],label = "test", color='red')
plt.legend(loc='upper left')
plt.xlabel("epochs")
plt.ylabel("accuracy")
plt.title("accuracy by epochs")
plt.show()


# In[ ]:


fig = plt.plot(history.history["loss"],label = "train", color='green')
plt.plot(history.history["val_loss"],label = "test", color='red')
plt.legend(loc='upper left')
plt.xlabel("epochs")
plt.ylabel("loss")
plt.title("loss by epochs")
plt.show()


# In[ ]:



