#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Sequential, Model
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import time
import cv2
from PIL import Image


# # Load training data

# In[ ]:


X_train=np.load('../input/train-imgs.npz')['arr_0']
Y_train=np.load('../input/train-labels.npz')['arr_0']


# # Build GAN model

# In[ ]:


img_rows = 28
img_cols = 28
channels = 1
img_shape = (img_rows, img_cols, channels)
latent_dim = 100


# In[ ]:


def generate_model_for_class(class_generator):
    _indices = np.where(Y_train==class_generator)
    x_train = X_train[_indices]
    
    def build_generator():
        model = Sequential()
        model.add(Dense(128 * 7 * 7, activation="relu", input_dim=latent_dim))
        model.add(Reshape((7, 7, 128)))
        model.add(UpSampling2D())
        model.add(Conv2D(128, kernel_size=3, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Activation("relu"))
        model.add(UpSampling2D())
        model.add(Conv2D(64, kernel_size=3, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Activation("relu"))
        model.add(Conv2D(channels, kernel_size=3, padding="same"))
        model.add(Activation("tanh"))
        model.summary()
        noise = Input(shape=(latent_dim,))
        img = model(noise)
        return Model(noise, img)
    
    def build_discriminator():
        model = Sequential()
        model.add(Conv2D(32, kernel_size=3, strides=2, input_shape=img_shape, padding="same"))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(64, kernel_size=3, strides=2, padding="same"))
        model.add(ZeroPadding2D(padding=((0, 1), (0, 1))))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(128, kernel_size=3, strides=2, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(256, kernel_size=3, strides=1, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(1, activation='sigmoid'))
        model.summary()
        img = Input(shape=img_shape)
        validity = model(img)
        return Model(img, validity)
    
    optimizer = Adam(0.0002, 0.5)
    
    discriminator = build_discriminator()
    discriminator.compile(loss='binary_crossentropy',
                          optimizer=optimizer,
                          metrics=['accuracy'])

    # build generator
    generator = build_generator()
    z = Input(shape=(100,))
    img = generator(z)

    # The discriminator takes generated images as input and determines validity
    valid = discriminator(img)

    # The combined model  (stacked generator and discriminator)
    # Trains the generator to fool the discriminator
    combined = Model(z, valid)
    combined.compile(loss='binary_crossentropy', optimizer=optimizer)
    
    
    def train(epochs, batch_size, save_interval, x_train):
        os.makedirs('images', exist_ok=True)        

        # Rescale -1 to 1
        x_train = x_train / 127.5 - 1.
        x_train = np.expand_dims(x_train, axis=3)

        # Adversarial ground truths
        valid = np.ones((batch_size, 1))
        fake = np.zeros((batch_size, 1))

        for epoch in range(epochs):
            # Select a random real images
            idx = np.random.randint(0, x_train.shape[0], batch_size)
            real_imgs = x_train[idx]

            # Sample noise and generate a batch of fake images
            noise = np.random.normal(0, 1, (batch_size, latent_dim))
            fake_imgs = generator.predict(noise)

            # Train the discriminator
            D_loss_real = discriminator.train_on_batch(real_imgs, valid)
            D_loss_fake = discriminator.train_on_batch(fake_imgs, fake)
            D_loss = 0.5 * np.add(D_loss_real, D_loss_fake)

            # Train the generator
            g_loss = combined.train_on_batch(noise, valid)

            # If at save interval
            if epoch % save_interval == 0:
                # Print the progress
                print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, D_loss[0], 100 * D_loss[1], g_loss))

    start = time.time()

    train(epochs=70000, batch_size=32, save_interval=1000, x_train=x_train)

    end = time.time()
    elapsed_train_time = 'elapsed training time: {} min, {} sec '.format(int((end - start) / 60),
                                                                         int((end - start) % 60))
    print(elapsed_train_time)
    generator.save('generator_'+str(class_generator)+'.h5')


# # Create a generative model for each class

# In[ ]:


for i in range(0,10):
    generate_model_for_class(i)
