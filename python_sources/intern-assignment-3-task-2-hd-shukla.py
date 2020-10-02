#!/usr/bin/env python
# coding: utf-8

# In[6]:


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


# In[7]:


from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras.optimizers import Adam
from keras import backend as K
from keras.layers.normalization import BatchNormalization

img_width, img_height = 224, 224

train_data_dir = '../input/flowers/flowers/'
nb_train_samples = 3462
nb_validation_samples = 861
epochs = 10
batch_size = 32

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

input_shape


# In[8]:


model = Sequential()
model.add(Conv2D(32, (2, 2), input_shape = input_shape))
model.add(Activation('relu'))
model.add(Conv2D(32, (2, 2)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=None, padding='valid', data_format=None))

model.add(Conv2D(64, (2, 2)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=None, padding='valid', data_format=None))
model.add(Conv2D(128, (2, 2)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=None, padding='valid', data_format=None))
model.add(BatchNormalization())

model.add(Conv2D(128, (2, 2)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=None, padding='valid', data_format=None))
model.add(BatchNormalization())

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(5))
model.add(Activation('softmax'))

model.compile(loss ='categorical_crossentropy',optimizer ='adam', metrics =['accuracy'])

data_gen = ImageDataGenerator(rescale = 1. / 255,shear_range = 0.2,zoom_range = 0.2,horizontal_flip = True,validation_split=0.2)

train_generator = data_gen.flow_from_directory(train_data_dir,target_size =(img_width, img_height),seed=13,
                                                    batch_size = batch_size, class_mode ='categorical',subset="training")


# In[9]:



validation_generator = data_gen.flow_from_directory(train_data_dir,target_size =(img_width, img_height),seed=13,
                                                        batch_size = batch_size, class_mode ='categorical',subset="validation")


# In[10]:



model.fit_generator(train_generator, steps_per_epoch = nb_train_samples // batch_size,
                    epochs = epochs, validation_data = validation_generator,
                    validation_steps = nb_validation_samples // batch_size)
