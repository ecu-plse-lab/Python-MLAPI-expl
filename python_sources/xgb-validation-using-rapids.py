#!/usr/bin/env python
# coding: utf-8

# ![](data:image/png;base64,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)

# # Environment

# In[ ]:


import sys
get_ipython().system('cp ../input/rapids/rapids.0.13.0 /opt/conda/envs/rapids.tar.gz')
get_ipython().system('cd /opt/conda/envs/ && tar -xzvf rapids.tar.gz > /dev/null')
sys.path = ["/opt/conda/envs/rapids/lib/python3.6/site-packages"] + sys.path
sys.path = ["/opt/conda/envs/rapids/lib/python3.6"] + sys.path
sys.path = ["/opt/conda/envs/rapids/lib"] + sys.path
get_ipython().system('cp /opt/conda/envs/rapids/lib/libxgboost.so /opt/conda/lib/')


# # Imports

# In[ ]:


import gc
import cudf
import pynvml
import numpy as np
import pandas as pd
import xgboost as xgb
from math import sqrt
from sklearn.model_selection import KFold, StratifiedKFold, GroupKFold
from sklearn.metrics import mean_squared_error,f1_score, accuracy_score


# # Reading (not using pandas)

# In[ ]:


train = cudf.read_csv('../input/ion-switch-model-ready-data-frame-to-work-locally/train_ion_switch.csv')
test  = cudf.read_csv('../input/ion-switch-model-ready-data-frame-to-work-locally/test_ion_switch.csv')


# # preparing train / test / target

# In[ ]:


y     = train['open_channels']
train = train.drop(['open_channels'],axis=1)

train = train.drop('time', axis = 1)
test  = test.drop( 'time', axis = 1)


# # train-test split (again not pandas)

# In[ ]:


from cuml import train_test_split

X_train, X_test, y_train, y_test = train_test_split(train, y, test_size=0.2, random_state=123)


# # Train

# In[ ]:


dtrain = xgb.DMatrix(X_train,y_train)
dval   = xgb.DMatrix(X_test, y_test)
dtest  = xgb.DMatrix(test)

evallist = [(dval, 'validation'), (dtrain, 'train')]
num_round=2500


# In[ ]:


trained_model = xgb.train(
                        {
                          'learning_rate': 0.01,
                          'colsample_bytree' : 0.25,
                          'max_depth': 10,
                          'objective': 'reg:squarederror',
                          'silent': True,
                          'tree_method':'gpu_hist',
                        },
                        dtrain,num_round, evallist,verbose_eval=100)


# # Predict

# In[ ]:


prediction = trained_model.predict(dtest)


# # Submission

# In[ ]:


sub = pd.read_csv("../input/liverpool-ion-switching/sample_submission.csv")

submission = pd.DataFrame()
submission['time']  = sub['time']
submission['open_channels'] = prediction
submission['open_channels'] = submission['open_channels'].round(decimals=0)
submission['open_channels'] = submission['open_channels'].astype(int)
submission.to_csv('submission.csv', float_format='%0.4f', index = False)


# In[ ]:


submission.tail()
