#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system(' rm -rf /kaggle/working/*')


# ## What is Augmentation and how does it helps?
# **Data augmentation** is a technique to increase the size and variation in a given dataset.
# It is a well known fact that **Deep Neural Nets** work best if Dataset is huge in both size and variety.
# 
# Other Augumentation techniques which can be at root of such exploration is **SMOTE.**
# 
# 
# This notebook will cover the aspect of Data Augumentation over Image Data.
# Focus will be on **Various techniques** to achieve **Data augmentation** 
# 
# 
# we will be using **Tensorflow** and **Keras** for implementation which will help us to understand the various aspect of the field.
# 
# More often when data is less in size of not having variety in it, Including **Data augmentation** in **Data preprocessing** steps, help producing larger amount of data with good amount of variety in it. 
# 

# In[ ]:


import random
from shutil import copyfile

import os,sys
import zipfile
import shutil
from os import path, getcwd, chdir

## Bare minimum library requirement
import tensorflow as tf
import keras
#Keras provide API for Augmentation helps in generation
from tensorflow.keras.optimizers import RMSprop


# * As kaggle does not allow us to do any create,delete or update within "/kaggle/input/" let's copy the dataset to working directory.
# * Path of the working directory is "/kaggle/working" and it is easily doable via magic commands. :) 

# In[ ]:


get_ipython().system(' cp -R /kaggle/input/* /kaggle/working')


# **Let's verify the data movement**

# In[ ]:


#List down all directories in "/kaggle/input/"
for dirName,_,fileName in os.walk("/kaggle/input/microsoft-catsvsdogs-dataset/"):
    print(dirName)


# In[ ]:


#List down all directories in "/kaggle/working/"
for dirName,_,fileName in os.walk("/kaggle/working/microsoft-catsvsdogs-dataset/"):
    count = 0
    print("Directory:: ",dirName)


# **Data set contains total of 12501 images and we will use Imagegenerator API of Keras so we need to restructure the directory accordingly.**

# In[ ]:


get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/training/')
get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/training/Dog/')
get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/training/Cat/')

get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/testing/')
get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/testing/Dog/')
get_ipython().system(' mkdir /kaggle/working/microsoft-catsvsdogs-dataset/testing/Cat/')


# In[ ]:


def split_data(SOURCE, TRAINING, TESTING, SPLIT_SIZE,DESTINATION):
    files = []
    for filename in os.listdir(SOURCE):
        file = SOURCE + filename
        if os.path.getsize(file) > 0:
            files.append(filename)
        else:
            print(filename + " has not enough pixels to represent it as an image, seems corrupted so ignoring.")

    training_length = int(len(files) * SPLIT_SIZE)
    testing_length = int(len(files) - training_length)
    shuffled_set = random.sample(files, len(files))
    training_set = shuffled_set[0:training_length]
    testing_set = shuffled_set[-testing_length:]

    for filename in training_set:
        this_file = SOURCE + filename
        destination = TRAINING + filename
        copyfile(this_file, destination)

    for filename in testing_set:
        this_file = SOURCE + filename
        destination = TESTING + filename
        copyfile(this_file, destination)

#####################################################################################

DESTINATION = "/kaggle/working"

CAT_SOURCE_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/PetImages/Cat/"
DOG_SOURCE_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/PetImages/Dog/"

TRAINING_CATS_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/training/Cat/"
TESTING_CATS_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/testing/Cat/"

TRAINING_DOGS_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/training/Dog/"
TESTING_DOGS_DIR = "/kaggle/working/microsoft-catsvsdogs-dataset/testing/Dog/"


# In[ ]:


split_size = .9
split_data(CAT_SOURCE_DIR, TRAINING_CATS_DIR, TESTING_CATS_DIR, split_size,DESTINATION)
split_data(DOG_SOURCE_DIR, TRAINING_DOGS_DIR, TESTING_DOGS_DIR, split_size,DESTINATION)


# Imagine the situation that we have to assign a category to an image that it is a **cat** or **dog** is in the image.
# and in our sample data set, we have got such images where we have several cats and dogs lined up one after another.
# 
# Now how can we play with such images on the fly before giving them to model to get trained on.
# Better augment them on the fly and produce a batch of tensors.
# 
# Doing the augmentation using **Keras** gives another upper hand to us, It doesn't modify or affect the original data source.

# In[ ]:


print("Total Cat iamge count :: ",len(os.listdir(TRAINING_CATS_DIR)))
print("Total Dog iamge count :: ",len(os.listdir(TRAINING_DOGS_DIR)))


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.pyplot import imread, imshow, subplots, show
CAT_TRAINING_DIR , DOG_TRAINING_DIR  =  TRAINING_CATS_DIR,TRAINING_DOGS_DIR

# Parameters for our graph; we'll output images in a 4x4 configuration
nrows = 4
ncols = 4

# Index for iterating over images
pic_index = 0


# In[ ]:


try:
    # Set up matplotlib fig, and size it to fit 4x4 pics
    fig = plt.gcf()
    fig.set_size_inches(ncols * 4, nrows * 4)
    pic_index += 8

    next_cat_pix = [os.path.join(CAT_TRAINING_DIR, fname) for fname in os.listdir('/kaggle/working/microsoft-catsvsdogs-dataset/PetImages/Cat/')[pic_index - 8:pic_index]]
    next_dog_pix = [os.path.join(DOG_TRAINING_DIR, fname) for fname in os.listdir('/kaggle/working/microsoft-catsvsdogs-dataset/PetImages/Dog/')[pic_index - 8:pic_index]]

    for i, img_path in enumerate(next_cat_pix + next_dog_pix):
        # Set up subplot; subplot indices start at 1
        sp = plt.subplot(nrows, ncols, i + 1)
        sp.axis('On')  # Don't show axes (or gridlines)
        img = mpimg.imread(img_path)
        plt.imshow(img)

    plt.show()

except:
    pass


# **Let's generate an UDF which would be helpful in plotting the various augmentated images from the source image.**

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def plot(data_generator):
    """
    Plots 4 images generated by an object of the ImageDataGenerator class.
    """
    data_generator.fit(images)
    image_iterator = data_generator.flow(images)
    
    #Plot the images given by the iterator
    fig, rows = subplots(nrows=1, ncols=4, figsize=(18, 18))
    for row in rows:
        row.imshow(image_iterator.next()[0].astype('int'))
        row.axis('on')
    show()


# Let's Do some basic augmentation and later we will apply various permutation and combination of these techniques. **Lets start with image rotation by few degrees so that features(Pixel values based on spatial arrangement) get affected and label unaffected.**

# In[ ]:


def imageAugmentor():
    data_generator = ImageDataGenerator(rotation_range=180)
    plot(data_generator)

    data_generator = ImageDataGenerator(featurewise_center=False,
                                        width_shift_range=0.65)
    plot(data_generator)

    data_generator = ImageDataGenerator(featurewise_center=False,
                                        width_shift_range=0.65)
    plot(data_generator)

    data_generator = ImageDataGenerator(vertical_flip=True,
                                        zoom_range=[0.2, 0.9],
                                        width_shift_range=0.2)
    plot(data_generator)

    data_generator = ImageDataGenerator(horizontal_flip=True,
                                        zoom_range=[1, 1.5],
                                        width_shift_range=0.2)
    plot(data_generator)

    data_generator = ImageDataGenerator(width_shift_range=[0.1, 0.5])
    plot(data_generator)

    data_generator = ImageDataGenerator(zoom_range=[1, 2], rotation_range=260)
    plot(data_generator)


# In[ ]:


pic_index += 8
next_pic = [
    os.path.join(CAT_TRAINING_DIR, fname) for fname in os.listdir('/kaggle/input/microsoft-catsvsdogs-dataset/PetImages/Cat/')[pic_index - 8:pic_index]
]
image = plt.imread(next_pic[0])
# Creating a dataset which contains just one image.
images = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
imshow(images[0])
show()


# **Few examples regarding how image augmentation looked like before going to model for training.**

# In[ ]:


imageAugmentor()


# <br>
# <br>

# ## Let's examine the scenario where augmentation before training can help better at prediction time

# ##### Dataset we are going to use in this experiment is to detect wether given image is a Cat or Dog

# In[ ]:


dict = {}
training_data_path = "/kaggle/working/microsoft-catsvsdogs-dataset/training/"
for directory in os.listdir(training_data_path):
    count = 0
    for fileName in os.listdir(training_data_path + directory):
        count += 1

    dict.update({"{0}".format(directory): count})
print(dict)


# In[ ]:


class NeuralNet:
    '''
    Responsible for Neural net skeleton
    '''
    '''
    Sequential design of layering to interconnect various layers.
    Hawk eye view would be
     ___________________________________________________
    |conv-->pool-->conv-->pool-->flatten-->dense-->dense|
     ---------------------------------------------------
    
    #Basic parameters to be passed on call 
    #1.training_data_path
    #2.validation_data_path
    #3.callback
    #4.epochs
    #5.batch_size
    #6.learning_rate
    '''
    
    def neuralModeling(self, training_data_path, validation_data_path,
                       callback, epochs, batch_size, learning_rate):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(16, (3, 3),
                                   activation='relu',
                                   input_shape=(150, 150, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        #Model compilation
        model.compile(
            optimizer=RMSprop(lr=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

        #model summary
        model.summary()

        #Make datagen for Train generator
        train_datagen = ImageDataGenerator(rescale=1./255)

        #Train generator
        train_generator = train_datagen.flow_from_directory(
            training_data_path,
            target_size=(150, 150),
            batch_size=batch_size,
            class_mode='binary')
        
        #Make datagen for validation generator
        validation_datagen = ImageDataGenerator(rescale=1./255)

        #validation generator
        validation_generator = validation_datagen.flow_from_directory(
            validation_data_path,
            target_size=(150, 150),
            batch_size=batch_size,
            class_mode='binary')
        logdir = "/kaggle/working/logs" + datetime.now().strftime("%Y%m%d-%H%M%S")
        
        tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)
        
        history = model.fit(train_generator,
                            validation_data=validation_generator,
                            epochs=epochs,
                            verbose=1,
                            callbacks = [tensorboard_callback]
                            )

        return history, model

    '''
    Constructor of the class    
    '''
    
    def __init__(self):
        print("Object getting created")


# In[ ]:


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
from packaging import version

class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        
        if (type(logs.get('accuracy'))!= None and logs.get('accuracy') > 0.99):
            print(
                "\n\n\nGot accuracy above 0.99% so cancelling any further training! \n\nas it might cause Overfitting\n\n"
            )
            self.model.stop_training = True


callback = myCallback()


# ## Model Training
# **Let's start the training the model and then run some image prediction directly from Google.com**

# In[ ]:


#Training data
training_data_path = "/kaggle/working/microsoft-catsvsdogs-dataset/training/"
validation_data_path = "/kaggle/working/microsoft-catsvsdogs-dataset/testing/"
#Epochs
epochs = 10
#Batch size
batch_size=100
#Learning Rate
learning_rate = 0.001


# In[ ]:


''' #Basic parameters to be passed on call 
    #1.training_data_path
    #2.validation_data_path
    #3.callback
    #4.epochs
    #5.batch_size
    #6.learning_rate
'''
net = NeuralNet()
history, model = net.neuralModeling(training_data_path, validation_data_path,callback, epochs, batch_size, learning_rate)


# In[ ]:


import matplotlib.pyplot as plt
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

epochs = range(len(acc))
plt.figure(figsize=(17, 10))
plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend(loc=0)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))
plt.figure(figsize=(17,10))
plt.plot(epochs, loss, 'r', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend(loc=0)
plt.show()


# ***Data augmentation does many changes on the fly in every image and makes a batch  before training to model.That is one of the prime reason that model training with data augmentation on is slower but effective.***
# 
# 