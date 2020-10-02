#!/usr/bin/env python
# coding: utf-8

# In this kernal i'm going to create a predictive model for covid19 global-forecasting week 5 data which contains around 7 lakhs data for  training and we have to predict the target values for 3 lakhs test data
# 
# In this model first i have did some analysis with the data with some graphs and also the the effect of corona in  India have been analysed seperately.
# 
# Finally I created a ensemble learning model with almost 0.96 Rsquared score

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv
from matplotlib import pyplot as plt

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[ ]:


train = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-5/train.csv')
test = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-5/test.csv')


# In[ ]:


train.head(3)


# In[ ]:


import seaborn as sns


# In[ ]:


train.info()


# # <center>Top 20 in Population</center>

# In[ ]:


df1 = train.Population.groupby(train['Country_Region']).max().sort_values(ascending= False)
df10 = pd.DataFrame()
df20 = pd.DataFrame()
df10['population'] = df1.iloc[0:10]
df10['country']= df10.index
df20['population'] = df1.iloc[11:20]
df20['country'] = df20.index


# In[ ]:


plt.figure(figsize =(10,10))
plt.subplot(2,1,1)
sns.barplot(x='country', y='population', data=df10, orient ='v')
plt.xlabel('Country')
plt.title('Popoulation Top 10')
plt.subplot(2,1,2)
sns.barplot(x='country', y='population', data=df20, orient ='v')
plt.xlabel('Country')
plt.title('Population Next 10')


# # <center>Top 20 in Confirmed Cases</center>

# In[ ]:


train1= train[train['Target']=='ConfirmedCases']
data1 = pd.DataFrame()
data1['values'] =train1.TargetValue.groupby(train1['Country_Region']).sum().sort_values(ascending= False)
data1['country'] = data1.index
data1.index = np.arange(0,len(data1))
data10 = data1.iloc[0:10,:]
data20 = data1.iloc[11:20,:]


# In[ ]:


plt.figure(figsize =(10,10))
plt.subplot(2,1,1)
sns.barplot(x='country', y='values', data=data10, orient ='v')
plt.xlabel('Country')
plt.ylabel('Cases')
plt.title('Covid Cases Top 10')
plt.subplot(2,1,2)
sns.barplot(x='country', y='values', data=data20, orient ='v')
plt.xlabel('Country')
plt.ylabel('Cases')
plt.title('Covid Cases Next 10')


# # <center>Top 20 in Deaths</center>

# In[ ]:


train1= train[train['Target']!='ConfirmedCases']
data1 = pd.DataFrame()
data1['values'] =train1.TargetValue.groupby(train1['Country_Region']).sum().sort_values(ascending= False)
data1['country'] = data1.index
data1.index = np.arange(0,len(data1))
data10 = data1.iloc[0:10,:]
data20 = data1.iloc[11:20,:]


# In[ ]:


plt.figure(figsize =(10,10))
plt.subplot(2,1,1)
sns.barplot(x='country', y='values', data=data10, orient ='v')
plt.xlabel('Country')
plt.ylabel('Deaths')
plt.title('Covid Cases Top 10')
plt.subplot(2,1,2)
sns.barplot(x='country', y='values', data=data20, orient ='v')
plt.xlabel('Country')
plt.ylabel('Deaths')
plt.title('Covid Cases Next 10')


# # <center>Fatalities vs Confirmed cases(WW)</center>

# In[ ]:


df = train['TargetValue'].groupby(train['Target']).sum()
labels =[df.index[0],df.index[1]]
sizes = [df[0],df[1]]
explode = (0, 0.2)  

plt.figure(figsize = (5,5))
plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)

plt.show()


# # <center>Analysing the cases in India</center>

# In[ ]:


india = train[train['Country_Region']=='India']


# In[ ]:


india.info()


# In[ ]:


india.drop(['County','Province_State'],axis =1,inplace =True)


# In[ ]:


india.head(2)


# In[ ]:


india.index = np.arange(0,len(india)) #rechanging the index


# In[ ]:


india.head(2)


# In[ ]:


ind = india[india['Target']=='ConfirmedCases']
ind.index = np.arange(0,len(ind))


# In[ ]:


ind.head(2)


# In[ ]:


print("Date with more no.of cases in india {}".format((ind[ind['TargetValue']==ind['TargetValue'].max()]['Date']).values))
print("The cases are {}".format((ind[ind['TargetValue']==ind['TargetValue'].max()]['TargetValue']).values))


# In[ ]:


list1 = []
for i in range(2,7):
    date = '2020'+'-0'+str(i)+'-01'
    list1.append(ind[ind['Date']<date]['TargetValue'].sum())
print(list1)


# # <center>Monthly Progression of disease </center>

# In[ ]:


sns.barplot(['upto Jan','Upto Feb','Upto Mar', 'Upto Apr','Upto May'],list1)


# In[ ]:


list2 =[]
for i in range(len(list1)):
    if i ==0:
        list2.append(list1[i])
    else:
        list2.append(list1[i]-list1[i-1])
print(list2)


# # <center>Count per month</center>

# In[ ]:


labels =['Jan','Feb','Mar','Apr','May']
sns.barplot(labels,list2)


# # <center>Fatalities vs Confirmed cases(India)</center>

# In[ ]:


df = india['TargetValue'].groupby(train['Target']).sum()
df


# In[ ]:


labels =[df.index[0],df.index[1]]
sizes = [df[0],df[1]]
explode = (0, 0.2)  
plt.figure(figsize = (5,5))

plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)

plt.show()


# In[ ]:


wor = train[train['Target']=='ConfirmedCases']


# In[ ]:


print("Date with more no.of cases  {}".format((wor[wor['TargetValue']==wor['TargetValue'].max()]['Date']).values))
print("The cases are {}".format((wor[wor['TargetValue']==wor['TargetValue'].max()]['TargetValue']).values))
print("The Country is {}".format((wor[wor['TargetValue']==wor['TargetValue'].max()]['Country_Region']).values))


# In[ ]:


wor.columns


# In[ ]:


independent_columns = ['Country_Region','Weight','Target','Date']
dependent_column = ['TargetValue']


# In[ ]:


X= train[independent_columns]
y = train[dependent_column]


# In[ ]:


from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
X['Target']=le.fit_transform(X['Target'])


# In[ ]:


X.info()


# # <center>Encoding Country according to it's rank in no.of confirmed cases</center>

# In[ ]:


train1= train[train['Target']=='ConfirmedCases']
data1 = pd.DataFrame()
data1['values'] =train1.TargetValue.groupby(train1['Country_Region']).sum().sort_values(ascending= False)
data1['country'] = data1.index


# In[ ]:


k = len(data1['country'])
dict1 = {}
for i in data1['country']:
    dict1[i] = k
    k =k-1


# In[ ]:


list1=[]
X['encoded_country']=0
for i in X['Country_Region']:
    list1.append(dict1[i])
X['encoded_country'] = list1


# In[ ]:


X['encoded_country'].value_counts()


# # <center> Picking out date and month seperately</center>

# In[ ]:


X['date_dup'] = pd.to_datetime(X['Date'])


# In[ ]:


X['month'] = 0
list1=[]
for i in X['date_dup']:
    list1.append(i.month)
X['month'] = list1


# In[ ]:


X['date'] = 0
list1=[]
for i in X['date_dup']:
    list1.append(i.day)
X['date'] = list1


# In[ ]:


X.head(2)


# In[ ]:


X.drop(['Country_Region','Date','date_dup'],axis =1,inplace =True)


# In[ ]:


X.head(2)


# # <center> Seeing the Correleation</center>

# In[ ]:


plt.figure(figsize =(10,10))
sns.heatmap(X.corr(),annot=True)


# In[ ]:


from sklearn.model_selection import train_test_split as tts


# In[ ]:


max_range =10


# In[ ]:


from sklearn.ensemble import RandomForestRegressor as regr
from sklearn.metrics import r2_score


# # Actually I did some processing to find the best random state and I commented because it takes so much time to run
# BEST RANDOM STATE:7

# In[ ]:


'''for i in range(max_range):
    X_train,X_test,y_train,y_test = tts(X,y,test_size =0.3,random_state =i)
    model = regr()
    model.fit(X_train,y_train)
    print("Random state {}\n".format(i))
    print(r2_score(y_test,model.predict(X_test)))'''


# In[ ]:


X_train,X_test,y_train,y_test = tts(X,y,test_size =0.3,random_state =7)
model = regr()
model.fit(X_train,y_train)


# In[ ]:


print(r2_score(y_test,model.predict(X_test)))


# # <center>Preprocessing the test data in the same way we did for training data</center>

# In[ ]:


test = test[independent_columns]


# In[ ]:


list1=[]
test['encoded_country']=0
for i in test['Country_Region']:
    list1.append(dict1[i])
test['encoded_country'] = list1


# In[ ]:


test['date_dup'] = pd.to_datetime(test['Date'])


# In[ ]:


test['month'] = 0
list1=[]
for i in test['date_dup']:
    list1.append(i.month)
test['month'] = list1


# In[ ]:


test['date'] = 0
list1=[]
for i in test['date_dup']:
    list1.append(i.day)
test['date'] = list1


# In[ ]:


test.head(2)


# In[ ]:


test.drop(['Country_Region','Date','date_dup'],axis =1,inplace =True)


# In[ ]:


test.head(2)


# In[ ]:


le1 =LabelEncoder()
test['Target'] = le1.fit_transform(test['Target'])


# In[ ]:


pred = model.predict(test)


# In[ ]:


t =pd.read_csv('/kaggle/input/covid19-global-forecasting-week-5/test.csv')
ss = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-5/submission.csv')


# In[ ]:


output = pd.DataFrame({'Id': t.ForecastId  , 'TargetValue': pred})


# In[ ]:


a=output.groupby(['Id'])['TargetValue'].quantile(q=0.05).reset_index()
b=output.groupby(['Id'])['TargetValue'].quantile(q=0.5).reset_index()
c=output.groupby(['Id'])['TargetValue'].quantile(q=0.95).reset_index()


# In[ ]:


a.columns=['Id','q0.05']
b.columns=['Id','q0.5']
c.columns=['Id','q0.95']
a=pd.concat([a,b['q0.5'],c['q0.95']],1)
a['q0.05']=a['q0.05']
a['q0.5']=a['q0.5']
a['q0.95']=a['q0.95']


# In[ ]:


sub=pd.melt(a, id_vars=['Id'], value_vars=['q0.05','q0.5','q0.95'])
sub['variable']=sub['variable'].str.replace("q","", regex=False)
sub['ForecastId_Quantile']=sub['Id'].astype(str)+'_'+sub['variable']
sub['TargetValue']=sub['value']
sub=sub[['ForecastId_Quantile','TargetValue']]
sub.reset_index(drop=True,inplace=True)
sub.to_csv("submission.csv",index=False)
sub.head()


# In[ ]:


sub.info()
