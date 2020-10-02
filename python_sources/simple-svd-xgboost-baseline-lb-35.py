#!/usr/bin/env python
# coding: utf-8

# We aim to use svd to dimensionally reduce the images to just a few features (20 per image in this particular case), which works nicely as it turns out most of variance in the image is just noise. LB should be aroun ~0.35, but I've played a bit with xgb parameters and the crossvalidation improved, this suggest that perhaps you can get lower LB if you submit this notebook. 

# In[ ]:


#load with pandas, manipulate with numpy, plot with matplotlib
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

#ML - we will classify using a naive xgb with stratified cross validation
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import log_loss




# In[ ]:


#filenames
inputFolder = "../input/"
trainSet = 'train.json'
testSet = 'test.json'
subName = 'iceberg-svd-xgb-3fold.csv'


# In[ ]:


#load data
trainDF = pd.read_json(inputFolder+trainSet)
testDF = pd.read_json(inputFolder+testSet)


# In[ ]:


#get numpy arrays for train/test data, prob there is a more pythonic approach
band1 = trainDF['band_1'].values
im1 = np.zeros((len(band1),len(band1[0])))
for j in range(len(band1)):
    im1[j,:]=np.asarray(band1[j])
    
band2 = trainDF['band_2'].values
im2 = np.zeros((len(band2),len(band2[0])))
for j in range(len(band2)):
    im2[j,:]=np.asarray(band2[j])
    
#get numpy array for test data
band1test = testDF['band_1'].values
im1test = np.zeros((len(band1test),len(band1test[0])))
for j in range(len(band1test)):
    im1test[j,:]=np.asarray(band1test[j])
    
band2test = testDF['band_2'].values
im2test = np.zeros((len(band2test),len(band2test[0])))
for j in range(len(band2test)):
    im2test[j,:]=np.asarray(band2test[j])


# In[ ]:


#svd of the two bands
U1,s1,V1 = np.linalg.svd(im1,full_matrices = 0)
U2,s2,V2 = np.linalg.svd(im2,full_matrices = 0)


# In[ ]:


#fraction of variance explained in the first 100 modes of train data.
#note band 2 is somehow much more dependent on the first svd mode than band 1

plt.figure()

frac1 = np.cumsum(s1)/np.sum(s1)
frac2 = np.cumsum(s2)/np.sum(s2)

plt.plot(frac1[:100])
plt.plot(frac2[:100],'r')


# In[ ]:


#original 

fig, ax = plt.subplots(2,3)
plt.suptitle('original')
ax[0,0].imshow(np.reshape(im2[0,:],(75,75)))

ax[0,1].imshow(np.reshape(im2[1,:],(75,75)))
ax[0,2].imshow(np.reshape(im2[2,:],(75,75)))
ax[1,0].imshow(np.reshape(im2[3,:],(75,75)))
ax[1,1].imshow(np.reshape(im2[4,:],(75,75)))
ax[1,2].imshow(np.reshape(im2[5,:],(75,75)))

#first 100 modes (only 1/16th total modes, ~35% of variance)

nmodes = 100

im1p=np.dot(np.dot(U1[:,:nmodes],np.diag(s1[:nmodes])),V1[:nmodes,])
im2p=np.dot(np.dot(U2[:,:nmodes],np.diag(s2[:nmodes])),V2[:nmodes,])

fig, ax = plt.subplots(2,3)
plt.suptitle('first 100 modes')
ax[0,0].imshow(np.reshape(im2p[0,:],(75,75)))

ax[0,1].imshow(np.reshape(im2p[1,:],(75,75)))
ax[0,2].imshow(np.reshape(im2p[2,:],(75,75)))
ax[1,0].imshow(np.reshape(im2p[3,:],(75,75)))
ax[1,1].imshow(np.reshape(im2p[4,:],(75,75)))
ax[1,2].imshow(np.reshape(im2p[5,:],(75,75)))

#first 20 modes (~27% of variance explained)

nmodes = 20

im1p=np.dot(np.dot(U1[:,:nmodes],np.diag(s1[:nmodes])),V1[:nmodes,])
im2p=np.dot(np.dot(U2[:,:nmodes],np.diag(s2[:nmodes])),V2[:nmodes,])

fig, ax = plt.subplots(2,3)

plt.suptitle('first 20 modes')
ax[0,0].imshow(np.reshape(im2p[0,:],(75,75)))

ax[0,1].imshow(np.reshape(im2p[1,:],(75,75)))
ax[0,2].imshow(np.reshape(im2p[2,:],(75,75)))
ax[1,0].imshow(np.reshape(im2p[3,:],(75,75)))
ax[1,1].imshow(np.reshape(im2p[4,:],(75,75)))
ax[1,2].imshow(np.reshape(im2p[5,:],(75,75)))


# In[ ]:


# OK, so first 20 modes (20 numbers per image) have most of useful information, 
# as most of variance is just noise. Let's run a simple xgboost classifier

#transofrm test data
U1test=np.dot(np.dot(im1test,V1.T),np.diag(1/s1))
U2test=np.dot(np.dot(im2test,V2.T),np.diag(1/s2))

nmodes = 20

X = np.hstack((U1[:,:nmodes],U2[:,:nmodes]))
X_test = np.hstack((U1test[:,:nmodes],U2test[:,:nmodes]))
y = trainDF['is_iceberg'].values


# In[ ]:


#is there a native xgb way of doing it?
def logloss_xgb(preds, dtrain):
    labels = dtrain.get_label()
    score = log_loss(labels, preds)
    return 'logloss', score


# In[ ]:


nfolds = 3;
xgb_mdl=[None]*nfolds


xgb_params = {
        'objective': 'binary:logistic',
        'n_estimators':1000,
        'max_depth': 8,
        'subsample': 0.9,
        'colsample_bytree': 0.9 ,
     #   'max_delta_step': 1,
     #   'min_child_weight': 10,
        'eta': 0.01,
      #  'gamma': 0.5
        }


folds = list(StratifiedKFold(n_splits=nfolds, shuffle=True, random_state=2016).split(X, y))

d_test = xgb.DMatrix(X_test)

preds = np.zeros((X_test.shape[0],nfolds))

for j, (train_idx, valid_idx) in enumerate(folds):
    X_train = X[train_idx]
    y_train = y[train_idx]
    
    X_valid = X[valid_idx]
    y_valid = y[valid_idx]
    
    d_train =  xgb.DMatrix(X_train,label=y_train)
    d_valid =  xgb.DMatrix(X_valid,label=y_valid)
    
    watchlist = [(d_train, 'train'), (d_valid, 'valid')]
    
    xgb_mdl[j]=xgb.train(
            xgb_params, 
            d_train, 
            1600, watchlist, 
            early_stopping_rounds=70, 
            feval=logloss_xgb, 
            maximize=False, 
            verbose_eval=100)
    preds[:,j] = xgb_mdl[j].predict(d_test)


# In[ ]:


y_pred = np.mean(preds,axis=1)
sub = pd.DataFrame()
sub['id'] = testDF['id']
sub['is_iceberg'] = y_pred
sub.to_csv(subName, index=False)
