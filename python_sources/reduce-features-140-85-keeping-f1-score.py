#!/usr/bin/env python
# coding: utf-8

# # Reduce features without degrading F1 score
# I found many needless columns in dataset. I removed them and ran prediction. Finally, the F1 score was almost the same as full features prediction with LightGBM.
# 
# **Leaderboard score**
# * 0.428 : reduced(85 features)
# * 0.425 : full(140 features)
# 
# This data processing gives us efficient predictions and saving time in future analyses.
# 
# 
# 

# In[ ]:


input_dir = '../input/'
working_dir = '../working/'


# In[ ]:


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


train = pd.read_csv(os.path.join(input_dir, 'train.csv'))
test = pd.read_csv(os.path.join(input_dir, 'test.csv'))

# Set index
train.index = train['Id'].values
test.index = test['Id'].values

print(train.shape)
print(test.shape)


# ### Clean Data
# I picked the following function from ["Data cleaning and random forest
# "](https://www.kaggle.com/katacs/data-cleaning-and-random-forest)
# 
# * dependency 'no' -> 0
# * edjefa, edjefe 'no' -> 0,  'yes' -> 1
# * meaneduc NaN -> mean escolari of household
# * v2a1 NaN -> 0
# * v18q1 NaN -> 0
# * rez_esc NaN -> 0

# In[ ]:


# copy from https://www.kaggle.com/katacs/data-cleaning-and-random-forest
def data_cleaning(data):
    data['dependency']=np.sqrt(data['SQBdependency'])
    data['rez_esc']=data['rez_esc'].fillna(0)
    data['v18q1']=data['v18q1'].fillna(0)
    data['v2a1']=data['v2a1'].fillna(0)
    
    conditions = [
    (data['edjefe']=='no') & (data['edjefa']=='no'), #both no
    (data['edjefe']=='yes') & (data['edjefa']=='no'), # yes and no
    (data['edjefe']=='no') & (data['edjefa']=='yes'), #no and yes 
    (data['edjefe']!='no') & (data['edjefe']!='yes') & (data['edjefa']=='no'), # number and no
    (data['edjefe']=='no') & (data['edjefa']!='no') # no and number
    ]
    choices = [0, 1, 1, data['edjefe'], data['edjefa']]
    data['edjefx']=np.select(conditions, choices)
    data['edjefx']=data['edjefx'].astype(int)
    data.drop(['edjefe', 'edjefa'], axis=1, inplace=True)
    
    meaneduc_nan=data[data['meaneduc'].isnull()][['Id','idhogar','escolari']]
    me=meaneduc_nan.groupby('idhogar')['escolari'].mean().reset_index()
    for row in meaneduc_nan.iterrows():
        idx=row[0]
        idhogar=row[1]['idhogar']
        m=me[me['idhogar']==idhogar]['escolari'].tolist()[0]
        data.at[idx, 'meaneduc']=m
        data.at[idx, 'SQBmeaned']=m*m
        
    return data


# In[ ]:


train = data_cleaning(train)
test = data_cleaning(test)


# ### Extract heads of household

# In[ ]:


train = train.query('parentesco1==1')
train = train.drop('parentesco1', axis=1)
test = test.drop('parentesco1', axis=1)
print(train.shape)


# ## Convert one-hot variables into numeric
# * 'epared', 'etecho', 'eviv' and 'instlevel' can be converted into numeric
# *  like (bad, regular, good) -> (0 ,1, 2)

# In[ ]:


def get_numeric(data, status_name):
    # make a list of column names containing 'sataus_name'
    status_cols = [s for s in data.columns.tolist() if status_name in s]
    print('status column names')
    print(status_cols)
    # make a DataFrame with only status_cols
    status_df = data[status_cols]
    # change its column name like ['epared1', 'epared2', 'epared3'] -> [0, 1, 2]
    status_df.columns = list(range(status_df.shape[1]))
    # get the column name which has the biggest value in every row
    # see https://stackoverflow.com/questions/26762100/reconstruct-a-categorical-variable-from-dummies-in-pandas
    # this is pandas.Series
    status_numeric = status_df.idxmax(1)
    # set Series name
    status_numeric.name = status_name
    # add status_numeric as a new column
    data = pd.concat([data, status_numeric], axis=1)
    return data


# In[ ]:


status_name_list = ['epared', 'etecho', 'eviv', 'instlevel']
for status_name in status_name_list:
    train = get_numeric(train, status_name)
    test = get_numeric(test, status_name)


# ## Delete needless columns
# ### redundant columns
# * r4t3, tamviv, tamhog, hhsize ... almost the same as hogar_total
# * v14a ... almost the same as saniatrio1
# * v18q, mobilephone ... can be generated by v18q1, qmobilephone
# * SQBxxx, agesq ... squared values
# * parentescoxxx ... only heads of household are in dataset now
# 
# ### extra columns
# (One-hot variables should be linearly independent. For example, female (or male) column is needless, because whether the sample is female or not can be explained only with male (or female) column.)
# * paredother, pisoother, abastaguano, energcocinar1, techootro, sanitario6, elimbasu6, estadocivil7, parentesco12, tipovivi5, lugar1, area1, female
# 
# ### obsolete columns
# * epared1~3, etecho1~3, eviv1~3, instlevel1~9 ... we don't use these columns anymore.
# 

# In[ ]:


needless_cols = ['r4t3', 'tamhog', 'tamviv', 'hhsize', 'v18q', 'v14a', 'agesq',
                 'mobilephone', 'paredother', 'pisoother', 'abastaguano',
                 'energcocinar1', 'techootro', 'sanitario6', 'elimbasu6',
                 'estadocivil7', 'parentesco12', 'tipovivi5',
                 'lugar1', 'area1', 'female', 'epared1', 'epared2',
                 'epared3', 'etecho1', 'etecho2', 'etecho3',
                 'eviv1', 'eviv2', 'eviv3', 'instlevel1', 'instlevel2',
                 'instlevel3', 'instlevel4', 'instlevel5', 'instlevel6',
                 'instlevel7', 'instlevel8', 'instlevel9']
SQB_cols = [s for s in train.columns.tolist() if 'SQB' in s]
parentesco_cols = [s for s in train.columns.tolist() if 'parentesco' in s]

needless_cols.extend(SQB_cols)
needless_cols.extend(parentesco_cols)

train = train.drop(needless_cols, axis=1)
test = test.drop(needless_cols, axis=1)


# In[ ]:


ori_train = pd.read_csv(os.path.join(input_dir, 'train.csv'))
ori_train_X = ori_train.drop(['Id', 'Target', 'idhogar'], axis=1)

train_X = train.drop(['Id', 'Target', 'idhogar'], axis=1)

print('feature columns \n {} -> {}'.format(ori_train_X.shape[1], train_X.shape[1]))


# ## Simple LightGBM

# In[ ]:


# Split data
train_Id = train['Id'] # individual ID
train_idhogar = train['idhogar'] # household ID
train_y = train['Target'] # Target value
train_X = train.drop(['Id', 'Target', 'idhogar'], axis=1) # features

test_Id = test['Id'] # individual ID
test_idhogar = test['idhogar'] # household ID
test_X = test.drop(['Id', 'idhogar'], axis=1) # features

# Union train and test
all_Id = pd.concat([train_Id, test_Id], axis=0, sort=False)
all_idhogar = pd.concat([train_idhogar, test_idhogar], axis=0, sort=False)
all_X = pd.concat([train_X, test_X], axis=0, sort=False)


# In[ ]:


from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, f1_score, make_scorer
import lightgbm as lgb

X_train, X_test, y_train, y_test = train_test_split(train_X, train_y, test_size=0.1, random_state=0)

F1_scorer = make_scorer(f1_score, greater_is_better=True, average='macro')

# gbm_param = {
#     'num_leaves':[210]
#     ,'min_data_in_leaf':[9]
#     ,'max_depth':[14]
# }
# gbm = GridSearchCV(
#     lgb.LGBMClassifier(objective='multiclassova', class_weight='balanced', seed=0)
#     , gbm_param
#     , scoring=F1_scorer
# )


# params = {'num_leaves': 13, 'min_data_in_leaf': 23, 'max_depth': 11, 'learning_rate': 0.09, 'feature_fraction': 0.74}
gbm = lgb.LGBMClassifier(boosting_type='dart', objective='multiclassova', class_weight='balanced', random_state=0)
# gbm.set_params(**params)

gbm.fit(X_train, y_train)
# gbm.best_params_


# In[ ]:


import pickle
with open(os.path.join(working_dir, '20180801_lgbm.pickle'), mode='wb') as f:
    pickle.dump(gbm, f)


# In[ ]:


y_test_pred = gbm.predict(X_test)
cm = confusion_matrix(y_test, y_test_pred)
f1 = f1_score(y_test, y_test_pred, average='macro')
print("confusion matrix: \n", cm)
print("macro F1 score: \n", f1)


# In[ ]:


pred = gbm.predict(test_X)
pred = pd.Series(data=pred, index=test_Id.values, name='Target')
pred = pd.concat([test_Id, pred], axis=1, join_axes=[test_Id.index])
pred.to_csv('20180801_lgbm.csv', index=False)
