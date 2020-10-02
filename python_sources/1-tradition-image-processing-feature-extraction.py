#!/usr/bin/env python
# coding: utf-8

# # Part 1 - Tradition Image processing for classification: feature extraction
# 
# The notebook is an educational experiment rather than a competitive one. The notebook explores traditional image processing methods for extracting features from images to use in classification. I've only used a subset of available techniques here, several other features can also be derived from the images.
# 
# Needless to mention, modern deep learning approaches will perform significantly better. It was fun to play around.

# In[ ]:


import pandas as pd 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook
from matplotlib.patches import Rectangle
import seaborn as sns
import pydicom as dcm
get_ipython().run_line_magic('matplotlib', 'inline')
plt.set_cmap(plt.cm.bone)
IS_LOCAL = True
import os
import cv2
import skimage
from skimage import feature, filters
from tqdm import tqdm

PATH="../input/rsna-pneumonia-detection-challenge"

print(os.listdir(PATH))


# In[ ]:


class_info_df = pd.read_csv(PATH+'/stage_2_detailed_class_info.csv')
train_labels_df = pd.read_csv(PATH+'/stage_2_train_labels.csv')
train_class_df = train_labels_df.merge(class_info_df, left_on='patientId', right_on='patientId', how='inner')


# In[ ]:


train_class_df.head()


# ## Utility functions

# In[ ]:


def load_images(data):
    imgs = []
    for path in data['patientId']:
        patientImage = path + '.dcm'
        imagePath = os.path.join(PATH,"stage_2_train_images/", patientImage)
        img = dcm.read_file(imagePath).pixel_array
        imgs.append(img)
    return imgs

def imshow_gray(img):
    plt.figure(figsize=(12,7))
    return plt.imshow(img, cmap='gray')
    
def imshow_with_labels(img, patient_id):
    rows = train_labels_df[train_labels_df['patientId'] == patient_id]
    for row in rows.itertuples():        
        x, y, w, h = row.x, row.y, row.width, row.height
        x, y, w, h = map(int, [x,y,w,h])
        cv2.rectangle(img, (x,y), (x+w,y+h), 255, 2)
    plt.figure(figsize=(12,7))
    return plt.imshow(img, cmap='gray')


# ## Sample a few images and process them

# In[ ]:


test_df = train_class_df[train_class_df['Target']==1].sample(4)
box = test_df.loc[test_df.index, ['x', 'y', 'width', 'height']]
test = load_images(test_df[0:3])


# In[ ]:


idx = 1
img = test[idx]
imshow_with_labels(img.copy(), test_df.iloc[idx,0])


# ## Image enhancement

# ### Histogram equalization

# In[ ]:


equ = cv2.equalizeHist(test[idx])
ax = imshow_gray(equ)


# Equalization presents a good contrast of the lungs, and further accents the presence of opacity

# ### Image sharpening

# In[ ]:


# apply hpf kernel
hpf_kernel = np.full((3, 3), -1)
hpf_kernel[1,1] = 9
im_hp = cv2.filter2D(equ, -1, hpf_kernel)

# use unsharpen mask filter
im_us = skimage.filters.unsharp_mask(equ)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,9))
ax1.imshow(im_hp, cmap='gray')
ax1.set_title('High pass filter')
ax2.imshow(im_us, cmap='gray')
ax2.set_title('unsharpen mask filter')
fig.suptitle('Image sharpening')


# High pass show more detail, while unmask is still a little blurry, not ideal for feature extraction

# ### Thresholding
# 

# In[ ]:


# otsu thresholding
ret, otsu = cv2.threshold(cv2.GaussianBlur(im_hp,(7,7),0),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
# local thresholding
local = im_hp > skimage.filters.threshold_local(im_hp, 5)
mean = im_hp > skimage.filters.threshold_mean(im_hp)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16,9))
ax1.imshow(otsu, cmap='gray')
ax1.set_title('Otsu thresholding')
ax2.imshow(local, cmap='gray')
ax2.set_title('Local thresholding')
fig.suptitle('Image sharpening')
ax3.imshow(mean, cmap='gray')
ax3.set_title('Mean thresholding')
fig.suptitle('Image thresholding')


