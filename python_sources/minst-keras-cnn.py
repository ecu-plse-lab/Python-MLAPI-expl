#!/usr/bin/env python
# coding: utf-8

# This notebook is referred from [this kernel](https://www.kaggle.com/drouholi/mnist-mlp), [this kernel](https://www.kaggle.com/adityaecdrid/mnist-with-keras-for-beginners-99457) and [this kernel](https://www.kaggle.com/kentaroyoshioka47/cnn-with-batchnormalization-in-keras-94).
# 
# We are going to build a CNNs for MNIST digit classification.

# **Data analysis**

# In[ ]:


#importing necessary libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.cm as cm


# Load the train and test dataset

# In[ ]:


#load the data
train_data = pd.read_csv("../input/train.csv")
test_data = pd.read_csv("../input/test.csv")

#reshape the train and test data
X_train = (train_data.ix[:,1:].values).astype('float32')
#data labels
y_train = train_data.ix[:,0].values.astype('int32')
#test data
X_test = test_data.astype('float32')

print("The MNIST dataset has a training set of %d examples." % len(X_train))
print("The MNIST database has a test set of %d examples." % len(X_test))


# In[ ]:


#Convert training data to img format 
X_train = X_train.reshape(X_train.shape[0], 28, 28)
X_train.shape
X_test = X_test.values.reshape(-1, 28, 28,1)
X_test.shape
for i in range(6):
    plt.subplot(330 + (i+1))
    plt.imshow(X_train[i], cmap=plt.get_cmap('gray'))
    plt.title(y_train[i]);


# Visualize the image

# In[ ]:


def visualize_input(img, ax):
    ax.imshow(img, cmap='gray')
    width, height = img.shape
    thresh = img.max()/2.5
    for x in range(width):
        for y in range(height):
            ax.annotate(str(round(img[x][y],2)), xy=(y,x),
                        horizontalalignment='center',
                        verticalalignment='center',
                        color='white' if img[x][y]<thresh else 'black')

fig = plt.figure(figsize = (12,12)) 
ax = fig.add_subplot(111)
visualize_input(X_train[5], ax)


# In[ ]:


#reshape the image and expand to 1 dimension
X_train = X_train.reshape(X_train.shape[0], 28, 28,1)
X_train.shape


# In[ ]:


X_test = X_test.reshape(X_test.shape[0], 28, 28,1)
X_test.shape


# In[ ]:


import seaborn as sns
sns.countplot(train_data['label'])


# In[ ]:


#normalize the image
X_train = X_train.astype('float32')/255
X_test = X_test.astype('float32')/255 


# **Data Augmentation**

# In[ ]:


from keras.preprocessing.image import ImageDataGenerator

# create and configure augmented image generator
datagen_train = ImageDataGenerator(
    width_shift_range=0.2,  # randomly shift images horizontally (10% of total width)
    height_shift_range=0.2,# randomly shift images vertically (10% of total height)
    rotation_range = 20,
    horizontal_flip=True,
    vertical_flip = True,
    shear_range = 0.1) 

# fit augmented image generator on data
datagen_train.fit(X_train)


# **Split into train and test data**
# One hot encoding for the labels

# In[ ]:


from keras.utils import np_utils
from sklearn.model_selection import train_test_split
# Set the random seed
random_seed = 2
# Split the train and the validation set for the fitting
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.1, random_state=random_seed)
# print first ten (integer-valued) training labels
print('Integer-valued labels:')
print(y_train[:10])

# one-hot encode the labels
y_train = np_utils.to_categorical(y_train, 10)
y_val = np_utils.to_categorical(y_val, 10)

# print first ten (one-hot) training labels
print('One-hot labels:')
print(y_train[:10])


# **Build the model**

# In[ ]:



from keras import optimizers
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Activation, BatchNormalization

model = Sequential()
model.add(Conv2D(32, (5, 5), padding='same',
                 input_shape=X_train.shape[1:]))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(Conv2D(32, (5, 5), padding='same'))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(10))
model.add(Activation('softmax'))

optimizer = optimizers.Adam(lr=0.001)
model.compile(loss='categorical_crossentropy',
              optimizer=optimizer,
              metrics=['accuracy'])

model.summary()
print("input shape ",model.input_shape)
print("output shape ",model.output_shape)


# In[ ]:


#train the data
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

batch_size = 256
nb_epoch = 50
checkpointer = [
    ReduceLROnPlateau(monitor='val_loss', 
                      patience=3, 
                      verbose=1,
                      factor=0.5,
                      min_lr = 0.00001,
                      cooldown=0),
    ModelCheckpoint('mnist.model.best.hdf5',
        monitor='val_acc', 
        save_best_only=True, 
        mode='max',
        verbose=1)
]
hist = model.fit(X_train, y_train, epochs=nb_epoch, batch_size=batch_size, validation_data=[X_val, y_val], callbacks=checkpointer,verbose=1, shuffle=True)


# In[ ]:


plt.title('Train Accuracy vs Val Accuracy')
plt.plot(hist.history['acc'], label='Train Accuracy', color='black')
plt.plot(hist.history['val_acc'], label='Validation Accuracy', color='red')
plt.legend()
plt.show()


# In[ ]:


# evaluate test accuracy

from keras.models import load_model

model = load_model('mnist.model.best.hdf5')
score = model.evaluate(X_val, y_val, verbose=0)
accuracy = 100*score[1]

# print test accuracy
print('Validation accuracy: %.4f%%' % accuracy)


# **Submit the test prediction**

# In[ ]:


predictions = model.predict_classes(X_test, verbose=1)

submissions = pd.DataFrame({"ImageId": list(range(1,len(predictions)+1)),
                            "Label": predictions})
submissions.to_csv("mnist_CNN_test.csv",index=False)
