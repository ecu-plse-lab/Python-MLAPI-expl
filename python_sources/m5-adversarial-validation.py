#!/usr/bin/env python
# coding: utf-8

# Getting a reliable validation strategies has been one of the biggest issues in this compettition. In this kernel we'll take a look at the adverserial validation, and what it may imply about our data. 
# 
# For features we have used feateus from thsi kernel: https://www.kaggle.com/kneroma/m5-first-public-notebook-under-0-50, which have been recomputed here: https://www.kaggle.com/tunguz/best-features-only/
# 
# Unfortunately, it is impossible to create and save the full dataset in Kaggle kernels, so we had to resort to subsampling. Due to this, it is very likely that there are some sampling isssues that skew the conclusions in some way. Results in this kernel are meant to be strictly preliminary.

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# In[ ]:


get_ipython().run_cell_magic('time', '', "import lightgbm as lgb\nfrom sklearn.model_selection import KFold\nfrom sklearn import model_selection, preprocessing, metrics\n\nfrom sklearn import preprocessing\nimport gc\n\n\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport warnings\nwarnings.simplefilter(action='ignore', category=FutureWarning)\n\n\n# Load data\n\n\ntest = pd.read_csv('../input/best-features-only/X_test.csv')\nfeatures = test.columns\ntrain = pd.read_csv('../input/best-features-only/X_train.csv', usecols=features)\n\ntrs = train.shape[0]\ntes = test.shape[0]\n\nprint(features)\nprint(train.shape)\nprint(test.shape)")


# In[ ]:


train = pd.concat([train, test], axis =0)
del test
gc.collect()


# In[ ]:


target = np.hstack([np.zeros(trs,), np.ones(tes,)])


# In[ ]:


train, test, y_train, y_test = model_selection.train_test_split(train, target, test_size=0.33, random_state=42, shuffle=True)
del target
gc.collect()


# In[ ]:


train = lgb.Dataset(train, label=y_train)
test = lgb.Dataset(test, label=y_test)


# In[ ]:


param = {'num_leaves': 50,
         'min_data_in_leaf': 30, 
         'objective':'binary',
         'max_depth': 5,
         'learning_rate': 0.01,
         "min_child_samples": 20,
         "boosting": "gbdt",
         "feature_fraction": 0.9,
         "bagging_freq": 1,
         "bagging_fraction": 0.9 ,
         "bagging_seed": 56,
         "metric": 'auc',
         "verbosity": -1}


# In[ ]:


num_round = 50
clf = lgb.train(param, train, num_round, valid_sets = [train, test], verbose_eval=50, early_stopping_rounds = 50)


# Wow, AUC of 0.9999 is as large as it gets! Let's see which columns are the most responsible for this discrepancy.

# In[ ]:


feature_imp = pd.DataFrame(sorted(zip(clf.feature_importance(),features)), columns=['Value','Feature'])

plt.figure(figsize=(20, 20))
sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False).head(100))
plt.title('LightGBM Features')
plt.tight_layout()
plt.show()
plt.savefig('lgbm_importances-01.png')


# Seems that the temporal features are the most disperate between the two models, which may not be surprising for a time-series problem. 

# Now we will repeat the same procedure, but now we'll drop 'week' from the features.

# In[ ]:


get_ipython().run_cell_magic('time', '', 'del train, test, clf\n\ngc.collect()\ngc.collect()\n\nfeatures = [\'item_id\', \'dept_id\', \'store_id\', \'cat_id\', \'state_id\', \'wday\', \'month\',\n       \'year\', \'event_name_1\', \'event_type_1\', \'event_name_2\', \'event_type_2\',\n       \'snap_CA\', \'snap_TX\', \'snap_WI\', \'sell_price\', \'lag_7\', \'lag_28\',\n       \'rmean_7_7\', \'rmean_28_7\', \'rmean_7_28\', \'rmean_28_28\',\n       \'quarter\', \'mday\']\n\ntest = pd.read_csv(\'../input/best-features-only/X_test.csv\', usecols=features)\ntrain = pd.read_csv(\'../input/best-features-only/X_train.csv\', usecols=features)\n\ntrain = pd.concat([train, test], axis =0)\ndel test\ngc.collect()\n\ntarget = np.hstack([np.zeros(trs,), np.ones(tes,)])\n\ntrain, test, y_train, y_test = model_selection.train_test_split(train, target, test_size=0.33, random_state=42, shuffle=True)\ndel target\ngc.collect()\n\ntrain = lgb.Dataset(train, label=y_train)\ntest = lgb.Dataset(test, label=y_test)\n\nclf = lgb.train(param, train, num_round, valid_sets = [train, test], verbose_eval=50, early_stopping_rounds = 50)\n\nfeature_imp = pd.DataFrame(sorted(zip(clf.feature_importance(),features)), columns=[\'Value\',\'Feature\'])\n\nplt.figure(figsize=(20, 20))\nsns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False).head(100))\nplt.title(\'LightGBM Features\')\nplt.tight_layout()\nplt.show()\nplt.savefig(\'lgbm_importances-02.png\')')


# Well, the AUC hardly changed. Let's see what happens if we leave out 'month' as well.

# In[ ]:


get_ipython().run_cell_magic('time', '', 'del train, test, clf\n\ngc.collect()\ngc.collect()\n\nfeatures = [\'item_id\', \'dept_id\', \'store_id\', \'cat_id\', \'state_id\', \'wday\',\n       \'year\', \'event_name_1\', \'event_type_1\', \'event_name_2\', \'event_type_2\',\n       \'snap_CA\', \'snap_TX\', \'snap_WI\', \'sell_price\', \'lag_7\', \'lag_28\',\n       \'rmean_7_7\', \'rmean_28_7\', \'rmean_7_28\', \'rmean_28_28\',\n       \'quarter\', \'mday\']\n\ntest = pd.read_csv(\'../input/best-features-only/X_test.csv\', usecols=features)\ntrain = pd.read_csv(\'../input/best-features-only/X_train.csv\', usecols=features)\n\ntrain = pd.concat([train, test], axis =0)\ndel test\ngc.collect()\n\ntarget = np.hstack([np.zeros(trs,), np.ones(tes,)])\n\ntrain, test, y_train, y_test = model_selection.train_test_split(train, target, test_size=0.33, random_state=42, shuffle=True)\ndel target\ngc.collect()\n\ntrain = lgb.Dataset(train, label=y_train)\ntest = lgb.Dataset(test, label=y_test)\n\nclf = lgb.train(param, train, num_round, valid_sets = [train, test], verbose_eval=50, early_stopping_rounds = 50)\n\nfeature_imp = pd.DataFrame(sorted(zip(clf.feature_importance(),features)), columns=[\'Value\',\'Feature\'])\n\nplt.figure(figsize=(20, 20))\nsns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False).head(100))\nplt.title(\'LightGBM Features\')\nplt.tight_layout()\nplt.show()\nplt.savefig(\'lgbm_importances-03.png\')')


# Still no substantial change. Let's now remove 'item_id'.

# In[ ]:


get_ipython().run_cell_magic('time', '', 'del train, test, clf\n\ngc.collect()\ngc.collect()\n\nfeatures = [\'dept_id\', \'store_id\', \'cat_id\', \'state_id\', \'wday\',\n       \'year\', \'event_name_1\', \'event_type_1\', \'event_name_2\', \'event_type_2\',\n       \'snap_CA\', \'snap_TX\', \'snap_WI\', \'sell_price\', \'lag_7\', \'lag_28\',\n       \'rmean_7_7\', \'rmean_28_7\', \'rmean_7_28\', \'rmean_28_28\',\n       \'quarter\', \'mday\']\n\ntest = pd.read_csv(\'../input/best-features-only/X_test.csv\', usecols=features)\ntrain = pd.read_csv(\'../input/best-features-only/X_train.csv\', usecols=features)\n\ntrain = pd.concat([train, test], axis =0)\ndel test\ngc.collect()\n\ntarget = np.hstack([np.zeros(trs,), np.ones(tes,)])\n\ntrain, test, y_train, y_test = model_selection.train_test_split(train, target, test_size=0.33, random_state=42, shuffle=True)\ndel target\ngc.collect()\n\ntrain = lgb.Dataset(train, label=y_train)\ntest = lgb.Dataset(test, label=y_test)\n\nclf = lgb.train(param, train, num_round, valid_sets = [train, test], verbose_eval=50, early_stopping_rounds = 50)\n\nfeature_imp = pd.DataFrame(sorted(zip(clf.feature_importance(),features)), columns=[\'Value\',\'Feature\'])\n\nplt.figure(figsize=(20, 20))\nsns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False).head(100))\nplt.title(\'LightGBM Features\')\nplt.tight_layout()\nplt.show()\nplt.savefig(\'lgbm_importances-04.png\')')
