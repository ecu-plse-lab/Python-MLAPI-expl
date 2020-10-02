#!/usr/bin/env python
# coding: utf-8

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


train_data=pd.read_csv('/kaggle/input/titanic/train.csv')
train_data.head()


# In[ ]:


test_data=pd.read_csv('/kaggle/input/titanic/test.csv')
test_data.head()


# In[ ]:


women=train_data.loc[train_data.Sex=='female']['Survived']
rate_women=sum(women)/len(women)
print('% of women who survived this freaky British Disaster be: ', rate_women)


# In[ ]:


first_class=train_data.loc[train_data.Pclass==1]['Survived']
rate_first_class=sum(first_class)/len(first_class)
print('% first class passengers survived: ',rate_first_class)


# In[ ]:


sec_class=train_data.loc[train_data.Pclass==2]['Survived']
rate_sec_class=sum(sec_class)/len(sec_class)
print('% second class passengers survived: ',rate_sec_class)


# In[ ]:


from sklearn.ensemble import RandomForestClassifier

y=train_data['Survived']

features=['Pclass','Sex','SibSp','Parch']
X=pd.get_dummies(train_data[features])
X_test=pd.get_dummies(test_data[features])
model=RandomForestClassifier(n_estimators=100, max_depth=5, random_state=1)
model.fit(X,y)
predictions=model.predict(X_test)

output=pd.DataFrame({'PassengerId': test_data.PassengerId, 'Survived': predictions})
output.to_csv('my_submission.csv', index=False)
print('Your submission was successfully saved!')


# In[ ]:



