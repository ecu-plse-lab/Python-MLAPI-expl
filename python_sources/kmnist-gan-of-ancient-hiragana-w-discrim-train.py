#!/usr/bin/env python
# coding: utf-8

# 
# This kernel use GAN(Generative Adversarial Network) to generate different ancient Japanese Hiragana, using KMNIST images.
# Based on implementation "GAN with MLP on MNIST" by Vincent Kao, itself based on the reference by Erik Linderen.
# 
# First step is to initalize and import the images

# In[ ]:


from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Lambda
from keras.layers.advanced_activations import LeakyReLU
from keras.models import Sequential, Model
from keras.optimizers import Adam
import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image

#For this project, we will only be using train_images
#To further improve the accuracy of the GAN, you could involve labels
PATH="../input/"
train_images = np.load(PATH+'kmnist-train-imgs.npz')['arr_0']
test_images = np.load(PATH+'kmnist-test-imgs.npz')['arr_0']
train_labels = np.load(PATH+'kmnist-train-labels.npz')['arr_0']
test_labels = np.load(PATH+'kmnist-test-labels.npz')['arr_0']


# ## Set up network parameters
# These will be handy later, also do some sampling parameters

# In[ ]:


img_rows = 28
img_cols = 28
channels = 1
img_shape = (img_rows, img_cols, channels)
latent_dim = 10 #10 classes and hence 10 dimensions
batch_size = 16
epsilon_std = 1.0

# View the dataset to get an idea of what we're dealing with
def plot_sample_images_data(images, labels):
    plt.figure(figsize=(12,12))
    for i in range(10):
        imgs = images[np.where(labels == i)]
        lbls = labels[np.where(labels == i)]
        for j in range(10):
            plt.subplot(10,10,i*10+j+1)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(imgs[j], cmap=plt.cm.binary)
            plt.xlabel(lbls[j])


# In[ ]:


plot_sample_images_data(train_images, train_labels)

def sampling(args):
    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=(batch_size, latent_dim), mean=0., stddev=epsilon_std)
    return z_mean + K.exp(z_log_var / 2) * epsilon


# ## Define a function to build an encoder
# Encoders job is to take an existing image and reduce it to its most simplest form?

# In[ ]:


def build_encoder():
    img = Input(shape=img_shape)
    h = Flatten()(img)
    h = Dense(512)(h)
    h = LeakyReLU(alpha=0.2)(h)
    h = Dense(512)(h)
    h = LeakyReLU(alpha=0.2)(h)
    mu = Dense(latent_dim)(h)
    log_var = Dense(latent_dim)(h)
    z = Lambda(sampling, output_shape=(latent_dim,), name='z')([mu, log_var])
    return Model(img, z)


# ## Define a function to build an decoder
# The decoders job is to build the image from an encoding, which is an artificial representation

# In[ ]:


def build_decoder():
    model = Sequential()
    model.add(Dense(512, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    # tanh is more robust: gradient not equal to 0 around 0
    model.add(Dense(np.prod(img_shape), activation='tanh'))
    model.add(Reshape(img_shape))
    model.summary()
    z = Input(shape=(latent_dim,))
    img = model(z)
    return Model(z, img)


# ## Define a function to build an discriminator
# The discriminator's job is to judge the generated images for authenticity, whether it's real or fake

# In[ ]:


def build_discriminator():
    #Added 1024 layer in discrim
    model = Sequential()
    model.add(Dense(1024, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1, activation="sigmoid"))
    model.summary()
    encoded_repr = Input(shape=(latent_dim,))
    validity = model(encoded_repr)
    return Model(encoded_repr, validity)


# ## Build GAN

# In[ ]:


optimizer = Adam(0.0002, 0.5)

# Build and compile the discriminator
discriminator = build_discriminator()
discriminator.compile(loss='binary_crossentropy',
                      optimizer=optimizer,
                      metrics=['accuracy'])

# Build the encoder / decoder
encoder = build_encoder()
decoder = build_decoder()

img = Input(shape=img_shape)
# The generator takes the image, encodes it and reconstructs it
# from the encoding
encoded_repr = encoder(img)
reconstructed_img = decoder(encoded_repr)

# First pass, train the generator only, then start training discrimnator
# if discriminator is attached to generator, set this flag to fix discriminator
#When we train the generator, we dont want to train the discriminator, and vice versa
#Hence ideally you should run this in two loops
discriminator.trainable = False

# The discriminator determines validity of the encoding
validity = discriminator(encoded_repr)

# The adversarial_autoencoder model  (stacked generator and discriminator)
#This is the generator part
#We define the loss as MSE and binary_crossentropy
adversarial_autoencoder = Model(img, [reconstructed_img, validity])
adversarial_autoencoder.compile(loss=['mse', 'binary_crossentropy'], loss_weights=[0.999, 0.001], optimizer=optimizer)
adversarial_autoencoder.trainable =True


# ## Define a function to train GAN

# In[ ]:


def train(epochs, batch_size=128, sample_interval=50):
    # Load the dataset
    X_train =train_images 

    # Normalization: Rescale -1 to 1
    X_train = (X_train.astype(np.float32) - 127.5) / 127.5
    X_train = np.expand_dims(X_train, axis=3)

    # Adversarial ground truths
    valid = np.ones((batch_size, 1))
    fake = np.zeros((batch_size, 1))

    for epoch in range(epochs):
        #  Train Discriminator

        # Select a random batch of images
        idx = np.random.randint(0, X_train.shape[0], batch_size)
        imgs = X_train[idx]

        latent_fake = encoder.predict(imgs)
        latent_real = np.random.normal(size=(batch_size, latent_dim))

        # Train the discriminator, this should only have a real effect if the discriminator is set to trainable
        # let latent_real's output is close to 1
        d_loss_real = discriminator.train_on_batch(latent_real, valid)
        # let latent_fake's output is close to 0
        d_loss_fake = discriminator.train_on_batch(latent_fake, fake)
        d_loss = 1* np.add(d_loss_real, d_loss_fake)

        # Train the generator
        # decrease reconstruction error and let discriminator's output is close to 1
        g_loss = adversarial_autoencoder.train_on_batch(imgs, [imgs, valid])

        # If at save interval
        if epoch % sample_interval == 0:
            # Plot the progress
            print("%d [D loss: %f, acc: %.2f%%] [G loss: %f, mse: %f]" % (
                epoch, d_loss[0], 100 * d_loss[1], g_loss[0], g_loss[1]))
            # save generated image samples
            sample_images(epoch)
            
        #Now that the intial training epoch has passed, we switch trainable roles
        if(discriminator.trainable==False):
            discriminator.trainable=True
            adversarial_autoencoder.trainable=False
        elif(discriminator.trainable==True):
            discriminator.trainable=False
            adversarial_autoencoder.trainable=True


# In[ ]:


# Save generated images per specified epochs 
def sample_images(epoch):
    r, c = 5, 5
    z = np.random.normal(size=(r * c, latent_dim))
    gen_imgs = decoder.predict(z)
    gen_imgs = 0.5 * gen_imgs + 0.5
    fig, axs = plt.subplots(r, c)
    cnt = 0
    for i in range(r):
        for j in range(c):
            axs[i, j].imshow(gen_imgs[cnt, :, :, 0], cmap=plt.cm.binary)
            axs[i, j].axis('off')
            cnt += 1
    fig.savefig("mnist_%d.png" % epoch)
    plt.close()


# ## Train GAN
# As we've set the discrimnator to be not trainable, we are only training the generator

# In[ ]:


epochs = 60000
sample_interval = 2000
sample_count = epochs/sample_interval


# In[ ]:


train(epochs=epochs, batch_size=batch_size, sample_interval=sample_interval)


# ## Show generated MNIST images per 200 epochs

# In[ ]:


Image.open('mnist_6000.png')


# In[ ]:


Image.open('mnist_10000.png')


# In[ ]:


Image.open('mnist_16000.png')


# In[ ]:


Image.open('mnist_20000.png')


# In[ ]:


Image.open('mnist_28000.png')


# ## Show single generated image

# In[ ]:


z = np.random.normal(size=(1, latent_dim))
gen_imgs = decoder.predict(z)
gen_imgs = 0.5 * gen_imgs + 0.5
plt.imshow(gen_imgs[0, :, :, 0], cmap='gray')


# ## Reference
# [Keras - Adversarial Autoencoder(AAE)](https://github.com/eriklindernoren/Keras-GAN#adversarial-autoencoder)

# In[ ]:



