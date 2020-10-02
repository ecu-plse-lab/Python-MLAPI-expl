#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from tqdm import tqdm, tqdm_notebook

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
print(os.listdir("../input"))
import gc


# Any results you write to the current directory are saved as output.
import tensorflow as tf
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from keras import layers
from keras import backend as K
from keras import regularizers
from keras.constraints import max_norm
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping, ReduceLROnPlateau
from keras.models import load_model
from keras.models import Model
from keras.initializers import glorot_uniform
from keras.layers import Input,Dense,Activation,ZeroPadding2D,BatchNormalization,Flatten,Conv2D,AveragePooling2D,MaxPooling2D,Dropout,concatenate
from sklearn import preprocessing

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
#from sklearn.metrics import auc
from sklearn.metrics import roc_auc_score

import warnings
warnings.filterwarnings("ignore")


# In[ ]:


# define helper functions. auc, plot_history
def auc(y_true, y_pred):
    #auc = tf.metrics.auc(y_true, y_pred)[1]
    y_pred = y_pred.ravel()
    y_true = y_true.ravel()
    return roc_auc_score(y_true, y_pred)

def auc_2(y_true, y_pred):
    return tf.py_func(roc_auc_score, (y_true, y_pred), tf.double)

def plot_history(histories, key='binary_crossentropy'):
    plt.figure(figsize=(16,10))
    #plt.plot([0, 1], [0, 1], 'k--')
    for name, history in histories:
        val = plt.plot(history.epoch, history.history['val_'+key], '--', label=name.title()+' Val')

    plt.plot(history.epoch, history.history[key], color=val[0].get_color(), label=name.title()+' Train')

    plt.xlabel('Epochs')
    plt.ylabel(key.replace('_',' ').title())
    plt.legend()

    plt.xlim([0,max(history.epoch)])
    plt.ylim([0, 0.4])
    plt.show()


# In[ ]:


def shuffle_col_vals_fix(x1, groups):
    group_size = x1.shape[1]//groups
    xs = [x1[:, i*group_size:(i+1)*group_size] for i in range(groups)]
    rand_x = np.array([np.random.choice(x1.shape[0], size=x1.shape[0], replace=False) for i in range(group_size)]).T
    grid = np.indices(xs[0].shape)
    rand_y = grid[1]
    res = [x[(rand_x, rand_y)] for x in xs]
    return np.hstack(res)

def augment_fix_fast(x,y,groups,t1=2, t0=2):
    # In order to make the sync version augment work, the df should be the form of:
    # var_1, var_2, var_3 | var_1_count, var_2_count, var_3_count | var_1_rolling, var_2_rolling, var_3_rolling
    # for the example above, 3 groups of feature, groups = 3
    xs,xn = [],[]
    for i in range(t1):
        mask = y>0
        x1 = x[mask].copy()
        x1 = shuffle_col_vals_fix(x1, groups)
        xs.append(x1)

    for i in range(t0):
        mask = (y==0)
        x1 = x[mask].copy()
        x1 = shuffle_col_vals_fix(x1, groups)
        xn.append(x1)

    xs = np.vstack(xs); xn = np.vstack(xn)
    ys = np.ones(xs.shape[0]);yn = np.zeros(xn.shape[0])
    x = np.vstack([x,xs,xn]); y = np.concatenate([y,ys,yn])
    return x,y


# In[ ]:


# load data 
train_df = pd.read_csv('../input/train.csv')
test_df =  pd.read_csv("../input/test.csv")
base_features = [x for x in train_df.columns.values.tolist() if x.startswith('var_')]


# In[ ]:


# mark real vs fake
train_df['real'] = 1

for col in base_features:
    test_df[col] = test_df[col].map(test_df[col].value_counts())
a = test_df[base_features].min(axis=1)

test_df = pd.read_csv('../input/test.csv')
test_df['real'] = (a == 1).astype('int')

train = train_df.append(test_df).reset_index(drop=True)
del test_df, train_df; gc.collect()


# In[ ]:


# count features
for col in tqdm(base_features):
    train[col + 'size'] = train[col].map(train.loc[train.real==1, col].value_counts())
cnt_features = [col + 'size' for col in base_features]


# In[ ]:


# magice features 1
for col in tqdm(base_features):
#        train[col+'size'] = train.groupby(col)['target'].transform('size')
    train.loc[train[col+'size']>1,col+'no_noise'] = train.loc[train[col+'size']>1,col]
noise1_features = [col + 'no_noise' for col in base_features]


# In[ ]:


# fill NA as mean, inspired by lightgbm
train[noise1_features] = train[noise1_features].fillna(train[noise1_features].mean())


# In[ ]:


# magice features 2
for col in tqdm(base_features):
#        train[col+'size'] = train.groupby(col)['target'].transform('size')
    train.loc[train[col+'size']>2,col+'no_noise2'] = train.loc[train[col+'size']>2,col]
noise2_features = [col + 'no_noise2' for col in base_features]


# In[ ]:


# fill NA as mean
train[noise2_features] = train[noise2_features].fillna(train[noise2_features].mean())


# In[ ]:


train_df = train[train['target'].notnull()]
test_df = train[train['target'].isnull()]
all_features = base_features + noise1_features + noise2_features
cols_info = [base_features, noise1_features, noise2_features]


# In[ ]:


train.to_csv('train_all.csv', index=None)


# In[ ]:


scaler = preprocessing.StandardScaler().fit(train_df[all_features].values)
df_trn = pd.DataFrame(scaler.transform(train_df[all_features].values), columns=all_features)
df_tst = pd.DataFrame(scaler.transform(test_df[all_features].values), columns=all_features)
y = train_df['target'].values


# In[ ]:


def get_keras_data(dataset, cols_info):
    X = {}
    base_feats, noise_feats, noise2_feats = cols_info
    X['base'] = np.reshape(np.array(dataset[base_feats].values), (-1, len(base_feats), 1))
    X['noise1'] = np.reshape(np.array(dataset[noise_feats].values), (-1, len(noise_feats), 1))
    X['noise2'] = np.reshape(np.array(dataset[noise2_feats].values), (-1, len(noise2_feats), 1))
    return X


# In[ ]:


#X = get_keras_data(df_trn[all_features], cols_info)
X_test = get_keras_data(df_tst[all_features], cols_info)


# In[ ]:


# define network structure -> 2D CNN
def Convnet(cols_info, classes=1):
    base_feats, noise1_feats, noise2_feats = cols_info
    
    # base_feats
    X_base_input = Input(shape=(len(base_feats), 1), name='base')
    X_base = Dense(16)(X_base_input)
    X_base = Activation('relu')(X_base)
    X_base = Flatten(name='base_last')(X_base)
    
    # noise1
    X_noise1_input = Input(shape=(len(noise1_feats), 1), name='noise1')
    X_noise1 = Dense(16)(X_noise1_input)
    X_noise1 = Activation('relu')(X_noise1)
    X_noise1 = Flatten(name='nose1_last')(X_noise1)

    # noise2
    X_noise2_input = Input(shape=(len(noise2_feats), 1), name='noise2')
    X_noise2 = Dense(16)(X_noise2_input)
    X_noise2 = Activation('relu')(X_noise2)
    X_noise2 = Flatten(name='nose2_last')(X_noise2)    
    
    X = concatenate([X_base, X_noise1, X_noise2])
    X = Dense(classes, activation='sigmoid')(X)
    
    model = Model(inputs=[X_base_input, X_noise1_input, X_noise2_input],outputs=X)
    
    return model
model = Convnet(cols_info)
model.summary()


# In[22]:


try:
    del train, df_tst
except:
    pass
gc.collect()


# In[28]:


# parameters
SEED = 2019
n_folds = 5
debug_flag = True
folds = 5
skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=SEED)


# In[29]:


#transformed_shape = tuple([-1] + list(shape))
#X_test = np.reshape(X_test, transformed_shape)

i = 0
result = pd.DataFrame({"ID_code": test_df.ID_code.values})
val_aucs = []
valid_X = train_df[['target']]
valid_X['predict'] = 0
for train_idx, val_idx in skf.split(df_trn, y):
    if i == folds:
        break
    i += 1    
    X_train, y_train = df_trn.iloc[train_idx], y[train_idx]
    X_valid, y_valid = df_trn.iloc[val_idx], y[val_idx]
    
    #aug
    X_train, y_train = augment_fix_fast(X_train.values, y_train, groups=3, t1=2, t0=2)
    X_train = pd.DataFrame(X_train, columns=all_features)
    
    X_train = get_keras_data(X_train, cols_info)
    X_valid = get_keras_data(X_valid, cols_info)
    #X_train = np.reshape(X_train, transformed_shape)
    #X_valid = np.reshape(X_valid, transformed_shape)
    
    model_name = 'NN_fold{}.h5'.format(str(i))
    
    model = Convnet(cols_info)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'binary_crossentropy', auc_2])
    checkpoint = ModelCheckpoint(model_name, monitor='val_auc_2', verbose=1, 
                                 save_best_only=True, mode='max', save_weights_only = True)
    reduceLROnPlat = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, 
                                       verbose=1, mode='min', epsilon=0.0001)
    earlystop = EarlyStopping(monitor='val_auc_2', mode='max', patience=10, verbose=1)
    history = model.fit(X_train, y_train, 
                        epochs=300, 
                        batch_size=1024 * 2, 
                        validation_data=(X_valid, y_valid), 
                        callbacks=[checkpoint, reduceLROnPlat, earlystop])
    #train_history = pd.DataFrame(history.history)
    #train_history.to_csv('train_profile_fold{}.csv'.format(str(i)), index=None)
    del X_train
    gc.collect()
    
    # load and predict
    model.load_weights(model_name)
    
    #predict
    y_pred_keras = model.predict(X_valid).ravel()
    
    # AUC
    valid_X['predict'].iloc[val_idx] = y_pred_keras
    
    fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_valid, y_pred_keras)
    auc_valid = roc_auc_score(y_valid, y_pred_keras)
    val_aucs.append(auc_valid)
    
    prediction = model.predict(X_test)
    result["fold{}".format(str(i))] = prediction


# In[ ]:


for i in range(len(val_aucs)):
    print('Fold_%d AUC: %.6f' % (i+1, val_aucs[i]))


# In[ ]:


# summary on results
auc_mean = np.mean(val_aucs)
auc_std = np.std(val_aucs)
auc_all = roc_auc_score(valid_X.target, valid_X.predict)
print('%d-fold auc mean: %.9f, std: %.9f. All auc: %6f.' % (n_folds, auc_mean, auc_std, auc_all))


# In[ ]:


y_all = result.values[:, 1:]
result['target'] = np.mean(y_all, axis = 1)
to_submit = result[['ID_code', 'target']]
to_submit.to_csv('NN_submission.csv', index=None)
result.to_csv('NN_all_prediction.csv', index=None)
valid_X['ID_code'] = train_df['ID_code']
valid_X = valid_X[['ID_code', 'target', 'predict']].to_csv('NN_oof.csv', index=None)


# In[ ]:



