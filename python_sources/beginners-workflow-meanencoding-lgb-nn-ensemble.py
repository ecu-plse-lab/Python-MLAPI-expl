#!/usr/bin/env python
# coding: utf-8

# Last Updated: 04/03/18   
# Mean encoding implement on version 19, such as teacher_prefix, school_state,  project_grade_category,   
# which performances much better than label encoding on single models.

# I have been in kaggle for half a year, I learned a lot from kaggle kernels, thanks to kagglers, I like these kernels!
# 
# In this kernel, I will show you different ways to do text classifier, including LogisticRegression, RandomForest, lightgbm and neural networks.
# 
# Then,  I'll introduce you a powerful tool for model stacking.

# 

# In[58]:


# kernel params config

# I set quick_run to True to run a little part of training datasets because of space and time limit, 
# you can run the whole datasets on you local machine.
quick_run = False

# max features for word embedding
max_features = 80000
# word vector length
embed_size = 300

# dpcnn config
pj_repeat = 3
rs_repeat = 1
dpcnn_folds = 5
batch_size = 64
epochs = 5
project_maxlen = 210
resouse_max_len = 30
maxlen = project_maxlen + resouse_max_len

# To complete this kernel in a very short time
if quick_run == True:
    max_features = 1000
    epochs = 2
    
EMBEDDING_FILE = '../input/fasttext-crawl-300d-2m/crawl-300d-2M.vec'


# In[59]:


import os; os.environ['OMP_NUM_THREADS'] = '4'
import gc
import numpy as np
import pandas as pd

from functools import reduce
from functools import partial

import warnings
warnings.filterwarnings('ignore')


# In[60]:


train_df = pd.read_csv('../input/donorschoose-application-screening/train.csv')
test_df = pd.read_csv('../input/donorschoose-application-screening/test.csv')
resouse_df = pd.read_csv('../input/donorschoose-application-screening/resources.csv')


# In[61]:


get_ipython().run_cell_magic('time', '', "resouse_df['description'].fillna('', inplace=True)\nres_nums = pd.DataFrame(resouse_df[['id', 'price']].groupby('id').price.agg(['count', \n                                                                             'sum', \n                                                                             'min', \n                                                                             'max', \n                                                                             'mean',  \n                                                                             'std', \n                                                                             lambda x: len(np.unique(x)),])).reset_index()\nres_nums = res_nums.rename(columns={'count': 'res_count', \n                                    'sum': 'res_sum',\n                                    'min':  'res_min', \n                                    'max':  'res_max',\n                                    'mean': 'res_mean', \n                                    'std':  'res_std',\n                                    '<lambda>': 'res_unique' })\nres_descp = resouse_df[['id', 'description']].groupby('id').description.agg([ lambda x: ' '.join(x) ]).reset_index().rename(columns={'<lambda>':'res_description'})\nresouse_df = res_nums.merge(res_descp, on='id', how='left')\ntrain_df = train_df.merge(resouse_df, on='id', how='left')\ntest_df = test_df.merge(resouse_df, on='id', how='left')\ndel res_nums\ndel res_descp\ndel resouse_df\ngc.collect()")


# In[62]:


if quick_run == True:
    train_df = train_df[:10000]
    test_df = test_df[:100]


# In[63]:


train_target = train_df['project_is_approved'].values
# train_df = train_df.drop('project_is_approved', axis=1)
gc.collect()


# In[64]:


train_df.shape, test_df.shape


# In[65]:


essay_cols = ['project_essay_1', 'project_essay_2','project_essay_3', 'project_essay_4']
essay_length_cols = [item+'_len' for item in essay_cols]

def count_essay_length(df):
    for col in essay_cols:
        df[col] = df[col].fillna('unknown')
        df[col+'_len'] = df[col].apply(len)
    return df
train_df = count_essay_length(train_df)
test_df = count_essay_length(test_df)

train_df['project_essay'] = ''
test_df['project_essay'] = ''
for col in essay_cols:
    train_df['project_essay'] += train_df[col] + ' '
    test_df['project_essay'] += test_df[col] + ' '
train_df[['project_essay']].head()


# In[66]:


time_cols = ['sub_year', 'sub_month', 'sub_day', 'sub_hour', 'sub_dayofweek', 'sub_dayofyear']
def time_stamp_features(df):
    time_df = pd.to_datetime(df['project_submitted_datetime'])
    df['sub_year'] = time_df.apply(lambda x: x.year)
    df['sub_month'] = time_df.apply(lambda x: x.month)
    df['sub_day'] = time_df.apply(lambda x: x.day)
    df['sub_hour'] = time_df.apply(lambda x: x.hour)
    df['sub_dayofweek'] = time_df.apply(lambda x: x.dayofweek)
    df['sub_dayofyear'] = time_df.apply(lambda x: x.dayofyear)
    return df
train_df = time_stamp_features(train_df)
test_df = time_stamp_features(test_df)


# In[67]:


str_cols = ['teacher_id', 'teacher_prefix', 'school_state',
       'project_submitted_datetime', 'project_grade_category',
       'project_subject_categories', 'project_subject_subcategories',
       'project_title', 'project_resource_summary','res_description', 'project_essay']
num_cols = ['teacher_number_of_previously_posted_projects', 
            'res_count', 'res_sum', 'res_min', 'res_max', 'res_mean', 'res_std', 'res_unique'] + essay_length_cols 
train_df[str_cols] =train_df[str_cols].fillna('unknown')
train_df[num_cols] = train_df[num_cols].fillna(0)
test_df[str_cols] =test_df[str_cols].fillna('unknown')
test_df[num_cols] = test_df[num_cols].fillna(0)
for col in str_cols:
    train_df[col] = train_df[col].str.lower()
    test_df[col] = test_df[col].str.lower()


# In[68]:


from sklearn.preprocessing import MinMaxScaler

std_scaler = MinMaxScaler()
train_none_text_features = std_scaler.fit_transform(train_df[num_cols].values)
test_none_text_features = std_scaler.transform(test_df[num_cols].values)

train_df = train_df.drop(num_cols, axis=1)
test_df = test_df.drop(num_cols, axis=1)
del std_scaler
gc.collect()


# In[69]:


train_df['project_descp'] = train_df['project_subject_categories'] + ' ' + train_df['project_subject_subcategories'] + ' ' + train_df['project_title'] + ' ' + train_df['project_resource_summary'] + ' ' + train_df['project_essay']
test_df['project_descp'] = test_df['project_subject_categories'] + ' ' + test_df['project_subject_subcategories'] + ' ' + test_df['project_title'] + ' ' + test_df['project_resource_summary'] + ' ' + test_df['project_essay']
train_df = train_df.drop([ 'project_essay'], axis=1)
test_df = test_df.drop(['project_essay'], axis=1)
gc.collect()


# In[70]:


from sklearn.preprocessing import LabelEncoder
label_cols = [
    # 'teacher_id',
    'teacher_prefix', 
    'school_state', 
    'project_grade_category', 
    'project_subject_categories', 
    'project_subject_subcategories'
] + time_cols

def mean_encoding(train_df, test_df, col):
    gp = train_df.groupby(col)['project_is_approved'].mean().reset_index().rename(columns={'project_is_approved': col+'_mean'})
    train_df = pd.merge(train_df, gp, how='left', on=[col])
    test_df = pd.merge(test_df, gp, how='left', on=[col])
    return train_df, test_df
for col in label_cols:
    train_df, test_df = mean_encoding(train_df, test_df, col)
label_mean_cols = [item+'_mean' for item in label_cols]
train_label_features = train_df[label_mean_cols].values
test_df[label_mean_cols] = test_df[label_mean_cols].fillna(test_df[label_mean_cols].mean())
test_label_features = test_df[label_mean_cols].values

'''for col in label_cols:
    le = LabelEncoder()
    le.fit(np.hstack([train_df[col].values, test_df[col].values]))
    train_df[col] = le.transform(train_df[col])
    test_df[col] = le.transform(test_df[col])
train_label_features = train_df[label_cols].values
test_label_features = test_df[label_cols].values'''

train_df = train_df.drop(label_cols, axis=1)
test_df = test_df.drop(label_cols, axis=1)
train_df = train_df.drop(label_mean_cols, axis=1)
test_df = test_df.drop(label_mean_cols, axis=1)
# del le
gc.collect()


# In[71]:


train_df.columns


# In[72]:


get_ipython().run_cell_magic('time', '', "import re\n\ndef clean_descp(descp):\n    low_case = re.compile('([a-z]*)')\n    words = low_case.findall(descp)\n    # words = [item for item in filter(lambda x: x not in stopwords, words)]\n    return ' '.join(words)\n\nfor col in essay_cols:\n    train_df[col] = train_df[col].apply(clean_descp)\n    test_df[col]  = test_df[col].apply(clean_descp)\ntrain_df['project_descp']  = train_df['project_descp'].apply(clean_descp)\ntest_df['project_descp']  = test_df['project_descp'].apply(clean_descp)")


# The cell below is  from @Ehsan's [Ultimate Feature Engineering -> XGB+LGB [LB 0.813]](https://www.kaggle.com/safavieh/ultimate-feature-engineering-xgb-lgb-lb-0-813)  
# Extracting text features one by one instead of processing them together can improve predicting score.
# 
# 

# In[73]:


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

def getTextFeatures(Col, max_features=10000):
    print('processing: ', Col)
    vectorizer = CountVectorizer(stop_words=None,
                                 # preprocessor=wordPreProcess,
                                 max_features=max_features,
                                 binary=True,
                                 ngram_range=(1,2))
    train_features = vectorizer.fit_transform(train_df[Col])
    test_features = vectorizer.transform(test_df[Col])
    return train_features, test_features
train_text_es1, test_text_es1 = getTextFeatures('project_essay_1', max_features=5000)
train_text_es2, test_text_es2 = getTextFeatures('project_essay_2', max_features=7000)
train_text_prs, test_text_prs = getTextFeatures('project_resource_summary', max_features=1000)
train_text_rsd, test_text_rsd = getTextFeatures('res_description', max_features=1000)
train_text_pjt, test_text_pjt = getTextFeatures('project_title', max_features=500)


# In[74]:


from scipy.sparse import csr_matrix, hstack
train_text_features = hstack([train_text_es1, train_text_es2, train_text_prs, train_text_rsd, train_text_pjt]).tocsr()
test_text_features = hstack([test_text_es1, test_text_es2, test_text_prs, test_text_rsd, test_text_pjt]).tocsr()
train_text_features.shape, test_text_features.shape


# In[75]:


train_features = hstack([train_none_text_features, train_label_features, train_text_features]).tocsr()
test_features = hstack([test_none_text_features, test_label_features, test_text_features]).tocsr()

del train_text_es1
del train_text_es2
del train_text_prs
del train_text_rsd
del train_text_pjt
del test_text_es1
del test_text_es2
del test_text_prs
del test_text_rsd
del test_text_pjt
del train_text_features
del test_text_features
gc.collect()


# It's convenient to do stacking on any model with the class below.
# 
# I named it qiaofeng to pay tribute to my big bother, sun e phone.

# In[76]:


from functools import reduce
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, KFold

class qiaofeng_kfold_stack:
    def __init__(self, train, train_target, test, split_target, model, preprocess_func=None, score_func=None, kfolds=5, random_seed=9527, logger=None):
        self.train = train
        self.train_target = train_target
        self.test = test
        self.split_target = split_target
        self.model = model
        self.preprocess_func = preprocess_func
        self.score_func = score_func
        self.kfolds = kfolds
        self.random_seed = random_seed
        self.logger= logger
        self.skf = KFold(n_splits=self.kfolds, random_state= self.random_seed)
        self.predict_test_kfolds = []
        self.predict_valid_kfolds = np.zeros((self.train.shape[0]))
    def print_params(self):
        print('kfolds : %s' % self.kfolds)
        print('random seed : %s' % self.random_seed)
    def preprocess(self):
        if self.preprocess_func != None:
            self.train, self.test = self.preprocess_func(self.train, self.test)
    def score(self, target, predict):
        return self.score_func(target, predict)
    def model_fit(self, train, train_target):
        self.model.fit(train, train_target)
    def model_predict(self, dataset):
        return self.model.predict(dataset)
    def model_fit_predict(self, train, train_target, dataset):
        self.model_fit(train, train_target)
        predict_train = None#self.model_predict(train)
        predict_valid = self.model_predict(dataset)
        predict_test = self.model_predict(self.test)
        return predict_train, predict_valid, predict_test
    def clear_predicts(self):
        self.predict_test_kfolds = []
        self.predict_valid_kfolds = np.zeros((self.train.shape[0]))
    def model_train_with_kfold(self):
        self.clear_predicts()
        for (folder_index, (train_index, valid_index)) in enumerate(self.skf.split(self.train)):
            x_train, x_valid = self.train[train_index], self.train[valid_index]
            y_train, y_valid = self.train_target[train_index], self.train_target[valid_index]
            predict_train, predict_valid, predict_test = self.model_fit_predict(x_train, y_train, x_valid)
            self.predict_test_kfolds.append(predict_test)
            self.predict_valid_kfolds[valid_index] = predict_valid
            if self.logger != None:
                valid_score = self.score(y_valid, predict_valid)
                # train_score = self.score(y_train, predict_train)
                self.logger('Fold: %s, valid score: %s' % (folder_index, valid_score))
    def predict_test_mean(self):
        return reduce(lambda x,y:x+y, self.predict_test_kfolds)  / self.kfolds


# In[77]:


class qiaofeng_predict_prob(qiaofeng_kfold_stack):
    def model_predict(self, dataset):
        return self.model.predict_proba(dataset)[:,1]


# In[78]:


get_ipython().run_cell_magic('time', '', 'from sklearn.ensemble import RandomForestClassifier\n\nmodel = RandomForestClassifier( n_jobs=4, \n                                criterion="entropy",\n                                max_depth=20, \n                                n_estimators=100, \n                                max_features=\'sqrt\', \n                                random_state=233,\n                                # min_samples_leaf = 50\n                                )\nqiaofeng_rf = qiaofeng_predict_prob(train=train_features, train_target=train_target, test=test_features, kfolds=5,split_target=train_target,\n                                          score_func=roc_auc_score, logger=print, model=model)\nqiaofeng_rf.model_train_with_kfold()\npred_valid_rf = qiaofeng_rf.predict_valid_kfolds\npred_test_avg_rf = qiaofeng_rf.predict_test_mean()\ndel qiaofeng_rf\ngc.collect()')


# In[79]:


get_ipython().run_cell_magic('time', '', 'import lightgbm as lgb\nfrom sklearn.model_selection import train_test_split\n\nclass qiaofeng_lgb_clf(qiaofeng_kfold_stack):\n    def model_fit(self, train, train_target):\n        X_tra, X_val, y_tra, y_val = train_test_split(train, train_target, train_size=0.95, random_state=233)\n        self.model = lgb.LGBMClassifier( n_jobs=4,\n                                         max_depth=4,\n                                         metric="auc",\n                                         n_estimators=1000,\n                                         num_leaves=15,\n                                         boosting_type="gbdt",\n                                         learning_rate=0.05,\n                                         feature_fraction=0.45,\n                                         colsample_bytree=0.45,\n                                         bagging_fraction=0.8,\n                                         bagging_freq=5,\n                                         reg_lambda=0.2)\n        self.model.fit(X=X_tra, y=y_tra,\n                      eval_set=[(X_val, y_val)],\n                      early_stopping_rounds=200,\n                      verbose=False)\n    def model_predict(self, dataset):\n        return self.model.predict_proba(dataset)[:,1]\n\nqiaofeng_lgb = qiaofeng_lgb_clf(train=train_features, train_target=train_target, test=test_features, kfolds=5,split_target=train_target,\n                                          score_func=roc_auc_score, logger=print, model=None)\nqiaofeng_lgb.model_train_with_kfold()\npred_valid_lgb = qiaofeng_lgb.predict_valid_kfolds\npred_test_avg_lgb = qiaofeng_lgb.predict_test_mean()\ndel qiaofeng_lgb\ngc.collect()')


# In[80]:


get_ipython().run_cell_magic('time', '', 'import lightgbm as lgb\nfrom sklearn.model_selection import train_test_split\n\nclass qiaofeng_lgb_clf(qiaofeng_kfold_stack):\n    def model_fit(self, train, train_target):\n        X_tra, X_val, y_tra, y_val = train_test_split(train, train_target, train_size=0.95, random_state=233)\n        self.model = lgb.LGBMClassifier( n_jobs=4,\n                                         max_depth=4,\n                                         metric="auc",\n                                         n_estimators=1000,\n                                         num_leaves=15,\n                                         boosting_type="gbdt",\n                                         learning_rate=0.05,\n                                         feature_fraction=0.45,\n                                         colsample_bytree=0.45,\n                                         bagging_fraction=0.8,\n                                         bagging_freq=5,\n                                         reg_lambda=0.2)\n        self.model.fit(X=X_tra, y=y_tra,\n                      eval_set=[(X_val, y_val)],\n                      early_stopping_rounds=200,\n                      verbose=False)\n    def model_predict(self, dataset):\n        return self.model.predict_proba(dataset)[:,1]\n\nqiaofeng_lgb = qiaofeng_lgb_clf(train=train_features.astype(np.bool).astype(np.float32), \n                                train_target=train_target, \n                                test=test_features.astype(np.bool).astype(np.float32), \n                                kfolds=5,split_target=train_target,\n                                score_func=roc_auc_score, \n                                logger=print, model=None)\nqiaofeng_lgb.model_train_with_kfold()\npred_valid_lgb_bool = qiaofeng_lgb.predict_valid_kfolds\npred_test_avg_lgb_bool = qiaofeng_lgb.predict_test_mean()\ndel qiaofeng_lgb\ngc.collect()')


# In[81]:


pd.Series(pred_valid_lgb).corr(pd.Series(pred_valid_lgb_bool)), pd.Series(pred_test_avg_lgb).corr(pd.Series(pred_test_avg_lgb_bool))


# In[82]:


from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from matplotlib import pyplot as plt
from wordbatch.models import FTRL, FM_FTRL

clf = FTRL(alpha=0.01, beta=0.1, L1=0.1, L2=1000.0, D=train_features.shape[1], iters=1, 
                 inv_link="identity", threads=4)
X_tra, X_val, y_tra, y_val = train_test_split(train_features, train_target, train_size=0.95, random_state=7)

train_scores = []
valid_scores = []
for i in range(10):
    clf.fit(X_tra, y_tra)
    train_predict = clf.predict(X_tra)
    tp = train_predict - train_predict.min()
    tp = tp / tp.max()
    valid_predict = clf.predict(X_val)
    vp = valid_predict - valid_predict.min()
    vp = vp / vp.max()
    train_auc = roc_auc_score(y_tra, tp)
    valid_auc = roc_auc_score(y_val, vp)
    train_scores.append(train_auc)
    valid_scores.append(valid_auc)
    print(i+1, train_auc, valid_auc)
plt.clf()
plt.figure(figsize=(10,10))
plt.plot(np.arange(len(train_scores)), train_scores, label='train')
plt.plot(np.arange(len(valid_scores)), valid_scores, label='valid')
valid_max = max(valid_scores)
plt.title('%s - %s'%(valid_scores.index(valid_max)+1, valid_max))
plt.legend()
plt.show()


# In[83]:


get_ipython().run_cell_magic('time', '', 'from wordbatch.models import FTRL, FM_FTRL\n\ndef sigmoid(x):\n    return 1 / (1 + np.exp(-x))\n\nclass qiaofeng_ftrl(qiaofeng_kfold_stack):\n    def model_fit(self, train, train_target):\n        self.model = FTRL(alpha=0.01, beta=0.1, L1=0.1, L2=1000.0, D=train_features.shape[1], iters=2, \n                             inv_link="identity", threads=4)\n        self.model.fit(train, train_target)\n    def model_predict(self, dataset):\n        predict = self.model.predict(dataset)\n        pred_nan = np.isnan(predict)\n        if pred_nan.shape[0] == predict.shape[0]:\n            predict[pred_nan] = 0\n        else:\n            predict[pred_nan] = np.nanmean(predict)\n        return sigmoid(predict)\n        \nqiaofeng_ftrl = qiaofeng_ftrl(train=train_features, train_target=train_target, test=test_features, kfolds=20, split_target=train_target,\n                                          score_func=roc_auc_score, logger=print, model=None)\nqiaofeng_ftrl.model_train_with_kfold()\npred_valid_ftrl = qiaofeng_ftrl.predict_valid_kfolds\npred_test_avg_ftrl = qiaofeng_ftrl.predict_test_mean()')


# In[84]:


del train_features
del test_features
gc.collect()


# In[85]:


from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.utils import shuffle

from keras.models import Model
from keras.layers import Input, Dense, Embedding, SpatialDropout1D, concatenate
from keras.layers import GRU, Bidirectional, GlobalAveragePooling1D, GlobalMaxPooling1D, LSTM, Dropout, BatchNormalization
from keras.preprocessing import text, sequence
from keras.callbacks import Callback, EarlyStopping, ModelCheckpoint

tokenizer = text.Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(list(train_df['project_descp']) + list(test_df['project_descp']) + list(train_df['res_description']) + list(test_df['res_description']))
train_pj = sequence.pad_sequences(tokenizer.texts_to_sequences(train_df['project_descp']), maxlen=project_maxlen)
test_pj = sequence.pad_sequences(tokenizer.texts_to_sequences(test_df['project_descp']), maxlen=project_maxlen)

train_res = sequence.pad_sequences(tokenizer.texts_to_sequences(train_df['res_description']), maxlen=resouse_max_len)
test_res = sequence.pad_sequences(tokenizer.texts_to_sequences(test_df['res_description']), maxlen=resouse_max_len)

train_seq = np.hstack([train_pj, train_res])
test_seq = np.hstack([test_pj, test_res])


# In[86]:


def get_coefs(word, *arr): return word, np.asarray(arr, dtype='float32')
embeddings_index = dict(get_coefs(*o.rstrip().rsplit(' ')) for o in open(EMBEDDING_FILE))

word_index = tokenizer.word_index
nb_words = min(max_features, len(word_index))
embedding_matrix = np.zeros((nb_words, embed_size))
for word, i in word_index.items():
    if i >= max_features: continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None: embedding_matrix[i] = embedding_vector


class RocAucEvaluation(Callback):
    def __init__(self, validation_data=(), interval=1):
        super(Callback, self).__init__()

        self.interval = interval
        self.X_val, self.y_val = validation_data

    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.interval == 0:
            y_pred = self.model.predict(self.X_val, verbose=0)
            score = roc_auc_score(self.y_val, y_pred)
            logs['roc_auc_val'] = score
            print("\n ROC-AUC - epoch: %d - score: %.6f \n" % (epoch+1, score))


# In[87]:


train_num_features = np.hstack([train_none_text_features, train_label_features])
test_num_features = np.hstack([test_none_text_features, test_label_features])

del train_none_text_features
del train_label_features
del test_none_text_features
del test_label_features
gc.collect()


# In[88]:


train_seq = np.hstack([train_seq, train_num_features])
test_seq = np.hstack([test_seq, test_num_features])


# In[89]:


gc.collect()
gc.disable()


# In[ ]:


from keras.models import Model
from keras.layers import Input, Dense, Embedding, SpatialDropout1D, concatenate
from keras.layers import GRU, Bidirectional, GlobalAveragePooling1D, GlobalMaxPooling1D, LSTM, Dropout, BatchNormalization,Conv1D
from keras.preprocessing import text, sequence
from keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
from keras.layers import Input, Dense, Embedding, MaxPooling1D, Conv1D, SpatialDropout1D
from keras.layers import add, Dropout, PReLU, BatchNormalization, GlobalMaxPooling1D

import tensorflow as tf
from keras import backend as K
from keras import optimizers
from keras import initializers, regularizers, constraints, callbacks

if 1:
    def get_model():
        session_conf = tf.ConfigProto(intra_op_parallelism_threads=4, inter_op_parallelism_threads=4)
        K.set_session(tf.Session(graph=tf.get_default_graph(), config=session_conf))

        filter_nr = 32
        filter_size = 3
        max_pool_size = 3
        max_pool_strides = 2
        dense_nr = 64
        spatial_dropout = 0.2
        dense_dropout = 0.05
        train_embed = False
        
        project = Input(shape=(project_maxlen,), name='project')
        emb_project = Embedding(max_features, embed_size, weights=[embedding_matrix], trainable=train_embed)(project)
        emb_project = SpatialDropout1D(spatial_dropout)(emb_project)
        
        pj_block1 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(emb_project)
        pj_block1 = BatchNormalization()(pj_block1)
        pj_block1 = PReLU()(pj_block1)
        pj_block1 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(pj_block1)
        pj_block1 = BatchNormalization()(pj_block1)
        pj_block1 = PReLU()(pj_block1)
        
        #we pass embedded comment through conv1d with filter size 1 because it needs to have the same shape as block output
        #if you choose filter_nr = embed_size (300 in this case) you don't have to do this part and can add emb_comment directly to block1_output
        pj_resize_emb = Conv1D(filter_nr, kernel_size=1, padding='same', activation='linear')(emb_project)
        pj_resize_emb = PReLU()(pj_resize_emb)
            
        pj_block1_output = add([pj_block1, pj_resize_emb])
        # pj_block1_output = MaxPooling1D(pool_size=max_pool_size, strides=max_pool_strides)(pj_block1_output)
        for _ in range(pj_repeat):  
            pj_block1_output = MaxPooling1D(pool_size=max_pool_size, strides=max_pool_strides)(pj_block1_output)
            pj_block2 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(pj_block1_output)
            pj_block2 = BatchNormalization()(pj_block2)
            pj_block2 = PReLU()(pj_block2)
            pj_block2 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(pj_block2)
            pj_block2 = BatchNormalization()(pj_block2)
            pj_block2 = PReLU()(pj_block2)
            pj_block1_output = add([pj_block2, pj_block1_output])
        
        resouse = Input(shape=(resouse_max_len,), name='resouse')
        emb_resouse = Embedding(max_features, embed_size, weights=[embedding_matrix], trainable=train_embed)(resouse)
        emb_resouse = SpatialDropout1D(spatial_dropout)(emb_resouse)
        
        rs_block1 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(emb_resouse)
        rs_block1 = BatchNormalization()(rs_block1)
        rs_block1 = PReLU()(rs_block1)
        rs_block1 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(rs_block1)
        rs_block1 = BatchNormalization()(rs_block1)
        rs_block1 = PReLU()(rs_block1)

        #we pass embedded comment through conv1d with filter size 1 because it needs to have the same shape as block output
        #if you choose filter_nr = embed_size (300 in this case) you don't have to do this part and can add emb_comment directly to block1_output
        rs_resize_emb = Conv1D(filter_nr, kernel_size=1, padding='same', activation='linear')(emb_resouse)
        rs_resize_emb = PReLU()(rs_resize_emb)

        rs_block1_output = add([rs_block1, rs_resize_emb])
        # rs_block1_output = MaxPooling1D(pool_size=max_pool_size, strides=max_pool_strides)(rs_block1_output)
        for _ in range(rs_repeat):  
            rs_block1_output = MaxPooling1D(pool_size=max_pool_size, strides=max_pool_strides)(rs_block1_output)
            rs_block2 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(rs_block1_output)
            rs_block2 = BatchNormalization()(rs_block2)
            rs_block2 = PReLU()(rs_block2)
            rs_block2 = Conv1D(filter_nr, kernel_size=filter_size, padding='same', activation='linear')(rs_block2)
            rs_block2 = BatchNormalization()(rs_block2)
            rs_block2 = PReLU()(rs_block2)
            rs_block1_output = add([rs_block2, rs_block1_output])
            

        pj_output = GlobalMaxPooling1D()(pj_block1_output)
        pj_output = BatchNormalization()(pj_output)
        rs_output = GlobalMaxPooling1D()(rs_block1_output)
        rs_output = BatchNormalization()(rs_output)
        inp_num = Input(shape=(train_seq.shape[1]-maxlen, ), name='num_input')
        bn_inp_num = BatchNormalization()(inp_num)
        conc = concatenate([pj_output, rs_output, bn_inp_num])
        
        output = Dense(dense_nr, activation='linear')(conc)
        output = BatchNormalization()(output)
        output = PReLU()(output)
        output = Dropout(dense_dropout)(output)
        output = Dense(1, activation='sigmoid')(output)
        model = Model(inputs=[project, resouse, inp_num], outputs=output)
        model.compile(loss='binary_crossentropy', 
                    optimizer='nadam',
                    metrics=['accuracy'])

        return model


# In[ ]:


class qiaofeng_dpcnn(qiaofeng_kfold_stack):
    def model_fit_predict(self, train, train_target, valid):
        self.model = get_model()
        early_stopping = EarlyStopping(monitor='roc_auc_val', patience=1, mode='max',min_delta=0.0005)  
        X_tra, X_val, y_tra, y_val = train_test_split(train, train_target, train_size=0.98, random_state=233)
        X_tra = { 'project' : X_tra[:,:project_maxlen], 'resouse' : X_tra[:,project_maxlen:project_maxlen+resouse_max_len], 'num_input' : X_tra[:,maxlen:]  }
        X_val = { 'project' : X_val[:,:project_maxlen], 'resouse' : X_val[:,project_maxlen:project_maxlen+resouse_max_len], 'num_input' : X_val[:,maxlen:]  }
        x_test = { 'project' : self.test[:,:project_maxlen], 'resouse' : self.test[:,project_maxlen:project_maxlen+resouse_max_len], 'num_input' : self.test[:,maxlen:]  }
        valid = { 'project' : valid[:,:project_maxlen], 'resouse' : valid[:,project_maxlen:project_maxlen+resouse_max_len], 'num_input' : valid[:,maxlen:]  }
        
        RocAuc = RocAucEvaluation(validation_data=(X_val, y_val), interval=1)
        hist = self.model.fit(X_tra, y_tra, batch_size=batch_size, epochs=epochs, validation_data=(X_val, y_val),
                             callbacks=[RocAuc, early_stopping], verbose=2)
        predict_train = None#self.model.predict(X_tra, batch_size=1024)[:, 0]
        predict_valid = self.model.predict(valid, batch_size=1024)[:, 0]
        predict_test = self.model.predict(x_test, batch_size=1024)[:, 0]
        return predict_train, predict_valid, predict_test            

