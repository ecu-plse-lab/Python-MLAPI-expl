#!/usr/bin/env python
# coding: utf-8

# Thise code is a slightly updated version of xhululu's kernel. Enjoy!
# > Xhulu's kernel: https://www.kaggle.com/xhlulu/ieee-fraud-xgboost-with-gpu-fit-in-40s

# In[ ]:


import os

import numpy as np
import pandas as pd
from sklearn import preprocessing
import xgboost as xgb


# In[ ]:


get_ipython().run_cell_magic('time', '', "train_transaction = pd.read_csv('../input/train_transaction.csv', index_col='TransactionID')\ntest_transaction = pd.read_csv('../input/test_transaction.csv', index_col='TransactionID')\n\ntrain_identity = pd.read_csv('../input/train_identity.csv', index_col='TransactionID')\ntest_identity = pd.read_csv('../input/test_identity.csv', index_col='TransactionID')\n\nsample_submission = pd.read_csv('../input/sample_submission.csv', index_col='TransactionID')\n\ntrain = train_transaction.merge(train_identity, how='left', left_index=True, right_index=True)\ntest = test_transaction.merge(test_identity, how='left', left_index=True, right_index=True)\n\nprint(train.shape)\nprint(test.shape)\n\ny_train = train['isFraud'].copy()\ndel train_transaction, train_identity, test_transaction, test_identity\n\n# Drop target, fill in NaNs\nX_train = train.drop('isFraud', axis=1)\nX_test = test.copy()\n\ndel train, test\n\n# Label Encoding\nfor f in X_train.columns:\n    if X_train[f].dtype=='object' or X_test[f].dtype=='object': \n        lbl = preprocessing.LabelEncoder()\n        lbl.fit(list(X_train[f].values) + list(X_test[f].values))\n        X_train[f] = lbl.transform(list(X_train[f].values))\n        X_test[f] = lbl.transform(list(X_test[f].values))   ")


# In[ ]:


get_ipython().run_cell_magic('time', '', '# From kernel https://www.kaggle.com/gemartin/load-data-reduce-memory-usage\n# WARNING! THIS CAN DAMAGE THE DATA \ndef reduce_mem_usage(df):\n    """ iterate through all the columns of a dataframe and modify the data type\n        to reduce memory usage.        \n    """\n    start_mem = df.memory_usage().sum() / 1024**2\n    print(\'Memory usage of dataframe is {:.2f} MB\'.format(start_mem))\n    \n    for col in df.columns:\n        col_type = df[col].dtype\n        \n        if col_type != object:\n            c_min = df[col].min()\n            c_max = df[col].max()\n            if str(col_type)[:3] == \'int\':\n                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:\n                    df[col] = df[col].astype(np.int8)\n                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:\n                    df[col] = df[col].astype(np.int16)\n                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:\n                    df[col] = df[col].astype(np.int32)\n                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:\n                    df[col] = df[col].astype(np.int64)  \n            else:\n                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:\n                    df[col] = df[col].astype(np.float16)\n                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:\n                    df[col] = df[col].astype(np.float32)\n                else:\n                    df[col] = df[col].astype(np.float64)\n        else:\n            df[col] = df[col].astype(\'category\')\n\n    end_mem = df.memory_usage().sum() / 1024**2\n    print(\'Memory usage after optimization is: {:.2f} MB\'.format(end_mem))\n    print(\'Decreased by {:.1f}%\'.format(100 * (start_mem - end_mem) / start_mem))\n    \n    return df\nX_train = reduce_mem_usage(X_train)\nX_test = reduce_mem_usage(X_test)')


# In[ ]:


get_ipython().run_cell_magic('time', '', "from sklearn.model_selection import KFold\nfrom sklearn.metrics import roc_auc_score\nEPOCHS = 3\nkf = KFold(n_splits = EPOCHS, shuffle = True)\ny_preds = np.zeros(sample_submission.shape[0])\ny_oof = np.zeros(X_train.shape[0])\nfor tr_idx, val_idx in kf.split(X_train, y_train):\n    clf = xgb.XGBClassifier(\n        n_estimators=500,\n        max_depth=9,\n        learning_rate=0.05,\n        subsample=0.9,\n        colsample_bytree=0.9,\n        tree_method='gpu_hist'\n    )\n    \n    X_tr, X_vl = X_train.iloc[tr_idx, :], X_train.iloc[val_idx, :]\n    y_tr, y_vl = y_train.iloc[tr_idx], y_train.iloc[val_idx]\n    clf.fit(X_tr, y_tr)\n    y_pred_train = clf.predict_proba(X_vl)[:,1]\n    y_oof[val_idx] = y_pred_train\n    print('ROC AUC {}'.format(roc_auc_score(y_vl, y_pred_train)))\n    \n    y_preds+= clf.predict_proba(X_test)[:,1] / EPOCHS\n \n    ")


# In[ ]:


sample_submission['isFraud'] = y_preds
sample_submission.to_csv('simple_xgboost.csv')


# In[ ]:



