#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os

from os import makedirs
from os.path import join, exists, expanduser

cache_dir = expanduser(join('~', '.keras'))
if not exists(cache_dir):
    makedirs(cache_dir)
models_dir = join(cache_dir, 'models')
if not exists(models_dir):
    makedirs(models_dir)
    
get_ipython().system('cp ../input/keras-pretrained-models/*notop* ~/.keras/models/')
get_ipython().system('cp ../input/keras-pretrained-models/imagenet_class_index.json ~/.keras/models/')
get_ipython().system('cp ../input/keras-pretrained-models/resnet50* ~/.keras/models/')


# In[2]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt # showing and rendering figures
import seaborn as sns
plt.style.use('fivethirtyeight')
import warnings
warnings.filterwarnings('ignore')
import plotly
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.tools as tls
import plotly.graph_objs as go
import plotly.tools as tls
# io related
from skimage.io import imread
import os
from glob import glob
# not needed in Kaggle, but required in Jupyter
get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

train_data_dir = os.path.join('..', 'input/rsna-bone-age')
train_data = pd.read_csv(os.path.join(train_data_dir, 'boneage-training-dataset.csv'))

train_data['path'] = train_data['id'].map(lambda x: os.path.join(train_data_dir,
                                                         'boneage-training-dataset', 
                                                         'boneage-training-dataset', 
                                                         '{}.png'.format(x)))
train_data['exists'] = train_data['path'].map(os.path.exists)


# In[4]:


print(train_data['exists'].sum(), 'images found of', train_data.shape[0], 'total')


# In[5]:


train_data['gender'] = train_data['male'].map(lambda x: 'male' if x else 'female')
print(train_data.gender.value_counts())
train_data['gender'].value_counts().plot.barh(width=0.9)
plt.show()


# In[6]:


bone_age_mean = train_data['boneage'].mean()
bone_age_div = 2 * train_data['boneage'].std()
train_data['bone_age_zscore'] = train_data.boneage.map(lambda x: (x - bone_age_mean)/bone_age_div)
train_data.dropna(inplace = True)
train_data.head(5)


# In[10]:


plt.figure(figsize=(8,6))
train_data.boneage.hist(bins=10,edgecolor='black', linewidth=1.2)
plt.title('bone_age_distribution')
plt.show()


# In[9]:


plt.figure(figsize=(8,6))
train_data.bone_age_zscore.hist(bins=10, edgecolor='black', linewidth=1.2)
plt.title('bone_age_zscore')
plt.show()


# In[11]:


train_data['boneage_category'] = pd.cut(train_data['boneage'], 10)
train_df = train_data.groupby(['boneage_category', 'male']).apply(lambda x: x.sample(500, replace = True)
                                                      ).reset_index(drop = True)
print('New train shape:', train_df.shape[0], 'pre-train shape:', train_data.shape[0])
train_df[['boneage', 'male']].hist(bins=10, edgecolor='black', figsize=(10,5))
plt.show()


# In[12]:


from sklearn.model_selection import train_test_split
train_data['gender'] = train_data['male'].map(lambda x: 1 if x else 0)

df_train, df_valid = train_test_split(train_df, test_size = 0.15, random_state = 0,
                                   stratify = train_df['boneage_category'])

print('train', df_train.shape[0], 'validation', df_valid.shape[0])


# In[13]:


from keras.preprocessing.image import ImageDataGenerator
from keras.applications.resnet50 import preprocess_input

IMG_SIZE = (500, 500)

train_datagen = ImageDataGenerator(samplewise_center=False, 
                              samplewise_std_normalization=False, 
                              horizontal_flip = True, 
                              vertical_flip = False, 
                              height_shift_range = 0.2, 
                              width_shift_range = 0.2, 
                              rotation_range = 5, 
                              shear_range = 0.01,
                              fill_mode = 'nearest',
                              zoom_range=0.25,
                             preprocessing_function = preprocess_input)


# In[14]:


### Takes the path to a directory, and generates batches of augmented/normalized data.
def flow_from_dataframe(img_data_gen, in_df, path_col, y_col, **dflow_args):
    base_dir = os.path.dirname(in_df[path_col].values[0])
    print('## Ignore next message from keras, values are replaced anyways')
    df_gen = img_data_gen.flow_from_directory(base_dir, 
                                     class_mode = 'sparse',
                                    **dflow_args)
    df_gen.filenames = in_df[path_col].values
    df_gen.classes = np.stack(in_df[y_col].values)
    df_gen.samples = in_df.shape[0]
    df_gen.n = in_df.shape[0]
    df_gen._set_index_array()
    df_gen.directory = '' # since we have the full path
    print('Reinserting dataframe: {} images'.format(in_df.shape[0]))
    return df_gen


train_gen = flow_from_dataframe(train_datagen, df_train, 
                            path_col = 'path',
                            y_col = 'bone_age_zscore', 
                            target_size = IMG_SIZE,
                            color_mode = 'rgb',
                            batch_size = 32)

valid_gen = flow_from_dataframe(train_datagen, df_valid, 
                            path_col = 'path',
                            y_col = 'bone_age_zscore', 
                            target_size = IMG_SIZE,
                            color_mode = 'rgb',
                            batch_size = 256) # we can use much larger batches for evaluation

# used a fixed dataset for evaluating the algorithm
test_X, test_Y = next(flow_from_dataframe(train_datagen, 
                            df_valid, 
                            path_col = 'path',
                            y_col = 'bone_age_zscore', 
                            target_size = IMG_SIZE,
                            color_mode = 'rgb',
                            batch_size = 512)) # one big batch


# In[15]:


