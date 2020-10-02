#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import sqrt
from datetime import datetime, timedelta,date
import seaborn as sns
from sklearn.metrics import mean_squared_error
#importing machine learning libraries
import pickle
import gc # to free some space from the memory
from sklearn.model_selection import KFold


#importing regressors
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor 
from xgboost import plot_importance
from lightgbm import plot_importance
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from lightgbm import LGBMRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB


from sklearn.feature_selection import SelectFromModel

#ignoring warnings
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import GridSearchCV

# time seires staff
import statsmodels.api as sm
import itertools
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX

from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.stattools import adfuller, acf, pacf,arma_order_select_ic

plt.style.use('ggplot') # plots style
# fixing the seed so that the code is reproduceable
random_state = 1


# In[ ]:


# Reading Data
item_categories = pd.read_csv("../input/translated/item_categories-translated.csv")
items = pd.read_csv("../input/translated/items-translated.csv")
sales = pd.read_csv("../input/competitive-data-science-predict-future-sales/sales_train.csv")
shops = pd.read_csv("../input/translated/shops-translated.csv")
test = pd.read_csv("../input/competitive-data-science-predict-future-sales/test.csv")


# Let's take a look on the data

# In[ ]:


print("----------Shape of Data----------")
print(sales.shape)
print("----------first 5 rows----------")
print(sales.head(5))
print("-----------data frame overview-----------")
print(sales.info())
print("----------Missing value-----------")
print(sales.isnull().sum())


# 1) Date 

# In[ ]:


# changing the type of the column into date time, this will ease future feature engineering
sales.date = pd.to_datetime(sales.date)
print("First date --> " , sales.date.min())
print("Last date --> " , sales.date.max())


# 2) date_block_num

# In[ ]:


#what is the number of items soled at each month ?
sales_grouped_by_month =  sales.groupby('date_block_num')['item_cnt_day'].sum()
plt.figure(figsize=(15,8))
plt.title("Number of items sold by each month")
plt.xlabel("Date_block_num")
plt.ylabel("Items_sum")
sns.lineplot(data = sales_grouped_by_month)


# 3) shop_id

# In[ ]:


print("Nuumber of shops is : ",sales.shop_id.nunique())


# In[ ]:


# what is the number of items soled at each shop ?
items_ordered_grouped_by_shop =  sales.groupby('shop_id')['item_cnt_day'].sum()
plt.figure(figsize=(20,8))
plt.title("Number of items sold by each shop")
plt.xlabel("shop_id")
plt.ylabel("Items_mean")
sns.barplot(x = sales.shop_id.unique(),y =  items_ordered_grouped_by_shop )


# There is a significant difference between the shops in terms number of ordered items.

# 4) item_id

# In[ ]:


#number of unique items
print(sales.item_id.nunique())
best_5_items = sales.groupby("item_id")['item_cnt_day'].sum().sort_values(ascending = False ).head(5)
items_info = items[items.item_id.isin(best_5_items.index)].sort_values(by = 'item_id')
items_info


# In[ ]:


plt.figure(figsize = (20,8))
plt.title("Most 5 items ordered")
plt.xlabel("Item Name")
plt.ylabel("Number of ordered items")
sns.barplot(x = items_info.item_name_translated.values , y = best_5_items.values)


# This is a big number compared to the other !

# 5) item_price

# In[ ]:


print(sales.item_price.describe().round(2))
plt.figure(figsize = (20 , 8))
sns.boxplot(sales.item_price)


# removing high and negative prices 

# In[ ]:


len(sales[sales.item_price > 25000] )/len(sales)


# In[ ]:


sales = sales[(sales.item_price > 0) & (sales.item_price <= 25000)]


# In[ ]:


print(sales.item_price.describe().round(2))
plt.figure(figsize = (20 , 8))
sns.boxplot(sales.item_price)


# 6) item_cnt_day (target variable):

# In[ ]:


print(sales.item_cnt_day.describe().round())
plt.figure(figsize = (20 , 8))
sns.boxplot(sales.item_cnt_day)


# # Time series forcating

# # Arima ( AutoRegressive Integrated Moving Average )

# In[ ]:


ts=sales.groupby(["date_block_num"])["item_cnt_day"].sum()
ts.astype('float')
plt.figure(figsize=(16,8))
plt.title('Total Sales by month')
plt.xlabel('Time')
plt.ylabel('Sales')
plt.plot(ts);


# There is a clear trend and seasonality in the data let's look in more details by making decomposition. It's an additive model as the frequency and amplitude is not changing over time.

# In[ ]:


decomp = sm.tsa.seasonal_decompose(ts.values , freq = 12 ,model = 'additive' )
fig = decomp.plot()


# To use Arima the data must be stationary, i will make Augmented dicky fuller test to check stationarity there are other tests but this is the most popular.

# In[ ]:


def ADF_test(ts) :
    df_test = adfuller(ts , autolag = "AIC")
    df_output = pd.Series(df_test[0:4] , index = ['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    print(df_output)


# In[ ]:


ADF_test(ts)


# In[ ]:


# create a differenced series
def difference(dataset, interval=1):
    diff = []
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return pd.Series(diff)

# invert the series to the original scale
def inverse_difference(last_ob, value):
    return value + last_ob


# In[ ]:


stationary_ts = difference(ts)
ADF_test(stationary_ts)


# The data is stationary now, only best parameter values left and arima has 3 parameters: (p, d, q). These three parameters account for seasonality, trend, and noise. plus another 3 parameters (P,D,Q) which are the same but for inserting the seasonaloity with us and using SARIMA.

# In[ ]:


p = d = q = range(0, 2) # taking values 0 , 1 , 2 respectively 
pdq = list(itertools.product(p, d, q)) #combine them in a list
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in pdq] #seasonal parameters will take all combinations of (0,1,2) 
# 12 is the time spane of repeating the seasonal pattern it could be differnt but i just choosed to make it 12 for simplicity


# In[ ]:


# I will use grid search to find the optimal set of parameters

aic = []
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(stationary_ts,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            )
            results = mod.fit()
            aic.append(results.aic)
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue
print(min(aic))


# `(0, 1, 1)x(1, 1, 0, 12)` are best paramaters with the least aic score `434.490322082242` Let's do it ...

# In[ ]:


stationary_train = stationary_ts[0:27]
stationary_test = stationary_ts[27:33]
print('train: \n', stationary_train , '\n\n')
print('test: \n', stationary_test)


# In[ ]:


# Fit the model on the stationary_train set
mod = sm.tsa.statespace.SARIMAX(stationary_train,
                                order=(0, 1, 1),
                                seasonal_order=(1, 1, 0, 12))
results = mod.fit()


# We should always run model diagnostics to investigate any unusual behavior

# In[ ]:


fig = results.plot_diagnostics(figsize=(15, 12))
diagnostigs = fig


# diagnostics is not bad so we are good and continue

# In[ ]:


yhat = results.predict(28, 33).tolist() # Predicting based on the stationary data
test = ts[28:34].tolist() # cinverting ti list to loop through it
yhat = [inverse_difference(test[i], yhat[i]) for i in range(len(yhat))]
yhat = pd.Series(yhat , index = ts[28:34].index) # converting it from list to a series to get the index 


# In[ ]:


plt.figure(figsize = (12,6))
plt.plot(ts[0:28] , label='Train')
plt.plot(ts[28:34] , label='Test')
plt.plot(yhat , label='six-months ahead Forecast')
plt.xlabel('Date block num')
plt.ylabel('number of items sold')
plt.legend()
plt.show()
rmse = sqrt(mean_squared_error(ts[28:34],yhat))
print('RMSE: %.1f' % rmse , "\n")
print(ts.describe()[1:3].round())


# In[ ]:


sales_ts = sales[sales.item_cnt_day <= 20]
sales_ts=sales_ts.groupby(["date_block_num" , 'shop_id'])["item_cnt_day"].sum()
sales_ts = pd.DataFrame(sales_ts.reset_index()) # converting it to a dataframe 
sales_ts = sales_ts.rename(columns = {'item_cnt_day':'item_cnt_month'}) # now we are working monthly
sales_ts


# In[ ]:


decomp = sm.tsa.seasonal_decompose(sales_ts.item_cnt_month , freq = 12 ,model = 'additive' )
fig = decomp.plot()


# In[ ]:


test_rows = int(len(sales_ts) * 0.2)
train = sales_ts[ :-test_rows]
test = sales_ts[- test_rows :]
print(train)
print(test)


# In[ ]:


# I will use grid search to find the optimal set of parameters
aic = []
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(pd.Series(train.item_cnt_month),
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            )
            results = mod.fit()
            aic.append(results.aic)
            print('ARIMA{}x{} - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue
print(min(aic))


# `(1, 0, 1)x(0, 1, 1, 12)`

# In[ ]:


mod = sm.tsa.statespace.SARIMAX(train.item_cnt_month,
                                            order=(1,0,1),
                                            seasonal_order=(0,1,1,12)
                                           )
results = mod.fit()


# In[ ]:


test


# In[ ]:


yhat = results.predict(len(train)+2, len(sales_ts)+1).tolist() # Predicting based on the stationary data
yhat = pd.Series(yhat , index = test.index) # converting it from list to a series to get the index 


# In[ ]:


len(yhat)


# In[ ]:


len(test)


# In[ ]:


plt.figure(figsize = (12,6))
plt.plot(train.item_cnt_month , label='Train')
plt.plot(test.item_cnt_month , label='Test')
plt.plot(yhat , label='six-months ahead Forecast')
plt.xlabel('Date block num')
plt.ylabel('number of items sold')
plt.legend()
plt.show()
rmse = sqrt(mean_squared_error(test.item_cnt_month,yhat))
print('RMSE: %.1f' % rmse , "\n")
print(test.item_cnt_month.describe()[1:3].round())


# # Machine learning

# # Starting with a base model

# In[ ]:


# Getting ready for the base model
sales.date = pd.to_datetime(sales.date)
sales['year'] = sales.date.dt.year

base = sales.copy() # leaving the original dataset untouched
base = pd.DataFrame(base.groupby(['date_block_num','shop_id','year','item_id'])['item_cnt_day'].sum())
base = base.reset_index() 
base = base.rename(columns = {'item_cnt_day':'item_cnt_month'})
base


# In[ ]:


def get_data_splits(df) :
    """
    Splits a dataframe into 90% train, 10% validation but first order by the date_block_num. 
    
    """
    df = df.sort_values(by = 'date_block_num') #sort values by the date_clock_num so that the test set is the last period of time
    train = df[df.date_block_num < 32]
    validation = df[df.date_block_num > 31] # taking the last 2 months to simulate the test set 
    return train, validation


# In[ ]:


train, validation = get_data_splits(base)


# In[ ]:



X_train = train.drop('item_cnt_month' , axis = 1)
y_train = train.item_cnt_month

X_val = validation.drop('item_cnt_month' , axis = 1)
y_val = validation.item_cnt_month


models = []
models.append(('LGBM',LGBMRegressor(n_jobs = -1 , random_state = random_state)))
models.append(('XGB' , XGBRegressor(n_jobs= -1 ,random_state = random_state)) )
models.append(('RF' ,RandomForestRegressor(verbose = False ,random_state = random_state) ))
models.append(('LR' ,LinearRegression() ))
for name, model in models :
    model.fit(X_train, y_train)
    rmse = sqrt( mean_squared_error(model.predict(X_val), y_val ) ) 
    print(name ,": ",rmse )


# These are the values of the base model and will be improved after every part in the notebook
# 
# LGBM :  16.25462807143281
# 
# XGB :  16.135782269473
# 
# RF :  14.926916180602934
# 
# LR :  16.547247380574465

# In[ ]:


# i want to insert in the first position the date_block_num to match the test with the train
test = pd.read_csv("../input/competitive-data-science-predict-future-sales/test.csv")
test.insert(0 , 'date_block_num' , [34 for i in range(0, len(test) )])
test = test.drop('ID' , axis= 1)
test['year'] = 2015
test


# In[ ]:


# submitting to the leaderboard
xgb = XGBRegressor(verbose = False , ,random_state = random_state)
xgb.fit(base.drop('item_cnt_month',axis = 1), base.item_cnt_month)
preds_xgb = xgb.predict(test)
sub = sample_submission
sub.item_cnt_month = preds_xgb
sub.to_csv('sub.csv' , index = False)


# I got about 6 RMSE with the base model

# # Feature Engineering

# In[ ]:


sales1 = base.copy() # Continue on the base model


# In[ ]:


# removing duplicate rows 
sales1.drop_duplicates(inplace = True , keep = 'first')


# In[ ]:


# what is the portion of data that has target variable value with more than 20
round((len(sales1[sales1.item_cnt_month > 20]) / len(sales1)),3)


# item_cnt_day has natural ouliers with values more than 20 and although they represent the real life but they are not a lot and make a lot of niose to the model so i will trim any value more than 20 and we will lose a small fraction of the data anyways
# 
# 

# In[ ]:


sales1 = sales1[sales1.item_cnt_month <= 20]
print(sales1.item_cnt_month.describe().round())
plt.figure(figsize = (20 , 8))
sns.boxplot(sales1.item_cnt_month)
plt.show()


# In[ ]:


# how many value in the target variable less than zero
print(len(sales1[sales1.item_cnt_month < 0 ]))
print(len(sales1[sales1.item_cnt_month < 0 ]) / len(sales1))


# I will remove the negative values as they will cause noise on the data

# In[ ]:


sales1 = sales1[sales1.item_cnt_month > 0]


# Testing the model performance after trimming all values greater than 20 and less than 0

# In[ ]:


# Validating after trimming the target variabel
train, validation = get_data_splits(sales1)
X_train = train.drop('item_cnt_month' , axis = 1)
y_train = train.item_cnt_month

X_val = validation.drop('item_cnt_month' , axis = 1)
y_val = validation.item_cnt_month


models = []
models.append(('XGB' , XGBRegressor(n_jobs= -1 , random_state = random_state)) )
models.append(('LGBM' ,LGBMRegressor( random_state = random_state) ))
for name, model in models :
    model.fit(X_train, y_train)
    rmse = sqrt( mean_squared_error(model.predict(X_val), y_val ) ) 
    print(name ,": ",rmse )


# XGB :  1.9368071858443434
# 
# LGBM :  1.8915577818949325

# Trimming the target variable improved the performance a lot on the validation data

# Since the results of lightGBM and XGB are very similar but light gbm is much much faster i will continue using lightgbm

# In[ ]:


# refitting on the full data and see the impact
lgbm = LGBMRegressor( n_jobs = -1 , random_state = random_state)
lgbm.fit(sales1.drop(['item_cnt_month'],axis = 1), sales1.item_cnt_month)

# saving the model in order to run it again witout taking so much time
file_name = 'lgbm_after_trimming.sav'
pickle.dump(lgbm , open(file_name, 'wb'))


# In[ ]:


# submitting in the leaderboard
# load the file from the disk
lgbm = pickle.load(open('/content/lgbm_after_trimming (1).sav', 'rb'))
test = test[sales1.drop('item_cnt_month',axis = 1).columns] # sorting column names in the same order
preds = lgbm.predict(test)
sub = sample_submission
sub.item_cnt_month = preds
sub.to_csv('lgbm_after_trimming.csv' , index = False)


# In[ ]:


lgbm = pickle.load(open('/content/lgbm_after_trimming (1).sav', 'rb'))
# ploting the importance
plot_importance(lgbm)


# ![](data:image/png;base64,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BAQEEB8ff82yW73gScqPilGkHDRr1oy9e/dSs2bNG95CsGnTJp555hm6d+8OXP7levjwYSpXrmxfx93dncLCQofHXblCNDk52T4vJSWF//znP8XKlZiYeN0yLy/btm1j0KBB9umtW7fajxDr16/PuXPn2L9/v33epUuX+Pe//+3wmOu5UkCFhYW4uLgA2Lf17bff8sADDwDw22+/XXMUW5QmTZoA8MMPP9CtW7drljdr1oyMjAxyc3Np0KBBibYtzqerUkXKwauvvsqBAwd49tln2b59O0lJSWzYsIFhw4Zx/PhxAOrUqcPKlSvZvn07+/fv54UXXnAoO4A77riDhIQEjh07RlpaGvn5+Xh5edGmTRsmTpzInj17SEhIoHfv3nh4eBSZ66233mLlypWMGDGC3bt3c+zYMb7//nv69etHTk5OmYzF1b7++mvi4uI4cuQIM2fOZMmSJYwcORKAe++9lxYtWtCzZ09++ukn9u3bR+/evcnNzWXgwIE33e4dd9wBwFdffUVqaipZWVkEBQVRqVIl5s2bx+HDh/n555/p0aMHXl5eJcocFRXFM888w6BBg1i0aBHHjh0jPj7efkXtvffeS+fOnenatSsrVqzg+PHjJCQkMHPmTObNm3cLoyTlScUoUg7uvPNOtm7dSlZWFg888AD16tWjf//+5OTk2O9znDp1KtWqVaNjx4506tSJqlWrXnM0MnLkSEJDQ2nYsCGVKlXip59+AuDDDz/E19eX1q1b8/TTT/PCCy9QpUqVInN17NiR9evXs3fvXtq2bUt0dDTDhw/Hz8/vmtOgZeX1119n7dq1NGzYkHHjxjFx4kQef/xx4PLpyxUrVlC3bl0eeughmjdvzpkzZ1izZg2hoaE33W7z5s0ZNmwYL774ImFhYQwZMgSr1crnn3/OsWPHiI6OJiYmhpdffrlYY3W1jz76iBdffJHXXnuNO++8k8cff5ykpCR77q+++oquXbsyfPhwe/5vvvmGmjVrlnyQpFxZjKvfmBARKScWi4WFCxfy7LPPOjuKiJ2OGEVERExUjCIiIia6KlVEnEbv5EhFpCNGERERExWjiIiIiU6l/gVcfa9bRREaGkpaWpqzY1xDuUqmouaCiptNuUrGGbkiIiJuuExHjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFSMIiIiJipGERERExWjiIiIiYpRRETERMUoIiJiomIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMRExSgiImKiYhQRETFRMYqIiJioGEVERExUjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFSMIiIiJipGERERExWjiIiIiYpRRETERMUoIiJiomIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMRExSgiImKiYhQRETFRMYqIiJi4OjuA/HGF/bs4O8J1nXV2gBtQrpKpqLmg4mZTruJzmfeVsyNcQ0eMIiIiJipGERFxqhdeeIHo6Gjuvfde+7zJkyfTtGlT7rvvPu677z7WrVsHQF5eHsOHD6dTp0507tyZrVu3ApCTk0OvXr1o164dHTt2ZNy4cbecR8V4A6+99hoAKSkpbNmypUz39cMPP/Djjz9eMz8lJYWRI0eW6b5FRJytV69efPrpp9fM79+/P2vWrGHNmjV06tQJgM8++wyAdevWsXjxYt566y1sNhsAAwYMYNOmTaxevZr4+HjWr19/S3lUjDfwzjvvAJCamlrmxXj//ffTvn37Mt2HiEhF1bZtWwIDA4u17uHDh2nTpg0AoaGh+Pv7s2fPHry8vOzz3d3dueuuuzh9+vQt5dHFNzfQq1cvFi5cyGeffcZvv/3G6NGjad++PX/729/49NNP2b9/P/n5+TzwwAPcd999JCYmsnTpUnx8fDh58iStWrUiMjKSb7/9lry8PEaPHk14ePh197V06VI8PT3p0qULx48f55///CcA0dHR5fmURUQqlI8++ogvvviC6OhoXn/9dQIDA6lXrx4//PADjz32GMnJyfzyyy8kJyfTuHFj++POnz/PmjVr6Nev3y3tV8VYhJ49e7Jq1SrGjBkDwNq1a/H29mb8+PHk5+czduxYGjZsCMCJEyeYOnUqvr6+DBkyhE6dOjF+/Hi+/fZbvv/+e2JiYorc3+zZs3nuueeoV68eCxcuvO46a9euZe3atQC89957pfNERUScIDQ0FFdXV4KCgnBxcSE0NBSAl19+mXfeeQeLxcIbb7zBxIkT+de//sWQIUP47bffeOSRR4iMjKRVq1YEBgbaH1dQUEDfvn0ZOnQoTZs2vaVMKsYS2rNnDydPnmTbtm0AZGdnc/r0aVxdXalZsyZBQUEAhIeH24/4IiMj2bdvX5HbvnjxIhcvXqRevXoAtGvXjt27d1+zXufOnencuXNpPSUREadJS0sjNDSU33//ncLCQtLS0gBwcXHh999/B+Dxxx+nT58+9mVjxoyxH6x06dKFSpUq2ZeNGDGC2267jZ49e9rnXU9ERMQNl6kYS8gwDPr27UujRo0c5icmJuLm5maftlgs9mmLxWJ/c1hERIp29uxZKleuDMB3331HnTp1gMtXnxqGgbe3N5s2bcLV1ZXatWsDMGHCBDIzM3n//ff/0L5VjEXw8vIiJyfHPt2oUSN++OEHGjRogKurK8nJyQQHB5fKvnx8fPDx8eHgwYPUrVuXzZs3l8p2RUQqsl69erFx40bS09Np2rQpo0aNYuvWrezfvx+LxcJtt93GhAkTgMtHmD179sRqtRIeHs6MGTMASE5OZsaMGURFRfHAAw8A0LdvX3r27FniPCrGIkRGRmK1Wh0uvklJSSE2NhYAf39/Ro8eXWr7GzRokP3imyvvXYqI/JUtXLjwmtOePXr0uO66t99++3UPGiIiIvjPf/5TKnkshmEYpbIlcZrk5GRnR7iu0NDQm57jdxblKpmKmgsqbjblKhln5LrZe4y6j1FERMREp1LL0bJly/j5558d5rVq1YquXbs6KZGIiFxNxViOunbtqhIUEangdCpVRETERMUoIiJiomIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMRExSgiImKiYhQRETFRMYqIiJioGEVERExUjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFSMIiIiJipGERERk1suxrNnz5KSklKaWURERJyu2MU4bdo0Dh06BMCGDRsYMWIEI0eOZP369WUWTkREpLwVuxj37dtHzZo1Afj6668ZO3Ys48aNY8WKFWUWTkREpLy5FnfFgoICXF1dSU9PJysri7p16wJw/vz5MgsnIiJS3opdjNWrV2f58uWkpqbSpEkTANLT0/Hy8iqzcCIiIuWt2KdSBwwYwMmTJ8nLy+Ppp58G4PDhw9xzzz1lFk5ERKS8FfuIMTw8nGHDhjnMu/vuu7n77rtLPZSIiIizFLsYDcNg3bp1bN26lQsXLvD+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mYo8lXrlClQREZH/BkUeMRYWFrJv3z77tM1mc5gGaNCgQeknExERcYIiizEgIMDhi4h9fX0dpi0WC3FxcWWTTkREpJwVWYyzZs0qjxwiIiIVQrHvYxQREflvoGIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMRExSgiImKiYhQRETFRMYqIiJioGEVERExUjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFydHUD+uML+XZwd4brOOjvADfyVc7nM+6oUtiLy301HjCJ/QefPn6d///60a9eO9u3bs2PHDhITE3nkkUfo1KkTffr0ITMz077+zJkzadOmDW3btmXjxo3OCy5SAagYRf6CXn/9dTp27MimTZtYs2YNtWrVYvTo0bz66qusW7eOBx98kH/+858AHD58mJUrV7J+/Xo+/fRTXn31VQoLC538DEScR8VYDIMHD+bChQtlsu309HQmT5583WVvvPEGx44dK5P9yl/XhQsX+Pe//02PHj0AcHd3JyAggOPHj3P33XcD0LZtW7799lsAVq9ezaOPPoqHhweRkZFUr16dXbt2OS2/iLOpGJ0sODiYkSNHOjuG/IWcPHmSkJAQhg8fzv3338+oUaPIzs6mdu3arF69GoCvv/6a5ORkAM6cOUNERIT98VWqVOHMmTNOyS5SEejim6vk5uYydepU0tPTsdlsPPHEEwB8//33JCQkUFBQwIgRI6hatSpZWVnMnj2blJQUPDw8eOGFF6hWrRpLly7l7NmznDlzhszMTLp06ULnzp2vu7+UlBQmTJjA5MmTycvLY/bs2Zw4cYKIiAjy8vKu+5i1a9eydu1aAN57772yGQj5UwoNDcXPz49ffvmFmTNn0qJFC0aMGMGHH37Ihx9+yIgRI4iLi+Phhx/Gw8OD0NBQPD098fPzIzQ0FABPT0/8/f3t066urvafK5qKmk25Sqai5VIxXmX37t0EBQXx97//HYDs7Gw+/fRT/Pz8mDBhAqtXr2bVqlUMGDCApUuXcscdd/DKK6+wb98+4uLimDRpEnD5r/Z3332X3NxcYmNjadKkCcHBwTfd9w8//IC7uztTp07lxIkTxMbGXne9zp0737Bo5b9bWloaXl5eVKlShRo1apCWlkanTp2Ii4tjyJAhLFiwAIBjx46xatUq0tLSCAwM5NChQ6SlpQGQlJSEt7e3fTo0NNT+c0VTUbMpV8k4I5f5LMnVdCr1KpGRkfzyyy8sWrSIAwcO4O3tDUDLli0BqFGjBqmpqQAcPHiQdu3aAdCgQQOysrLIzs4GoFmzZri7u+Pv70/9+vU5evRokfvev3+/fXvVqlWjWrVqpf785K8vLCyMiIgI+/9zW7ZsoXbt2vZfPDabjenTp9OrVy8A7r//flauXMmlS5c4efIkSUlJNG7c2Gn5RZxNR4xXiYiIYMKECezcuZPFixdz1113AZcP9QGsVmuxrtizWCw3nRYpS/BVzhAAABIrSURBVG+//TZDhw4lPz+fyMhIpkyZwhdffMHHH38MwN/+9jeeeuopAOrUqcMjjzxCx44dcXFx4d1338XFxcWJ6UWcS8V4lfT0dHx9fWnXrh0+Pj6sW7fuhuvWrVuXzZs3061bNxITE/Hz87MfYcbHx/PYY49x6dIlEhMT6dmzZ5H7rlevHlu2bKFBgwacPHmSEydOlNrzkv8uDRo04LvvvnOY9/zzz/P8889fd/1hw4YxbNiw8ogmUuGpGK9y8uRJFi1ahMViwdXVleeff54pU6Zcd93u3bsze/ZsRo0ahYeHB4MHD7Yvq1atGm+++SaZmZk88cQTRb6/CJdPac2ePZvhw4dTtWpVatSoUWrPS0REisdiGIbh7BB/NUuXLsXT05MuXcrno9quXHZf0eiN/pJRrpKrqNmUq2R08Y2IiEgFplOpZaB79+7XzDt58iQzZ850mOfm5sa4cePKK5aIiBSDirGcREZG2u9xFBGRikunUkVERExUjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFSMIiIiJipGERERExWjiIiIiYpRRETERMUoIiJiomIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMRExSgiImKiYhQRETFRMYqIiJioGEVERExUjCIiIiYqRhERERMVo4iIiImKUURExETFKCIiYqJiFBERMVExioiImKgYRURETFSMIiIiJipGERERExWjiIiIiYpRRETERMUoIiJiomIUERExUTGKiIiYqBhFRERMVIwiIiImKkYRERETFaOIiIiJilFERMTEYhiG4ewQIiIiFYWOGP/kxowZ4+wI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)

# # Mean Encoding

# `Motivation` : the item_id is not ordinal and if we one hot encoded it we will fall in the curse of dimensionality hence mean encoding is needed to solve this trap.

# In[ ]:


from itertools import product # to make cartisien product
index_cols = ['shop_id' , 'item_id' , 'date_block_num']
grid = []
for block_num in sales.date_block_num.unique() : # iterating over the 34 month
    curr_shops = sales[sales.date_block_num == block_num]['shop_id'].unique() # get the unique shops in this month
    curr_items = sales[sales.date_block_num == block_num]['item_id'].unique() # get the unique items in this month
    grid.append(np.array(list(product (*[ curr_shops, curr_items, [block_num]]))))
grid = pd.DataFrame(np.vstack(grid) , columns = index_cols ) 
all_data = grid.merge(sales1[['shop_id' , 'item_id' , 'date_block_num','item_cnt_month']] , how = 'left' , on = index_cols).sort_values(index_cols).fillna(0) #to add the item_cnt_month
all_data


# In[ ]:


def downcasting(df) :
    """
    make 2 lists onc contains index of float64 columns and the other int64 or int32,
    then change the dtype of these column into less memory consumer data type
    """
    float_cols = [ col for col in df if df[col].dtype == "float64" ]
    int_cols = [col for col in df if df[col].dtype in ['int64','int32']]
    df[float_cols] = df[float_cols].astype(np.float32)
    df[int_cols] = df[int_cols].astype(np.int16)
    return df


# In[ ]:


# reducing memory usage
all_data = downcasting(all_data)
all_data.item_cnt_month = all_data.item_cnt_month.astype('int16')
all_data.info()


# adding category_id to mean encode it

# In[ ]:


# for each item_id put the item_category_id
all_data = all_data.merge(items[['item_id','item_category_id']] ) 
test = test.merge(items[['item_id','item_category_id']])
all_data


# In[ ]:


all_data.isna().sum() # no nulls and every thing is right


# working with item category

# In[ ]:


item_categories


# In[ ]:


all_data = all_data.merge(item_categories) # getting the item_category_name
test = test.merge(item_categories) # getting the item_category_name 

#extracting the main_category and sub_category
all_data['main_category'] = all_data.item_category_name_translated.str.split('-').map(lambda x: x[0].strip()) 
all_data['sub_category'] = all_data.item_category_name_translated.str.split('-').map(lambda x: x[1].strip() if len(x) > 1 else x[0].strip())

test['main_category'] = test.item_category_name_translated.str.split('-').map(lambda x: x[0].strip()) 
test['sub_category'] = test.item_category_name_translated.str.split('-').map(lambda x: x[1].strip() if len(x) > 1 else x[0].strip())


# working with shop name

# In[ ]:


shops.shop_name_translated.unique()[:10]


# the shop name starts with a city name

# In[ ]:


all_data = all_data.merge(shops) #adding shop_name
all_data['city'] = all_data.shop_name_translated.str.split(' ').map(lambda x : x[0]) #the first word is a city name

test = test.merge(shops) #adding shop_name
test['city'] = test.shop_name_translated.str.split(' ').map(lambda x : x[0]) #the first word is a city name


# adding the year and month

# In[ ]:


all_data['year'] = all_data['date_block_num'].map(lambda x : 2013 if x < 12 else 2014 if x < 24 else 2015)
test['year'] = 2015


# In[ ]:


all_data['month'] = all_data['date_block_num'] % 12
test['month'] = test['date_block_num'] % 12


# Working with regularized mean encoding in order to decrease the leakage

# In[ ]:


# encoding item_id, category_id, shop_id
kf = KFold(n_splits = 5 , shuffle = False)
for train_ind, val_ind in kf.split(all_data) :
    train_data , val_data = all_data.iloc[train_ind], all_data.iloc[val_ind]
    all_data.loc[all_data.index[val_ind] , 'item_target_enc'] = val_data['item_id'].map(train_data.groupby('item_id')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'category_target_enc'] = val_data['item_category_id'].map(train_data.groupby('item_category_id')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'shop_target_enc'] = val_data['shop_id'].map(train_data.groupby('shop_id')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'city_target_enc'] = val_data['city'].map(train_data.groupby('city')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'main_category_target_enc'] = val_data['main_category'].map(train_data.groupby('main_category')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'sub_category_target_enc'] = val_data['sub_category'].map(train_data.groupby('sub_category')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'year_target_enc'] = val_data['year'].map(train_data.groupby('year')['item_cnt_month'].mean())
    all_data.loc[all_data.index[val_ind] , 'month_target_enc'] = val_data['month'].map(train_data.groupby('month')['item_cnt_month'].mean())

all_data.fillna(all_data.item_cnt_month.mean(), inplace=True) # fill na that happend from values in validation not in the train with the global mean    


# In[ ]:


# making a column to map item_target_enc to the test set
item_mean_enc = all_data.groupby('item_id')['item_target_enc'].unique()
item_mean_enc = item_mean_enc.apply(lambda x: x.mean())
test['item_target_enc'] = test['item_id'].map(item_mean_enc) # mapping the variable in the test 

# making a column to map item_category_id to the test set
category_mean_enc = all_data.groupby('item_category_id')['category_target_enc'].unique()
category_mean_enc = category_mean_enc.apply(lambda x: x.mean())
test['category_target_enc'] = test['item_category_id'].map(category_mean_enc) # mapping the variable in the test 

# making a column to map the shop_target_enc to the test set
shop_mean_enc = all_data.groupby('shop_id')['shop_target_enc'].unique()
shop_mean_enc = shop_mean_enc.apply(lambda x: x.mean())
test['shop_target_enc'] = test['shop_id'].map(shop_mean_enc) # mapping the variable in the test 


# In[ ]:


# mapping city
city_mean_enc = all_data.groupby('city')['city_target_enc'].unique()
city_mean_enc = city_mean_enc.apply(lambda x: x.mean())
test['city_target_enc'] = test['city'].map(city_mean_enc) # mapping the variable in the test 

# mapping sub_category
sub_category_mean_enc = all_data.groupby('sub_category')['sub_category_target_enc'].unique()
sub_category_mean_enc = sub_category_mean_enc.apply(lambda x: x.mean())
test['sub_category_target_enc'] = test['sub_category'].map(sub_category_mean_enc) # mapping the variable in the test 

# mapping main_category
main_category_mean_enc = all_data.groupby('main_category')['main_category_target_enc'].unique()
main_category_mean_enc = main_category_mean_enc.apply(lambda x: x.mean())
test['main_category_target_enc'] = test['main_category'].map(main_category_mean_enc) # mapping the variable in the test 


# In[ ]:


# mapping year
year_mean_enc = all_data.groupby('year')['year_target_enc'].unique()
year_mean_enc = year_mean_enc.apply(lambda x: x.mean())
test['year_target_enc'] = test['year'].map(year_mean_enc) # mapping the variable in the test 

# mapping month
month_mean_enc = all_data.groupby('month')['month_target_enc'].unique()
month_mean_enc = month_mean_enc.apply(lambda x: x.mean())
test['month_target_enc'] = test['month'].map(month_mean_enc) # mapping the variable in the test 

test.fillna(all_data.item_cnt_month.mean() , inplace = True)


# droping the category name and shop name

# In[ ]:


all_data.drop(['item_category_name_translated','shop_name_translated'],axis = 1, inplace = True)
test.drop(['item_category_name_translated','shop_name_translated'],axis = 1, inplace = True)


# In[ ]:


all_data.head()


# seeing the importance of the added features

# In[ ]:


# submitting in the leaderboard
lgbm = pickle.load(open('/content/lgbm_mean_encoding.sav', 'rb'))
test = test[all_data.drop('item_cnt_month',axis = 1).columns] # sorting the columns
preds_lgbm = lgbm.predict(test.drop(['city','main_category','sub_category'],axis = 1))
sub = sample_submission
sub.item_cnt_month = preds_lgbm
sub.to_csv('lgbm_mean_encoding.csv' , index = False)


# In[ ]:


# ploting the importance
lgbm = pickle.load(open('/content/lgbm_mean_encoding.sav', 'rb'))
plt.style.use('ggplot')
ax = plot_importance(lgbm)
fig = ax.figure
fig.set_size_inches(9, 13)


# ![](data:image/png;base64,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AqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERHJR65cuUK/fv2oVasWjRs3Zvv27cTGxvLCCy/QvHlzXnnlFa5duwbArl27CA4OJjg4mKCgIFavXp3H1dtY8roAEREREbl7b731Fk2bNuW7777jzJkz3Lhxg65duzJu3DgaNmzI4sWLef/99xk5ciTVqlVj9erVWCwWzp8/bw+jFkveRkAF0EfMwIEDmTZtGp6eng987kuXLvHpp58SGhqaZduECRMICQmhYsWKd5wnvV+bB15bfnI+rwt4SKgPNuqDjfpgoz7YPIp9cJi/AoCrV6+ybds23nnnHQAKFSpEoUKFOHbsGIGBgQA888wzvPzyy4wcORIXFxf7HDdv3sRkMhlffDa0BC8PTLFixbINnyIiIvJgnDp1iuLFizNs2DACAgIYMWIESUlJVKlShbVr1wLw/fffc+bMGfsxO3fupGnTpjRv3pzp06fn+dVP0BXQAi05OZk5c+Zw6dIlMjIy6NixIwBr1qxhx44dpKWlMXz4cHx8fEhMTCQ8PJz4+HicnJzo378/5cqVIyIigvPnz3Pu3DmuXbtGmzZtCAoKyvZ88fHxzJgxg//85z+kpKQQHh7OyZMn8fb2JiUlxciPLiIiUiClp6ezZ88e3n77bVq0aMGAAQN47733mD17NuPGjeOdd96hRYsWODo62o958skn2bhxI4cPH2bo0KE0bdoUZ2fnPPwUCqAF2m+//UbRokUZM2YMAElJSSxatAgPDw9mzJjB2rVrWblyJa+99hoRERFUqFCBkSNHsnfvXt577z1mzZoF2H7amjJlCsnJyYwaNYonn3ySYsWK3fbc69ato1ChQsyZM4eTJ08yatSoHPeNjIwkMjISgOnTpz+gTy8iIlJweHl5AfD4449TpkwZWrRogcVioVu3bsyaNYvAwEDWr18PwKFDh/j555/tx/x1jiJFinD+/Hnq1q1r+Gf4KwXQAszX15eFCxfy5ZdfUrduXapXrw5AgwYNAPDz8yM6OhqAAwcO2JfPa9asSWJiIklJSQDUq1fPfo/J448/zpEjRwgICLjtufft20erVq0AKFeuHOXKlctx36CgoByvqoqIiAgkJCQAYLFYKFWqFFu3biUwMJAffviB8uXLc+DAAby8vMjIyGDChAl07dqVhIQETp06hbe3NxaLhbi4OPbv34+Hh4d9vtzm7e2d7bgCaAHm7e3NjBkz2LlzJ4sXL6ZWrVoA9ns/zGYz6enpd5zn7zcsPyw3MIuIiDyK3n77bQYNGkRGRgY+Pj7Mnj2bb775hs8++wyAVq1a8dJLLwEQHR3NvHnzsFgsmM1mpk6desdVTCMogBZgly5dwt3dnWeffRY3Nzd+/PHHHPetVq0amzZtolOnTsTGxuLh4YGrqysAMTExtGvXjps3bxIbG0u3bt3ueO4aNWqwefNmatasyalTpzh58uQD+1wiIiKPspo1a7J69Wq8vLzsVzL79u1L3759s+zbqVMnOnXqZHSJd6QAWoCdOnWKL7/8EpPJhMVioW/fvsyePTvbfTt37kx4eDgjRozAycmJgQMH2reVK1eOiRMncu3aNTp27HhXPzm1aNGC8PBwhg0bho+PD35+fndd962vmnhU/fUPlEeZ+mCjPtioDzbqg436kP+ZrFarNa+LkIdXREQEzs7OtGlj3Hdz/vWrIx5F+oPVRn2wUR9s1Acb9cFGfbDJD33I6R5QfQ+oiIiIiBhKS/ByW507d84ydurUKebOnZtpzNHRkalTpxpVloiIiORjCqByz3x9fe3fESoiIiJyr7QELyIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDGXJ6wJERETk4dKgQQPc3d0xm81YLBZWr17NzJkzWbduHSaTCS8vL+bMmUPp0qUB2LJlC+PHjyctLY1ixYrx7bff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H0LK6dh76cvAgQPv2E+H+SvuuE9Bpit/IiJS0JmsVqs1r4t4FC1YsIAKFSrQrFmzXJk/OTkZZ2dn0tPTmTVrFs2aNSMgICBXzvWgnTlzJq9LyFMKoDbqg436YKM+2KgPNuqDTX7og+4BfYiMGjUKZ2fnLMuQD1JERAR79uwhNTUVf39/6tevn2vnEhEREbkXCqB5YMaMGVnGxo4da3+g6JZBgwbh6+t7X+f4J+F26dKlREVFZRpr2LAhHTp0uO85RURERG5RAH1ITJ06Na9LsOvQoYPCpoiIiOQaPQUvIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGMqS1wWISME0fPhwIiMj8fLyYsOGDQC89tprHD16FICrV6/i6enJ+vXr+eWXX5g6dSqpqak4Ojry5ptv0q5du7wsX0REcpECqDx00vu1yesS8tT5vC7gH3KYvwKAzp0706tXL4YMGWLf9sEHH9hfT5w4EU9PTwCKFSvGZ599RunSpTlw4AAvv/yyAqiISAGmJfg7ePPNNwGIj49n8+bNeVxNZkuXLs3rErJYt24dP//8c5bx+Ph4QkND86AiySuBgYEUKVIk221Wq5WVK1fStm1bAGrWrEnp0qUBqFq1KsnJydy8edOwWkVExFgKoHcwefJkAC5cuPDQBdDvvvsu18+Rnp5+T/u3aNGCxo0b51I1UlBs27aNEiVK4Ofnl2XbDz/8QM2aNXFycsqDykRExAhagr+DkJAQFi5cyFdffUVcXBxhYWE0btyYVq1asWjRIvbt20dqaiotW7YkODiY2NhYIiIicHNz49SpUzRs2BBfX19WrVpFSkoKYWFh9is9f3f58mXmz59PfHw8AH379qVq1arMnDmTixcvkpqaSqtWrQgKCmLRokX2+cqWLcvgwYP55ZdfWL16NWlpaVSuXJm+fftiNpvZsGEDy5cvx9XVlXLlyuHo6EifPn2Ij4/n/fff59q1a3h6ejJgwAC8vLyYN28ejo6OnDhxgqpVq7Jjxw4mT56Mp6cnGRkZDBkyhClTptiXT/8qIiICZ2dn2rRpw7Fjx3j//fcB8Pf3z73fJMl3li1bZr/6+VcHDx5k6tSpfPXVV3lQlYiIGEUB9C5169aNlStXMnr0aAAiIyNxdXVl2rRppKamMm7cOGrXrg3AyZMnmTNnDu7u7rzxxhs0b96cadOmsWrVKtasWUPPnj2zPcenn35KjRo1CAsLIyMjg+TkZAAGDBiAu7s7KSkpjBkzhgYNGvDyyy+zZs0aZs2aBUBcXBxbtmzh7bffxmKx8PHHH7Np0yZq1arFt99+y4wZM3B2dmbSpEmUK1cOgE8++YTGjRvTpEkTNmzYwCeffMLIkSMBuHTpEpMnT8ZsNuPq6sqmTZt4/vnn2bNnD+XKlcs2fP5deHg4vXv3pkaNGixcuDDH/SIjI4mMjARg+vTpd/G7IQ8zLy8v++vExEQcHBwyjaWlpbF27VqioqIyjcfFxdG/f38+++wz6tWrh8ViybT9UaU+2KgPNuqDjfpgk5/7oAB6n37//XdOnTrF1q1bAUhKSuLs2bNYLBYqVqxI0aJFAShdurT96p+vry979+7Ncc69e/fyxhtvANiDH8CqVauIiYkBICEhgbNnz+Lh4ZHl2OPHjzNmzBgAUlJS8PT0xMXFherVq+Pu7g7Y7ss7e/YsAIcPH2bEiBEAPPvssyxatMg+X2BgIGaz7Q6Npk2bMmvWLJ5//nk2btxI06ZN79if69evc/36dWrUqGGf/7fffst236CgIIKCgu44p+QPCQkJ9td//vkn6enpmcY2btyIn58fzs7O9vErV67QsWNHRo0aRZUqVUhISMDLyyvTcY8q9cFGfbBRH2zUB5v80Advb+9sxxVA75PVaqVXr17UqVMn03hsbCyOjo729yaTyf7eZDKRkZFxT+eJjY1lz549TJ48GScnJyZMmEBqamq29TRu3Jhu3bplGo+Ojr6n893i7Oxsf+3l5UXhwoXZu3cvR44cYfDgwfc1pzxaBgwYQFRUFJcuXaJu3bqMGDGCrl27snz58izL759++iknTpxgzpw5zJkzB4C1a9fafwgSEZGCRX+63yUXFxdu3Lhhf1+nTh3WrVtHWloaAGfOnLEvmd+vWrVqsW7dOgAyMjJISkoiKSkJNzc3nJyc+OOPPzh8+LB9f4vFYj9/rVq12Lp1K1euXAFsS58XLlygUqVK7N+/n8TERNLT09m2bZv9+CpVqrBlyxYANm/eTLVq1XKsrVmzZsydOzfTldHbcXNzw83NjQMHDgCwadOme+yG5Hfh4eHs2rWLkydPsmPHDrp27QrAO++8Q48ePTLtO3ToUI4cOcL69evtv0qWLJkXZYuIiAF0BfQu+fr6YjabMz2EFB8fz6hRowDw9PQkLCzsH52jZ8+efPTRR2zYsAGz2Uy/fv2oU6cO69evZ9iwYTz22GNUrlzZvn/z5s0JCwujQoUKDB48mC5dujB58mSsVisODg706dOHKlWq0L59e8aOHYu7uzve3t72pf3evXsTHh7OihUr7A8h5aRevXq8//77d7X8fsuAAQPsDyHduj/2btz6HslHVX5YUhEREfknTFar1ZrXRUjuSk5OxtnZmfT0dGbNmkWzZs0ICAi4pzmOHj3K559/zqRJk3Kpyv/fmTNncv0cDzMFUBv1wUZ9sFEfbNQHG/XBJj/0QfeAPsIiIiLYs2cPqamp+Pv7U79+/Xs6ftmyZaxbt073foqIiMgDoQCaB5YuXUpUVFSmsYYNG9KhQ4dcOd/f77e7V+3atcvyzyIa/RlERESk4FAAzQMdOnTI90GtIHwGERERyRt6Cl5EREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiDxww4cPx9/fn2bNmtnHXnvtNYKDgwkODqZBgwYEBwcDcOnSJTp16kTlypX517/+lVcli4iIgRRA/5/Y2FgOHjyY12Vkcv36ddauXWvIuaKjo4mLizPkXFLwde7cmUWLFmUa++CDD1i/fj3r16+nVatWtGrVCgBnZ2dGjhzJuHHj8qJUERHJA5a8LuBhERsbi7OzM1WrVs21c1itVqxWK2bz3eX+69evs27dOlq2bJlr57glJiaGunXrUqZMmXs6Ljek92uT1yXkqfN5XcA/4DB/BQCBgYGcPn06232sVisrV64kIiICAFdXVwIC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P9EaQX2wUR9s1Acb9cFGfbDJD33QFdCHmIeHx30t4+eWvn375nUJIiIiUoAV6KfgRUREROThowAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAq8ogZPnw4/v7+NGvWzD42c+ZMgoKCCA4OpmvXrpw7dw6AtWvX2sefe+45oqOj86psEREpQExWq9Wa10XIg7d9+3bi4uJo165drp3jgw8+oHXr1pQpU+aBznv6+XoPdD6xcZi/AoCtW7fi5ubGkCFD2LBhAwDXrl3Dw8MDgAULFnDo0CFmzJjB9evXcXV1xWQysW/fPl577TV++eUXQ+r18vIiISHBkHM9zNQHG/XBRn2wUR9s8kMfvL29sx23GFyHGKRevXrUq5d7QS4jI4PXXnst1+aX3BMYGMjp06czjd0KnwBJSUmYTCYA3Nzcsh0XERH5JxRA86H4+HimTp1K5cqVOXToEBUrVqRJkyYsWbKEK1euMHjwYOLi4jh69Ch9+vRh3rx5uLi4cOzYMS5fvkz37t0JDAzMdu7Y2FgiIiJwdnbm3LlzPP744/Tt2xez2UxISAjBwcHs2bOHPn36sHjxYkJCQqhYsSK//fYb//vf/8jIyMDDw4O33nqL5ORkPvnkE06fPk16ejovvvgi9evXN7hbcremT5/ON998g6enJ0uWLLGPr169mmnTpnHx4kU+//zzPKxQREQKCgXQfOrcuXMMHz6cMmXKMGbMGDZv3sykSZPYvn07S5cuJSAgINP+ly9fZtKkSZw5c4YZM2bkGEABjhw5wuzZsylRogRTpkwhOjqawMBAbt68SaVKlejRo0em/a9evcqHH37IxIkTKVmyJImJiQAsXbqUmjVrMmDAAK5fv87YsWOpVasWzs7OmY6PjIwkMjISsIUgyR1eXl7214mJiTg4OGQa+/e//82///1vZs6cyddff81bb70FQEhICCEhIWzatIkpU6awZs0aQ+q1WCyZ6ntU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ERGRO1+RA+hff9tReno6ubm5VK1alTlz5hR7YSIiIiJyZypyAJ07d26+ZavVyscff+zUl9CLiIiISNlT5NcwXbOj2cxjjz3GunXrirMeEREREbnD3XIABTh48CBm820dQkRERETKmSJPwf/zn//Mt5yTk0NOTg4DBw4s9qJERERE5M5V5AA6bNiwfMvu7u4EBATg6elZ7EWJiIiIyJ2ryAH0l19+oXv37tes//zzz+nWrVuxFiUiIiIid64i38D58ccf39R6EREREZGC3PAK6NUX0Fut1mteRv/777/rNUwiIiIiclNuGECvvoA+Jycn38voTSYTvr6+DBgwoOSqExEREZE7zg0D6NUX0M+ZM4ehQ4eWeEEiIiIicmcr8j2gCp8iIiIiUhyK/BR8ZmYma9as4ciRI1y8eBGbzeb42l9/T7yIiIiISGGKfAV04cKFnDhxgscff5yMjAwGDBiAn58fXbt2Lcn6REREROQOU+QAevDgQUaNGkWbNm0wm820adOGESNGsH379pKsT0RERETuMEUOoDabzfFbjzw8PMjMzMTX15ezZ8+WWHEiIiIicucp8j2gtWrV4siRIzRr1oyGDRuycOFCPDw8CAgIKMn6REREROQOU+QroC+88AJ33XUXAM8++yxubm5cunRJT8eLlLCRI0fSvHlzOnXq5Fh37tw5evfuTfv27enduzfnz58HYO3atURERBAeHk737t2Jj493VtkiIiKFMtn+/Di7SClwumtrZ5dQKrgs+AyAPXv24OXlxfDhw9myZQsAb7zxBr6+vgwdOpQ5c+Zw4cIFXnnlFfbt20dwcDC+vr5s2bKFGTNm8PnnnzvzNG6Zn58fqampzi7D6dQHO/XBTn2wUx/sykIfAgMDC1x/U/eAxsbGMmHCBKKiogA4cuQIu3btKp4KpcwZN26cs0soF0JDQ/H19c23buPGjfTq1QuAXr168eWXXwLQpk0bx7YtW7YkKSnJ2GJFRESKoMgBdNWqVWzdupWIiAhH2q5atSrr1q0rseKkdMrLywPsV+HEOVJTU7n77rsB8Pf3L/An4I8++oiwsDCjSxMREbmhIj+E9PXXXzN16lR8fHxYuHAhYP+PLzk5ucSKk/+TnJzM5MmTCQ4OJiEhgbp169KxY0fWrFnDhQsXePHFFwFYsmQJV65cwc3NjcjISAIDA/n88885deoUkZGRnDp1itmzZzN58mTc3d2vGWf16tX8/vvvnD17losXL9K9e3ciIiKIj49n1apVeHl5kZiYyOzZs3nyySdZtmwZAJ9++inbt2/HbDYTEhJCv379OHv2LIsWLSI9PR13d3deeOEFqlevbmjfygOTyYTJZMq3bufOnaxcuZJPPvnESVWJiIgUrsgB1Gq14uHhkW9ddnb2Neuk5Jw9e5aRI0dSo0YNxowZw44dO5g4cSL79+9n7dq1DB06lIkTJ+Li4sLBgwdZsWIFUVFRdOnShQkTJvDNN9+wdu1aBg0aVGD4vOrUqVNMmjSJ7OxsXn75ZVq2bAnAiRMnmD59Ov7+/vm2//7779m/f78j1GZkZADw/vvvM2jQIAICAvj5559ZuHAh48ePv2a82NhYYmNjAZgyZUpxtavM8/Pzc3zOyMjAxcXFse7uu+/mypUrBAQEkJSUhL+/v+Nrhw4d4uWXX+azzz6jfv36Tqm9OFgslnw9KK/UBzv1wU59sFMf7MpyH4ocQO+55x4+/PBDnn76acB+T+iqVato1apViRUn+fn7+xMUFARAzZo1adasGSaTiaCgIFJSUsjMzGTu3LmOd7NenSo3m81ERkYSFRVF586dadiw4XXHad26NW5ubri5udGkSRN++eUXvLy8qFev3jXhE+yBp2PHjo5Q6+3tTXZ2NkePHmXGjBmO7XJzcwscLyIigoiIiJtvyB3uz9Pq586dIy8vz7EuPDyc+fPnM3ToUObPn++4Nea3337jiSeeYNasWVSpUqXU35x+PWXh5nojqA926oOd+mCnPtiVhT4U9hDSDQPo+fPn8fX15amnnmLu3Lk888wz5Obm8tRTT9G8eXO9hslArq6ujs8mk8mxbDKZsFqtrFq1iiZNmhAdHU1ycjITJkxwbJ+UlISHhwdpaWk3HOev07lXl6931fSvrFYrXl5eTJs2rcj7SMEiIyPZvXs3aWlptGrViqioKIYMGcLgwYNZuXIlNWrU4L333gNg5syZnDt3jrFjxwL2n45jYmKcWb6IiMg1bhhAhw8fzgcffICnpyfR0dG8+eab9OrVCz8/v2uezBXnyszMpEqVKgDExcXlW79kyRImTJjA4sWL2bNnD6GhoYUeZ9++ffTo0YPLly8THx9P3759r/s0dfPmzfnf//7H//t//88xBe/t7Y2/vz+7d++mXbt22Gw2fv31V2rXrl1cp1tuzJs3r8D1q1evvmbd22+/zdtvv13SJYmIiNyWGwbQv74mNCEhgXr16pVYQXLrHn30UebOncvatWsd920CLF26lIceeojAwEAGDx7MhAkTaNSoEZUqVSrwOLVq1WLChAlcvHiRnj17UqVKlesG0JCQEE6ePMno0aOxWCzcc8899O3blxdffJEFCxawdu1acnNzad++fZEC6NX3X5ZXZWFKRURE5Hbc8EX0Tz/9NB988IFj+dlnn2XJkiUlXpg4x+rVq/Hw8KB79+5OqyExMdFpY5cGCqB26oOd+mCnPtipD3bqg11Z6MMt3wOal5fH4cOHHctWqzXfMkDTpk1vszwRERERKS9uGEArVarEu+++61j29vbOt2wymZgzZ07JVCclZuvWrWzYsCHfugYNGvDcc885qSIREREpL24YQOfOnWtEHWKwsLAw/ZYcERERcYoi/ypOEREREZHioAAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqhIKbJw4ULuuecewsLCWLBgQb6vvffee1SvXp20tDQnVSciIlI8FEBFSomffvqJFStWsHPnTjZv3kxsbCwnTpwA4LfffmPbtm1Ur17dyVWKiIjcPouzC5CSN27cON544w2Sk5NJSEjg/vvvL7GxNm3ahLu7Ox06dMi3Pjk5malTpzJ9+vQbHiNvUPeSKq/UclnwGT///DP33HMPnp6eZGZmEhoaSkxMDJGRkbz22mu88sorDBgwwNmlioiI3DZdAS0H3njjDQBSUlLYsWNHiY714IMPXhM+pWgaNmzI3r17+eOPP8jKymLLli0kJiayceNGAgICaNKkibNLFBERKRa6AloOPPnkkyxbtowVK1Zw5swZoqOj6dChA126dOG///0vR44c4cqVKzz00EN07tyZ+Ph4Vq9ejZeXF6dOnaJdu3YEBQWxYcMGcnJyiI6Oplq1agWOtXr1ajw8POjevTvHjx/n3XffBaB58+ZGnnKZFBwczJAhQ+jatStubm40adKEnJwc3nnnHVasWOHs8kRERIqNAmg50rdvX9avX8/o0aMBiI2NxdPTkzfffJMrV67w6quv0qJFCwB+/fVXZs6cibe3N0OHDiU8PJw333yTDRs28OWXX/LMM8/ccLx58+YxYMAAGjduzLJlywrdLjY2ltjYWACmTJly+ydaBvn5+QEwbNgwRowYQW5uLq+++ir+/v5s2rSJhx9+GICkpCS6dOnCjh07Cv0h4E5hsVgcfSnP1Ac79cFOfbBTH+zKch8UQMuxH374gVOnTrFnzx4AMjMzSUpKwmKxULduXSpXrgxAtWrVHFcwg4KCOHz48A2PfenSJS5dukTjxo0BeOCBBzhw4ECB20ZERBAREVEcp1RmpaamOv5s2LAhP/zwAx9//DHr16+nT58+ju3uvfdeNmzYgMVicexzp/Lz87vjz7Eo1Ac79cFOfbBTH+zKQh8CAwMLXK8AWo7ZbDaeffZZQkJC8q2Pj4/H1dXVsWwymRzLJpMJq9VqaJ3lyaBBg0hPT8dkMjFp0iQqVark7JJERESKnQJoOVKhQgWysrIcyyEhIWzatImmTZtisVhITEykSpUqxTKWl5cXXl5e/PTTTzRs2JDt27cXy3HvdJ988sl1f6Ldu3evwRWJiIgUPwXQciQoKAiz2ZzvIaTk5GRefvllAHx8fIiOji628SIjIx0PIV29t7QoXBZ8Vmw1iIiISOljstlsNmcXIfJniYmJzi7BqcrCPT1GUB/s1Ac79cFOfbBTH+zKQh8KuwdU7wEVEREREUNpCl5uydq1a9m9e3e+de3ateOxxx5zUkUiIiJSViiAyi157LHHFDZFRETklmgKXkREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVMSJ3n//fcLCwujUqRORkZFkZ2ezZcsWHnroITp37kyPHj04ceKEs8sUEREpVhZnFyBl0/79+zlz5gw9evQo9mPnDepe7McsbVwWfEZSUhKLFy9m69atVKhQgRdeeIF169Yxb948Fi5cSHBwMEuXLmX27NnMmjXL2SWLiIgUGwVQuWl5eXm0bt2a1q1bO7uUMi83N5fs7GxcXV3JysqiWrVqmEwmLl68CMDFixe5++67nVyliIhI8VIALUWSk5OZPHkywcHBJCQkULduXTp27MiaNWu4cOECL774IjVq1GDx4sWcPn2avLw8evXqRZs2bUhOTmbOnDlcvnwZgAEDBtCgQQPi4+NZs2YNFStW5PTp09SpU4dhw4ZhMpkKrGHIkCG0a9eO77//Hjc3N4YPH061atWYO3curq6unDx5kgYNGlCrVi2OHTvGwIEDOX/+PAsWLCA5ORmA5557jgYNGrBt2zZiYmLIzc0lODiY5557DrNZd31cFRAQwODBg2nbti0eHh506NCBDh068N5779GzZ088PDyoWLEi69evd3apIiIixUoBtJQ5e/YsI0eOpEaNGowZM4YdO3YwceJE9u/fz9q1a6lRowZNmzYlMjKSS5cuMXbsWJo1a0alSpUYN24cbm5uJCUlMXv2bKZMmQLAiRMnmDFjBpUrV+bVV1/g9BBOAAAgAElEQVTl6NGjNGzYsNAaPD09mT59Ol9//TVLly5l9OjRAKSlpfHGG29gNpuJi4tzbL9kyRIaN25MdHQ0VquV7Oxszpw5w65du3j99dexWCwsXLiQ7du306FDh2vGi42NJTY2FsBR853Oz8+Pc+fOsXXrVhISEvD19aVPnz5s2rSJdevWsX79etq2bcv06dOZOnUq7733nrNLNpzFYsHPz8/ZZTid+mCnPtipD3bqg11Z7oMCaCnj7+9PUFAQADVr1qRZs2aYTCaCgoJISUkhLS2Nb7/91nFVLCcnh9TUVKpUqcKiRYs4efIkZrOZpKQkxzHr1atH1apVAahduzbJycnXDaDt27d3/PnBBx841oeGhhZ4BfPw4cMMHToUALPZjKenJ9u2bePEiROMGTPGUaePj0+B40VERBAREVHkHt0JUlNTWb9+vWPK/cKFC4SHh7NlyxZ++OEH6tSpQ2pqKhERESxZsoTU1FRnl2w4Pz+/cnnef6U+2KkPduqDnfpgVxb6EBgYWOB6BdBSxtXV1fHZZDI5lk0mE1arFbPZzKhRo675hq5evZpKlSoxbdo0bDYb/fr1K/CYZrMZq9V63Rr+PD3/588eHh5FPg+bzUaHDh3o27dvkfcpb6pXr853331HVlYWHh4e7NixgxYtWrBhwwaOHTtG3bp12bZtG8HBwc4uVUREpFjphrwypkWLFsTExGCz2QAcr+jJzMykcuXKmM1mtm3bdsOQeT27du1y/FmU8NOsWTM2bdoEgNVqJTMzk2bNmrFnzx4uXLgAQEZGBikpKbdc052oZcuWdO3alYceeojw8HCsViv9+vXj3Xff5fnnnyciIoKPP/6YcePGObtUERGRYqUroGXM448/ztKlS4mKisJms+Hv78/o0aN56KGHmD59Otu2baNFixa4u7vf8hgZGRlERUXh6urK8OHDb7j9M888w/vvv8+WLVswm80MGjSI+vXr07t3b9544w1sNhsuLi4MHDiQu+6664bHc1nw2S3XXtZERUURFRWVb92jjz7quA1CRETkTmSyXb2UJoL9Kfg333yz0Ps1jZCYmOi0sUuDsnBPjxHUBzv1wU59sFMf7NQHu7LQh8LuAdUUvIiIiIgYSlPw5dS0adMc7+28ql+/fsydO9dJFYmIiEh5oQBaTkVHRzu7BBERESmnNAUvIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMZXF2ASJlyb333ou3tzdmsxmLxUJMTAyDBw/m2LFjAKSnp+Pj48PmzZudXKmIiEjppQAqxeLSpUvs2LGDhx56CID4+HjWr1/P6NGjb/pYeYO6F3d5t8VlwWf5ltesWUOVKlUcy++9957j84QJE/Dx8TGsNhERkbJIU/BSLC5dusSmTZucXYZT2Ww21q9fz6OPPursUkREREo1XQEth5KTk5k8eTLBwcEkJCRQt25dOnbsyJo1a7hw4QIvvvgi1apVY968eSQnJ+Pu7s7zzz9PrVq1WL16NampqSQnJ5OamkqXLl3o0qULK1as4OzZs0RHR9O8eXNatmxJdnY206dP5/Tp09SpU4dhw4ZhMpmcffq3xWQy0adPH0wmE/3796d///6Or+3du5e77rqLOnXqOLFCERGR0k8BtJw6e/YsI0eOpEaNGowZM4YdO3YwceJE9u/fz9q1a/Hz8+Nvf/sbL730EocPH2bOnDlMmzYNgMTERMaPH09WVhb/+te/ePDBB+nbty+nT592bBMfH8+JEyeYMWMGlStX5tVXX+Xo0aM0bNjQmad92z755BMCAgJITU2ld+/e1KtXj9DQUAA+/fRTXf0UEREpAgXQcsrf35+goCAAatasSbNmzTCZTAQFBZGSkkJqaiqjRo0CoGnTpmRkZJCZmQlAy5YtcXV1xdXVlUqVKnHhwoUCx6hXrx5Vq1YFoHbt2iQnJxcYQGNjY4mNjQVgypQpxX6ut8vPz++az35+fvTs2ZOEhAS6detGbm4uGzduZPfu3fm2vxUWi+W2j3EnUB/s1Ac79cFOfbBTH+zKch8UQMspV1dXx2eTyeRYNplMWK1WXFxcCt3XYvm/vzZms5m8vLwbjmE2m7FarQVuFxERQURExE3Vb6TU1FQAMjMzsVqteHt7k5mZSUxMDCNGjCA1NZWtW7dSp04dPDw8HNvfKj8/v9s+xp1AfbBTH+zUBzv1wU59sCsLfQgMDCxwvQKoFKhhw4Zs376dxx9/nPj4eCpWrIinp2eh21eoUIGsrCwDKzReSkoKAwcOBCAvL48ePXoQFhYGwLp16zT9LiIiUkQKoFKgJ554gnnz5hEVFYW7uztDhgy57vYVK1akQYMGjBo1ipCQEFq2bHnLY//1tUelRa1atRy3CvzVrFmzDK5GRESk7DLZbDabs4sQ+bPExERnl+BUZWFKxQjqg536YKc+2KkPduqDXVnoQ2FT8HoPqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihrI4uwCRsuLee+/F29sbs9mMxWIhJiYGgMWLF7N06VJcXFwIDw9n3Lhx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i1/QokUL0tLSsNlsF2x3uWw2m6byUR9qqA8+6oOP+uCjPvg05j4ogF6GpKQk3njjDdasWcPNN9/MjTfeCPjujgZITk7miy++AGD//v1MmjQJgG7dulFWVobL5QKgT58+hISEEBISQteuXTl8+DD9+vX70eN7PB5Wr17N119/jdVq5cSJE/732rdvT3x8vP/Y/fv3x2q1EhUVRdeuXQEoKCggPz+f2bNnA77QGB0dfUnn/mPb1tSfnJxMUVERALt37+ZnP/sZQUFBANjt9lr3nZqaWucocKDV3FTkcrnwer3Y7XZcLhfr169nwoQJ3HHHHaxfv55u3bpx5MgR3G73edtdibi4ON3MhPpQQ33wUR981Acf9cGnMfQhMTGx1uUKoJchMTGR+fPns2PHDv7whz/QvXt3AP+ol9VqvaRrMH84PXup07X/+7//i8PhICsrC8MweOihh/zv1dwE82NatWrFnDlzLmndy9k2ODgY8PXA6/Ve0f4bspMnT5KRkQH4fhG49957SUlJobKykkmTJnHHHXcQHBzMokWLNP0uIiLyI3QT0mUoLi4mJCSEQYMGMXz4cL766qs61+3cuTOffPIJAHl5eURERBAeHg7A1q1bqayspLS0lLy8vDqnvZs1a0ZFRYX/tcvlIjo6GqvVyqZNm+oMep06deL//u//8Hq9nDlzhry8PMAXoM+ePcvBgwcB37R6fn4+AGFhYecd64cutm1depxJwIoAABymSURBVPTowYcffugP5XVNwTcGrVu39l8qsGHDBp566ikAQkJCWLJkCf/4xz94//33ue222wJcqYiISMOnEdDL8M0337BmzRosFgs2m43HHnuMhQsX1rpueno6y5cvZ/LkyYSGhjJ69Gj/e61bt+bZZ5+ltLSU+++/v9brP8E35W+1Wv03Id15551kZ2ezadMmevbsWeeo5y233MKePXuYOHEisbGxJCcnEx4ejs1mY9KkSbzyyiu4XC48Hg9Dhw7lhhtuYPDgwaxatarOm5Autm1dhgwZwokTJ5g8eTI2m40hQ4Zw1113/VibL3j2poiIiFxbLIZhGIEuoilZt24dYWFhDB9evw9bd7vdhIWFUVpayjPPPMPs2bOJioqq12NeLQUFBYEuIaAawzU9ZlAffNQHH/XBR33wUR98GkMfdA1oEzNv3jzKy8uprq7m/vvvbzThU0RERK59CqAmS09Pv2DZN998w5IlS85bFhwczNy5c6/4OLNmzbribbOysvx3std46KGH6NWr1xXvU0RERKSGAmgDkJSU5H9GaEMwZcqUQJcgIiIi1zDdBS8iIiIiplIAFRERERFTKYCKiIiIiKkUQEVERETEVAqgIiIiImIqBVARERERMZUCqIiIiIiYSgFUREREREylACoiIiIiplIAFRERERFTKYCKiIiIiKkUQEVERETEVAqgIiIiImIqBVARERERMZUCqIiIiIiYSgFUREREREylACoiIiIiplIAFRERERFTKYCKiIiIiKkUQEVERETEVAqgIiIiImIqBVARERERMZUCqIiIiIiYyhboAkTqm9vt5v777+fcuXN4PB6GDRvG5MmT+eabb8jMzOT06dN0796dl156iZCQkECXKyIics3TCKhc80JDQ1m3bh25ubl88MEHbNy4ke3btzNnzhwef/xxPvvsMxwOB2vXrg10qSIiIk2CRkDrWXl5OZ9++il33nknAHl5eeTk5DBt2rRL2v6dd94hNTWV0NDQ+iyTr7/+muLiYnr37l2vx7kUnseHX5X9BK36OwAWi4XmzZsDUF1dTVVVFRaLhc8++4xly5YB8MADD7Bw4UIeffTRq3JsERERqZtGQOtZeXk5H3zwwRVv/+6773Lu3LnL2sbr9V72cb7++mt27tx52ds1Fh6Ph7S0NHr06MGgQYNo06YNDocDm833O9h1111HYWFhgKsUERFpGjQC+j1FRUXMnTuXDh06cPDgQdq1a8fgwYP505/+RElJCePGjSMhIYHly5dTVFREaGgoTzzxBK1bt2bdunU4nU6KiopwOp0MHTqUoUOH8uabb1JYWMiUKVPo0aMHvXv3xu12k52dTX5+PsnJyYwdOxaLxXJBPe+++y7FxcU8++yzREZGMnPmTFatWsWRI0eorKykf//+pKenAzB69GgGDBjAnj17GD58OM2aNeP1118nNDSUTp06UVRUxLRp03C73bz88svk5+fj8Xh44IEHuOmmm/jjH/9IZWUl+/fv5+c//zm33nrrBfXUtm3fvn3ZuHEj27Zt49y5c3z33Xf069ePhx9+GIBdu3axdu1avF4vERER/Pa3v63fb2IdgoKC+PDDDykpKSEjI4PDhw8HpA4RERFRAL1AYWEhEydOpFWrVkyfPp1PP/2U3/3ud2zbto233nqLuLg42rZty9SpU9m7dy9Lly4lKysLgIKCAmbOnElFRQXjx4/nZz/7GQ8++CD5+fn+dfLy8jh69CgLFy4kOjqaGTNmcODAATp37nxBLUOHDuWdd95h5syZREZGAjBy5Ejsdjter5ff/e53HDt2jNatWwMQERHB/Pnzqays5KmnnuLZZ58lPj6eRYsW+ff51ltv0a1bNzIzMykvL+eZZ56he/fu/Pu//ztHjhwhIyOjzt7UtS34RlAXLFiAzWZj/Pjx3HXXXYSEhLBy5Up/HWVlZbXuNzc3l9zcXADmzZt3ud+yOsXFxdW6LC0tjX379lFaWkpUVBQ2m43Dhw9zww031LqN2Ww2W4OoI9DUBx/1wUd98FEffNQHn8bcBwXQH4iPjycpKQmAG264ge7du2OxWEhKSuLkyZM4nU4mTZoEQLdu3SgrK8PlcgHQu3dvgoODCQ4OxuFwUFJSUusx2rdvT2xsLABt2rShqKio1gBam82bN/PRRx/h8Xg4ffo03377rT+A1oxaFhQUEB8fT3x8PAC33XabP+Dt3r2b7du3k5OTA0BlZSVOp/OSjn2xbbt160Z4eDgArVq1wul0UlZWxo033uivw26317rf1NRUUlNTL6mGy1FT26lTp7DZbDgcDioqKnjvvffIzMykf//+vPbaa9xzzz2sWrWKlJSUS+5FfYqLi2sQdQSa+uCjPvioDz7qg4/64NMY+pCYmFjrcgXQHwgODvZ/bbFY/K8tFgter5egoKA6t625nhDAarXi8Xh+9BhWq/WSr9ksKioiJyeH559/HrvdzrJly6iqqvK/fyk3KhmGwaRJky74gbiUKemLbfvDc6rr3APhu+++Y/z48Xi9XrxeL//2b/9GWloaHTt2JDMzkwULFtC1a1dGjhwZ6FJFRESaBN2EdJk6d+7MJ598Avim0yMiIvwjf7Vp1qwZFRUVV3y8sLAw3G43AC6Xi7CwMMLDwzlz5gy7du2qdZvExESKioooKioCfKOmNXr27Mn69esxDAOAo0eP+o/zY3XWtW1dOnbsyL59+/x11DUFX9+6dOnCBx98QG5uLv/4xz+YMGECAK1bt+add97hs88+47//+7/r/UkDIiIi4qMR0MuUnp7O8uXLmTx5MqGhoYwePfqi60dERNCpUycmTZpEr169LvsxR6mpqcyZM4eYmBhmzpxJmzZtmDBhArGxsXTq1KnWbUJCQsjIyGDu3LmEhobSrl07/3sjRozg1VdfZfLkyRiGQXx8PNOmTaNbt2787W9/Y8qUKXXehFTXtnWJjIzkiSee4IUXXsAwDCIjI5kxY8aPnnPN45NERETk2mQxaoaz5JridrsJCwvDMAxWr15NQkICd999d6DLuiQFBQWBLiGgGsM1PWZQH3zUBx/1wUd98FEffBpDH3QNaBOTm5vLxx9/THV1NW3btiUtLS3QJYmIiIgACqANRlZWlv9ayRoPPfQQvXr1uqL93X333Vc84rlhwwbefffd85Z16tSJxx577Ir2JyIiIvJ9CqANxJQpUwJdgl9KSgopKSmBLkNERESuUboLXkRERERMpQAqIiIiIqZSABURERERUymAioiIiIipFEBFRERExFQKoCIiIiJiKgVQERERETGVAqiIiIiImEoBVERERERMpQAqIiIiIqZSABURERERUymAioiIiIipFEBFRERExFQKoCIiIiJiKgVQERERETGVAqiIiIiImEoBVERERERMpQAqIiIiIqZSABURERERUymAioiIiIipFEBFRERExFQKoCIiIiJiKgVQERERETGVAqiIiIiImEoBVBqk48ePM2LECAYPHkxKSgr/8z//E+iSRERE5CqxBboAkdrYbDZmzpxJ9+7dKSsr46677mLQoEF07Ngx0KWJiIjIT6QRUDGV1+u9pPVatmxJ9+7dAbDb7XTo0IHCwsL6LE1ERERMohFQqdMf//hH7HY7w4YNA2Dt2rU4HA6qq6v5/PPPqaqqol+/fqSnpwOwYMECTp06RVVVFUOHDiU1NRWAX/7yl6SlpbFnzx4yMjLo3LnzZdWRn5/P3r17uemmm67uCYqIiEhAaARU6pSSksKmTZsA38jl5s2biYqK4sSJE8ydO5cFCxbw1Vdf8eWXXwKQmZnJ/PnzmTdvHuvXr6e0tBSAc+fO0b59e7Kysi47fJaXl/P444/z7LPPEhERcXVPUERERAJCI6BSp/j4eOx2O0ePHqWkpIQ2bdpw+PBhdu/ezdSpUwFwu90UFhbSpUsX3n33XbZu3QqA0+nkxIkTREREYLVa6d+/f53Hyc3NJTc3F4B58+YRFxcHQFVVFY8++igPP/wwjzzySD2fbcNhs9n8PWjK1Acf9cFHffBRH3zUB5/G3AcFULmoIUOGsHHjRs6cOUNKSgp79+7l3nvvJS0t7bz18vLy2LNnD8899xyhoaHMmjWLqqoqAIKDg7Fa6x5sT01N9U/Xgy+8GobBU089RevWrXn44YdxOp31c4INUFxcXJM637qoDz7qg4/64KM++KgPPo2hD4mJibUu1xS8XFS/fv3YtWsXR44coVevXvTs2ZMNGzbgdrsBKC4upqSkBJfLRfPmzQkNDeX48eMcOnToJx1369at/OUvf2Hz5s2kpaWRlpbGRx99dDVOSURERAJMI6ByUTabja5du9K8eXOsVis9e/bk+PHj/OY3vwEgLCyMsWPH0qtXLz788EMmTJjAddddR4cOHX7Scfv168fx48evximIiIhIA6MAKhfl9Xo5dOgQEydO9C8bOnQoQ4cOvWDdZ555ptZ9vPHGG/VWn4iIiDQ+moKXOn377beMGzeO7t27c9111wW6HBEREblGaARU6tSqVSuWLl0a6DJERETkGqMRUBERERExlQKoiIiIiJhKAVRERERETKUAKiIiIiKmUgAVEREREVMpgIqIiIiIqRRARURERMRUCqAiIiIiYioFUBERERExlQKoiIiIiJhKAVRERERETKUAKiIiIiKmUgAVEREREVMpgIqIiIiIqRRARURERMRUCqAiIiIiYioFUBERERExlQKoiIiIiJhKAVRERERETKUAKiIiIiKmUgAVEREREVMpgIqIiIiIqRRARURERMRUCqAiIiIiYioFUBERERExlQKoiIiIiJhKAVRERERETKUAKiIiIiKmUgAVEREREVMpgIqIiIiIqSyGYRiBLkJEREREmg6NgEqDMm3atECXEHDqgY/64KM++KgPPuqDj/rg05j7oAAqIiIiIqZSABURERERUwXNmjVrVqCLEPm+5OTkQJcQcOqBj/rgoz74qA8+6oOP+uDTWPugm5BERERExFSaghcRERERU9kCXYAIwK5du3jllVfwer0MGTKEe++9N9Al1Zvly5ezY8cOHA4H2dnZAJSVlfHiiy9y8uRJWrRowYQJE7Db7RiGwSuvvMLOnTsJDQ0lMzOz0U63/JDT6WTZsmWcOXMGi8VCamoqQ4cObXK9qKysZObMmVRXV+PxeOjfvz/p6ekUFRWxaNEiSktLSU5OZuzYsdhsNqqqqli6dClfffUVERERjB8/nvj4+ECfxlXh9XqZNm0aMTExTJs2rUn2YPTo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AVREpIGLjY3FZrOxevXqWm8GWrt2LQDZ2dnY7Xa++OILXn755Tr3Fxoayrlz5/yvvV4vZ8+eveLjX23FxcUYhuEPoU6nkz59+hAdHU1ZWRkVFRX+EOp0Oi/6hIDvB1mAqqoqsrOzGTNmDH369MFms7FgwYJLqisiIoLg4GAKCwtp06bNee/FxsYycOBAnnzyycs4U5GmS1PwIiINXHR0ND179uT111/H5XLh9XopLCz0T7NXVFQQFhZGeHg4xcXF5OTknLd9VFQURUVF/teJiYlUVVWxY8cOqqur+ctf/kJVVdUVH/9qKykpYf369VRXV/P5559z/PhxbrrpJuLi4ujUqRNvvvkmlZWVHDt2jA0bNjBw4MA69+VwODh58iRerxeA6upqqqqqiIyMJCgoiJ07d7J79+5LqstqtZKSksLrr79OcXExXq+XgwcPUlVVxcCBA9m+fTu7du3C6/VSWVlJXl4ep06duio9EbnWaARURKQRGDNmDL///e+ZOHEiFRUVtGzZknvuuQeABx54gKVLl/Loo4+SkJDAoEGDeOedd/zb3nvvvbz88susWbOG++67j+HDh/PYY4+xYsUKvF4vw4cP/9Gp64sd/2rr0KEDJ06cICMjg6ioKCZOnEhERAQATz31FKtWreJXv/oVdrudBx544KKPrBowYACffPIJGRkZxMfHM3/+fP7jP/6DF198kaqqKm6++Wb69OlzybU98sgjvPnmm0yfPh23202bNm34zW9+Q1xcHFOnTmXNmjUsXrwYq9VK+/btefzxx39yP0SuRXoQvYiINBg1j2GaPXt2oEsRkXqkKXgRERERMZUCqIiIiIiYSlPwIiIiImIqjYCKiIiIiKkUQEVERETEVAqgIiIiImIqBVARERERMZUCqIiIiIiYSgFUREREREz1/wDDM2tCThxfGQAAAABJRU5ErkJggg==)

# Mean encodnig improved the model performance the RMSE is about `1.25`

# working with the price 

# In[ ]:


item_prices = pd.DataFrame(sales.groupby('item_id')['item_price'].unique()).reset_index()
item_prices


# In[ ]:


# taking different statictical measurements of the price
item_prices['mean_price'] = item_prices.item_price.apply(lambda p : np.mean(p))


# In[ ]:


item_prices


# adding mean_price and removing item_price

# In[ ]:


all_data = all_data.merge(item_prices.drop('item_price',axis = 1) , how = 'left' , on = 'item_id')
test = test.merge(item_prices.drop('item_price',axis = 1) , how = 'left' , on = 'item_id')
all_data.head()


# In[ ]:


test.isna().sum() # let's see if there are any nulls


# In[ ]:


len([i for i in test.item_id.unique() if i not in sales.item_id.unique()]) # how many item_id is in the test and not in the train


# In[ ]:


test.item_id.nunique()


# there are `366` out of `5100` unique test item_id not in the train data so i will impute them with the category_id_mean_price

# I will impute the missing prices with the mean price of the category of that item

# In[ ]:


# for each category get its mean price
category_mean_prices = pd.DataFrame(all_data.groupby('item_category_id')['mean_price'].mean()).reset_index()
category_mean_prices


# In[ ]:


dic = {} # making a dictionary wehere each item_category correspond to mean value of that category
for i in category_mean_prices.item_category_id.unique() :
  dic[i] =category_mean_prices[category_mean_prices.item_category_id == i]['mean_price'].values[0]
dic


# In[ ]:


# now get the index of the items that do not have prices and impute with the made dictionary
ind = test[test.mean_price.isna()].index
for i in ind :
  test.loc[i , 'mean_price'] = dic[test.loc[i , 'item_category_id']]
  
# there are no nulls now


# # Adding lags

# In[ ]:


# train lags for shop_id and item_id
lag_list = [1, 2, 3,4,5,12 ]

for lag in lag_list:
    ft_name = ('item_shop_lag_%s' % lag)
    all_data[ft_name] = all_data.sort_values('date_block_num').groupby(['shop_id','item_id'])['item_cnt_month'].shift(lag)
    # Fill the empty shifted features with 0
    all_data[ft_name].fillna(0, inplace=True)


# adding the lags to the test data

# In[ ]:


# for the shop_id - item_id lags
def get_test_lags_shop(all_data , test, lag) :
    
    shifted = all_data[['date_block_num','shop_id','item_id', 'item_cnt_month']]
    shifted.columns = ['date_block_num','shop_id','item_id', 'item_shop_lag_'+ str(lag)]
    shifted['date_block_num'] -= lag
    test_lag = pd.merge(test, shifted, on=['date_block_num','shop_id','item_id'] , how = 'left')
    return test_lag['item_shop_lag_'+ str(lag)] #return the last column (the lags) 


# In[ ]:


test_lags = test.copy() # taking a copy to experemint with
for lag in [1,2,3,4,5,12] :
    lag_values = get_test_lags_shop(all_data ,test_lags, lag)
    test_lags['item_shop_lag_'+ str(lag)] = lag_values
test_lags.fillna(0 , inplace = True) 


# testing the lags impact

# In[ ]:


lgbm = LGBMRegressor(verbose = 0 , n_jobs = -1,random_state = random_state)
lgbm.fit(all_data.drop(['item_cnt_month','city','main_category','sub_category'],axis = 1), all_data.item_cnt_month)

# saving the model in order to run it again witout taking so much time
file_name = 'lgbm_adding_lags.sav'
pickle.dump(lgbm , open(file_name, 'wb'))


# In[ ]:


# submitting in the leaderboard
lgbm = pickle.load(open('/content/lgbm_adding_lags.sav', 'rb'))
preds_lgbm = lgbm.predict(test_lags.drop(['city','main_category','sub_category'],axis = 1))
sub = sample_submission
sub.item_cnt_month = preds_lgbm
sub.to_csv('lgbm_adding_lags.csv' , index = False)


# RMSE : `1.25644`

# In[ ]:


# plot importance
plt.style.use('ggplot')
ax = plot_importance(lgbm)
fig = ax.figure
fig.set_size_inches(9, 13)


# ![](data:image/png;base64,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oRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiLyhDp//jxdu3alVatWtG7dmoULFwLw22+/0b17d5o1a0b37t25evUqAOvWrSMgIIDAwEDat2/Pnj17CrJ8EXmCmSwWi6WgixD5swsXLhR0CZIDDw8PkpKSCroMyUVO83Px4kUSExOpU6cOycnJtGvXji+++ILw8HCKFi3K4MGDmTt3Lr///jvvvPMO169fx8XFBZPJRGxsLAMGDGDr1q0F9I6eHPqzY9s0P/nL09Mzx3Z7g+t4bI0fP57Q0FASExM5evQozZs3N3T8LVu2cOLECfr27Zsv/c+bN48GDRrQuHHjR9LfoUOHWLJkCRkZGdjb29OzZ09q166dp3Mz+73wSGqQR+tiQRcgd/Xn+bFbsBKA0qVLU7p0aQDc3Nzw9vYmISGBdevWERERAcD//M//0LVrV9555x1cXV2tfdy4cQOTyWRY/SLy96IAmkehoaEAXLp0ie3btxseQB83hQsXZsyYMRQvXpy4uDgmT57Mp59+WtBlifxtnT17lujoaOrXr09SUpI1mJYqVSrb6s+aNWsICwvj8uXLfPnllwVVrog84RRA86hnz54sXryYpUuXcu7cOUJCQvDz86NDhw4sWbKE2NhY0tPTadu2LYGBgcTExBAeHo6rqytxcXE0adIELy8vVq9eTVpaGiEhIZQpUybHsaKiooiIiMBsNuPi4sLEiROBW9dtTZ48mYsXL+Lr60uPHj0A2L59O9999x0A9evXt7b37NkTf39/Dh06RNGiRRk+fDju7u73fK8RERHs27ePtLQ0qlWrRv/+/TGZTBw/fpxPPvkEk8mEj48PBw4cYObMmTn2UalSJevj8uXLk5aWRnp6Og4ODnn/0EXkkbh+/Tr9+vVj4sSJFC5cONtrJpMp20pn+/btad++Pbt27WLGjBl88803RpcrIn8DCqD3KSgoiFWrVjF27FgAIiMjcXFxISwsjPT0dCZMmEDdunUBOHPmDLNnz8bNzY3Bgwfj7+9PWFgYq1evZu3atfTu3TvHMSIiInjnnXcoXrw4169ft7afPn2a6dOnY29vz/Dhw2nXrh1m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cnFxITc313ocFBTE119/TUBAACaTiZSUFBo0aHBbY5w7dw5fX198fX3Zt28fFy9eLPfcVq1asWrVKjIzM6lbty47duygb9++QElxvGvXLrp27UpCQgL+/v43HbugoAAAd3d38vLy2L17N507d8bNzQ0XFxeOHTuGr68vO3bsuGE/1+IxGo2cP3+es2fPctddd1Xo81/b5Sz2xd5mCZYuXXpd21NPPVXmuWPHjmXs2LHVHZKIiFSQCtBK8vb2xmg0ltqElJqaypQpU4CSwi0qKuq2xvjwww85e/YsULLs3rx5c06ePFnmufXr12fgwIHWjUrt27enU6dOADg5OXH8+HHi4uJwd3fn+eefv+nYbm5uhIeHM2nSJDw9PUvNWI4ePZply5ZhMBho27Ztmcvp1xw6dIiYmBgcHBwwGo2MGDGCunXrVvQrEBERkVpMD6Kvxa7t3K8qeXl5ODs7A/Dpp5+SkZHBsGHDqqz/a/QgevtkbzOgUpryY7+UG/um/FQv3QMqty0xMZH169dTXFyM2WzWkqaIiIjcEhWgNSguLo6dO3eWagsLC+Oxxx6rkv7Lmv1csWIFR44cKdUWGRlJz549b9pfly5drLvqr9m3b991j2Ty8vK67dsQREREpPbSErzYHS3B2yctU9k35cd+KTf2TfmpXuUtwRttHIeIiIiI/MWpABURERERm1IBKiIiIiI2pQJURERERGxKBaiIiIiI2JQKUBERERGxKRWgIiIiImJTKkBFRERExKZUgIqIiIiITakAFRERERGbUgEqIiIiIjalAlREREREbEoFqIiIiIjYlApQEREREbEpFaAiIiIiYlMqQEVERETEplSAioiIiIhNqQAVEREREZtSASoid5SJEycSGBhIr169rG1z584lIiKC3r1789RTT3Hu3DkAjh8/zsMPP8w999zDO++8U1Mhi4jIn6gAlSqRnZ3NV199ZT1OTk5m9uzZNRiR1FZPPPEEq1evLtX2r3/9i/j4eL755hsiIiJYtGgRAJ6enrz22muMGjWqJkIVEZFymGo6AKkdsrOz+frrr+nTp89t91U0on8VRCRV7XwNj++wfAMAoaGhnD59utR79erVs77OycnBYDAAYDabMZvNfPvtt7YLVEREbkoF6F9Qamoqr7/+Or6+vhw9ehQfHx969OjB2rVruXz5Ms8++yyNGjVi6dKlpKam4uTkxMiRI2nevDkxMTGkpaWRmppKWloakZGRREZGsmbNGs6dO0dUVBSBgYF06NCBvLw8FixYwOnTp2nZsiXjx4+3FgYiVW327NnExsbi7u7O2rVrazocERG5AS3B/0WdO3eOhx9+mEWLFvH777+TkJDAjBkzGDx4MHFxccTExHDPPfcwf/58nnrqKd566y3rtSkpKUyfPp3XX3+d2NhYCgsLGThwII0aNWLevHkMHjwYgF9//ZWhQ4eycOFCzp8/z5EjR2rq48pfwNSpU/nxxx959NFHWbVqVU2HIyIiN6AZ0L8oLy8vvL29AWjWrBn33nsvBoMBb29vLly4QFpaGpMmTQIgICCArKwscnJyAOjQoQOOjo44Ojri4eHB5cuXyxyjVatWNGzYEIAWLVqQmpqKv7//defFx8cTHx8PoPtGpVxms9n6OisrCwcHh1Jt1wwfPpxHHnmk1J8lV1dXXF1dyzy/tjCZTLX6893JlBv7pvzUDBWgf1GOjo7W1waDwXpsMBgoLi7GwcGh3GtNpv/7Y2M0GikqKrrpGEajkeLi4jLPi4iIICIiolLxy19PWlqa9XVGRgZFRUXWthMnTtCyZUsAPv74Y1q0aFHq/Gv3hf6xrbYxm821+vPdyZQb+6b8VK/GjRuX2a4CVMrk7+/P9u3befzxx0lOTqZevXq4urqWe76Liwu5ubk2jFD+qsaMGcPOnTtJT08nODiYyZMns2XLFn755ReMRiNNmjSxzn6mpqby4IMPkpWVhdFoZPny5WzdurXUpiUREbE9FaBSpieeeIKlS5cyefJknJycGDt27A3Pr1evHq1bt2bSpEkEBQXRoUOHWx772m5nsS/2MkuwdOnS69qeeuqpMs/18vJi79691R2SiIhUksFisVhqOgiRP0pJSanpEKQM9lKAStmUH/ul3Ng35ad6lbcEr13wIiIiImJTKkBFRERExKZUgIqIiIiITakAFRERERGbUgEqIiIiIjalAlREREREbEoFqIiIiIjYlApQEREREbEpFaAiIiIiYlMqQEVERETEplSAioiIiIhNqQAVEREREZtSASoiIiIiNqUCVERERERsSgWoiIiIiNiUClARERERsSkVoCIiIiJiUypARURERMSmVICKiIiIiE2pABURERERm1IBKiIiIiI2pQJURERERGxKBaiI1JiJEycSGBhI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gF66dAmAIUOGkJGRwdChQ8nJyWHIkCFcuHCBp59+utqDFBEREZHa46a74J977jnee+89XF1diYqKYtasWQwYMACz2Yynp6ctYhQRERGRWuSmBajFYil1fPToUVq1alVtAYmIiIhI7XbTJfhrO95FRERERKrCTWdAi4qKSEpKsh4XFxeXOgYICAio+shEREREpFa6aQHq4eHB22+/bT2uW7duqWODwcBbb71VPdGJiIiISK1z0wJ0yZIltohDRERERP4iKvwcUBGR2zVx4kQCAwPp1auXtW3jxo307NmTpk2bsn///uuu+f333/H19eWdd96xZagiIlKNbjoDKmJrRSP613QIUobzt3Gtw/INADzxxBMMGzaM5557zvqev78/y5cvZ+rUqWVe+8orr9CzZ8/bGF1EROyNZkCryddff822bdsA2Lp1K+np6bfUT1xcXFWGVa7k5GSOHDlik7Hkrys0NPS65wf7+vqW+2i3zZs34+3tTevWrW0RnoiI2IgK0GrywAMP0L17d6CkAM3IyLilftavX1/pa4qLiyt9jQpQsTfZ2dksWbKEiRMn1nQoIiJSxbQEX0W2bdvGxo2xMKn3AAAgAElEQVQbMRgMeHt7c9ddd+Hs7IyXlxe//PIL//u//0udOnV46qmniI+P59///jcABw4c4KuvviIqKuq6PlevXk1+fj5RUVE0a9aMZ599lrlz53Lx4kUKCgqIjIwkIiICgMGDB9O7d28OHjzI8OHDSUlJ4bPPPsPV1ZXmzZvj6OjI8OHDyczM5N133+XixYsA/POf/6RBgwZ88803GI1Gtm/fzjPPPEObNm2ui6esa/39/YmJiSEtLY3U1FTS0tKIjIwkMjKyzO9l/Pjx1fL9S+2zYMECRowYgZubW02HIiIiVUwFaBU4ffo0cXFxvPbaa7i7u5OVlcWmTZuAkiXHzZs3M3jwYHx8fLBYLLz//vtkZmbi7u7Od999V+79bU8//TSbN29m3rx51rYxY8ZQt25d8vPzeeGFF+jcuTP16tXj6tWrtGrViiFDhpCens6bb77JnDlzcHZ2ZsaMGTRv3hyAVatW8dBDD+Hv709aWhrR0dEsWrSI3r174+zsTP/+5d9/Wd61ACkpKbz88svk5uYyYcIEHnjgAc6ePXvd91KW+Ph44uPjAZg9e3blEyB2z2w2W19nZWXh4OBQqg3A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ubmu11FRUaxevZq6detisVhIT0+/6quBfo+AgAACAgLYt28fNWvWZOPGjTd97I2eGL+bVa5c2XW7wa/Nnj3bDdWIiIi4hwLofaRSpUqYzearHkLKyMhgxIgRAAQFBTFs2LA7Nl5CQoLrIaQr95aKiIiI6IvoxePc619Ef7fSfVKeTf3xXOqNZ1N/SlZx94Dqb8GLiIiIiKG0BC+3ZenSpXz77bdXbWvRogXPPPOMmyoSERGRu4UCqNyWZ555RmFTREREbouW4EVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVCRO8Rut9OuXTv+/Oc/A9C/f38effRR/ud//ofBgwdTUFDg5gpFREQ8gwKoB1u+fDl5eXklPs7hw4fZvn17iY9zr/vXv/5F9erVXa87derEhg0bWLt2LTabjYULF7qxOhEREc9hcXcBAg6HA7P52n8LrFixgkcffRRfX9/ffa7rOXz4MGlpaTRs2PCWjisp9j4d3F3CTfGa/bnr5/T0dNauXcuLL77Iu+++C0Dbtm1d70dFRXHixAnDaxQREfFECqC3aPHixVitVuLi4gBYtGgRwcHBFBYW8u2331JQUEDTpk3p1q0bAFOmTOHMmTMUFBTQvn17YmJiAOjVqxexsbHs3r2b+Ph4atasedU4K1asICsri7FjxxIUFMSYMWOYPXs2aWlp5Ofn07x5c9cY/fr1o0WLFuzevZsOHTpQqlQpPvjgA3x9falRowYZGRkkJiZis9mYO3cux44dw26307VrVx555BEWL15Mfn4++/bto1OnTrRs2fKa6y7q2CZNmrB+/Xq2bt1KXl4ep06domnTpjz77LMA7Ny5k0WLFuFwOAgMDOQf//hHifXF3caMGcPLL7/MxYsXr3mvoKCATz/9lFdffdUNlYmIiHgeBdBbFB0dTXJyMnFxcTgcDjZt2kT37t3ZvXs3EyZMwOl0MmXKFH788Udq165NQkICVquV/Px8Ro4cSbNmzQgMDCQvL49q1aq57hf8rfbt27N8+XLGjBlDUFAQAN27d8dqteJwOHj11Vc5cuQIlStXBiAwMJDJkyeTn5/P3//+d8aOHUt4eDhvvvmm65xLly6lbt26JCQkcOnSJUaNGkW9evX405/+RFpaGvHx8cVed3HHwuUZ1ClTpmCxWBg4cCBPPPEEPj4+vPPOO646igpm94o1a9YQFhZG/fr12bRp0zXvjxo1imbNmtGsWTM3VCciIuJ5FEBvUXh4OFarlUOHDnH+/HkiIyM5cOAAu3btYvjw4cDl2cKTJ09Su3ZtVqxYwZYtWwDIzMzkxIkTBAYGYjabad68+S2NvWnTJtauXYvdbufs2bMcP37cFUCvzFqmp6cTHh5OeHg4AK1atSIlJQWAXbt2sW3bNpYtWwZAfn4+mZmZNzX29Y6tW7cu/v7+AFSsWJHMzEwuXrxIrVq1XHVYrdZiz52SkuKqcdKkSTf/gbhZWFgYAKmpqaxdu5aWLVtis9m4cOECQ4cOZd68eYwbN47s7GzmzJlzy7dGeBqLxeK6ZvE86o/nUm88m/rjHgqgt6Ft27asX7+ec+fOER0dzZ49e3j66aeJjY29ar/U1FR2797NuHHj8PX15ZVXXnE9Ce3t7X1LgSQjI4Nly5YxceJErFYrM2fOvOqp6pu5T9TpdDJkyBAiIiKu2n7gwIHfday3t7frtdlsxm633/B8vxYTE+O6NeFuciWADxw4kIEDBwKX/5Ewa9YsXn/9dd566y1WrFjB4sWLycrKcmepd0RYWNhN/4NFjKf+eC71xrOpPyXrt7nhirt7SsZNmjZtys6dO0lLSyMqKooGDRqwbt06bDYbAFlZWZw/f56cnBwCAgLw9fXll19+4eeff76lcfz8/FznzMnJwc/PD39/f86dO8fOnTuLPCYiIoKMjAwyMjIArloSbtCgAStXrsTpdAJw6NAh1zi5ubnXraW4Y4vz8MMPs3fvXlcd9/ISfHESExPJzMykQ4cOxMbGMnXqVHeXJCIi4hE0A3obLBYLderUISAgALPZTIMGDfjll1946aWXgMuBbsCAAURFRbFmzRoGDRpE+fLlr/qKnpsRExPD+PHjKVOmDGPGjCEyMpJBgwYRGhpKjRo1ijzGx8eH+Ph4JkyYgK+vL1WrVnW916VLF+bNm8fQoUNxOp2Eh4eTmJhI3bp1+eyzzxg2bFixDyEVd2xxgoKC6Nu3L6+//jpOp5OgoCBGjx59U9f966fL7zYtW7Z0fX5Hjx51czUiIiKeyeS8MqUlN83hcDBixAgGDx5M+fLl3V3ONWw2G35+fjidTubMmUO5cuV46qmn3F3WTUtPT3d3CVIELVN5NvXHc6k3nk39KVnFLcFrBvQWHT9+nEmTJtG0aVOPDJ9w+aGer776isLCQh566KFr7k0VERERcSfNgHqApKQk172SV/Ts2ZOoqCjDa1m3bh0rVqy4aluNGjV4/vnnDatBM6CeSbMEnk398VzqjWdTf0pWcTOgCqDicRRAPZN+SXs29cdzqTeeTf0pWXoKXkREREQ8ggKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDKUAKiIiIiKGUgAVEREREUMpgIqIiIiIoRRARURERMRQCqAiIiIiYigFUBERERExlAKoiIiIiBhKAVREREREDGVxdwEidxubzUbnzp3Jy8vDbrcTFxfH0KFD2bhxI+PGjcPhcBAQEMDUqVN56KGH3F2uiIiIx1EAFblFvr6+LFmyhICAAAoKCujUqRPR0dGMHDmS9957j+rVqzNv3jymTZvGm2++6e5yRUREPI4CaAm7dOkSX3/9NY8//jgAqampLFu2jMTExJs6fvny5cTExODr61uSZXL48GGysrJo2LBhiY5zM+x9Ori7hCJ5zf4cAJPJREBAAACFhYUUFBRgMpkwmUxkZ2cDkJ2dTdmyZd1Wq4iIiCfTPaAl7NKlS6xevfq2j1+xYgV5eXm3dIzD4bjlcQ4fPsyOHTtu+bj7ld1uJzY2lvr169O6dWsaNmzI66+/Tq9evWjUqBGffvop/fv3d3eZIiIiHkkzoL+SkZHBhAkTqF69Ovv376dq1ao89thjfPzxx5w/f54XX3yRcuXK8fbbb5ORkYGvry99+/alcuXKLFmyhMzMTDIyMsjMzKR9+/a0b9+ehQsXcvLkSYYNG0b9+vVp2LAhNpuN5ORkjh07RpUqVRgwYAAmk+maelasWEFWVhZjx44lKCiIMWPGMHv2bNLS0sjPz6d58+Z069YNgH79+tGiRQt2795Nhw4dKFWqFB988AG+vr7UqFGDjIwMEhMTsdlszJ07l2PHjmG32+natSuPPPIIixcvJj8/n3379tGpUydatmx5TT1FHdukSRPWr1/P1q1bycvL49SpUzRt2pRnn30WgJ07d7Jo0SIcDgeBgYH84x//KNkmGsTLy4s1a9Zw/vx54uPj2bdvH7Nnz2b+/Pk0bNiQf/7zn4wdO5bXX3/d3aWKiIh4HAXQ3zh58iSDBw+mYsWKjBw5kq+//ppXX32VrVu3snTpUsLCwnjooYcYPnw4e/bsYcaMGSQlJQGQnp7OmDFjyM3NZeDAgbRr144ePXpw7Ngx1z6pqakcOnSIN954g5CQEEaPHs1PP/1EzZo1r6mlffv2LF++nDFjxhAUFARA9+7dsVqtOBwOXn31VY4cOULlypUBCAwMZPLkyeTn5/P3v/+dsWPHEh4eftV9iEuXLqVu3bokJCRw6dIlRo0aRb169fjTn/5EWloa8fHxxX42xR0Ll2dQp0yZgsViYeDAgTzxxBP4+PjwzjvvuOq4ePFikedNSUkhJSUFgEmTJt1qywwTFhZW5LbY2Fi+++479u3bR7t27QB47rnn+OMf/1jkMXcri8VyT13PvUb98VzqjWdTf9xDAfQ3wsPDqVSpEgAPPvgg9erVw2QyUalSJU6fPk1mZiZDhgwBoG7duly8eJGcnBwAGjZsiLe3N97e3gQHB3P+/Pkix6hWrRqhoaEAREZGkpGRUWQALcqmTZtYu3Ytdruds2fPcvz4cVcAvTJrmZ6eTnh4OOHh4QC0atXKFfB27drFtm3bWLZsGQD5+flkZmbe1NjXO7Zu3br4+/sDULFiRTIzM7l48SK1atVy1WG1Wos8b0xMDDExMTdVgztdudYzZ85gsVgIDg4mNzeXVatWkZCQwLlz5/juu++oWrUqn332GVWqVLnpz/ZuEBYWdk9dz71G/fFc6o1nU39KVkRERJHbFUB/w9vb2/WzyWRyvTaZTDgcDry8vIo91mL5v4/TbDZjt9tvOIbZbL7pezYzMjJYtmwZEydOxGq1MnPmTAoKClzv38yDSk6nkyFDhlzzH8SBAwd+17G/vabirv1ecOrUKQYOHIjD4cDhcPDHP/6R2NhYkpKS6Nu3LyaTidKlS5OcnOzuUkVERDySHkK6RTVr1mTjxo3A5eX0wMBA18xfUUqVKkVubu5tj+fn54fNZgMgJycHPz8//P39OXfuHDt37izymIiICDIyMsjIyAAuz5pe0aBBA1auXInT6QTg0KFDrnFuVGdxxxbn4YcfZu/eva46iluCv9vUrl2b1atXk5KSwpdffsmgQYMAePLJJ1m7di0pKSl88sknrplpERERuZpmQG9Rt27dePvttxk6dCi+vr7069fvuvsHBgZSo0YNhgwZQlRU1C1/zVFMTAzjx4+nTJkyjBkzhsjISAYNGkRoaCg1atQo8hgfHx/i4+OZMGECvr6+VK1a1fVely5dmDdvHkOHDsXpdBIeHk5iYiJ169bls88+Y9iwYcU+hFTcscUJCgqib9++vP766zidToKCghg9evQNr/nK1x2JiIjIvcnkvDKdJfcUm82Gn58fTqeTOXPmUK5cOZ566il3l3VT0tPT3V2CFEH3SXk29cdzqTeeTf0pWboH9D6TkpLCV199RWFhIQ899BCxsbHuLklEREQEUAD1GElJSa57Ja/o2bMnUVFRt3W+p5566rZnPNetW8eKFSuu2lajRg2ef/752zqfiIiIyK9pCV48jpbgPZOWqTyb+uO51BvPpv6UrOKW4PUUvIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihlIAFRERERFDKYCKiIiIiKEUQEVERETEUAqgIiIiImIoBVARERERMZQCqIiIiIgYSgFURERERAylACoiIiIihrK4uwART2Kz2ejcuTN5eXnY7Xbi4uIYOnQoR48eJSEhgbNnz1KvXj3eeustfHx83F2uiIjIXemuCqBLlizBz8+PDh063PFzf//990RERFCxYsU7fu7blZGRwf79+2nVqlWJj7V+/Xrq169PmTJlSnysG7H3ufP9vRlesz/H19eXJUuWEBAQQEFBAZ06dSI6Opp3332XPn360LFjR0aMGMGiRYt47rnn3FKniIjI3U5L8P+/LVu2cPz48RIdw26339L+p0+f5uuvvy7RMa5Yv349Z8+eva1j7yUmk4mAgAAACgsLKSgowGQy8c033xAXFwdA165d+eKLL9xZpoiIyF3N7TOgNpuNqVOnkpWVhcPhoHPnznz44YdMnDiRoKAg0tLSmD9/Pq+88goAR44c4aWXXiI7O5sOHToQExNT7Ln/85//sHHjRsxmM1FRUfTs2ZOUlBTWrl1LYWEhZcuWZcCAARw+fJitW7fy448/8umnnzJkyBAA5syZw4UL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++9p1arVnb5cuQGLxXJNT8RzqD+eS73xbOqPeyiAynW1bduW9evXc+7cOaKjo9mzZw9PP/00sbGxV+2XmprK7t27GTduHL6+vrzyyisUFBQA4O3tjdlc/GR7TEyMa7n+1zIzMzlz5gwWi4Xg4GByc3NZtWoVCQkJZGZm3tkLlRsKCwvT5+7B1B/Ppd54NvWnZEVERBS5XUvwcl1NmzZl586dpKWlERUVRYMGDVi3bh02mw2ArKwszp8/T05ODgEBAfj6+vLLL7/w888/35HxT506RdeuXYmJiSEuLo7WrVtfE35FRETk7qIZULkui8VCnTp1CAgIwGw206BBA3755RdeeuklAPz8/BgwYABRUVGsWbOGQYMGUb58eapXr37bY3rN/tz1c+3atVm9evXvvg4RERHxHCan0+l0dxHiuRwOByNGjGDw4MGUL1/ekDHT09MNGUdujZapPJv647nUG8+m/pQsLcHLLTt+/Dgvvvgi9erVMyx8ioiIyL1PS/BSrIoVKzJjxgx3lyEiIiL3GM2AioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihFEBFRERExFAKoCIiIiJiKAVQERERETGUAqiIiIiIGEoBVEREREQMpQAqIiIiIoZSABURERERQymAioiIiIihTE6n0+nuIkRERETk/qEZUPEoiYmJ7i5BiqHeeDb1x3OpN55N/XEPBVARERERMZQCqIiIiIgYSgFUPEpMTIy7S5BiqDeeTf3xXOqNZ1N/3EMPIYmIiIiIoTQDKiIiIiKGsri7ABGAnTt38t577+FwOGjbti1PP/20u0u677z99tts376d4OBgkpOTAbh48SJTp07l9OnTPPDAAwwaNAir1YrT6eS9995jx44d+Pr6kpCQQJUqVdx8BfeuzMxMZs6cyblz5zCZTMTExNC+fXv1x0Pk5+czZswYCgsLsdvtNG/enG7dupGRkcGbb75JdnY2VapUYcCAAVgsFgoKCpgxYwYHDx4kMDCQgQMHEh4e7u7LuKc5HA4SExMpU6YMiYmJ6o0H0AyouJ3D4WDOnDmM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)

# In[ ]:





# In[ ]:


all_data.shop_id = all_data.shop_id.astype('int8')
all_data.date_block_num = all_data.date_block_num.astype('int8')
all_data.item_cnt_month = all_data.item_cnt_month.astype('int8')
all_data.item_category_id = all_data.item_category_id.astype('int8')


# adding interaction features with label encoding

# In[ ]:


pd.factorize(['A','b','c','A'])[0]


# In[ ]:


import itertools
cat_features= ['shop_id','item_id','mean_price','month']
# Iterate through each pair of 2 features, combine them into interaction features
all_combinations = list(itertools.combinations(cat_features, 2))
for combination in all_combinations: #for each pair of columns convert them to strings then join them with the + operator.
  interaction = all_data[combination[0]].map(str) + '_' + all_data[combination[1]].map(str)
  interaction_name = combination[0] + '_' + combination[1]

  all_data[interaction_name] = pd.factorize(interaction)[0] # return the interaction column label encoded directly


# In[ ]:


# let's go back to test again
import gc
test = test_lags.copy()
del test_lags
gc.collect()


# In[ ]:


for combination in all_combinations: #for each pair of columns convert them to strings then join them with the + operator.
  interaction = test[combination[0]].map(str) + '_' + test[combination[1]].map(str)
  interaction_name = combination[0] + '_' + combination[1]
  test[interaction_name] = pd.factorize(interaction)[0] # return the interaction column label encoded directly


# In[ ]:


# we don't need them any more
all_data.drop(['city','main_category','sub_category'],axis = 1 , inplace = True)
test.drop(['city','main_category','sub_category'],axis = 1 , inplace = True)


# In[ ]:


lgbm = LGBMRegressor(verbose = 0 , n_jobs = -1,random_state = random_state)
lgbm.fit(all_data.drop(['item_cnt_month'],axis = 1), all_data.item_cnt_month)

# saving the model in order to run it again witout taking so much time
file_name = 'lgbm_after_interactions.sav'
pickle.dump(lgbm , open(file_name, 'wb'))


# In[ ]:


# submitting in the leaderboard
lgbm = pickle.load(open('/content/lgbm_after_interactions.sav', 'rb'))
test = test[all_data.drop('item_cnt_month' , axis = 1).columns] # sorting columns in the same order
preds_gbm = lgbm.predict(test)
sub = sample_submission
sub.item_cnt_month = preds_gbm
sub.to_csv('lgbm_all_features_updated.csv' , index = False)


# RMSE `1.23940`

# working on the lags

# In[ ]:


all_data['sum_lags'] = all_data.item_shop_lag_1 + all_data.item_shop_lag_2 + all_data.item_shop_lag_3 + all_data.item_shop_lag_4 + all_data.item_shop_lag_5
all_data['mean_lags'] = (all_data.sum_lags/5)

test['sum_lags'] = test.item_shop_lag_1 + test.item_shop_lag_2 + test.item_shop_lag_3 + test.item_shop_lag_4 + test.item_shop_lag_5
test['mean_lags'] = (test.sum_lags/5)


# In[ ]:


# validating that the calculation is right
all_data[all_data.item_cnt_month > 5][['item_cnt_month','item_shop_lag_1','item_shop_lag_2','item_shop_lag_3','item_shop_lag_4','item_shop_lag_5','sum_lags','mean_lags']]


# In[ ]:


lgbm = LGBMRegressor(verbose = 0 , n_jobs = -1,random_state = random_state)
lgbm.fit(all_data.drop(['item_cnt_month'],axis = 1), all_data.item_cnt_month)
# saving the model in order to run it again witout taking so much time
file_name = 'working_with_lags.sav'
pickle.dump(lgbm , open(file_name, 'wb'))


# In[ ]:


lgbm = pickle.load(open('/content/working_with_lags.sav', 'rb'))
preds_gbm = lgbm.predict(test)
sub = sample_submission
sub.item_cnt_month = preds_gbm
sub.to_csv('working_with_lags.csv' , index = False)


# RMSE `1.25988`

# In[ ]:


feature_imp = pd.DataFrame(sorted(zip(lgbm.feature_importances_,test.columns) , reverse= True), columns=['Value','Feature'])
plt.figure(figsize=(20, 10))
sns.barplot(x="Value", y="Feature", data=feature_imp)
plt.title('LightGBM Features importance based on gain ')
plt.tight_layout()
plt.show()


# ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABZgAAALICAYAAADyhJW9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAADh0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW9uMy4yLjEsIGh0dHA6Ly9tYXRwbG90bGliLm9yZy+j8jraAAAgAElEQVR4nOzdeVyVZf7/8fc5soMYiohouKCBS4JpKGYuibnk+HXMlrFsXNIatdXIJS01FZfSGsc2txrUCo1JnVEzyn3JhTBFM3M3oANpliyynPv3hw/Pr5MgeAQP4uv5ePiI+7qv+7o+93VurpnHh+tct8kwDEMAAAAAAAAAAFwjs7MDAAAAAAAAAADcnEgwAwAAAAAAAAAcQoIZAAAAAAAAAOAQEswAAAAAAAAAAIeQYAYAAAAAAAAAOIQEMwAAAAAAAADAISSYAQAAbgGdOnXSk08+eU3XDBw4UNHR0eUUEZyJz7Z8bNy4USaTSWfOnHF2KEVyZB6oaCrDPQAAUNmQYAYAAKgESkoYJiQkaPbs2WXe75QpU1S/fv0iz50+fVojR45Uo0aN5OHhoZo1ayoyMlIzZsxQZmamrV6nTp1kMpls/6pXr64uXbpox44ddu1dPr9q1aor+vrrX/8qk8lUYuLpj/1c/ufh4XHtN16MM2fOyGQyaePGjWXWZnl4++23tXz5cmeHcVU3y1jixiqvuQwAADiOBDMAAMAtoHr16vL19b1h/SUnJysiIkLbt2/X9OnT9e2332rXrl2aPHmy9u3bp0WLFtnV79+/v9LS0pSWlqYNGzaoevXq6tGjhy5cuGBXLzg4WAsWLLArS01N1f/+9z/dfvvtpYrtX//6l62vtLQ0nTx58vputpwYhqH8/PxyabtatWry8/Mrl7bLQl5enrNDQAV1o+cyAABQMhLMAAAAt4A/f608JydHw4YNsyUahw8frrFjx6pRo0ZXXPvBBx+oXr168vX1Ve/evfXzzz9Lkj788ENNmDBBJ0+etK0GnjhxogzD0BNPPKG6detq165d6tevn5o0aaIGDRqoe/fuWrZsmWJiYuz68PT0VGBgoAIDAxUeHq5XX31V58+f15EjR+zqDR48WOvWrdNPP/1kK1u0aJHuvfdeNWzYsFRjUa1aNVtfgYGBqlWrlu3c3LlzFRYWJg8PDzVu3FhTp05VQUGB7fyyZcvUpk0bVatWTf7+/nrggQf0ww8/2M5fTnJ37txZJpPJtrp74sSJV4zt1q1bZTKZdOLECdt4uri4aMOGDWrZsqXc3d2VmJio/Px8TZw4UQ0aNJCHh4eaNWum999/366tBQsWqEmTJvLw8FD16tXVoUOHq27T8OcV75eP586dq7p168rHx0dPPvmk8vPz9d5776levXry8/PTsGHD7JK/nTp10uDBgzVmzBj5+/vL19dXw4YNU25urq1Ofn6+xowZozp16sjNzU1NmzbVsmXL7OIxmUz65z//qf79+6tatWoaMGBAsWN5/Phx9e3bV0FBQfLy8tKdd96puLg4u/YuP++vv/66AgMDVb16dT3xxBNX/MHi008/VatWreTh4aEaNWqoR48eOnfunO18Sc9Dcb799ltFRkbKw8NDzZs319dff207ZxiGhg4dqpCQEHl6eqphw4YaN26cLl68aKtz5swZPfjgg/L395eHh4caNmyoWbNm2Y1pSc/EyZMn1b17d3l6eur222/X3LlzS4xbknbu3KkOHTrI09NTfn5+6t+/vywWi+385Wd55cqVCgsLk7e3tzp16nTF7+qflWbOSUpKUo8ePRQQECAfHx/dfffdWrdunV07f57LSvtZAwCA8kOCGQAA4BY0evRorVy5UnFxcdq5c6eqVaumd95554p6u3fv1oYNG/S///1PX3zxhfbv36+XXnpJkvTII49o9OjRqlu3rm018EsvvaR9+/Zp//79Gj16tFxcXIrs32QyFRtbdna2PvzwQ/n7+6tx48Z250JCQtShQwctXrxYkmS1WrVw4UINHTrU0aGwmThxot544w3Fxsbq0KFDevvtt/X+++9r0qRJtjoXL17U+PHjlZSUpC+//FJVqlTRAw88YEu6JiUlSZI+++wzpaWlaffu3dcUg9Vq1ejRozV79mx9//33at26tYYOHaqEhAS9//77OnTokF599VWNHj1aCxculCTt3btXTz/9tMaOHavDhw9r06ZNeuKJJ675/nft2qU9e/boyy+/1Mcff6wlS5aod+/e2r59u9atW6clS5YoLi7O1u9lK1as0C+//KItW7Zo6dKl+vzzzzV27Fjb+XHjxmn+/Pl66623dODAAT3++ON6/PHH9dVXX9m1M2nSJLVr105JSUmaMmVKsWN54cIF3XfffVq7dq3279+vYcOGadCgQdqwYcMVcZ09e1YbN27UJ598ov/+97+aMWOG7fzixYv1+OOPq0+fPkpKStKGDRvUvXt3FRYWSird81CcF198Ua+++qq+/fZbtWnTRn/5y1+UlpYm6VKCOSAgQMuWLdOhQ4f01ltvafHixZo2bZrt+uHDh+v8+fNKTEzU999/r4ULF6pu3bq28yU9E4Zh6K9//at++eUXbdy4UatXr9aqVatsY1qc9PR03X///bY/Dq1evVoHDhxQv3797OqlpaXp3Xff1dKlS7V9+3b9/vvvGjx48FXbLs2c89tvv+mRRx7Rhg0blJSUpG7duql37952f8QpSkmfNQAAKGcGAAAAbnp///vfjS5duhR7vmPHjsaQIUMMwzCMCxcuGG5ubsaCBQvs6rRp08YICQmxa7NmzZpGbm6urWz69OlGYGCg7fj111836tWrZ9fOp59+akgykpKS7Mrr1KljeHt7G97e3kb37t3tYnNxcbGdk2T4+/sbW7dutbtekhEXF2d8+umnRv369Q2r1WqsXbvW8Pf3Ny5evGh3j8WRZLi7u9v68vb2NiZPnmxkZWUZnp6extq1a+3qf/TRR0a1atWKbe+XX34xJNliPX36tCHJ2LBhg1291157zW5sDcMwtmzZYkgyjh8/bhiGYSxevNiQZGzevNlW59ixY4bJZDIOHTpkd+2kSZOM8PBwwzAMIyEhwfD19TXOnz9/1Xv/oz8/L5c/64sXL9rKevbsadSoUcPu8+/du7fx4IMP2o47duxo1KtXzygoKLCVvf/++4a7u7tx4cIFIysry3BzczPmzZtn13+fPn2Mzp07244lGYMHD7arU9xYFqV3797Gk08+aRdXixYt7Oo8/fTTRtu2bW3Ht99+uzFixIgi23P0ediwYYMhye53Kz8/3wgODjbGjx9f7HWzZ882GjVqZDtu0aKF8dprrxVZtzTPxJdffmlIMg4fPmw7b7FYDA8Pj6v+jowfP96oU6eO3XOQnJxsSDI2bdpkGMalZ7lKlSqGxWKx1fnkk08Mk8lk5OTkFNluaeecorRo0cKYMmWK7fjPv+el+awBAED5KnpJCQAAACqtH3/8UXl5eWrbtq1deVRUlFavXm1XFhYWJnd3d9txUFCQbYuMkhiGYXe8ZcsWFRYWaty4cXZfuZcuvaTv8grOs2fP6p133lHfvn21a9cu1atXz65unz59NHLkSH355Zf64IMP9MQTT8jNza1UMUnS1KlT9X//93+24+rVqyslJUU5OTl68MEH7VZXFxYWKjc3VxkZGapZs6aSk5M1adIkJScnKzMz03aPJ0+e1D333FPqGK7m7rvvtv28Z88eGYah1q1b29UpKChQlSpVJEldu3ZVw4YN1aBBA3Xt2lX33Xef+vbtK39//2vqt0mTJnbjGBgYqNDQULvPPzAwUIcOHbK7LjIy0haLJN1zzz26ePGijh49KunSfsodOnSwu6Zjx46KjY29op3SyM7O1uTJk7V69WqlpaUpLy9PFy9eVOfOne3qhYeH2x0HBQXpiy++kCRZLBadPn1a999/f5F9lPZ5KE5UVJTtZxcXF0VGRiolJcVWNn/+fC1YsEAnTpxQVlaWCgoKZLVabeeff/55PfXUU1q7dq06deqkBx54wDaGpXkmDh48KH9/f91xxx228zVr1lRoaGixMV++77Zt29o9B+Hh4apWrZpSUlJsMQQFBdndf1BQkAzDkMViUXBw8BXtlnbOycjI0Guvvaavv/5a6enpKigoUG5ubon7pF/tswYAAOWPBDMAAMAt6mrbVFz258StyWS6InH8Z5eTWocOHdJdd91lK2/QoIEkydfX94oEs6+vr91erK1atVK1atU0f/58TZky5YqYBg4cqKlTp2rHjh367rvvSryPP6pVq9YV+yFf3j92+fLldkm5y6pXr67s7Gzdf//9at++vRYvXmzbu7lZs2YlvpTObDZfMW5FvcCvSpUq8vDwsB1fTjpu375dXl5ednUvf34+Pj7as2ePtm3bpsTERL333nt6+eWX9dVXX6lVq1ZXjeuPXF1dr2i/qLI/JkLLkre3d6nqxcTEaOXKlZo9e7ZCQ0Pl7e2tUaNG6fz583b1inp2Sxv75XpXex4ctXz5co0YMULTp09Xx44d5evrq+XLl+uVV16x1Rk0aJC6d++udevWacOGDerRo4f++te/asmSJaV6JspbUWMrqcTxLSm+gQMH6tSpU5o5c6YaNGggT09PPfrooyX+fl3PZw0AAK4fezADAADcYho1aiQ3Nzft2LHDrnznzp3X3Jabm5ttz9rLwsPD1bx5c02fPr3IJGppmEwmmc1m5eTkFHl+2LBh2rJli9q2bauwsDCH+vijZs2aycPDQ8eOHVOjRo2u+FelShUdOnRIGRkZmjp1qjp16qQmTZro3Llzdonjy4muP49JQECALBaLXXlJ++FKsiWIT506dUVMISEhtnpVqlRRhw4dNHnyZO3du1e1a9e+4kV65WX37t1297V9+3a5u7srJCREjRo1kru7uzZv3mx3zaZNm9S8efOrtlvcWG7evFmPPfaYHn74YYWHh6thw4Yl7tH7ZwEBAapbt67Wr19f5PnSPA9X88ffpYKCAu3atUtNmza1xd+yZUu9+OKLatWqlRo3bmx70eMf1a5dW4MGDdK///1vLVy4UEuXLtVvv/1WqmeiadOmyszMtHvxXmZmpg4fPnzVuJs1a6adO3faJXT37dun8+fPl/h5XU1p55zNmzdr+PDh6t27t+68807Vrl1bx44dc7hfAABwY7CCGQAAoJK4cOGCkpOT7co8PDyuSMB6e3vrqaee0vjx41WrVi3dcccd+uijj3To0KGrfu2/KA0aNFB6erp27Nihxo0by8vLS15eXvroo4/UpUsXRUZG6pVXXlGzZs3k4uKi7777Tlu3blWdOnXs2snJyVF6erqkS1tkzJs3T1lZWerdu3eR/TZq1EiZmZl2q32vh4+Pj8aNG6dx48bJZDIpOjpaBQUF2r9/v7799lvNmDFD9erVk7u7u+bOnatRo0bpxIkTGjNmjN2qTH9/f/n4+Gj9+vVq1qyZ3N3d5efnp86dOys7O1uvvvqqBg8erKSkJM2bN6/EuBo1aqTBgwdr6NChmjlzpqKiopSVlaW9e/cqIyPD9uK0Y8eOqUOHDqpZs6b27t2r06dP2xKa5e2XX37RiBEj9Nxzz+nYsWOaMGGCnnrqKduK5GeffVYTJkxQzZo1FR4erhUrVmjlypX68ssvr9pucWMZGhqqlStX6sEHH5SPj49mz56t1NRU24ry0nrttdf0j3/8Q7Vq1VK/fv1ktVq1YcMGPfroo/L39y/xebia6dOnKzAwUA0aNNDs2bOVkZGh4cOHS5JCQ0O1cOFCrVy5Us2bN9d///tfJSQk2F0/cuRI9ezZU6GhocrNzVVCQoJuv/12Va1aVb6+viU+E126dFF4eLgef/xxzZ07V25ubho9evQVK9L/bOTIkXr77bc1cOBAjRs3Tr/++quGDx+ue++9V/fee+81je8flXbOCQ0N1dKlS9W+fXsVFhbq1VdfveIPDAAAoOJhBTMAAEAl8c0336hly5Z2//r06VNk3RkzZugvf/mL+vfvr8jISJ07d04DBw685oRtnz599NBDD+mBBx5QzZo1NXPmTEnSXXfdpX379ikqKkqjR49WRESEIiIiNGXKFD300EP6+OOP7dpZtmyZateurdq1aysqKkp79+7VZ599po4dOxbbd/Xq1a/YIuB6TJgwQbNnz9b8+fMVHh6u9u3ba86cOapfv76kSwnPJUuW6Msvv1SzZs300ksv6Y033pDZ/P//L7XZbNa8efMUHx+vunXrqmXLlpIuJc7mz5+vjz/+WM2bN9eiRYtse06X5IMPPtALL7ygqVOnqmnTpurSpYs++ugjNWzYUJLk5+en1atXq3v37rrjjjv08ssva/z48RoyZEiZjc3V9OvXT1WrVlX79u316KOPqlevXpo+fbrt/NSpUzV06FA9//zzat68uZYsWaIlS5aoS5cuV223uLGcM2eO6tWrp86dO6tLly6qU6eO+vXrd81xP/nkk/rwww+1YsUKRUREqEOHDlq7dq1cXC6twSnpebiaN954QxMmTFBERIS2bdumlStXKigoSJL01FNPacCAARo0aJBatmypb775RhMnTrS73jAM23h16NBBWVlZWrt2re2PGSU9EyaTSZ9//rmqVaumDh06qFevXurZs6fdljVFqVWrltavX68zZ87o7rvvVq9evdS8eXOtWLHiGkf3SqWZcxYvXiyr1arIyEj16dNH3bt3t9uTHAAAVEwmo6RN9AAAAHBLuO++++Tn56fPPvvM2aHgJtGpUyc1atRICxYscHYouAkx5wAAUDmwRQYAAMAtaP/+/UpKSlJUVJTy8vIUFxenDRs2aO3atc4ODUAlxJwDAEDlRYIZAADgFmQymfTuu+/q2WefldVqVVhYmP7zn/+oe/fuzg4NQCXEnAMAQOXFFhkAAAAAAAAAAIfwkj8AAAAAAAAAgENIMAMAAAAAAAAAHMIezKhwUlNTnR0CgErC399fmZmZzg4DQCXCvAKgLDGnAChrzCsoT0FBQUWWs4IZAAAAAAAAAOAQVjCjwnFd+bWzQwBQSZyX5OrsIABUKswrAMoScwqAssa8cmPl/999zg6hQmAFMwAAAAAAAADAISSYAQAAAAAAAAAOIcEMAAAAAAAAAHAICWYAAAAAAAAAgENIMAMAAAAAAAAAHEKC2QHjx4+XJFksFm3durVc+9q1a5fOnDlTrn1IUlZWlr744oty7wcAAAAAAABA5UGC2QFTpkyRJGVkZJR7gnn37t3XnGAuLCy85n6ysrK0fv36a74OAAAAAAAAwK3LxdkB3IwGDBiguLg4LVu2TGfOnFFMTIw6duyonj17aunSpTp48KDy8/PVrVs3de3aVSkpKYqPj5e3t7dOnTqlqKgoBQcHa82aNcrLy1NMTIwCAwOv6Ofw4cPas2ePDh48qM8++0yjRo3SgQMH9NVXX6mgoEC1atXSM888I3d3d82bN0+urq46ceKEQkND1a1bN82dO1e5ubm6++679b///U9xcXGSpFWrVmnHjh3Kz89XZGSkHn74YS1btkzp6emKiYlRixYtNGDAgCLvvahrLRaLYmNjFRoaqh9++EHVq1fXyy+/LDc3N6Wnp2v+/Pn67bffZDab9cILLxR5rwAAAAAAAABuPiSYr0P//v21evVqjRkzRpKUmJgoLy8vxcbGKj8/XxMmTFB4eLgk6eTJk5ozZ458fHw0cuRIdenSRbGxsVqzZo3WrVungQMHXtF+aGioWrdurVatWqlt27aSJG9vb0VHR0uSPvnkE3399dfq0aOHJOns2bOaMmWKzGazpk+frh49eqh9+/Z2K5P37duntLQ0TZs2TYZhaObMmTp48KD69++v06dPa9asWcXeb3HX+vv7Ky0tTc8995yefvppzZ49Wzt37lSHDh30z3/+U3369FFkZKTy8vJkGMYV7SYmJioxMVGSNH36dAc+CQAAAAAAAADOQIK5DO3bt0+nTp3Szp07JUnZ2dlKS0uTi4uLQkJC5OfnJ0kKDAxUixYtJEnBwcE6cOBAqfs4ffq0PvnkE2VlZSk3N9eWwJaktm3bymy+tOvJDz/8oJiYGElS+/btbauX9+3bp++++04vv/yyJCk3N1fp6eny9/cv1f0Vd21AQIDq168vSWrYsKEyMjKUk5Ojs2fPKjIyUpLk5uZWZLvR0dG2pDkAAAAAAACAmwcJ5jJkGIYGDRqkiIgIu/KUlBS5urrajk0mk+3YZDLJarWWuo958+YpJiZG9evX18aNG5WSkmI75+HhUao2+vTpo65du9qVWSyW67r2j/dnNpuVl5dXqvYAAAAAAAAA3Lx4yd918PT0VE5Oju04IiJC69evV0FBgSQpNTVVubm5ZdpHbm6u/Pz8VFBQoC1bthR7XePGjfXNN99IkrZv324rDw8P14YNG2xxnT17VufPn7+in6IUd+3VYq9Ro4Z27dolScrPz9fFixdLuGMAAAAAAAAANwtWMF+H4OBgmc1mu5f8WSwWjR49WpLk6+tr26bCUe3atdP777+vtWvX6sUXX9QjjzyicePGydfXV40bNy42KTxw4EDNnTtXCQkJioiIkJeXl6RLSeKffvpJr7zyiqRLq56feeYZBQYGKjQ0VKNGjVJERESRL/kr7trL23IUZeTIkfrggw8UHx+vKlWq6MUXX1StWrWua0wAAAAAAAAAVAwmo6i3ruGmd/HiRbm5uclkMmnbtm3atm2bbe/kii7j3SXODgEAAAAAAAC4qvz/u8/ZIdxQQUFBRZazgrmSOnbsmBYtWiTDMOTt7a1//OMfzg4JAAAAAAAAQCXDCuYKIiEhQTt27LAri4qKUt++fW94LKdOndLcuXPtylxdXTVt2rQb0j8rmAEAAAAAAFDRsYL5EhLMqHBSU1OdHQKASsLf31+ZmZnODgNAJcK8AqAsMacAKGvMKyhPxSWYi387GwAAAAAAAAAAV0GCGQAAAAAAAADgEBLMAAAAAAAAAACHkGAGAAAAAAAAADjExdkBAH/msmq5s0MAUEn8Kv6HDkDZYl4pHwW9H3J2CAAAAHAQK5gBAAAAAAAAAA4hwQwAAAAAAAAAcAgJZgAAAAAAAACAQ0gwAwAAAAAAAAAcQoIZAAAAAAAAAOAQEswAAAAAAAAAAIeQYL4FjB8/XpJksVi0devWcu1r/fr12rRp0xXlFotFo0aNKte+AQAAAAAAANxYLs4OAOVvypQpkqSMjAxt3bpV7du3L7e+7r///nJrGwAAAAAAAEDFQoL5FjBgwADFxcVp2bJlOnPmjGJiYtSxY0f17NlTS5cu1cGDB5Wfn69u3bqpa9euSklJUXx8vLy9vXXq1ClFRUUpODhYa9asUV5enmJiYhQYGFhkX/Hx8fLw8FDv3r117Ngxvfvuu5KkFi1aFBtfYmKiEhMTJUnTp08v+wEAAAAAAAAAUC5IMN9C+vfvr9WrV2vMmDGSLiV2vby8FBsbq/z8fE2YMEHh4eGSpJMnT2rOnDny8fHRyJEj1aVLF8XGxmrNmjVat26dBg4cWGJ/77zzjgYPHqymTZsqLi6u2HrR0dGKjo4uk3sEAAAAAAAAcOOQYL6F7du3T6dOndLOnTslSdnZ2UpLS5OLi4tCQkLk5+cnSQoMDLStQA4ODtaBAwdKbDsrK0tZWVlq2rSpJKlDhw5KTk4upzsBAAAAAAAA4AwkmG9hhmFo0KBBioiIsCtPSUmRq6ur7dhkMtmOTSaTrFbrDY0TAAAAAAAAQMVkdnYAuHE8PT2Vk5NjO46IiND69etVUFAgSUpNTVVubm6Z9OXt7S1vb299//33kqQtW7aUSbsAAAAAAAAAKg5WMN9CgoODZTab7V7yZ7FYNHr0aEmSr6+vYmJiyqy/4cOH217yd3lvZwAAAAAAAACVh8kwDMPZQQB/ZHnvbWeHAAAAgBuooPdDzg4BcAp/f39lZmY6OwwAlQjzCspTUFBQkeVskQEAAAAAAAAAcAhbZMAhCQkJ2rFjh11ZVFSU+vbt66SIAAAAAAAAANxobJGBCic1NdXZIQCoJPh6GICyxrwCoCwxpwAoa8wrKE9skQEAAAAAAAAAKFMkmAEAAAAAAAAADiHBDAAAAAAAAABwCC/5Q4Vj/Ge6s0MAUElkODsAAJUO88q1M/11jLNDAAAAQDliBTMAAAAAAAAAwCEkmAEAAAAAAAAADiHBDAAAAAAAAABwCAlmAAAAAAAAAIBDSDADAAAAAAAAABxCghkAAAAAAAAA4BASzNcpPj5eq1atKvb8rl27dObMGYfanjdvnnbu3HlFeUpKiqZPn+5QmwMGDHDoOgAAAAAAAAD4MxLM5Wz37t0OJ5gBAAAAAAAAoCJzcXYAN6OEhARt2rRJvr6+qlGjhho2bKjExER99dVXKigoUK1atfTMM8/oxIkT2rNnjw4ePKjPPvtMo0aNkiQtXLhQv/32m9zd3fXUU0+pTp06xfb13Xff6fPPP1dOTo6eeOIJtWrVyu78hQsX9M4778hiscjd3V3Dhg1TvXr1lJubq0WLFuno0aMymUzq16+f2rZta7vut99+04wZM/Tggw/qrrvuuqLflJQULV++XFWrVtXp06fVsGFDPfPMMzKZTBoxYoRiY2Pl6+uro0ePKi4uThMnTlR8fLwsFossFosyMzP197//XUeOHNG3336r6tWra/To0XJxufKRS0xMVGJioiQ5vDIbAAAAAAAAwI1HgvkaHTt2TNu2bdPMmTNVWFio0aNHq2HDhmrTpo2io6MlSZ988om+/vpr9ejRQ61bt1arVq1syd3Jkydr6NChql27to4cOaIFCxbotddeK7a/jIwMTZs2TT///LMmTZqkO++80+58fHy8GjRooJdfflkHDhzQv/71L82aNUsrVqyQl5eX3nzzTUmXEtGX/frrr5o5c6YeffRRtWjRoti+jx8/rtmzZ8vPz08TJkzQ4cOHFRYWdtXx+fnnn/Xaa6/pzJkzGj9+vEaNGqXHH39cs2bNUlJSkiIjI6+4Jjo62jZ2AAAAAAAAAG4eJJiv0aFDhxQZGSl3d3dJUuvWrSVJp0+f1ieffKKsrCzl5uYqPDz8imtzc3N1+PBhzZ4921ZWUFBw1f6ioqJkNvn7KHoAACAASURBVJtVu3Zt1apVS6mpqXbnv//+e9vK6ObNm+vChQvKzs7W/v379fzzz9vq+fj4SJIKCwv1+uuva8iQIWratOlV+27UqJFq1KghSapfv74sFkuJCeaWLVvKxcVFwcHBslqtioiIkCQFBwcrIyPjqtcCAAAAAAAAuLmQYC4j8+bNU0xMjOrXr6+NGzcqJSXlijpWq1Xe3t6aNWtWqds1mUxlGaaqVKmiBg0aKDk5ucQEs6urq+1ns9ksq9Vq+9kwDElSfn6+3TWXt8Awm82qUqWKLX6TyaTCwsIyuw8AAAAAAAAAzsdL/q5RkyZNtHv3buXl5SknJ0d79+6VdGl1sp+fnwoKCrRlyxZbfU9PT+Xk5EiSvLy8FBAQoB07dkiSDMPQiRMnrtrfzp07ZbValZ6erp9//llBQUF258PCwmz9paSkqGrVqvLy8lKLFi30xRdf2Or9cYuM4cOHKzU1VZ9//rlDYxAQEKBjx47Z4gMAAAAAAABwa2IF8zVq2LCh2rVrp5iYGPn6+iokJESS9Mgjj2jcuHHy9fVV48aNbUnldu3a6f3339fatWv14osv6tlnn9X8+fOVkJCggoIC3XPPPapfv36x/dWoUUPjxo1TTk6Ohg4dKjc3N7vzDz/8sN555x299NJLcnd314gRIyRJDz74oBYsWKBRo0bJbDarX79+atOmjaRLq4ufe+45zZw5U56enurWrds1jUG/fv303nvv6dNPPy1xFTQAAAAAAACAystkXN7rAKggfpr3rLNDAAAAQBkx/XWMs0MAKix/f39lZmY6OwwAlQjzCsrTn3dWuIwtMgAAAAAAAAAADmGLjAogISHBti/zZVFRUerbt2+5933q1CnNnTvXrszV1VXTpk0r974BAAAAAAAA3NzYIgMVTmpqqrNDAFBJ8PUwAGWNeQVAWWJOAVDWmFdQntgiAwAAAAAAAABQpkgwAwAAAAAAAAAcQoIZAAAAAAAAAOAQEswAAAAAAAAAAIe4ODsA4M9+/fxpZ4cAoJL41dkBAKh0KvO8cluf95wdAgAAAG5CrGAGAAAAAAAAADiEBDMAAAAAAAAAwCEkmAEAAAAAAAAADiHBDAAAAAAAAABwCAlmAAAAAAAAAIBDSDDjqiZOnKijR486OwwAAAAAAAAAFRAJZgAAAAAAAACAQ1ycHQAck5ubqzlz5ujs2bOyWq168MEHtXTpUsXGxsrX11dHjx5VXFycJk6cqPj4eFksFlksFmVmZurvf/+7jhw5om+//VbVq1fX6NGj5eJS8qMwf/58HT16VHl5eWrbtq0efvhhSVJSUpL+/e9/y93dXaGhobJYLBozZowOHjyoxYsXS5JMJpMmTZokT0/Pch0XAAAAAAAAADcOCeabVHJysvz8/DR27FhJUnZ2tpYuXVps/Z9//lmvvfaazpw5o/Hjx2vUqFF6/PHHNWvWLCUlJSkyMrLEPv/2t7/Jx8dHVqtVkydP1smTJ1W7dm3Nnz9fkyZNUkBAgN566y1b/VWrVmnIkCEKCwtTbm6uXF1di2w3MTFRiYmJkqTp06dfyzAAAAAAAAAAcCISzDep4OBgxcXFacmSJWrVqpWaNGly1fotW7aUi4uLgoODZbVaFRERYWsnIyOjVH1u375dX331lQoLC3Xu3DmdOXNGhmEoICBAAQEBkqT27dvbksVhYWH697//rfbt26tNmzaqUaNGke1GR0crOjq6tLcOAAAAAAAAoIJgD+abVFBQkGbMmKHg4GB98sknWrFihcxmswzDkCTl5+fb1b+8BYbZbFaVKlVkMpkkXdq6orCwsMT+LBaLVq9erQkTJuiNN97QXXfddUUff9anTx89/fTTysvL04QJE/TTTz85cqsAAAAAAAAAKigSzDeps2fPys3NTR06dFDv3r117NgxBQQE6NixY5KknTt3lml/2dnZ8vDwkJeXl3799VclJydLupTovry/s3RplfNl6enpCg4OVp8+fRQSEkKCGQAAAAAAAKhk2CLjJnXq1CktWbJEJpNJLi4uevLJJ5WXl6f33ntPn376qZo2bVqm/dWvX1/169fXCy+8oBo1aig0NFSS5ObmpiFDhmjatGlyd3dXSEiI7Zo1a9YoJSVFJpNJdevWVcuWLcs0JgAAAAAAAADOZTIu76kAOCg3N1ceHh4yDEMLFy5UYGCgevXq5XB7B9/pXYbRAQAAoDRu6/Oes0MAbjn+/v7KzMx0dhgAKhHmFZSnoKCgIstZwYzrlpiYqE2bNqmgoEANGjRQ165dnR0SAAAAAAAAgBuABDMkSbNmzbLto3zZY489poiIiBKv7dWr13WtWAYAAAAAAABwc2KLDFQ4qampzg4BQCXB18MAlDXmFQBliTkFQFljXkF5Km6LDPMNjgMAAAAAAAAAUEmQYAYAAAAAAAAAOIQEMwAAAAAAAADAISSYAQAAAAAAAAAOcXF2AMCfHf/vMGeHAKCSOO7sAABUOmU5rzTo9UEZtgYAAAA4ByuYAQAAAAAAAAAOIcEMAAAAAAAAAHAICWYAAAAAAAAAgENIMAMAAAAAAAAAHEKCGQAAAAAAAADgEBLMAAAAAAAAAACHkGAupfHjx0uSLBaLtm7desP737hxoxYuXFhu7c+bN087d+4ss/Z+//13TZo0SQMGDCjXuAEAAAAAAAA4DwnmUpoyZYokKSMjwykJ5puNq6urHnnkEQ0YMMDZoQAAAAAAAAAoJy7ODuBmMWDAAMXFxWnZsmU6c+aMYmJi1LFjR/Xs2VNLly7VwYMHlZ+fr27duqlr165KSUlRfHy8vL29derUKUVFRSk4OFhr1qxRXl6eYmJiFBgYWGRfO3bs0IoVK2Q2m+Xl5aVJkyZJks6dO6epU6fq559/VmRkpB5//HFJ0tatW/Wf//xHktSyZUtb+YABA9SlSxd99913uu222/T888/L19e3xHtdsWKF9u7dq7y8PN1xxx0aNmyYTCaTfvzxR7333nsymUxq0aKFkpOT9eabbxbZhoeHh8LCwpSenl5if4mJiUpMTJQkTZ8+vcT6AAAAAAAAACoGEszXqH///lq9erXGjBkj6VJy1MvLS7GxscrPz9eECRMUHh4uSTp58qTmzJkjHx8fjRw5Ul26dFFsbKzWrFmjdevWaeDAgUX2sWLFCr3yyiuqXr26srKybOUnTpzQzJkz5eLioueff17du3eX2WzW0qVLNWPGDHl7e2vKlCnatWuXIiMjdfHiRYWEhGjgwIFasWKFli9friFDhpR4j927d1e/fv0kSXPnztXevXvVunVrvfvuu3rqqad0xx13aOnSpdc5kv9fdHS0oqOjy6w9AAAAAAAAADcGCebrtG/fPp06dcq2f3F2drbS0tLk4uKikJAQ+fn5SZICAwPVokULSVJwcLAOHDhQbJuhoaGaN2+eoqKi1KZNG1t58+bN5eXlJUmqW7euMjMz9fvvv6tZs2a2lcn33nuvDh06pMjISJlMJrVr185W/sYbb5Tqng4cOKBVq1bp4sWLunDhgm6//XY1adJEOTk5uuOOOyRJ7du3V1JS0rUMFQAAAAAAAIBKhgTzdTIMQ4MGDVJERIRdeUpKilxdXW3HJpPJdmwymWS1Wottc9iwYTpy5IiSkpI0ZswY27YRf2zPbDarsLDwmmI1mUwl1snLy9PChQsVGxsrf39/xcfHKy8v75r6AQAAAAAAAHBr4CV/18jT01M5OTm244iICK1fv14FBQWSpNTUVOXm5l5XH+np6WrcuLEeeeQR+fr66pdffim2bqNGjXTw4EH99ttvslqt2rZtm5o2bSrpUvL78srqrVu3KiwsrMS+8/PzJUm+vr7Kzc3VN998I0ny9vaWp6enjhw5Iknatm3bdd0jAAAAAAAAgJsfK5ivUXBwsMxms91L/iwWi0aPHi3pUmI2JibmuvpYsmSJ0tLSJF3aFqNevXo6ceJEkXX9/PzUv39/24sAW7ZsqbvvvluS5O7urh9//FEJCQny9fXVCy+8UGLf3t7e6tKli0aNGqXbbrtNISEhtnNPP/203n//fZlMJjVt2tS2XUdxRowYoezsbBUUFGj37t0aP3686tatW5ohAAAAAAAAAHATMBmGYTg7CJSPAQMGKC4urszay83NlYeHhyTp888/17lz5zRo0KAya/+ybR/0KvM2AQAAKpoGvT5wdggAnMzf31+ZmZnODgNAJcK8gvIUFBRUZDkrmFFqSUlJ+s9//iOr1Sp/f3+NGDHC2SEBAAAAAAAAcCISzE6UkJCgHTt22JVFRUWpb9++ZdJ+UauXFyxYoMOHD9uV9ezZU507dy6xvXbt2qldu3Z2ZcnJyVq6dKldWUBAwHVvEwIAAAAAAACg4mOLDFQ4qampzg4BQCXB18MAlDXmFQBliTkFQFljXkF5Km6LDPMNjgMAAAAAAAAAUEmQYAYAAAAAAAAAOIQEMwAAAAAAAADAIbzkDxXOvrVPOjsEAACuWXiPBc4OAQAAAABuOFYwAwAAAAAAAAAcQoIZAAAAAAAAAOAQEswAAAAAAAAAAIeQYAYAAAAAAAAAOIQEMwAAAAAAAADAISSYAQAAAAAAAAAOIcEMh+zZs0eff/65s8MAAAAAAAAA4EQuzg4AN5/CwkK1bt1arVu3dnYoAAAAAAAAAJyIBHMFYrFYNG3aNDVu3Fg//PCDQkJC1KlTJy1fvlznz5/Xs88+q7p162rRokU6ffq0CgsL9dBDD+nuu++WxWLRv/71L128eFGSNHjwYIWGhiolJUXLly9X1apVdfr0aTVs2FDPPPOMTCZTkTGMGDFCUVFR+vbbb+Xm5qbnnntOgYGBmjdvnlxdXXXixAmFhoaqXr16Onr0qIYMGaJff/1V8+fPl8VikSQ9+eSTCg0N1ebNm7V27VoVFBSocePGevLJJ2U2X7loPjExUYmJiZKk6dOnl9PoAgAAAAAAAChrJJgrmPT0dL344ouqW7euxo4dq61bt2ry5Mnas2ePEhISVLduXTVv3lzDhw9XVlaWxo0bpzvvvFPVqlXT+PHj5ebmprS0NL399tu2ZO3x48c1e/Zs+fn5acKECTp8+LDCwsKKjcHLy0tvvvmmNm3apA8//FBjxoyRJJ09e1ZTpkyR2WzWxo0bbfUXL16spk2bKiYmRlarVbm5uTpz5oy2b9+u119/XS4uLlqwYIG2bNmijh07XtFfdHS0oqOjy3YgAQAAAAAAAJQ7EswVTEBAgIKDgyVJt99+u+68806ZTCYFBwcrIyNDZ8+e1d69e7V69WpJUl5enjIzM1W9enUtXLhQJ06ckNlsVlpamq3NRo0aqUaNGpKk+vXry2KxXDXBfM8999j++9FHH9nK27ZtW+QK5AMHDmjkyJGSJLPZLC8vL23evFnHjx/X2LFjbXH6+vpez9AAAAAAAAAAqGBIMFcwrq6utp9NJpPt2GQyyWq1ymw2a9SoUQoKCrK7Lj4+XtWqVdOsWbNkGIYee+yxIts0m82yWq1XjeGP22f88WcPD49S34dhGOrYsaP69+9f6msAAAAAAAAA3FyuXI6KCi08PFxr166VYRiSLm1/IUnZ2dny8/OT2WzW5s2bS0wiX8327dtt/23cuHGJ9e+8806tX79ekmS1WpWdna0777xTO3fu1Pnz5yVJFy5cUEZGhsMxAQAAAAAAAKh4WMF8k+nXr58+/PBDvfTSSzIMQwEBARozZoy6deumN998U5s3b1Z4eLjc3d0d7uPChQt66aWX5Orqqueee67E+gMHDtQHH3ygr7/+WmazWUOHDtUdd9yhRx99VFOmTJFhGKpSpYqGDBmimjVrOhwXAAAAAAAAgIrFZFxeCgtIGjFihGJjY526X/LahT2d1jcAAI4K77HA2SHgBvD391dmZqazwwBQSTCnAChrzCsoT3/esvcytsgAAAAAAAAAADiELTJuUbNmzZLFYrEre+yxxzRv3jwnRQQAAAAAAADgZsMWGahwUlNTnR0CgEqCr4cBKGvMKwDKEnMKgLLGvILyxBYZAAAAAAAAAIAyRYIZAAAAAAAAAOAQEswAAAAAAAAAAIeQYAYAAAAAAAAAOMTF2QEAf7b1i8HODgEAUA7ad1vk7BAAAAAAAGWMFcwAAAAAAAAAAIeQYAYAAAAAAAAAOIQEMwAAAAAAAADAISSYAQAAAAAAAAAOIcEMAAAAAAAAAHDILZNgHj9+vCTJYrFo69at5drX+vXrtWnTpivKLRaLRo0aVa5930iffvqpvvvuO2eHAQAAAAAAAMBJXJwdwI0yZcoUSVJGRoa2bt2q9u3bl1tf999/f7m1XVFYrVY98sgjzg4DAAAAAAAAgBPdMgnmAQMGKC4uTsuWLdOZM2cUExOjjh07qmfPnlq6dKkOHjyo/Px8devWTV27dlVKSori4+Pl7e2tU6dOKSoqSsHBwVqzZo3y8vIUExOjwMDAIvuKj4+Xh4eHevfurWPHjundd9+VJLVo0eKqMW7cuFG7du3SxYsXlZ6err/85S8qKCjQ5s2b5erqqrFjx8rHx0fp6elauHChfvvtN7m7u+upp55SnTp1tGfPHiUkJKigoEBVq1bVM888o9tuu03x8fHKzMyUxWJRZmamevbsqZ49exYZg8Vi0bRp09SwYUMdP35cdevW1ciRI+Xu7q4RI0YoKipK+/fvV+/evZWcnKxWrVqpbdu2+vHHH/Xhhx/q4sWLcnFx0auvvip3d/cixxYAAAAAAABA5XDLbJFxWf/+/dWkSRPNmjVLvXr10tdffy0vLy/FxsYqNjZWX331lSwWiyTp5MmTGjp0qObMmaPNmzcrLS1NsbGx6tKli9atW1eq/t555x0NGjRIs2bNKlX906dP66WXXlJsbKw+/vhjubm5aebMmWrcuLFt240PPvhAgwcP1owZMzRgwAAtWLBAkhQWFqapU6dq5syZateunVatWmVrNzU1Va+88oqmTZumFStWqKCgoNgYUlNTdf/992vOnDny9PTUF198YTtXtWpVzZgxQ/fcc4+trKCgQG+99ZYGDhyoWbNmacKECXJzc7vq2P5RYmKixowZozFjxpRqjAAAAAAAAABUDLfMCubi7Nu3T6dOndLOnTslSdnZ2UpLS5OLi4tCQkLk5+cnSQoMDLStQA4ODtaBAwdKbDsrK0tZWVlq2rSpJKlDhw5KTk6+6jXNmjWTp6enPD095eXlpdatW9v6PHXqlHJzc3X48GHNnj3bds3lZPHZs2f11ltv6dy5cyooKFBAQICtzl133SVXV1e5urqqWrVqOn/+vGrUqFFkDDVq1FBYWJgt5jVr1qh3796SpHbt2l1RPzU1VX5+fmrUqJEkycvLS1LxY/vHuCQpOjpa0dHRVx0XAAAAAAAAABXPLZ9gNgxDgwYNUkREhF15SkqKXF1dbccmk8l2bDKZZLVayyWeP/ZpNpvl4uJi+7mwsFBWq1Xe3t5FrohetGiRevXqpdatWyslJUXLly+3nbvczh/bKo7JZCr22N3dvdT3UtzYAgAAAAAAAKgcbrktMjw9PZWTk2M7joiI0Pr1622rgFNTU5Wbm1smfXl7e8vb21vff/+9JGnLli3X3aaXl5cCAgK0Y8cOSZeSuCdOnJB0aYVw9erVJcm2nYYjMjMz9cMPP0iStm7dalvNXJygoCCdO3dOP/74oyQpJydHhYWF5Tq2AAAAAAAAAJzvllvBHBwcLLPZbPeSP4vFotGjR0uSfH19FRMTU2b9DR8+3PaSv/Dw8DJp89lnn9X8+fNtL/S75557VL9+fT300EOaPXu2vL291bx58yL3Oy6NoKAgrVu3Tu+++67q1Kmj+++//6r1XVxc9Pzzz2vx4sXKy8uTm5ubJkyYoPvuu69cxxYAAAAAAACAc5kMwzCcHQQqDovFohkzZujNN990Wgzxi7s7rW8AQPlp322Rs0MArpu/v78yMzOdHQaASoI5BUBZY15BeQoKCiqy/JbbIgMAAAAAAAAAUDZuuS0yylJCQoJtL+TLoqKi1Ldv36tel5ycrKVLl9qVBQQE3NDtI37//XdNnjz5ivJXX33VqauXAQAAAAAAANw82CIDFU5qaqqzQwBQSfD1MABljXkFQFliTgFQ1phXUJ7YIgMAAAAAAAAAUKZIMAMAAAAAAAAAHEKCGQAAAAAAAADgEBLMAAAAAAAAAACHuDg7AODP1iQOcnYIAIDr1DN6sbNDAAAAAADcAKxgBgAAAAAAAAA4hAQzAAAAAAAAAMAhJJgBAAAAAAAAAA4hwQwAAAAAAAAAcAgJZgAAAAAAAACAQ0gwAwAAAAAAAAAcQoIZN5TVanV2CAAAAAAAAADKiIuzA0DF9emnn8rHx0cPPPCAJOnjjz9WtWrVVFBQoB07dig/P1+RkZF6+OGHJUkzZ87UL7/8ovz8fPXs2VPR0dGSpAEDBqhr167av3+/hgwZorCwMKfdEwAAAAAAAICyQ4IZxercubPefPNNPfDAA7Jardq+fbv+9re/af/+/Zo2bZoMw9DMmTN18OBBNW3aVMOHD5ePj4/y8vI0duxYtWnTRlWrVtXFixfVqFEjPfHEE0X2k5iYqMTEREnS9OnTb+QtAgAAAAAAALgOJJhRrICAAPn4+Oj48eM6f/686tevrx9//FHfffedXn75ZUlSbm6u0tPT1bRpU61Zs0a7d++WJGVmZiotLU1Vq1aV2WxW27Zti+0nOjrattoZAAAAAAAAwM2DBDOuqkuXLtq4caN+/fVXde7cWQcOHFCfPn3UtWtXu3opKSnav3+/pkyZInd3d02cOFH5+fmSJFdXV5nNbPcNAAAAAAAAVDZk/XBVkZGRSk5O1tGjRxUREaHw8HBt2LBBubm5kqSzZ8/q/Pnzys7Olre3t9zd3fXTTz/pyJEjTo4cAAAAAAAAQHljBTOuysXFRc2aNZO3t7fMZrPCw8P1008/6ZVXXpEkeXh46JlnnlFERIS+/PJLvfDCC6pdu7YaN27s5MgBAAAAAAAAlDcSzLgqq9WqI0eO6MUXX7SV9ezZUz179ryi7rhx44psIy4urtziAwAAAAAA+H/s3XlUVfX+//HXOTEjKMilQgUVZ5EwEYcmTbSivt5bNlp0tbpmkWYiola/bEBBQr9ehwaH7jelDBUr+3bV6GZXTc0hB8A09Soa0pEwmTxM5/z+cHm+kSBIBw/Y87FWa7H32fvzee2D67Nabz++NwDHoUUGanXy5EmNHz9evXr10vXXX+/oOAAAAAAAAACaGHYwo1Zt27bV/PnzHR0DAAAAAAAAQBPFDmYAAAAAAAAAQIOwgxlNTlTke46OAOAq4efnp/z8fEfHAAAAAADgqsUOZgAAAAAAAABAg1BgBgAAAAAAAAA0CAVmAAAAAAAAAECD0IMZTc6KjaMdHQEArgoPD6KnPQAAAACgcbGDGQAAAAAAAADQIBSYAQAAAAAAAAANQoEZAAAAAAAAANAgFJgBAAAAAAAAAA1CgRkAAAAAAAAA0CAUmAEAAAAAAAAADUKB2U5iYmJUWFjYKGMXFBQoJSWlxs+mT5+uI0eO1HrvzJkzVVJSopKSEq1fv75R8l2wc+dOffzxxzV+Fh0d3ahzAwAAAAAAALjyKDA3A76+voqNjW3QvVOnTpWnp6dKSkq0YcMGOyerLjw8XH/5y18adQ4AAAAAAAAATYeTowM0R2azWXPmzFFBQYEsFotGjBghSVq3bp127dqlyspKTZw4UW3atFFxcbEWLlwok8kkV1dXjRkzRkFBQUpLS9NPP/2kvLw8FRUVafjw4YqMjKxxPpPJpKSkJKWkpKi8vFwLFy7U8ePHFRAQoPLy8ktmjYmJ0cyZM/XBBx8oLy9PcXFxCg0NVXR0tD799FNt3bpVFRUVioiI0IMPPiiTyaQZM2aoc+fOOnTokIKDgzVo0CCtXLlSZ8+e1fjx49WpU6ca59q4caOOHDmiJ598UiaTSXPnzpXZbFbfvn0vmTEjI0MZGRmSpMTExLq+fgAAAAAAAABNBAXmBtizZ498fHw0depUSVJpaalSU1Pl5eWlpKQkrV+/XmvXrtXYsWOVlpamDh06aPLkycrMzNT8+fOVnJwsScrJyVFCQoLMZrPi4+N14403ytfX95Jzb9iwQS4uLpozZ46OHz+u+Pj4emUeOXKkTpw4YZt77969OnXqlGbMmCGr1apZs2YpOztbfn5+ysvL08SJE9W2bVtNnTpVmzdv1muvvaadO3cqPT1dkydPrnO+9957T8OGDdNtt92mdevWXfLayMjIWovrAAAAAAAAAJouWmQ0QGBgoPbv36/ly5frwIED8vDwkCT169dPktSxY0edPn1akvT999/r1ltvlSSFhISouLhYpaWlks63lHBxcZG3t7d69uypw4cP1zl3dna2bbygoCAFBQU16Bn27t2rffv2afLkyYqPj9ePP/6ovLw8SZK/v78CAwNlNBrVrl079erVSwaDQYGBgbbnqsvBgwd10003SZItLwAAAAAAAICrCzuYGyAgIEBJSUnavXu3VqxYoV69ekmSnJzOf51Go1FVVVV1jmMwGC553Nj+8pe/aOjQodXOmUwmOTs7V8t04dhgMMhisdR7/Cv9PAAAAAAAAACuLHYwN0BBQYFcXFx06623avjw4Tp69Git13br1k2bNm2SJGVlZcnLy8u243nHjh0qLy9XUVGRsrKyFBwcXOfcPXr00ObNmyWdb7Fx/PjxemV2d3fXuXPnbMc33HCDvvrqK5nNZtsznT17tl5j1UfXrl21ZcsWSbLlBQAAAAAAAHB1YQdzA+Tk5Gj58uUyGAxycnLSU089pdmzZ9d47YMPPqiFCxdq0qRJcnV1VUxMjO2zoKAgvfrqqyoqKtKIESPq7L8sScOGDdPChQv1wgsvqE2bNurYsWO9Mnt5ealr166KjY1VWFiYoqOj9eOPP+rFF1+UJLm5uWncuHEyGu3zmNr9jQAAIABJREFUdw6jR4/W3Llz9cknn9T5kj8AAAAAAAAAzZPBarVaHR3ijygtLU1ubm4aPny4o6M0ObM/uMPREQDgqvDwoPccHQG46vj5+Sk/P9/RMQBcJVhTANgb6woaU0BAQI3naZEBAAAAAAAAAGgQWmQ4yIMPPnjRuZycHM2bN6/aOWdnZ82YMaPO8aZNm6aKiopq58aNG6fAwMDfF7QGX331lT7//PNq57p27aqnnnrK7nMBAAAAAAAAaLpokYEmJzc319ERAFwl+OdhAOyNdQWAPbGmALA31hU0JlpkAAAAAAAAAADsigIzAAAAAAAAAKBBKDADAAAAAAAAABqEAjMAAAAAAAAAoEGcHB0A+K15W55wdAQAuCqMu2mpoyMAAAAAAK5y7GAGAAAAAAAAADQIBWYAAAAAAAAAQINQYAYAAAAAAAAANAgFZgAAAAAAAABAg1BgBgAAAAAAAAA0CAXmenrppZckSSaTSZs3b77i82/cuFFLlixptPEXLFigbdu22W28ffv2KT4+XrGxsYqPj1dmZqbdxgYAAAAAAADQNFBgrqc33nhDknT69GmHFJibGy8vL8XHxyslJUUxMTGaN2+eoyMBAAAAAAAAsDMnRwdoLqKjo7Vs2TJ98MEHOnnypOLi4nTbbbcpKipKqampys7OVkVFhe644w4NHTpUWVlZSktLk6enp3JycjRgwAAFBgbq888/V3l5ueLi4nTdddfVONfWrVu1atUqGY1GeXh46NVXX5UknTlzRgkJCfrpp58UERGhxx57TJK0efNmrVmzRpLUu3dv2/no6GgNGTJE+/btU6tWrTRhwgR5e3vX+ayrVq3Srl27VF5eri5dumjMmDEyGAw6fPiw3n77bRkMBoWGhmrPnj1KSUmpcYwOHTrYfm7Xrp3Ky8tVUVEhZ2fni67NyMhQRkaGJCkxMbHOfAAAAAAAAACaBgrMl2nkyJFau3atpkyZIul8cdTDw0MzZ85URUWFXn75Zd1www2SpOPHj2vOnDlq0aKFnnvuOQ0ZMkQzZ87U559/rnXr1mnUqFE1zrFq1Sq9+OKL8vX1VUlJie38sWPHNGvWLDk5OWnChAm68847ZTQalZqaqqSkJHl6euqNN97Qt99+q4iICJWVlSk4OFijRo3SqlWrtHLlSj355JN1PuOdd96p+++/X5I0b9487dq1S+Hh4Xrrrbf09NNPq0uXLkpNTa33d7Z9+3Z17NixxuKyJEVGRioyMrLe4wEAAAAAAABoGigw/0579+5VTk6OrX9xaWmpTp06JScnJwUHB8vHx0eSdN111yk0NFSSFBgYeMmexF27dtWCBQs0YMAA9evXz3Y+JCREHh4ekqS2bdsqPz9fRUVF6tmzp21n8i233KIDBw4oIiJCBoNBAwcOtJ1/88036/VMmZmZ+vTTT1VWVqbi4mK1a9dO3bt317lz59SlSxdJ0s0336zdu3fXOdaJEyeUmpqqF198sV5zAwAAAAAAAGg+KDD/TlarVaNHj1ZYWFi181lZWdV27BoMBtuxwWCQxWKpdcwxY8bohx9+0O7duzVlyhRb24hfj2c0GlVVVXVZWQ0GQ53XlJeXa8mSJZo5c6b8/PyUlpam8vLyy5rngp9//llvvvmmYmJiam0HAgAAAAAAAKD54iV/l8nd3V3nzp2zHYeFhWnDhg2qrKyUJOXm5spsNv+uOfLy8tS5c2c99NBD8vb21s8//1zrtZ06dVJ2drYKCwtlsVi0ZcsW9ejRQ9L54veFndWbN29Wt27d6py7oqJCkuTt7S2z2azt27dLkjw9PeXu7q4ffvhBkrRly5ZLjlNSUqLExESNHDmyXvMCAAAAAAAAaH7YwXyZAgMDZTQaq73kz2QyKT4+XtL5wmxcXNzvmmP58uU6deqUpPNtMYKCgnTs2LEar/Xx8dHIkSNtLwLs3bu3+vbtK0lydXXV4cOHlZ6eLm9vb73wwgt1zu3p6akhQ4YoNjZWrVq1UnBwsO2zsWPH6p133pHBYFCPHj1s7Tpqsm7dOuXl5WnVqlVatWqVJOmll15Sy5Yt6/UdAAAAAAAAAGj6DFar1eroEGgc0dHRWrZsmd3GM5vNcnNzkyR9/PHHOnPmjEaPHm238S+YuvJOu48JAH9E425a6ugIwFXHz89P+fn5jo4B4CrBmgLA3lhX0JgCAgJqPM8OZtTb7t27tWbNGlksFvn5+SkmJsbRkQAAAAAAAAA4EAVmB0pPT9fWrVurnRswYIDuu+8+u4xf0+7lxYsX6+DBg9XORUVFafDgwXWON3DgQA0cOLDauT179ig1NbXaOX9//9/dJgQAAAAAAABA00eLDDQ5ubm5jo4A4CrBPw8DYG+sKwDsiTUFgL2xrqAx1dYiw3iFcwAAAAAAAAAArhIUmAEAAAAAAAAADUKBGQAAAAAAAADQIBSYAQAAAAAAAAAN4uToAMBv/W3nE46OAADNyqLwpY6OAAAAAAD4g2IHMwAAAAAAAACgQSgwAwAAAAAAAAAahAIzAAAAAAAAAKBBKDADAAAAAAAAABqEAjMAAAAAAAAAoEEoMMMuSkpKtH79ettxVlaWEhMTHZgIAAAAAAAAQGOjwAy7KCkp0YYNGxwdAwAAAAAAAMAV5OToALjyTCaTZsyYoc6dO+vQoUMKDg7WoEGDtHLlSp09e1bjx4/Xddddp4ULF8pkMsnV1VVjxoxRUFCQ0tLSlJ+fL5PJpPz8fEVFRSkqKkoffPCB8vLyFBcXp9DQUN14440ym81KSUnRiRMn1LFjR40bN04Gg8HRjw8AAAAAAADATigw/0Hl5eVp4sSJatu2raZOnarNmzfrtdde086dO5Weni4/Pz916NBBkydPVmZmpubPn6/k5GRJUm5url555RWdO3dOEyZM0LBhwzRy5EidOHHCdk1WVpb+85//aPbs2fLx8dHLL7+sgwcPqlu3bhdlycjIUEZGhiTRVgMAAAAAAABoRigw/0H5+/srMDBQktSuXTv16tVLBoNBgYGBOn36tPLz8xUbGytJCgkJUXFxsUpLSyVJN954o5ydneXs7KyWLVvq7NmzNc7RqVMntW7dWpLUvn17mUymGgvMkZGRioyMbIzHBAAAAAAAANCI6MH8B+Xs7Gz72WAw2I4NBoMsFssl73Vy+r+/lzAajaqqqqpzDqPRWOe4AAAAAAAAAJoXCsyoUbdu3bRp0yZJ59tdeHl5ycPDo9br3d3dde7cuSsVDwAAAAAAAEATQIsM1OjBBx/UwoULNWnSJLm6uiomJuaS13t5ealr166KjY1VWFiYbrzxxiuUFAAAAAAAAICjGKxWq9XRIYBfu/vTOx0dAQCalUXhSx0dAfjD8PPzU35+vqNjALhKsKYAsDfWFTSmgICAGs/TIgMAAAAAAAAA0CAUmAEAAAAAAAAADUKBGQAAAAAAAADQILzkD00OvUQB2Av9xwAAAAAAaFzsYAYAAAAAAAAANAgFZgAAAAAAAABAg1BgBgAAAAAAAAA0CD2Y0eQ89e1cR0cAALtZHPG8oyMAAAAAANBo2MEMAAAAAAAAAGgQCswAAAAAAAAAgAahwAwAAAAAAAAAaBAKzAAAAAAAAACABqHADAAAAAAAAABoEArMAAAAAAAAAIAGaVYF5rS0NH366aeNMva3336rkydPNsrYDWUymbR58+YrMtfGjRtVUFBwReYCAAAAAAAAcHVoVgXmxrRjx45GLzBXVVVd1vWnT5++7ALz5c5xwcaNG3XmzJkG3QsAAAAAAADgj8nJ0QHMZrPmzJmjgoICWSwWjRgxQqmpqZo5c6a8vb115MgRLVu2TNOnT5ckHT9+XC+++KKKioo0fPhwRUZG1jr2xx9/rE2bNsloNCosLEyPPvqoMjIy9OWXX6qyslLXXnutxo0bp2PHjmnnzp3Kzs7W6tWrFRsbK0lasmSJCgsL5erqqqefflpt2rRRXl6e5s2bJ7PZrL59++p///d/tWzZMlmtVi1fvlx79uyRJI0YMUIDBw5UVlaWPvroI3l6eio3N1cDBw5UixYtdPfdd0uSPvzwQ7Vs2VJRUVEX5f/ggw908uRJxcXF6bbbblNERITmz5+vsrIySdITTzyhrl27XjTHnDlztHTpUmVmZqp169ZycnLS4MGD1b9/fx09elT/8z//I7PZLG9vbz377LM6ePCgjhw5or///e9ycXFRQkKCXFxcLspT070+Pj6aPn26OnXqpKysLJWWlmrs2LHq3r27LBaLli9frr1798pgMGjIkCG66667Lho3IyNDGRkZkqTExMTL+NMDAAAAAAAAwJEcXmDes2ePfHx8NHXqVElSaWmpUlNTa70+JydHCQkJMpvNio+P14033ihfX9+Lrvvuu++0c+dOzZgxQ66uriouLpYk9evXz1aUXrFihf71r3/prrvuUnh4uPr06aP+/ftLkl577TX97W9/0/XXX68ffvhBixcv1iuvvKJ//OMfuuuuu3TzzTdrw4YNtvm2b9+uY8eOKTk5WYWFhZo6daq6d+8uSfrPf/6jlJQU+fv7y2QyKSUlRXfffbcsFou++eYbzZgxo8ZnHTlypNauXaspU6ZIksrKyvTSSy/JxcVFp06d0ty5c20F2V/PsW3bNp0+fVqzZ89WYWGhXnjhBQ0ePFiVlZVaunSpJk+eLG9vb33zzTf68MMP9eyzz2rdunWKjo5WcHBwjVkuda8kWSwWzZw5U7t379aqVav08ssvKyMjQ6dPn9asWbN0zTXX2H4HvxUZGXnJvygAAAAAAAAA0DQ5vMAcGBioZcuWafny5erTp4+tKFub8PBwubi4yMXFRT179tThw4cVERFx0XX79+/XoEGD5OrqKklq0aKFJOnEiRNasWKFSkpKZDabdcMNN1x0r9ls1sGDBzV79mzbucrKSknSoUOHFBcXJ0m6+eabtWzZMknS999/r5tuuklGo1GtWrVSjx49dOTIEbm7u6tTp07y9/eXJPn7+6tFixb6z3/+o7Nnz6p9+/by8vKq13dVVVWlJUuW6NixYzIajTp16pTts1/P8f3336t///62LD179pQk5ebm6sSJE3r99dclnS8K+/j41Gvuuu698Dvo2LGjTCaTJGnfvn0aNmyYrrnmGkn/9zsAAAAAAAAAcHVweIE5ICBASUlJ2r17t1asWKFevXrJaDTKarVKkioqKqpdbzAYLnlclwULFiguLk7t27fXxo0blZWVddE1FotFnp6eSk5OvsynqdmFIvcFQ4YM0caNG/XLL79o8ODB9R7ns88+U8uWLZWcnCyr1apHH3201jlq07ZtWyUkJNR7zvre6+zsLEkyGo2yWCwNGh8AAAAAAABA8+Lwl/wVFBTIxcVFt956q4YPH66jR4/K399fR48elSRt27at2vU7duxQeXm5ioqKlJWVVWtLh9DQUG3cuNHWr/hCewaz2SwfHx9VVlZq06ZNtuvd3d117tw5SZKHh4f8/f21detWSZLVatWxY8ckSZ07d9b27dslSd98843t/u7du2vr1q2yWCwqLCzUgQMH1KlT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)

# In[ ]:





# the RMSE is worst and the mean lags is not important at  all, but it will be handled in the feature selection

# # Feature selection

# In[ ]:


train = all_data[all_data.date_block_num < 31]
val = all_data[all_data.date_block_num >= 32]
train_X = train.drop('item_cnt_month' , axis = 1)
train_y = train.item_cnt_month
val_X = val.drop('item_cnt_month' , axis = 1)
val_y = val.item_cnt_month


# In[ ]:


lgbm = LGBMRegressor(verbose = 0 , n_jobs = -1,random_state = random_state)
lgbm.fit(train_X,train_y)
# saving the model in order to run it again witout taking so much time
file_name = 'feature_selection.sav'
pickle.dump(lgbm , open(file_name, 'wb'))


# I will use backawrd elimination method to select the features based on their gain importance 

# the next cell will take a lot of time you can skip it and run the one after it

# In[ ]:


lgbm_FS = pickle.load(open('/content/feature_selection.sav', 'rb')) # FS stands for feature selection and it will be used for selection

thresholds = sorted(lgbm_FS.feature_importances_ )[:20] # check the least 20 importance score  
for thresh in thresholds:
    # select features using threshold
    selection = SelectFromModel(lgbm_FS, threshold=thresh, prefit=True)
    select_train = selection.transform(train_X)
    # train model
    selection_model = LGBMRegressor(n_jobs = -1 , random_state = random_state)
    selection_model.fit(select_train, train_y )
        # eval model
    select_val = selection.transform(val_X)
    predictions = selection_model.predict(select_val)
    RMSE = sqrt(mean_squared_error(val_y, predictions))
    print("Thresh=%.3f, n=%d, RMSE: %.2f" % (thresh, select_train.shape[1], RMSE))


# Thresh=0.000, n=29, RMSE: 0.76
# Thresh=1.000, n=28, RMSE: 0.76
# Thresh=12.000, n=27, RMSE: 0.76
# Thresh=29.000, n=26, RMSE: 0.76
# Thresh=32.000, n=25, RMSE: 0.77
# Thresh=34.000, n=24, RMSE: 0.76
# Thresh=42.000, n=23, RMSE: 0.76
# Thresh=43.000, n=22, RMSE: 0.76
# Thresh=43.000, n=22, RMSE: 0.76
# Thresh=44.000, n=20, RMSE: 0.76
# Thresh=48.000, n=19, RMSE: 0.76
# Thresh=49.000, n=18, RMSE: 0.76
# Thresh=54.000, n=17, RMSE: 0.77
# Thresh=60.000, n=16, RMSE: 0.76
# Thresh=68.000, n=15, RMSE: 0.77
# Thresh=83.000, n=14, RMSE: 0.77
# Thresh=101.000, n=13, RMSE: 0.77
# Thresh=102.000, n=12, RMSE: 0.77
# Thresh=112.000, n=11, RMSE: 0.77
# Thresh=112.000, n=11, RMSE: 0.77

# `Thresh=60.000, n=16, RMSE: 0.76` so i will use this thresh and select the best 16 feature

# In[ ]:


lgbm_FS = pickle.load(open('/content/feature_selection.sav', 'rb')) # FS stands for feature selection and it will be used for selection
feature_imp = pd.DataFrame(sorted(zip(lgbm_FS.feature_importances_,test.columns) , reverse= True), columns=['Value','Feature'])

feature_imp = feature_imp[feature_imp.Value >= 60.000]
selected_cols = list(feature_imp['Feature'].values)
Final_train = all_data[selected_cols]
Final_test = test[selected_cols]
# adding item_cnt_month
Final_train['item_cnt_month'] = all_data['item_cnt_month']


# testing the impact

# In[ ]:


lgbm_after_selection = LGBMRegressor(verbose = 0 , n_jobs = -1,random_state = random_state)
lgbm_after_selection.fit(all_data.drop(['item_cnt_month'],axis = 1), all_data.item_cnt_month)

# saving the model in order to run it again witout taking so much time
file_name = 'after_selection.sav'
pickle.dump(lgbm_after_selection , open(file_name, 'wb'))


# In[ ]:


lgbm_after_selection = pickle.load(open('/content/after_selection.sav', 'rb'))
preds_gbm = lgbm_after_selection.predict(test)
sub = sample_submission
sub.item_cnt_month = preds_gbm
sub.to_csv('after_selection.csv' , index = False)


# RMSE `1.24497`

# # hyper paramter tuning

# i will use a single validation set to keep it simple and fast

# In[ ]:


train = Final_train[Final_train.date_block_num < 33]
val = Final_train[Final_train.date_block_num == 33] # taking the last month to simulate the test set
X_train = train.drop('item_cnt_month',axis = 1)
y_train = train.item_cnt_month
X_val = val.drop('item_cnt_month',axis = 1)
y_val = val.item_cnt_month


# 1) Tuning number of leafs

# In[ ]:


for num_leaves in [10,15,20,25,30,35,40,50] :

    lgbm = LGBMRegressor(random_state=random_state ,num_leaves= num_leaves)
    lgbm.fit(X_train,y_train)
    print("num_leaves : " , num_leaves, " RMSE : ", sqrt(mean_squared_error(lgbm.predict(X_val) , y_val)) ,'\n')


# `num_leaves :  50  RMSE :  0.7731009500323047 ` is the best
# 

# 2) Tuning bagging_fraction

# In[ ]:


for fraction in [0.7,0.8,0.9] :

    lgbm = LGBMRegressor(random_state=random_state , num_leaves=50 , bagging_fraction = fraction)
    lgbm.fit(X_train,y_train)
    print("bagging_fraction : " , fraction, " RMSE : ", sqrt(mean_squared_error(lgbm.predict(X_val) , y_val)) ,'\n')


# bagging_fraction :  0.7  RMSE :  0.7731009500323047 
# 
# bagging_fraction :  0.8  RMSE :  0.7731009500323047 
# 
# bagging_fraction :  0.9  RMSE :  0.7731009500323047 
# 
# 
# `No difference`

# 4) Tuning feature_fraction

# In[ ]:


for fraction in [0.7,0.8,0.9] :

    lgbm = LGBMRegressor(random_state=random_state ,num_leaves=50 , feature_fraction = fraction)
    lgbm.fit(X_train,y_train)
    print("feature_fraction : " , fraction, " RMSE : ", sqrt(mean_squared_error(lgbm.predict(X_val) , y_val)) ,'\n')


# `feature_fraction :  0.9  RMSE :  0.7710114141411256 ` is the best
# 
# 

# 5) Tuning min_data_in_leaf

# In[ ]:


# trying wide range first and then narrow the range
for value in [0,1,5,10,15,20,25,30,50,60] :

    lgbm = LGBMRegressor(random_state=random_state , num_leaves=50, feature_fraction = 0.9, min_data_in_leaf = value)
    lgbm.fit(X_train,y_train)
    print("min_data_in_leaf : " , value, " RMSE : ", sqrt(mean_squared_error(lgbm.predict(X_val) , y_val)) ,'\n')


# ` no improvments`

# 6) Tuning n_estimators based on small learning rate

# In[ ]:


eval_set = [(X_val , y_val),(X_train,y_train)]
lgbm = LGBMRegressor(n_jobs= -1 , random_state= random_state ,n_estimators= 1000 , learning_rate= 0.02 , num_leaves=50,feature_fraction = 0.9)
lgbm.fit(X_train, y_train ,eval_set =eval_set, early_stopping_rounds=30 ) 


# In[ ]:


plt.figure(figsize=(12,6))
results = lgbm.evals_result_
epochs = len(results['valid_0']['l2'])
x_axis = range(0, epochs)
# plot acuuracy
fig, ax = plt.subplots()
ax.plot(x_axis, results['training']['l2'], label='Train')
ax.plot(x_axis, results['valid_0']['l2'], label='validation')
ax.legend()
plt.ylabel('RMSE')
plt.title('LGBM RMSE')
plt.show()


# Early stopping, best iteration is:
# [917]	training's l2: `0.594811`	valid_0's l2: `0.590641`

# see the impact on the test set

# In[ ]:


AHPT_lgbm = LGBMRegressor(random_state = random_state  , learning_rate = 0.02 , n_estimators = 917,num_leaves = 50, feature_fraction = 0.9) # AHPT : After Hyper Paramater Tuning
AHPT_lgbm.fit(Final_train.drop(['item_cnt_month'],axis = 1),Final_train.item_cnt_month)

# save the model
filename = 'after_hyperparamater_tuning.sav'
pickle.dump(AHPT_lgbm,open(filename,'wb'))


# In[ ]:


# load the model from the disk
AHPT_lgbm = pickle.load(open('/content/after_hyperparamater_tuning.sav','rb'))
AHPT_preds = AHPT_lgbm.predict(Final_test)
sub = sample_submission
sub.item_cnt_month = AHPT_preds
sub.to_csv('after_hyperparamater_tuning.csv' , index = False)


# RMSE : `1.26008`

# Surprisngly the RMSE is more than the one before hyper paramater tning mabye because the validation is not simulating the test set perfectly but any ways it's very small fraction that we can ignore

# # Stacking

# make test_level2 using :
# 
# 1) linear regression ( linear algorithms)
# 
# 2) lightgbm (ensamble with dependent trees)
# 
# 3) knn (similarity measures)
# 
# 4) naive_bais (bayesian algotithms)

# A side note that i tried random forest and decision tree but the RAM was crashing so i removed them

# In[ ]:


zeros_array = np.zeros(len(Final_test)) # to initiate the test_level2 with
test_level2 = pd.DataFrame({'lr':zeros_array,'lgbm':zeros_array,'knn':zeros_array,'nb':zeros_array})
test_level2


# In[ ]:


# initiating the models
# fitting the models
# predicting and put the predictions in test_level2 data frame to test on it with the meta model

lr =  LinearRegression()
lr.fit(Final_train.drop(['item_cnt_month'],axis = 1),Final_train.item_cnt_month)
pred = lr.predict(Final_test)
test_level2['lr'] = pred


# In[ ]:


knn= KNeighborsRegressor()
knn.fit(Final_train.drop(['item_cnt_month'],axis = 1),Final_train.item_cnt_month)
pred = knn.predict(Final_test)
test_level2['knn'] = pred


# In[ ]:


nb = GaussianNB()
nb.fit(Final_train.drop(['item_cnt_month'],axis = 1),Final_train.item_cnt_month)
pred = nb.predict(Final_test)
test_level2['nb'] = pred


# In[ ]:


lgbm = LGBMRegressor(random_state = random_state  , learning_rate = 0.02 , n_estimators = 917,num_leaves = 50, feature_fraction = 0.9) 
lgbm.fit(Final_train.drop(['item_cnt_month'],axis = 1),Final_train.item_cnt_month)
pred = lgbm.predict(Final_test)
test_level2['lgbm'] = pred


# In[ ]:


# taking all the dates we have to make conditions on it
dates = Final_train.date_block_num
# this validation_dates will help me making conditions as you will see next
validation_dates = Final_train[dates.isin([24,25,26,27,28])].date_block_num


# In[ ]:


# And here we create 2nd level feeature matrix, init it with zeros first
validation_size = len(Final_train[dates.isin([24,25,26,27,28])])
zeros_array = np.zeros(validation_size )
X_train_level2 = pd.DataFrame({'lr':zeros_array,'lgbm':zeros_array,'knn':zeros_array,'nb':zeros_array , 'dates':validation_dates})

# making the y_train
Final_train_sub = Final_train.loc[dates >  23]
y_train_level2 = Final_train_sub.item_cnt_month


# In[ ]:


models = []
models.append(('lr', LinearRegression()))
models.append(('lgbm',LGBMRegressor(random_state = random_state  , learning_rate = 0.02 , n_estimators = 71,num_leaves = 10)))
models.append(('knn', KNeighborsRegressor()))
models.append(('nb', GaussianNB()))


# In[ ]:


# Now fill `X_train_level2` with metafeatures
for cur_block_num in [28,29,30,31,32]:
    
    print(cur_block_num)
     
    # 1. Split `X_train` into parts
    X = Final_train.loc[dates <  cur_block_num].drop('item_cnt_month', axis=1)
    y= Final_train.loc[dates < cur_block_num, 'item_cnt_month']
    X_test = Final_train.loc[dates ==  cur_block_num].drop('item_cnt_month', axis=1)
    
    
    for name, model in models : # i'm using cross validation but with respect to time and this is done for each model in the 4
        model.fit(X,y)
        pred = model.predict(X_test)
        X_train_level2.loc[X_train_level2.dates == cur_block_num ,name] = pred


# now the meta model will fit on X_train_level2 and predict on test_level2.
# 

# I will get the best paramaters using Randomgridsearch with 4 folds

# In[ ]:


# 2) lighgbm with randomGridSearch on 4 folds

# Define our search space for grid search
search_space = [
  {
               'feature_fraction': [0.7,0.8,0.9,1],
                'n_estimators': [100,150,200,250,300,350,400,450,500,600,700],
               'min_data_in_leaf': [0,1,5,10,50,100,200], 
               'bagging_fraction': [0.7,0.8,0.9,1], 
               'learning_rate': [0.01,0.02], 
               'num_leaves': [1,2,3,4,5,10,15,20,25,30],
               'verbose':[0]
  }
]
# Define cross validation
kfold = StratifiedKFold(n_splits=4, random_state=random_state)
# Define grid search
random_grid = RandomizedSearchCV(
  LGBMRegressor(),
  param_distributions=search_space,
  cv=kfold,
  scoring='neg_root_mean_squared_error',
  verbose=1,
  n_jobs=-1,
  refit = True
)


# In[ ]:


random_grid.fit(X_train_level2.drop('dates',axis = 1) , y_train_level2)

# save the model
filename = 'meta_lgbm.sav'
pickle.dump(random_grid,open(filename,'wb'))

preds = random_grid.predict(test_level2)
sub = sample_submission
sub.item_cnt_month = preds
sub.to_csv('meta_lgbm.csv' , index = False)


# RMSE : `1.21`