dpcnn_kfold_model = qiaofeng_dpcnn(train=train_seq, train_target=train_target, test=test_seq, kfolds=dpcnn_folds, split_target=train_target,
                                          score_func=roc_auc_score, logger=print, model=None)
dpcnn_kfold_model.model_train_with_kfold()
pred_valid_dpcnn = dpcnn_kfold_model.predict_valid_kfolds
pred_test_avg_dpcnn = dpcnn_kfold_model.predict_test_mean()
    
del dpcnn_kfold_model
gc.enable()
gc.collect()
gc.disable()


# In[ ]:


from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

predict_valid_list = [pred_valid_rf, pred_valid_lgb, pred_valid_dpcnn, pred_valid_ftrl]
predict_test_list = [pred_test_avg_rf, pred_test_avg_lgb, pred_test_avg_dpcnn, pred_test_avg_ftrl]

valid_results = np.hstack([scaler.fit_transform(item.reshape((item.shape[0], 1))) for item in predict_valid_list])
test_results = np.hstack([scaler.fit_transform(item.reshape((item.shape[0], 1))) for item in predict_test_list])
train_features = np.hstack([valid_results ])
test_features = np.hstack([test_results ])

lgb_model = lgb.LGBMClassifier(  n_jobs=4,
                                 max_depth=4,
                                 metric="auc",
                                 n_estimators=400,
                                 num_leaves=10,
                                 boosting_type="gbdt",
                                 learning_rate=0.01,
                                 feature_fraction=0.45,
                                 colsample_bytree=0.45,
                                 bagging_fraction=0.4,
                                 bagging_freq=5,
                                 reg_lambda=0.2)
X_tra, X_val, y_tra, y_val = train_test_split(train_features, train_target, train_size=0.8, random_state=233)
lgb_model.fit(X=X_tra, y=y_tra,
              eval_set=[(X_val, y_val)],
              verbose=False)
print('Valid Score is %.4f' % roc_auc_score(y_val, lgb_model.predict_proba(X_val)[:,1]))
final_predict = lgb_model.predict_proba(test_features)[:,1]

if quick_run == False:
    sample_df = pd.read_csv('../input/donorschoose-application-screening/sample_submission.csv')
    sample_df['project_is_approved'] = final_predict
    sample_df.to_csv('submission.csv', index=False)


# In[ ]:


from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

predict_valid_list = [pred_valid_rf, pred_valid_lgb, pred_valid_dpcnn, pred_valid_ftrl, pred_valid_lgb_bool]
predict_test_list = [pred_test_avg_rf, pred_test_avg_lgb, pred_test_avg_dpcnn, pred_test_avg_ftrl, pred_test_avg_lgb_bool]

valid_results = np.hstack([scaler.fit_transform(item.reshape((item.shape[0], 1))) for item in predict_valid_list])
test_results = np.hstack([scaler.fit_transform(item.reshape((item.shape[0], 1))) for item in predict_test_list])
train_features = np.hstack([valid_results ])
test_features = np.hstack([test_results ])

lgb_model = lgb.LGBMClassifier(  n_jobs=4,
                                 max_depth=4,
                                 metric="auc",
                                 n_estimators=400,
                                 num_leaves=10,
                                 boosting_type="gbdt",
                                 learning_rate=0.01,
                                 feature_fraction=0.45,
                                 colsample_bytree=0.45,
                                 bagging_fraction=0.4,
                                 bagging_freq=5,
                                 reg_lambda=0.2)
X_tra, X_val, y_tra, y_val = train_test_split(train_features, train_target, train_size=0.8, random_state=233)
lgb_model.fit(X=X_tra, y=y_tra,
              eval_set=[(X_val, y_val)],
              verbose=False)
print('Valid Score is %.4f' % roc_auc_score(y_val, lgb_model.predict_proba(X_val)[:,1]))
final_predict = lgb_model.predict_proba(test_features)[:,1]

if quick_run == False:
    sample_df = pd.read_csv('../input/donorschoose-application-screening/sample_submission.csv')
    sample_df['project_is_approved'] = final_predict
    sample_df.to_csv('submission_with_lgb_bool.csv', index=False)


# # TODO LIST:
# 
# 1.  Text propressing, move stop words, word stem.
# 2.  Meta features of texts,  text length, word length and so on.
# 3. More nn networks, such as BiRNN, RCNN, which are widely used in Toxic Comment Classification Challenge.
# 4. Try MLP and bool features, like [https://www.kaggle.com/lopuhin/mercari-golf-0-3875-cv-in-75-loc-1900-s](http://)