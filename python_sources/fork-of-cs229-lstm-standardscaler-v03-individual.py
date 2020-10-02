# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.

import gc
#to plot within notebook
import matplotlib.pyplot as plt
from matplotlib import pyplot
# get_ipython().run_line_magic('matplotlib', 'inline')

#setting figure size
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,10

#for normalizing data
from sklearn.preprocessing import MinMaxScaler, StandardScaler
scaler1 = MinMaxScaler(feature_range=(0, 1))
scaler2 = StandardScaler()

from sklearn.metrics import log_loss, mean_squared_error
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

#Set missing value
pd.options.mode.use_inf_as_na = False

#date time
import datetime


sample_assetCode = 'ABT.N'


merge_data = pd.read_pickle('../input/merge_fianl_df.pkl')




train_index = (merge_data.date < datetime.date(2016, 1, 1)) & ( merge_data.assetCode == sample_assetCode)
test_index = (merge_data.date >= datetime.date(2016, 1, 1)) & ( merge_data.assetCode == sample_assetCode)
train = merge_data[train_index]
test = merge_data[test_index]





# temp_sample = merge_data.loc[:,('assetCode', 'date', 'returnsOpenNextMktres10')]

# train.groupby('assetCode').apply(np.max(temp_sample.returnsOpenNextMktres10))
# #plot
# sample_assetCode = 'BKS.N'
# plt.plot(merge_data[merge_data.assetCode == sample_assetCode].date, merge_data[merge_data.assetCode == sample_assetCode].returnsOpenNextMktres10)
# plt.title('returnsOpenNextMktres10 on Sample assetCode == ' + sample_assetCode)
# a3d = train.drop(['returnsOpenNextMktres10','date', 'assetCode', 'assetName', 'news_time', 'market_time'], axis=1).values
# train.set_index(['assetCode','date'])
# a3d = np.array(list(train.groupby('assetCode').apply(pd.DataFrame.values)))
# a3d.shape



# In[ ]:

#Standardilization, and converting dataset into x_train and y_train np.array
scaler = scaler2
scaled_x = scaler.fit_transform(merge_data.drop(['returnsOpenNextMktres10','date', 'assetCode', 'assetName', 'news_time', 'market_time'], axis=1))
orginal_y = np.array(merge_data.returnsOpenNextMktres10).reshape(-1, 1)
scaled_y = scaler.fit_transform(orginal_y)

# np.savetxt('scaled_x.csv', scaled_x, delimiter=",")
# np.savetxt('scaled_y.csv', scaled_y, delimiter=",")
# np.savetxt('orginal_y.csv', orginal_y, delimiter=",")



# In[ ]:


x_train = scaled_x[train_index]
y_train = scaled_y[train_index]

x_test = scaled_x[test_index]
y_test = scaled_y[test_index]
y_test_orginal = orginal_y[test_index]

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)




# Long Short Term Memory (LSTM)

# In[ ]:

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM


# In[ ]:
# reshape input to be 3D [samples, timesteps, features]
x_train = x_train.reshape((x_train.shape[0], 1, x_train.shape[1]))
x_test = x_test.reshape((x_test.shape[0], 1, x_test.shape[1]))
print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)

x_train_3 = np.zeros((x_train.shape[0]-3, 3, x_train.shape[2]))
for t in range(3, x_train.shape[0]):
    x_train_3[t-3, 0, :] = x_train[t-3, 0, :]
    x_train_3[t-3, 1, :] = x_train[t-2, 0, :]
    x_train_3[t-3, 2, :] = x_train[t-1, 0, :]
y_train_3 = y_train[3:]
x_test_3 = np.zeros((x_test.shape[0]-3, 3, x_test.shape[2]))
for t in range(3, x_test.shape[0]):
    x_test_3[t-3, 0, :] = x_test[t-3, 0, :]
    x_test_3[t-3, 1, :] = x_test[t-2, 0, :]
    x_test_3[t-3, 2, :] = x_test[t-1, 0, :]
y_test_3 = y_test[3:]
y_test_orginal_3 = y_test_orginal[3:]
print(x_train_3.shape, y_train_3.shape, x_test_3.shape, y_test_3.shape)



# In[ ]:
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2])))
# model.add(LSTM(units=50))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# # history = model.fit(x_train, y_train, epochs=5, batch_size=72, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.036874786328739285
# # sign_accuaracy =  0.49234361319194475
# # history = model.fit(x_train, y_train, epochs=10, batch_size=5, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.006475105070768455
# # sign_accuaracy =  0.478957096993871
# history = model.fit(x_train, y_train, epochs=10, batch_size=50, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.006773932511615138
# # sign_accuaracy =  0.49793429970489994



# In[ ]:
# batch_size = 50
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2]), dropout=0.5, stateful = False))
# model.add(LSTM(units=50, dropout=0.5))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# history = model.fit(x_train, y_train, epochs=10, batch_size=batch_size, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.005576371512983373
# # sign_accuaracy =  0.4887699841099977
# # model_v02_1 = model



# # In[ ]:
# batch_size = 50
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2]), dropout=0.5, stateful = False))
# model.add(LSTM(units=50, dropout=0.5))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# history = model.fit(x_train, y_train, epochs=10, batch_size=batch_size, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.0016818516830942162
# # sign_accuaracy =  0.5088967971530249
# # model_v03_1 = model