# Otsu thresholding helps extract smooth edges, so we choose it and it segments the lungs portion better

# ### Edge detection

# In[ ]:


sobel = filters.sobel(otsu)
canny = feature.canny(otsu/255)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,9))
ax1.imshow(canny, cmap='gray')
ax1.set_title('Canny edge detection')
ax2.imshow(sobel, cmap='gray')
ax2.set_title('Sobel operator')
fig.suptitle('Edge detection')


# Sobel fiter extracts the edges better than canny

# ### Lung segmentation
# 
# Find and pull out contours

# In[ ]:


contours, hier = cv2.findContours((sobel * 255).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
print('Contours found ', len(contours))

srt_contours = sorted(contours, key=lambda x: x.shape[0], reverse=True)
select_contour = srt_contours[0]  # probably not the best assumption

test = img.copy()
img_contour = cv2.drawContours(test, [select_contour], 0, (255,0,0), thickness=3)

imshow_gray(img_contour)


# After identifying the lung segment we can extract the center of moment of this segment. Since, all the X-ray images are from the same dimension, this can be a valid feature for prediction

# In[ ]:


M = cv2.moments(select_contour)
cx = int(M['m10'] / M['m00'])
cy = int(M["m01"] / M["m00"])

test = img.copy()
cv2.circle(test, (cx, cy), 7, (255, 255, 255), -1)
imshow_gray(test)


# But there are images were the subject is slightly rotated, and differently sized so we want center of moment to be invariant to rotation and scale. So we pick **Hu moments**. We will also log the moments to make it easy to compare and drop the 3rd moment as it depends on the other moments and 7th moment as it distinguishes mirror images and there are no flipped images in the dataset

# In[ ]:


def get_hu_moments(contour):
    M = cv2.moments(select_contour)
    hu = cv2.HuMoments(M).ravel().tolist()
    del hu[2]
    del hu[-1]
    log_hu = [-np.sign(a)*np.log10(np.abs(a)) for a in hu]
    return log_hu

get_hu_moments(select_contour)


# ## Feature extraction
# We derive the following features from our above results to build a classifier for pneumonia detection:
# * Area of opacity
# * Perimeter of visible lung regions
# * Irregularity index
# * Equivalent diameter
# * Mean, sd of unenhanced image
# * Hu moments
# <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAf8AAAEZCAYAAACZ7CwhAAAGinRFWHRteGZpbGUAJTNDbXhmaWxlJTIwaG9zdCUzRCUyMnd3dy5kcmF3LmlvJTIyJTIwbW9kaWZpZWQlM0QlMjIyMDE5LTA5LTI3VDA4JTNBMzglM0EyNi4zMTFaJTIyJTIwYWdlbnQlM0QlMjJNb3ppbGxhJTJGNS4wJTIwKFgxMSUzQiUyMExpbnV4JTIweDg2XzY0JTNCJTIwcnYlM0E2OS4wKSUyMEdlY2tvJTJGMjAxMDAxMDElMjBGaXJlZm94JTJGNjkuMCUyMiUyMGV0YWclM0QlMjJKTm9aZjB0bmJwblhvSEdGZmpwUCUyMiUyMHZlcnNpb24lM0QlMjIxMS4zLjIlMjIlMjB0eXBlJTNEJTIyZGV2aWNlJTIyJTIwcGFnZXMlM0QlMjIxJTIyJTNFJTNDZGlhZ3JhbSUyMGlkJTNEJTIyZklmRnE3RklQUWdzaWpjYlAtRFklMjIlMjBuYW1lJTNEJTIyUGFnZS0xJTIyJTNFNVZuYlV0c3dFUDJhUE5LSkw3bndDQW1GenJSVHBxUlQ2SnV3TjVhS0xLV3ljdVBydTdMbE9MWURrMUl5Q3ZRbDR6MlNvdFdlcyUyQnUxM1FsRzZlcFNrUm45SW1QZ0hiOGJyenJCdU9QN3cxNkl2d1pZRjBEWUR3b2dVU3d1SUs4Q2J0Z2pXTEJyMFRtTElhdE4xRkp5eldaMU1KSkNRS1JyR0ZGS0x1dlRwcExYZDUyUkJGckFUVVI0RyUyRjNCWWszdHNmeEJoVjhCUzJpNXM5YyUyRkxVWlNVazYySjhrb2llVnlDd291T3NGSVNhbUxxM1ExQW01aVY4YWxXUGZ4aWRHTll3cUUzbWZCZDMlMkY2c05DUDZ0S1B2WiUyQlRId3N4aWFLVHZ2Vk5yOHNEUTR6bnQ2WlVtc3BFQ3NJdkt2UmN5Ym1Jd2Z4ckY2MXF6bWNwWndoNkNQNENyZGVXVERMWEVpR3FVMjVIMFdHMXZyWHJjJTJCUE9HQjk2cFRsZWJRJTJCTzE5WXFmRFVPUGhrQ0MyVnlyaUo0NXR5bGxJaEtRRDh6ejk4UWhRSUhtUUw2ZyUyQnNVY0tMWm91NEhzVkpMTnZNcU52RENFdklYNUhpZUUzWldUTjlXZktCMXR6VlNVV01NaDh4NFhhZlVGUCUyQjdJSHh1ZCUyRnFxV01Jd3pvamVubndqNjd3RVJKUUphSkZZcDJoSm1ZYWJHY21qc3NRaVdxZkRiZ1JLdyUyQnI1NExaallSZUV0Z0xaRXV3RjFsNVdCYzBycXhUZEttYjk3b0dpTiUyRmhQcTQ2JTJGcDdZRGw5TDJXOUslMkJZcG1XaVNLcGljUHZPZUhzRWYyUXdybXdqMCUyRlp3N2RTc2F0c3FCTGdycWIlMkZnMmREc0djMmhDNnpJV2hsdzZmVXRJeDVQNmRtSUpoSW5PZEJHQnhiSHB5JTJCbFR4NFJUMkhlJTJCcTU1N1M2ZDUwd1UxWWJyJTJCUHEzcnN2TzU3VGxqOXNsWnNKVlpCUmZHdzl4a0t6dVFFN0t6UyUyQmsyZWtWOVRsdjFZRHUlMkZSYU10eDVRMVF3cUJNVkRCc0VGSGxnVnpVNDJManhjbHA2TFIyYiUyQkp2M1FLQWhPb3Jtc2FubG9PZGF5JTJCVTdyNjJvcFVBd1VxTThVakVzV2tIRDQlMkJ0NlpES3Q1QU9NSkpjS0VTR0ZFZnlVY2Q2QXNJdFBCSm9SaGdzUVB6ZkJaQkhoWjNZZ1pYR2NaOHN1S3Vwa3ZRSWJ3MFpoMmRIQmhEdTQ4QSUyRkdSZnN4NkV3QmViOEVCSTFucVkzTW5USFFicjA3ZnAlMkJiYU1jTU02R2ZtTXRyVUF6M3d3RGFNZHhyYSUyRmdkOCUyQlUzeXRmQU5WJTJGREolMkZtaVhzbkhtWXBNY0NJOVY3REZXRFdoQkdjbE1LSDViWU1SJTJCd0lpaGl4UzdCNHkwOHpac2VrVThyQmglMkZDako4aUVpWXZ5ZEFqRTdHUUI1VnlUU1lHQW1ERUFpV3E0b2Q3MVhUVCUyRlF1ZGtCeEpTaE9reERGNHg3bFRYSnV3JTJGVG91JTJGV2tFVEJUSG4lMkJEWUdpMWtBY1FsZjlYcjBNREhmY0ZVOTM2TXA3Z2JEUXJMNSUyRkZLMUg5UkVwdVBnRCUzQyUyRmRpYWdyYW0lM0UlM0MlMkZteGZpbGUlM0WU8fnmAAAgAElEQVR4nO3dfXgU5b038K8QAtWCBENIaJBILa+xQEVNIa2goNUDHrWWo/T0RUWRR6DUxqIFS1Qujkfg+Pa0eKxY2kPxIG2p8nCuviEc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" style="cursor:pointer;max-width:100%;" onclick="(function(img){if(img.wnd!=null&&!img.wnd.closed){img.wnd.focus();}else{var r=function(evt){if(evt.data=='ready'&&evt.source==img.wnd){img.wnd.postMessage(decodeURIComponent(img.getAttribute('src')),'*');window.removeEventListener('message',r);}};window.addEventListener('message',r);img.wnd=window.open('https://www.draw.io/?client=1&lightbox=1&edit=_blank');}})(this);"/>

# In[ ]:


def area(img):
    # binarized image as input
    return np.count_nonzero(img)

def perimeter(img):
    # edges of the image as input
    return np.count_nonzero(img)

def irregularity(area, perimeter):
    # area and perimeter of the image as input, also called compactness
    I = (4 * np.pi * area) / (perimeter ** 2)
    return I

def equiv_diam(area):
    # area of image as input
    ed = np.sqrt((4 * area) / np.pi)
    return ed

def get_hu_moments(contour):
    # hu moments except 3rd and 7th (5 values)
    M = cv2.moments(contour)
    hu = cv2.HuMoments(M).ravel().tolist()
    del hu[2]
    del hu[-1]
    log_hu = [-np.sign(a)*np.log10(np.abs(a)) for a in hu]
    return log_hu


# ### The image preprocessing and feature extraction pipeline

# In[ ]:


def extract_features(img):
    mean = img.mean()
    std_dev = img.std()
    
    # hist equalization
    equalized = cv2.equalizeHist(img)
    
    # sharpening
    hpf_kernel = np.full((3, 3), -1)
    hpf_kernel[1,1] = 9
    sharpened = cv2.filter2D(equalized, -1, hpf_kernel)
    
    # thresholding
    ret, binarized = cv2.threshold(cv2.GaussianBlur(sharpened,(7,7),0),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    # edge detection
    edges = skimage.filters.sobel(binarized)
    
    # moments from contours
    contours, hier = cv2.findContours((edges * 255).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    select_contour = sorted(contours, key=lambda x: x.shape[0], reverse=True)[0]
    
    # feature extraction
    ar = area(binarized)
    per = perimeter(edges)
    irreg = irregularity(ar, per)
    eq_diam = equiv_diam(ar)
    hu = get_hu_moments(select_contour)
    
    return (mean, std_dev, ar, per, irreg, eq_diam, *hu)


# In[ ]:


# test the function
extract_features(img)


# # Save generated features

# ## Load the required data
# We select only the normal and pneumonia images for model building

# In[ ]:


pneumonia_ids = train_labels_df[train_labels_df['Target'] == 1]['patientId'].unique()
pneumonia_labels = [1] * len(pneumonia_ids)

normal_ids = class_info_df[class_info_df['class'] == 'Normal']['patientId'].unique()
normal_labels = [0] * len(normal_ids)

data = dict()
data['patientId'] = np.concatenate((pneumonia_ids, normal_ids))
data['target'] = np.concatenate((pneumonia_labels, normal_labels))

print(f'Pneumonia images: {len(pneumonia_ids)}\nNormal images: {len(normal_ids)}')


# ## Generate features
# For each ID generate the features from the image and store it in the dataset

# In[ ]:


from tqdm import tqdm


# In[ ]:


features = []

for path in tqdm(data['patientId']):
    patientImage = path + '.dcm'
    imagePath = os.path.join(PATH,"stage_2_train_images/", patientImage)
    img = dcm.read_file(imagePath).pixel_array
    feats = extract_features(img)
    features.append(feats)

data['features'] = features


# In[ ]:


df = pd.DataFrame(data)
df.to_csv('img_features.csv')


# After the features are generated, they can be loaded and trained using machine learning models to perform classification. Results with different ML algorithms are presented in the the [2nd part of this notebook](https://www.kaggle.com/suryathiru/2-tradition-image-processing-model-training)