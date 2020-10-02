#!/usr/bin/env python
# coding: utf-8

# In[26]:


import numpy as np
import cv2
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, Flatten, MaxPooling2D,Dense,Dropout
from keras.models  import Sequential
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img, array_to_img
import random,os,glob
import matplotlib.pyplot as plt


# In[2]:


dir_path = '../input/garbage classification/Garbage classification'


# In[3]:


img_list = glob.glob(os.path.join(dir_path, '*/*.jpg'))


# In[4]:


len(img_list)


# In[50]:


train=ImageDataGenerator(horizontal_flip=True, vertical_flip=True,validation_split=0.1,rescale=1./255,
                         shear_range = 0.1,zoom_range = 0.1,
                         width_shift_range = 0.1,
                         height_shift_range = 0.1,)
test=ImageDataGenerator(rescale=1/255,validation_split=0.1)
train_generator=train.flow_from_directory(dir_path,target_size=(300,300),batch_size=32,
                                          class_mode='categorical',subset='training')
test_generator=test.flow_from_directory(dir_path,target_size=(300,300),batch_size=32,
                                        class_mode='categorical',subset='validation')
labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())

print(labels)


# In[51]:


model=Sequential()
    
model.add(Conv2D(32,(3,3), padding='same',input_shape=(300,300,3),activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 
model.add(Conv2D(64,(3,3), padding='same',activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 
model.add(Conv2D(32,(3,3), padding='same',activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 
model.add(Flatten())
model.add(Dense(64,activation='relu'))
model.add(Dense(6,activation='softmax'))

filepath="trained_model.h5"
checkpoint1 = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint1]


# In[47]:


model.summary()


# In[52]:


model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])


# In[53]:


model.fit_generator(train_generator, epochs=100, steps_per_epoch=2276//32,validation_data=test_generator,
                    validation_steps=251//32,callbacks=callbacks_list)