# # In[ ]:
# batch_size = 5
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2]), dropout=0.5, stateful = False))
# model.add(LSTM(units=50, dropout=0.5))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# history = model.fit(x_train, y_train, epochs=10, batch_size=batch_size, verbose=2, validation_data=(x_test, y_test))
# # mes =  0.0016768612091851182
# # sign_accuaracy =  0.5231316725978647
# # model_v03_2 = model



# # In[ ]:
# batch_size = 5
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2]), dropout=0.5, stateful = False))
# model.add(LSTM(units=50, dropout=0.5))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# history = model.fit(x_train, y_train, epochs=10, batch_size=batch_size, verbose=2)
# # mes =  0.0015348001249528564
# # sign_accuaracy =  0.5693950177935944
# # model_v03_3 = model


# # In[ ]:
# batch_size = 5
# # create and fit the LSTM network
# model = Sequential()
# model.add(LSTM(50, return_sequences=True,  input_shape=(x_train.shape[1], x_train.shape[2]), dropout=0.5, stateful = False))
# model.add(LSTM(units=50, dropout=0.5))
# model.add(Dense(1))

# # fit network
# model.compile(loss='mean_squared_error', optimizer='adam')
# history = model.fit(x_train, y_train, epochs=10, batch_size=batch_size, verbose=2)
# # mes =  0.0014741747947406602
# # sign_accuaracy =  0.5907473309608541
# # model_v03_4 = model
# # history = model.fit(x_train, y_train, epochs=50, batch_size=batch_size, verbose=2)
# # mes =  0.0014838772274075737
# # sign_accuaracy =  0.5338078291814946
# # model_v03_5 = model

















# # In[ ]:
# #predicting 246 values, using past 60 from the train data
# y_pred = model.predict(x_test)
# y_pred = scaler.inverse_transform(y_pred)
# test['Prediction'] = y_pred

# # In[ ]:
# #predicted mean_squared_error
# mes=mean_squared_error(y_test_orginal,y_pred)
# print("mes = ",mes)

# # predicted sign accuaracy
# sign_accuaracy = np.sum(y_pred*y_test_orginal>0) / len(y_pred)
# print("sign_accuaracy = ",sign_accuaracy)

# # In[ ]:


# #plot
# plt.figure(figsize=(16,8))
# plt.plot(train[train.assetCode == sample_assetCode].date, train[train.assetCode == sample_assetCode].returnsOpenNextMktres10)
# plt.plot(test[test.assetCode == sample_assetCode].date, test[test.assetCode == sample_assetCode].returnsOpenNextMktres10)
# plt.plot(test[test.assetCode == sample_assetCode].date, test[test.assetCode == sample_assetCode].Prediction)
# plt.title('returnsOpenNextMktres10 on Sample assetCode == ' + sample_assetCode)

# # In[ ]:
# # plot history
# plt.figure(figsize=(16,8))
# pyplot.plot(np.array(history.history['loss']) / x_train.shape[0], label='train')
# # plt.figure(figsize=(16,8))
# # pyplot.plot(np.array(history.history['val_loss']) / x_test.shape[0], label='test')
# pyplot.legend()
# pyplot.show()














# In[ ]:
batch_size = 5
# create and fit the LSTM network
model = Sequential()
model.add(LSTM(50, return_sequences=True,  input_shape=(x_train_3.shape[1], x_train_3.shape[2]), dropout=0.5, stateful = False))
model.add(LSTM(units=50, dropout=0.5))
model.add(Dense(1))

# fit network
model.compile(loss='mean_squared_error', optimizer='adam')
history = model.fit(x_train_3, y_train_3, epochs=10, batch_size=batch_size, verbose=2)



# In[ ]:
#predicting 246 values, using past 60 from the train data
y_pred = model.predict(x_test_3)
y_pred = scaler.inverse_transform(y_pred)
test['Prediction'] = y_pred

# In[ ]:
#predicted mean_squared_error
mes=mean_squared_error(y_test_orginal_3,y_pred)
print("mes = ",mes)

# predicted sign accuaracy
sign_accuaracy = np.sum(y_pred*y_test_orginal_3>0) / len(y_pred)
print("sign_accuaracy = ",sign_accuaracy)

# In[ ]:


#plot
plt.figure(figsize=(16,8))
plt.plot(train[train.assetCode == sample_assetCode].date, train[train.assetCode == sample_assetCode].returnsOpenNextMktres10)
plt.plot(test[test.assetCode == sample_assetCode].date, test[test.assetCode == sample_assetCode].returnsOpenNextMktres10)
plt.plot(test[test.assetCode == sample_assetCode].date, test[test.assetCode == sample_assetCode].Prediction)
plt.title('returnsOpenNextMktres10 on Sample assetCode == ' + sample_assetCode)

# In[ ]:
# plot history
plt.figure(figsize=(16,8))
pyplot.plot(np.array(history.history['loss']) / x_train.shape[0], label='train')
# plt.figure(figsize=(16,8))
# pyplot.plot(np.array(history.history['val_loss']) / x_test.shape[0], label='test')
pyplot.legend()
pyplot.show()