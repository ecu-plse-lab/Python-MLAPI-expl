#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

train_data_df = pd.read_csv('../input/train.csv')
test_data_df = pd.read_csv('../input/test.csv')


# In[ ]:


# Memory saving function credit to https://www.kaggle.com/gemartin/load-data-reduce-memory-usage
def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.        
    """
    #start_mem = df.memory_usage().sum() / 1024**2
    #print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)

    #end_mem = df.memory_usage().sum() / 1024**2
    #print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    #print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df


# In[ ]:


import numpy as np

train_data_df = reduce_mem_usage(train_data_df)
test_data_df = reduce_mem_usage(test_data_df)


# In[ ]:


mean_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('mean').reset_index().loc[:, 'assists':'winPoints']
size_match_features = pd.DataFrame(train_data_df.groupby(['matchId'])[train_data_df.columns[3]].agg('size').reset_index()[train_data_df.columns[3]])
size_match_features.columns = ['match_size']
# max_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('max').reset_index().loc[:, 'assists':'winPoints']
# min_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('min').reset_index().loc[:, 'assists':'winPoints']
# std_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('std').reset_index().loc[:, 'assists':'winPoints']


# In[ ]:


# features_one = mean_match_features.join(max_match_features, lsuffix='_match_mean', rsuffix='_match_max')
# features_two = min_match_features.join(std_match_features, lsuffix='_match_min', rsuffix='_match_std')
# features_1 = features_one.join(features_two)
# features_1 = features_1.fillna(0.0)
# features_1 = features_1.replace([np.inf, -np.inf], 0.0)
features_1 = mean_match_features.join(size_match_features, lsuffix='_match_mean', rsuffix='_match_size')
features_1['matchId'] = list(set(train_data_df.sort_values(by=['matchId'])['matchId'].values))


# In[ ]:


mean_group_features = train_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('mean').reset_index().loc[:, 'assists':'winPoints']
max_group_features = train_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('max').reset_index().loc[:, 'assists':'winPoints']
min_group_features = train_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('min').reset_index().loc[:, 'assists':'winPoints']
size_group_features = pd.DataFrame(train_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3]].agg('size').reset_index()[train_data_df.columns[3]])
size_group_features.columns = ['group_size']


# In[ ]:


features_three = mean_group_features.join(max_group_features, lsuffix='_group_mean', rsuffix='_group_max')
features_four = min_group_features.join(size_group_features, lsuffix='_group_min', rsuffix='_group_size')
features_2 = features_three.join(features_four)
features_2['matchId'] = train_data_df.groupby(['matchId', 'groupId'])['matchId'].agg('mean').values
features_2 = features_2.fillna(0.0)
features_2 = features_2.replace([np.inf, -np.inf], 0.0)


# In[ ]:


features = pd.merge(features_2, features_1, on='matchId', how='right')


# In[ ]:


features = features.drop(['matchId'], axis=1)
features


# In[ ]:


targets = train_data_df.groupby(['matchId', 'groupId'])['winPlacePerc'].agg('mean').reset_index()['winPlacePerc']
targets


# In[ ]:


train_data_df.groupby(['matchId', 'groupId'])['winPlacePerc'].agg('max')


# In[ ]:


train_features = features.values[0:np.int32(0.8*len(features))]
train_targets = targets.values[0:np.int32(0.8*len(features))]

val_features = features.values[np.int32(0.8*len(features)):len(features)]
val_targets = targets.values[np.int32(0.8*len(features)):len(features)]


# In[ ]:


import sklearn


# In[ ]:


from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(-1, 1)).fit(features.values)

train_features = scaler.transform(train_features)
val_features = scaler.transform(val_features)


# In[ ]:


import catboost
from catboost import CatBoostRegressor

model = CatBoostRegressor(iterations=250, learning_rate=0.1, eval_metric='MAE', max_depth=8)
model.fit(train_features, train_targets, eval_set=(val_features, val_targets))


# In[ ]:


mean_match_features = test_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('mean').reset_index().loc[:, 'assists':'winPoints']
size_match_features = pd.DataFrame(test_data_df.groupby(['matchId'])[train_data_df.columns[3]].agg('size').reset_index()[train_data_df.columns[3]])
size_match_features.columns = ['match_size']
# max_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('max').reset_index().loc[:, 'assists':'winPoints']
# min_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('min').reset_index().loc[:, 'assists':'winPoints']
# std_match_features = train_data_df.groupby(['matchId'])[train_data_df.columns[3:-1]].agg('std').reset_index().loc[:, 'assists':'winPoints']


# In[ ]:


# features_one = mean_match_features.join(max_match_features, lsuffix='_match_mean', rsuffix='_match_max')
# features_two = min_match_features.join(std_match_features, lsuffix='_match_min', rsuffix='_match_std')
# features_1 = features_one.join(features_two)
# features_1 = features_1.fillna(0.0)
# features_1 = features_1.replace([np.inf, -np.inf], 0.0)
features_1 = mean_match_features.join(size_match_features, lsuffix='_match_mean', rsuffix='_match_size')
features_1['matchId'] = list(set(test_data_df.sort_values(by=['matchId'])['matchId'].values))


# In[ ]:


mean_group_features = test_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('mean').reset_index().loc[:, 'assists':'winPoints']
max_group_features = test_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('max').reset_index().loc[:, 'assists':'winPoints']
min_group_features = test_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3:-1]].agg('min').reset_index().loc[:, 'assists':'winPoints']
size_group_features = pd.DataFrame(test_data_df.groupby(['matchId','groupId'])[train_data_df.columns[3]].agg('size').reset_index()[train_data_df.columns[3]])
size_group_features.columns = ['group_size']


# In[ ]:


features_three = mean_group_features.join(max_group_features, lsuffix='_group_mean', rsuffix='_group_max')
features_four = min_group_features.join(size_group_features, lsuffix='_group_min', rsuffix='_group_size')
features_2 = features_three.join(features_four)
features_2['matchId'] = test_data_df.groupby(['matchId', 'groupId'])['matchId'].agg('mean').values
features_2 = features_2.fillna(0.0)
features_2 = features_2.replace([np.inf, -np.inf], 0.0)


# In[ ]:


features = pd.merge(features_2, features_1, on='matchId', how='right')


# In[ ]:


matches = test_data_df.groupby(['matchId', 'groupId'])['matchId'].agg('mean').values


# In[ ]:


groups = test_data_df.groupby(['matchId', 'groupId'])['groupId'].agg('mean').values


# In[ ]:


features = features.drop(['matchId'], axis=1)


# In[ ]:


test_features = features.values
test_features = scaler.transform(test_features)


# In[ ]:


predictions = model.predict(test_features)


# In[ ]:


features['winPlacePercPred'] = predictions
features['matchId'] = matches
features['groupId'] = groups
group_preds = features.groupby(['matchId', 'groupId'])['winPlacePercPred'].agg('mean').groupby(['matchId']).rank(pct=True)


# In[ ]:


test_data_df = test_data_df.sort_values(['matchId', 'groupId'])


# In[ ]:


dictionary = dict(zip(features['groupId'].values, group_preds.values))


# In[ ]:


new_ranking_preds = []
    
for i in test_data_df['groupId'].values:
    new_ranking_preds.append(dictionary[i])
    
test_data_df['winPlacePercPred'] = new_ranking_preds


# In[ ]:


import numpy as np

predictions = pd.DataFrame(np.transpose(np.array([test_data_df.loc[:, 'Id'], test_data_df['winPlacePercPred']])))
predictions.columns = ['Id', 'winPlacePerc']
predictions['Id'] = np.int32(predictions['Id'])
predictions = predictions.sort_values(by=['Id'])

predictions.head(20)


# In[ ]:


maxPlaces = test_data_df.sort_values(by=['Id'])['maxPlace'].values
numGroups = test_data_df.sort_values(by=['Id'])['numGroups'].values
new_predictions = predictions['winPlacePerc'].values

for i in range(0, len(test_data_df)):
    gap = 1.0 / (maxPlaces[i] - 1.0)
    new_predictions[i] = round(new_predictions[i]/gap)*gap


# In[ ]:


predictions['winPlacePerc'] = new_predictions


# In[ ]:


predictions.head(20)


# In[ ]:


predictions.to_csv('PUBG_preds.csv', index=False)


# In[ ]:



