#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[ ]:


train_data = pd.read_csv("/kaggle/input/titanic/train.csv")
y = train_data["Survived"]
train_data.head()


# In[ ]:


test_data = pd.read_csv("/kaggle/input/titanic/test.csv")
test_data.head()


# In[ ]:


women = train_data.loc[train_data.Sex == 'female']["Survived"]
rate_women = sum(women)/len(women)

print("% of women who survived:", rate_women)


# In[ ]:


col_keep = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch']
train_final = train_data[col_keep]
train_final.head()


# In[ ]:


test_final = test_data[col_keep]
test_final.head()


# In[ ]:


features = ["Pclass", "Sex", "SibSp", "Parch"]
X = pd.get_dummies(train_final[features])
X_test = pd.get_dummies(test_final[features])


# In[ ]:


from xgboost import XGBClassifier
classifier = XGBClassifier()
classifier.fit(X, y)

predictions = classifier.predict(X_test)


# In[ ]:


output = pd.DataFrame({'PassengerId': test_data.PassengerId, 'Survived': predictions})
output.to_csv('my_submission.csv', index=False)
print("Your submission was successfully created!")


# In[ ]:



