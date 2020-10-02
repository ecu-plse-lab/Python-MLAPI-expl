#!/usr/bin/env python
# coding: utf-8

# # Goal
# The goal is to make a simple model that can go from an image (taken with a smartphone) to a prediction of which skin-lesion it is most likely to be (the training data is only made up of skin lesions)
# 
# ## Setup
# We basically take the precomputed color features and build simple linear models in order to determine which lesion type it might be

# In[ ]:


import warnings # tf needs to learn to stfu
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('retina')
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams["figure.figsize"] = (5, 5)
plt.rcParams["figure.dpi"] = 125
plt.rcParams["font.size"] = 14
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.style.use('ggplot')
sns.set_style("whitegrid", {'axes.grid': False})
plt.rcParams['image.cmap'] = 'gray' # grayscale looks better


# In[ ]:


from pathlib import Path
import numpy as np
import pandas as pd
import os
from skimage.io import imread as imread
from skimage.util import montage
from PIL import Image
montage_rgb = lambda x: np.stack([montage(x[:, :, :, i]) for i in range(x.shape[3])], -1)
from skimage.color import label2rgb


# In[ ]:


# a list of all the colors in the web palette 
web_color_list = np.array(Image.new(size=(1,1), mode='RGB').convert('P', palette='web').getpalette()).reshape((-1, 3))


# In[ ]:


# a list of all the color names
import zlib
web_color_names = zlib.decompress(b'x\x9c\xbd\x96\xed\x92\xab \x0c\x86o\xc8\x9b\x8a\x92*[$.`;\xde\xfd\x02\x01\xf9\xa8\xee\xf9\xb13\xe7GC\xd2\xe6\r\xe6\t8\x1d\x15L\xcfa\xfc\xb3]\xc1\x10\xe9A\x80y\x1a\x14C\xfe\x84x6\x88\xba\xf2,\x08\xa1p4\xf4n\xfd\x874\xde\x93\xbe\x18\x19\xd03\xde\xe9I\xc9\x17&;-4\x91\x02\x87\x95\x86\xb3\x1ed\xd0\xbaOE\xacCJ\xa06$\x92jPre\xc3\xf9\n\xde\x9a\xbd\x03\x95\xa27\xfbA\xc5\xe6L\xaf2\xa7\x05\x8c3\xb8[L\xa2\xbc$>Rh9/nT;fX\xdc\xf6d\xe4j\xa9\xac\xe1\x01mh\xc9\xd7=\xba\xa8\xc6\xd5C\xab\xf5\x05Yl\xfa2\xb4\x12\xb5\x86\x8a\xa0\xa3\x15\x1c5\xe0> \n\x03c\xe5mh\xf6a\xf2\x10UM\xef\xf4jz=I\xe6\xdf\xe2\xec\xe9G\x9b0\xd6~Z4\xbc\x8eAj!g\x1a\xb6\xddl\n\xf3\xb2\xa2\x90\xfb\xfa\x92\xa4\xd0\xc5c\x84\xb8mRwc\xb8!\x1d\x7fc\xba\xa18\xe8\xa6\x82C\xdfl\xa7\x94k\\\xa3)\x12\x0bj\xf5\xf3\x88\x02\x8bp\xb6\x94\x12C\x8d\xe7\x02O\xe9\x13\xb58\xd2}\xd8\x8c\xd43\xa7r\x13\xa7\xb2\x0b\x8b\xfc\x9f\x85j_\x85\xee?\\\x96\x97r\x11A"\x9b\x96\xf0\xf5\n3j\x07\xf7xOm\x0b\xf33"3-R\xdc\x17bh\x0eQEIa\x1d\xcd\x06\n\x8bh!wn>\x1d\x90\x1a;AM \xb0\xcc;\xea\r\xd9\x84\x89SyP\xad\xac\x8d\xf8A\xe1{\x07\x7fw\xa5N-\xe5_\x9d\xdf\xd4\x1fF\xf8\xa2\xf7"]>~\x17\xb3\xbc\x1eDh\xa7\xf2\xce\xcb\xc1\xf3`)\xbf7\x8a\x1b\xf6g\x047n;\xab\xa81t@\xc5\xf3z\x18)\xc8P\x8b\xe6J\xcd\x92t\xe9:e\x0b\xb0\xcc\xd2\xbf.\xf4\xc3__4\xedP6\xb5\xaf,:\xa7\xe9v\xf3\xbd\x93\xb4y\xa3\xfb\x987;\xf7\xc8p}\xd5\xcfZ\xc5\xab\xe6Y\xb93HmG24(\xf4\xe7\xc27\xf5x\x84\xb7u|-d\xf3\x0b\xf0\xb4v\xd0*Q\xe56\xcc\xb3R\x90\x98\x13\x9d\xa2O\'\xa8C_\xe2T#?W)Q\xb9\x1d\xfafz\x11\x7fV\xfbkh\x9f\x07\xcb+\x9f)_\x06\xf0B-\xd0\x14\'\xde\xc4h*\xb4\xe1|wC\x8b)|m\xfe\xfe/\xe4\xbf\xdb\x1f_\xd2\x9b\x15')
web_color_names = np.array(web_color_names.decode().split(','))


# In[ ]:


dx_name_dict = {
    'nv': 'melanocytic nevi',
    'mel': 'melanoma',
    'bcc': 'basal cell carcinoma',
    'akiec': 'Actinic keratoses and intraepithelial carcinoma',
    'vasc': 'vascular lesions',
    'bkl': 'benign keratosis-like',
    'df': 'dermatofibroma'
}

dx_name_id_dict = {id: name for id, name in enumerate(dx_name_dict.values())}
dx_name_vec = np.array([dx_name_id_dict[k] for k in sorted(dx_name_id_dict.keys())])


# ## Read in the Color Features

# In[ ]:


from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(sparse=False, categories="auto")

color_file = Path('..') / 'input' /  'skin-images-to-features' / 'color_features.json'
color_feat_df = pd.read_json(color_file).reset_index(drop=True)
color_feat_df['dx_vec'] = [x for x in ohe.fit_transform(color_feat_df['dx_id'].values.reshape(-1, 1))]
color_feat_df.sample(2)


# In[ ]:


x_vec = np.stack(color_feat_df['color_features'].values, 0)
y_vec = np.stack(color_feat_df['dx_vec'].values, 0)
print(x_vec.shape, y_vec.shape)


# ## Examine the Correlation 
# $$  \rho_{X,Y}=\frac{\operatorname{E}[(X-\mu_X)(Y-\mu_Y)]}{\sigma_X\sigma_Y} $$

# In[ ]:


full_xy_corr = np.corrcoef(np.concatenate([x_vec, y_vec], 1).T)
yx_corr = full_xy_corr[:-y_vec.shape[1], -y_vec.shape[1]:].T
fig, ax1 = plt.subplots(1, 1, figsize=(30, 6))
sns.heatmap(yx_corr, 
            vmin=-1, 
            vmax=1, 
            cmap='RdBu', 
            ax=ax1, 
            xticklabels=web_color_names,
            yticklabels=dx_name_vec
           )
ax1.set_aspect(5)
ax1.set_xlabel('Colors')
ax1.set_ylabel('Diseases');


# ### Just keep the 10 most important colors
# Here we trim down the list of colors to the 10 most important. We can then see that the 10 most important colors are 

# In[ ]:


most_imp_vars = np.argsort(-(np.nanmax(yx_corr, 0)-np.nanmin(yx_corr, 0)))[:10]
fig, ax1 = plt.subplots(1, 1, figsize=(20, 4))
sns.heatmap(yx_corr[:, most_imp_vars], 
            vmin=-1, 
            vmax=1, 
            cmap='RdBu',
            annot=True,
            fmt='2.0%',
            xticklabels=web_color_names[most_imp_vars],
            yticklabels=dx_name_vec,
            ax=ax1)
ax1.set_aspect(1)
ax1.set_xlabel('Colors')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_ylabel('Diseases');


# # Setup our Problem
# So here we can setup our problem which is classifying melanocytic nevi from benign kerastosis-like lesions. So we define 
# - $y=1$ as positive for melanocytic nevi
# - $y=0$ for neither
# - $y=-1$ for positive for benign kerastosis-like

# In[ ]:


def dx_to_y(in_dx_name):
    if in_dx_name=='melanocytic nevi':
        return 1
    elif in_dx_name=='benign keratosis-like':
        return -1
    else:
        return 0


# In[ ]:


simple_y_vec = color_feat_df['dx_name'].map(dx_to_y)
simple_y_vec.hist()


# ## X / Independent Variable
# We can now use one (or more) of the colors as the independent variable. In this case we just use gray

# In[ ]:


simple_x_vec = x_vec[:, most_imp_vars[0]]
plt.hist(simple_x_vec)


# In[ ]:


plt.plot(simple_x_vec, simple_y_vec, '.')


# In[ ]:


fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))
#
sns.violinplot(x=simple_x_vec, y=simple_y_vec, orient='h', ax=ax1)
sns.stripplot(x=simple_x_vec, y=simple_y_vec, orient='h', ax=ax1, alpha=0.25)

ax1.set_xlim(0, 0.25)
ax1.set_xlabel('Grayness')
ax1.set_ylabel('Disease')


# In[ ]:


from sklearn.linear_model import LinearRegression
simple_lin_reg = LinearRegression()


# In[ ]:


simple_lin_reg.fit(simple_x_vec.reshape((-1, 1)), simple_y_vec)
simple_lin_reg.coef_, simple_lin_reg.intercept_


# In[ ]:


pred_disease = simple_lin_reg.coef_*simple_x_vec+simple_lin_reg.intercept_
fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))
ax1.plot(simple_x_vec, simple_y_vec+0.1*np.random.uniform(-1, 1, size=simple_y_vec.shape[0]), '.', label='In Data')
ax1.plot(simple_x_vec, pred_disease, '-', label='Fit Model')
ax1.legend()


# ## Looking at Various Images
# We can now look at what goes into the model and sort the images by grayness

# In[ ]:


N_PANELS = 10
gray_order = np.argsort(simple_x_vec)
fig, m_axs = plt.subplots(1, N_PANELS, figsize=(30, 5))

for c_ax, c_idx in zip(m_axs, 
                       np.linspace(0, simple_x_vec.shape[0]-1, N_PANELS).astype(int)):
    c_row = color_feat_df.iloc[gray_order[c_idx]]
    c_img = imread(c_row['image_path'])
    c_ax.imshow(c_img)
    c_ax.set_title('{dx_name}\n{localization}'.format(**c_row))
    c_ax.axis('off')


# ## Sort by top colors
# We can also sort by the other top colors

# In[ ]:


from skimage.color import label2rgb
N_PANELS = 4
fig, m_axs = plt.subplots(8, 1+N_PANELS, figsize=(20, 30))
for i, n_axs in enumerate(m_axs):
    c_color = most_imp_vars[i]
    c_x_vec = x_vec[:, c_color]
    
    color_order = np.argsort(c_x_vec)
    solid_img = np.tile(web_color_list[c_color].reshape((1, 1, 3)), (10, 10, 1)).astype('uint8')
    n_axs[0].imshow(solid_img)
    n_axs[0].axis('off')
    n_axs[0].set_title(web_color_names[c_color])
    
    for c_ax, c_idx in zip(n_axs[1:], 
                           np.linspace(0, simple_x_vec.shape[0]-1, N_PANELS).astype(int)):
        c_row = color_feat_df.iloc[color_order[c_idx]]
        c_img = Image.open(c_row['image_path'])
        c_img_arr = np.array(c_img)
        mask_img = np.array(c_img.convert('P', palette='web'))==most_imp_vars[i]
        new_color_img = label2rgb(label=mask_img, image=c_img_arr, bg_label=0)
        new_color_img = np.clip(new_color_img*255, 0, 255).astype('uint8')
        c_ax.imshow(np.concatenate([c_img_arr, new_color_img], 0))
        c_ax.set_title('{dx_name}\n{localization}'.format(**c_row))
        c_ax.axis('off')


# In[ ]:



