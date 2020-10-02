#!/usr/bin/env python
# coding: utf-8

# # **Image Matching using Approximate Nearest Neighbours**
# 
# ### After browsing through the image datasets, you will occasionally see images that are carbon copies of each other. A simple strategy to classify the test data is to find the images that look similar to your query image (input test data). 
# 
# ### To identify similar images, we can measure the distance between each of the pixels of 2 images (color image are just 3 layers of pixels, with each layer corresponding to Red, Green and Blue channel), and look for the image sets which are closest to each other. The images similar to our query image is known as the nearest neighbours. We can then decide the sub-category of our query image by looking at its neighbours' labels. This is a lazy-learning technique known as **K - Nearest Neighbour (KNN)**.
# 
# ### However, we have some constraints. Traditional KNN is computationally and memory expensive (imagine we got to store all the training images, and for each image query, we do a blind search on these training images). Thus, in this notebook, I will show you a proof of concept of image matching using **Approximate Nearest Neighbours (ANN)** instead, which is theoretically faster with decent search accuracy. I will use **[Annoy](https://github.com/spotify/annoy)** package for the ANN, because it is **~~annoying~~** straight forward to use.
# 
# ### As for the dataset, I will use the **[Fashion dataset](https://www.kaggle.com/burn874/fashionfull)** which is kindly prepared and shared by **[Chua Cheng Hong](https://www.kaggle.com/burn874)**. 

# In[ ]:


import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

import os
import glob
import cv2
import annoy
import time

from tqdm import tqdm
from numpy.linalg import norm
from scipy.spatial import distance


# # **First, load the files.**

# In[ ]:


train_folder_dir = '../input/fashionfull/fashion_image_resized/fashion_image_resized/train/'
test_folder_dir = '../input/fashionfull/fashion_image_resized/fashion_image_resized/test/'

df_train = pd.read_csv('../input/fashionfull/fashion.csv')
df_test = pd.read_csv('../input/fashionfull/fashion_test.csv')

train_image_paths = df_train['image_name'].values
test_image_paths = df_test['image_name'].values


# # **We need an image generator that generates resized images.**
# 
# ### This function will resize the image to 25 x 25 x 3, mainly to deal with the memory constraint of Kaggle kernels. You are free to use higher resolution images (but make sure to standardize the size across all images) if you have monstrous RAM (probably 32GB or more for this dataset) or found a way to read directly from disk without loading them in RAM.

# In[ ]:


def image_generator(image_paths, base_dir):
    for path in image_paths:
        img = cv2.imread(base_dir + path)
        resized = cv2.resize(img, (25,25))
        yield resized.flatten()


# ### Just to give you an understanding of how much quality difference we are talking about:

# In[ ]:


plt.figure(figsize=(20,12))

image1 = cv2.imread(train_folder_dir + train_image_paths[3])
resized1 = cv2.resize(image1, (25,25))

image2 = cv2.imread(train_folder_dir + train_image_paths[300])
resized2 = cv2.resize(image2, (25,25))


plt.subplot(1, 4, 1)
plt.imshow(cv2.cvtColor(image1, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('Original Image 1',fontsize=16)

plt.subplot(1, 4, 2)
plt.imshow(cv2.cvtColor(resized1, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('Resized Image 1',fontsize=16)

plt.subplot(1, 4, 3)
plt.imshow(cv2.cvtColor(image2, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('Original Image 2',fontsize=16)

plt.subplot(1, 4, 4)
plt.imshow(cv2.cvtColor(resized2, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('Resized Image 2',fontsize=16)

plt.tight_layout()
plt.show()


# # **Next, create and map the indices of all images and build the ANN (trees)**
# 
# ### Higher number of trees = higher accuracy & longer building time.

# In[ ]:


start_time = time.time()

vector_length = 25*25*3

t = annoy.AnnoyIndex(vector_length)

for i, v in enumerate(image_generator(train_image_paths, train_folder_dir)):
    t.add_item(i, v)

print(f'Time taken : {(time.time() - start_time) / 60:.2f} mins')


# In[ ]:


start_time = time.time()

Ntrees = 100
t.build(Ntrees)

print(f'Time taken : {(time.time() - start_time) / 60:.2f} mins')


# # **Now lets check out the ANN using some test data.**
# 
# ### We will look for the 4 nearest neighbours to the query image and print out the neighbours.

# In[ ]:


def plot_neighbours(query_vector, n = 4):
    
    n_indices = t.get_nns_by_vector(query_vector, n)
    n_vectors = [np.array(query_vector, dtype=np.uint8).reshape((25,25,3))]
    n_distances = [0]
    
    for i in n_indices:
        n_vec = t.get_item_vector(i)
        n_arr = np.array(n_vec, dtype=np.uint8).reshape((25,25,3))
        n_vectors.append(n_arr)
        n_distances.append(np.abs(distance.cosine(n_vectors[0].ravel(), n_arr.ravel())))
        
    rows = n // 5 + 1
    
    plt.figure(figsize=(20, rows * 4))
    
    for i, n in enumerate(n_vectors):
        plt.subplot(rows, 5, i + 1)
        plt.imshow(cv2.cvtColor(n, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        if i == 0:
            plt.title('Query Image', fontsize=16)
        else:
            plt.title(f'N{i}, Cosine_dist = {n_distances[i]:.2f}', fontsize=16)
        
    plt.tight_layout()
    plt.show()


# In[ ]:


for image in image_generator(test_image_paths[0:10], test_folder_dir):
    plot_neighbours(image, n=4)


# # **Hmmm ok.**
# 
# ### Not too bad. Note that by default, Annoy uses cosine distance to look for the query image's nearest neighbour, if you would like to build a model on a different distance measure, you have to specify it in the first step where you map the Annoy Index. 
# 
# ### For ideal results, you will likely require a combinations of distance measures, each with a fine-tuned threshold. You can experiment yourself and figure them out.
# 
# ### Also, there will be some images which are not duplicated within the dataset, and thus, you won't be able to find any similar matches (though Annoy will still return you the nearest neighbours). For these images, you will need to rely on the text data to classify them instead.
# 
# # **Lastly, remember to save the ANN model, so that you can load it quickly (like in seconds) next time.**

# In[ ]:


t.save('fashion_100trees.ann')

# To load it next time, just run the following line with the appropriate file path
# t.load('../input/image-matching-fashion-v1/fashion_100trees.ann')


# # **Hope it was useful!** 
# 
# ### Closing thought : No data is totally useless. Always strive to find patterns and use cases within the available data and squeeze out every last bit of available information from the data.

# In[ ]:



