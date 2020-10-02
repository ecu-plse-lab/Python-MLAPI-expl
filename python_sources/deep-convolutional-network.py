#!/usr/bin/env python
# coding: utf-8

# In[41]:


import pandas as pd
import numpy as np
import scipy.io as sio
import os
import matplotlib.pyplot as plt
import keras.backend as K
from ipywidgets import interact
from keras.layers import Input, Dense, Dropout,Conv2D,MaxPooling2D,Flatten
from keras.layers import GlobalMaxPooling2D,UpSampling2D,GlobalMaxPooling1D, Lambda
from keras.models import Model
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Print out the folders where our datasets live. 
print("Datasets: {0}".format(os.listdir("../input/danbury-ai-june-2018")))


# Here we load in numpy matricies for the training images (train_x), training labels (train_y), and test images (test_x). 

# In[49]:


# The training images. 
X = np.load("../input/danbury-ai-june-2018/train_x.npy")
y = np.load("../input/danbury-ai-june-2018/train_y.npy")

# We subtract 1 from the labels in order to scale the the labels between 0,9. 
y = y - 1

# These are the images we will need to predict lables for. 
test  = np.load("../input/danbury-ai-june-2018/test.npy")


# We will now do our standard training/validation split so we can evaluate our model's generalization characteristics. 

# In[50]:


X_train, X_validation, y_train , y_validation = train_test_split(X,to_categorical(y,10), test_size=0.2)


# Here we define a convolutional neural network with a max pooling layer and gobal pooling layer. 

# In[95]:


def makeModel(inputSize):
    inputs = Input(shape=inputSize,name="input")
    x = Conv2D(64, (3, 3), padding='same', activation='sigmoid')(inputs)
    x = MaxPooling2D(pool_size=(2, 2), strides=None, padding='valid')(x)
    x = Dropout(0.25)(x)
    x = Conv2D(64, (3, 3), padding='same', activation='sigmoid')(x)
    x = MaxPooling2D(pool_size=(3, 3), strides=None, padding='valid')(x)
    x = Dropout(0.25)(x)
    x = Conv2D(64, (3, 3), padding='same', activation='sigmoid')(x)
    x = GlobalMaxPooling2D()(x)
    x = Dropout(0.25)(x)
    out = Dense(10,activation='softmax', name="output")(x)

    model = Model(inputs=inputs, outputs=out)
    model.compile(optimizer="adam",loss="categorical_crossentropy",metrics=['acc'])
    
    return model

model2 = makeModel((32,32,3,))
model2.summary()


# We will now train our model. 

# In[97]:


#hist2 = model2.fit(X_train, y_train, batch_size=1000,epochs=1000, validation_data=(X_validation,y_validation))
hist2 = model2.fit(X,to_categorical(y,10), batch_size=1000,epochs=500)


# Now that we have trained our network, let's look at the training loss over the training epochs. 

# In[ ]:


def learningCurves(hist):
    histAcc_train = hist.history['acc']
    histLoss_train = hist.history['loss']
    histAcc_validation = hist.history['val_acc']
    histLoss_validation = hist.history['val_loss']
    maxValAcc = np.max(histAcc_validation)
    minValLoss = np.min(histLoss_validation)

    plt.figure(figsize=(12,12))
    epochs = len(histAcc_train)

    plt.plot(range(epochs),histLoss_train, label="Training Loss", color="#acc6ef")
    plt.plot(range(epochs),histLoss_validation, label="Validation Loss", color="#a7e295")

    plt.scatter(np.argmin(histLoss_validation),minValLoss,zorder=10,color="green")

    plt.xlabel('Epochs',fontsize=14)
    plt.title("Learning Curves",fontsize=20)

    plt.legend()
    plt.show()

    print("Max validation accuracy: {0}".format(maxValAcc))
    print("Minimum validation loss: {0}".format(minValLoss))
    
#learningCurves(hist2)


# Predict the class lables with our model 

# In[38]:


pred = model2.predict(test)
pred = np.argmax(pred,1)
pred = pred + 1


# In[39]:


submission = pd.DataFrame.from_items([
    ('id',list(range(pred.shape[0]))),
    ('label', pred)])

submission.to_csv('submission.csv', index = False)