t_x, t_y = next(train_gen)
fig, m_axs = plt.subplots(2, 4, figsize = (16, 8))
for (c_x, c_y, c_ax) in zip(t_x, t_y, m_axs.flatten()):
    c_ax.imshow(c_x[:,:,0], cmap = 'bone', vmin = -127, vmax = 127)
    c_ax.set_title('%2.0f months' % (c_y*bone_age_div+bone_age_mean))
    c_ax.axis('off')


# In[16]:


import keras
from keras.metrics import mean_absolute_error

def mae_months(in_gt, in_pred):
    return mean_absolute_error(bone_age_div*in_gt, bone_age_div*in_pred)


# In[24]:


from keras.layers import GlobalAveragePooling2D, Dense, Dropout, Flatten, Input, Conv2D, multiply, LocallyConnected2D, Lambda, ActivityRegularization
from keras.layers import BatchNormalization
from keras.models import Model

def Resnet50_v2(use_imagenet=True):
    # load pre-trained model graph, don't add final layer
    input_layer = Input(t_x.shape[1:])
    model = keras.applications.ResNet50(include_top=False, input_shape = t_x.shape[1:] ,
                                          weights='imagenet' if use_imagenet else None)
    model.trainable = False
    pre_trained_depth = model.get_output_shape_at(0)[-1]
    pre_trained_features = model(input_layer)
    bn_features = BatchNormalization()(pre_trained_features)
    ##attention
    attention_layer = Conv2D(64, kernel_size = (1,1), padding = 'same', activation = 'relu')(bn_features)
    attention_layer = Conv2D(16, kernel_size = (1,1), padding = 'same', activation = 'relu')(attention_layer)
    attention_layer = Conv2D(1, 
                    kernel_size = (1,1), 
                    padding = 'valid', 
                    activation = 'sigmoid')(attention_layer)
    up_c2_w = np.ones((1, 1, 1, pre_trained_depth))
    up_c2 = Conv2D(pre_trained_depth, kernel_size = (1,1), padding = 'same', 
               activation = 'linear', use_bias = False, weights = [up_c2_w])
    
    up_c2.trainable = False
    attention_layer = up_c2(attention_layer)
    
    mask_features = multiply([attention_layer, bn_features])
    gap_features = GlobalAveragePooling2D()(mask_features)
    gap_mask = GlobalAveragePooling2D()(attention_layer)
    
    
    gap = Lambda(lambda x: x[0]/x[1], name = 'RescaleGAP')([gap_features, gap_mask])
    gap_dr = Dropout(0.5)(gap)
    
    dr_steps = Dropout(0.25)(Dense(512, activation = 'elu')(gap_dr))
    
    
    out_layer = Dense(1, activation = 'linear')(dr_steps) 

    model = Model(inputs = [input_layer], outputs = [out_layer])
    return model


# In[25]:


import keras
model = Resnet50_v2()


# In[26]:


model.summary()


# In[28]:


print(len(model.layers))


# In[29]:


model.compile(optimizer = 'adam', loss = 'mse',
                           metrics = [mae_months])


# In[31]:


from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping, ReduceLROnPlateau
weight_path="{}resnet50v2_weights.best.hdf5".format('bone_age')

checkpoint = ModelCheckpoint(weight_path, monitor='val_loss', verbose=1, 
                             save_best_only=True, mode='min', save_weights_only = True)


reduceLROnPlat = ReduceLROnPlateau(monitor='val_loss', factor=0.8, patience=10, verbose=1, mode='auto', epsilon=0.0001, cooldown=5, min_lr=0.0001)

early = EarlyStopping(monitor="val_loss", 
                      mode="min", 
                      patience=5) 

callbacks_list = [checkpoint, early, reduceLROnPlat]


# In[ ]:


model.fit_generator(train_gen, 
                                  validation_data = (test_X, test_Y), 
                                  epochs = 15, 
                                  callbacks = callbacks_list,
                                   
                                )


# In[ ]:


model.load_weights(weight_path)


# In[ ]:


pred_Y = bone_age_div*model.predict(test_X, batch_size = 32, verbose = True)+bone_age_mean
test_Y_months = bone_age_div*test_Y+bone_age_mean


# In[ ]:


ord_idx = np.argsort(test_Y)
ord_idx = ord_idx[np.linspace(0, len(ord_idx)-1, 8).astype(int)] # take 8 evenly spaced ones
fig, m_axs = plt.subplots(4, 2, figsize = (16, 32))
for (idx, c_ax) in zip(ord_idx, m_axs.flatten()):
    c_ax.imshow(test_X[idx, :,:,0], cmap = 'bone')
    
    c_ax.set_title('Age: %2.1fY\nPredicted Age: %2.1fY' % (test_Y_months[idx]/12.0, 
                                                           pred_Y[idx]/12.0))
    c_ax.axis('off')
fig.savefig('trained_img_predictions.png', dpi = 300)


# In[ ]:


from sklearn.metrics import mean_absolute_error, median_absolute_error
print(mean_absolute_error(pred_Y, test_Y_months))
print(median_absolute_error(pred_Y, test_Y_months))


# In[ ]:


fig, ax1 = plt.subplots(1,1, figsize = (6,6))
ax1.plot(test_Y_months, pred_Y, 'r.', label = 'predictions')
ax1.plot(test_Y_months, test_Y_months, 'b-', label = 'actual')
ax1.legend()
ax1.('Actual value (months)')
ax1.set_ylabel('Predicted value (months)')


# In[ ]:


pred_Y.to_csv('preds_resnet50.csv', index = False)
test_Y_months.to_csv('actual_value_rs50.csv', index = False)
