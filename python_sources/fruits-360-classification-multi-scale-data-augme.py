#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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


# In[ ]:


get_ipython().system('ls')


# In[ ]:


import sklearn.datasets
import sklearn.model_selection
import keras.preprocessing.image
import keras.utils
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from skimage import color
from sklearn.metrics import accuracy_score
import keras.callbacks
import os
import numpy as np
import cv2

#def load_data(infDir):
#    infData=sklearn.datasets.load_files(infDir,load_content=False)
#    y_inf = np.array(infData['target'])
#    y_inf_names = np.array(infData['target_names'])
#    nclasses = len(np.unique(y_inf))
#    target_size=50
#    x_inf=[]
#    for filename in infData['filenames']:
#        x_inf.append(
#                keras.preprocessing.image.img_to_array(
#                        keras.preprocessing.image.load_img(filename,target_size=(target_size, target_size))
#                )
#        )
#    return([x_inf,y_inf])
    
    

train_dir = '../input/fruits-360/Training'
trainData=sklearn.datasets.load_files(train_dir,load_content=False)

test_dir = '../input/fruits-360/Test'
testData=sklearn.datasets.load_files(test_dir,load_content=False)


y_train = np.array(trainData['target'])
y_train_names = np.array(trainData['target_names'])

y_test = np.array(testData['target'])
y_test_names = np.array(testData['target_names'])

nclasses = len(np.unique(y_train))
target_size=50

x_train=[]
for filename in trainData['filenames']:
    x_train.append(
            keras.preprocessing.image.img_to_array(
                    keras.preprocessing.image.load_img(filename,target_size=(target_size, target_size))
                    )
            )
    
    
x_test=[]
for filename in testData['filenames']:
    x_test.append(
            keras.preprocessing.image.img_to_array(
                    keras.preprocessing.image.load_img(filename,target_size=(target_size, target_size))
                    )
            )


# In[ ]:


x_train=np.array(x_train)
x_train=x_train/255
y_train=keras.utils.np_utils.to_categorical(y_train,nclasses)


x_test=np.array(x_test)
x_test=x_test/255
y_test=keras.utils.np_utils.to_categorical(y_test,nclasses)


# In[ ]:


x_train, x_val, y_train, y_val = sklearn.model_selection.train_test_split(
        x_train, y_train, test_size=0.2
)
print(y_train.shape)
print(y_val.shape)


# In[ ]:


model = keras.models.Sequential()
#model.add(keras.layers.Conv2D(filters = 3, kernel_size = 1, input_shape=x_train.shape[1:],activation='tanh'))
#model.add(keras.layers.Conv2D(filters = 1, kernel_size = 1, padding='same' ,activation='sigmoid'))

model.add(keras.layers.Conv2D(filters = 64, kernel_size = (3,3), activation='relu',input_shape=((None,None,3)), name="conv_1"))
model.add(keras.layers.MaxPooling2D((2,2)))
model.add(keras.layers.Conv2D(filters = 128, kernel_size = (3,3), activation='relu', name="conv_2"))
model.add(keras.layers.MaxPooling2D((2,2)))
model.add(keras.layers.Conv2D(filters = 128, kernel_size = (3,3), activation='relu', name="conv_3"))
#model.add(keras.layers.Flatten())
model.add(keras.layers.pooling.GlobalAveragePooling2D(name="avg_1"))
model.add(keras.layers.Dense(nclasses,activation = 'softmax', name='output'))
model.summary()


# In[ ]:


from IPython.display import SVG
import IPython
from keras.utils import model_to_dot

print(model.summary())

keras.utils.plot_model(model, to_file='test_keras_plot_model.png', show_shapes=True)
IPython.display.Image('test_keras_plot_model.png')


# In[ ]:


model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])
checkpointer = keras.callbacks.ModelCheckpoint(filepath = 'cnn_from_scratch_fruits.hdf5', verbose = 1, save_best_only = True)
earlystopper = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='auto', baseline=None, restore_best_weights=False)


# In[ ]:


def resize_generator(batches, resize, nchannels):
    """Take as input a Keras ImageGen (Iterator) and generate random
    crops from the image batches generated by the original iterator.
    """
    while True:
        batch_x, batch_y = next(batches)
        
        
        r1 = np.random.randint(resize[0], resize[1])
        r2 = np.random.randint(resize[0], resize[1])
        new_resize = (batch_x.shape[1]+r1, batch_x.shape[2]+r2)
        
        
        batch_crops = np.zeros((batch_x.shape[0], new_resize[0], new_resize[1], nchannels))
        
        for i in range(batch_crops.shape[0]):
            batch_crops[i,:,:,:] = cv2.resize(batch_x[i], (new_resize[1], new_resize[0]))
        
        yield (batch_crops, batch_y)




datagen = ImageDataGenerator(
    #horizontal_flip=True,
    #width_shift_range=[-0.2, +0.2], #padding
    #fill_mode='wrap'
)

batch_size=32
epochs = 30
steps_per_epoch = x_train.shape[0]//batch_size

it = datagen.flow(x_train, y_train, batch_size=batch_size)
it = resize_generator(batches=it, resize=(-20, +50), nchannels=3)


# In[ ]:


history = model.fit_generator(it, steps_per_epoch=steps_per_epoch, validation_data=(x_val, y_val), epochs = epochs, callbacks = [checkpointer])


# In[ ]:


history = model.fit_generator(it, steps_per_epoch=steps_per_epoch, validation_data=(x_val, y_val), epochs = epochs, callbacks = [checkpointer])


# In[ ]:


history = model.fit_generator(it, steps_per_epoch=steps_per_epoch, validation_data=(x_val, y_val), epochs = epochs, callbacks = [checkpointer])


# In[ ]:


model.load_weights('cnn_from_scratch_fruits.hdf5')


# In[ ]:


plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()


# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()


# In[ ]:


y_test_pred = model.predict(x_test)
accuracy_score(np.argmax(y_test_pred,axis=1), np.argmax(y_test,axis=1))
