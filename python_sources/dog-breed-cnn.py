#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import cv2
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.


# In[2]:


get_ipython().run_line_magic('ls', "'../input/'")
labels=pd.read_csv('../input/labels.csv')
test=pd.read_csv('../input/sample_submission.csv')


# In[3]:


path=labels['id']
target1=labels['breed']
testpath=test['id']


# In[4]:


target=target1.append(target1)
target=target.append(target)


# In[5]:


from keras.preprocessing.image import load_img,img_to_array
image_train1=[]
for x in path:
    y=cv2.imread('../input/train/'+x+'.jpg')
    y=cv2.resize(y,(64,64))
    y=cv2.GaussianBlur(y,(5,5),0)
    y=cv2.cvtColor(y, cv2.COLOR_RGB2GRAY)
    image_train1.append(img_to_array(y))


# In[6]:


image_test=[]
for x in testpath:
    y=cv2.imread('../input/test/'+x+'.jpg')
    y=cv2.resize(y,(64,64))
    y=cv2.GaussianBlur(y,(5,5),0)
    y=cv2.cvtColor(y, cv2.COLOR_RGB2GRAY)
    image_test.append(img_to_array(y))


# In[7]:


image_train=np.array(image_train1)
image_test=np.array(image_test)


# In[8]:


image_train.shape


# In[9]:


image_train=np.append(image_train,image_train,0)
image_train=np.append(image_train,image_train,0)


# In[10]:


image_train.shape


# In[11]:


target_all=pd.get_dummies(target,sparse=True)
target=np.asarray(target_all)


# In[12]:


from keras.layers import Dense,Dropout,Flatten,Conv2D,MaxPool2D,AvgPool2D
from sklearn.model_selection import train_test_split as tts
xtrain,xtest,ztrain,ztest=tts(image_train,target,train_size=0.8)


# In[13]:


from keras.models import Sequential
from keras.layers import MaxPool2D,AvgPool2D
model=Sequential()
model.add(Conv2D(filters=64,kernel_size=(3,3),activation='relu',input_shape=(64,64,1)))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Dropout(0.2))
model.add(Conv2D(filters=32,kernel_size=(3,3),activation='relu'))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Conv2D(filters=16,kernel_size=(3,3),activation='relu'))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(500, activation = "relu"))
model.add(Dropout(0.2))
model.add(Dense(300, activation = "relu"))
model.add(Dropout(0.2))
model.add(Dense(200, activation = "relu"))
model.add(Dropout(0.2))
model.add(Dense(120, activation = "softmax"))
from keras.preprocessing.image import ImageDataGenerator
data=ImageDataGenerator(height_shift_range=0.1,width_shift_range=0.1,rotation_range=0.1,zoom_range=0.1)


# In[14]:


model.compile(loss='categorical_crossentropy',optimizer='rmsprop',metrics=['accuracy'])


# In[17]:


history=model.fit_generator(data.flow(xtrain,ztrain,batch_size=3000),steps_per_epoch=20,epochs=10,validation_data=[xtest,ztest])


# In[ ]:



