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


df_train = pd.read_csv('/kaggle/input/titanic/train.csv')
df_test = pd.read_csv('/kaggle/input/titanic/test.csv')


# In[ ]:


print('Train: ',df_train.shape,'\nTest: ',df_test.shape)


# In[ ]:


women = train_data.loc[train_data.Sex == 'female']['Survived']
rate_women = sum(women)/len(women)
print(round(rate_women,4)*100,'% of women who Survived')


# In[ ]:


men = train_data.loc[train_data.Sex == 'male']['Survived']
rate_men = sum(men)/len(men)
print(round(rate_men,4)*100,'% of men who Survived')


# In[ ]:


df_train['Sex'] = pd.get_dummies(df_train['Sex'],drop_first=True)


# In[ ]:


df_test['Sex'] = pd.get_dummies(df_test['Sex'],drop_first=True)


# In[ ]:


X_train = df_train.drop(['PassengerId','Name','Survived','Ticket','Cabin','Age'],axis=1)
X_train['Embarked'] = X_train['Embarked'].fillna('C')


# In[ ]:


from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(X_train['Embarked'])
X_train['Embarked'] = le.transform(X_train['Embarked'])


# In[ ]:


X_train.isna().sum().sum()


# In[ ]:


X_test = df_test.drop(['PassengerId','Name','Ticket','Cabin','Age'],axis=1)
X_test['Embarked'] = X_test['Embarked'].fillna('C')
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(X_test['Embarked'])
X_test['Embarked'] = le.transform(X_test['Embarked'])
X_test['Fare'] = X_test['Fare'].fillna(X_test['Fare'].mode())
X_test['Fare'] = X_test['Fare'].fillna(np.mean(X_test['Fare']))
X_test.head()


# In[ ]:


y_train = df_train['Survived']


# In[ ]:


from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()
model = lr.fit(X_train,y_train)
prediction = pd.DataFrame(df_train['Survived'])
prediction['Prediction'] = model.predict(X_train)
(prediction['Survived'] == prediction['Prediction']).value_counts()


# In[ ]:


model.predict(X_test)


# In[ ]:


#from sklearn.ensemble import RandomForestClassifier

#y = train_data["Survived"]

#features = ["Pclass", "Sex", "SibSp", "Parch"]
#X = pd.get_dummies(train_data[features])
#X_test = pd.get_dummies(test_data[features])

#model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=1)
#model.fit(X, y)
predictions = model.predict(X_test)

output = pd.DataFrame({'PassengerId': test_data.PassengerId, 'Survived': predictions})
output.to_csv('my_submission.csv', index=False)
print("Your submission was successfully saved!")


# In[ ]:



