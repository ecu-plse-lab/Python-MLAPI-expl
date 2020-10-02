#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
job_df=pd.read_csv("../input/job-classification-dataset/jobclassinfo2.csv")
job_df.info()


# In[ ]:


job_df=job_df.drop(["ID","JobFamilyDescription","JobClass","JobClassDescription","PG"],axis=1)
#all the useless variables has been droped
job_df[0:8]


# In[ ]:


import matplotlib.pyplot as plt
import seaborn as sn
get_ipython().run_line_magic('matplotlib', 'inline')

influential_features=['JobFamily',
 'EducationLevel',
 'Experience',
 'OrgImpact',
 'ProblemSolving',
 'Supervision',
 'ContactLevel',
 'FinancialBudget','PayGrade']

sn.pairplot(job_df[influential_features], height=2)


# In[ ]:


job_df[influential_features].corr()


# In[ ]:


plt.figure(figsize=(10,7))
sn.heatmap(job_df[influential_features].corr(), annot=True)


# In[ ]:


x_features=list(job_df.columns)
x_features.remove("PayGrade")
x_features.remove("JobFamily")
#removing unnccesary variables after analysing correlation
x_features


# In[ ]:


categorical_vars=x_features


# In[ ]:


job_df_dum=pd.get_dummies(job_df[x_features],columns=categorical_vars,drop_first=True)
x_features=job_df_dum.columns
x_features


# In[ ]:


import statsmodels.api as sm
from sklearn.model_selection import train_test_split

y=job_df.PayGrade
x=sm.add_constant(job_df_dum)
train_x,test_x,train_y,test_y=train_test_split(x,y,train_size=0.7,random_state=42)


# In[ ]:


from sklearn import linear_model
from sklearn import metrics

model_1_job=linear_model.LogisticRegression()
model_1=model_1_job.fit(train_x,train_y)


# In[ ]:


y_pred = model_1.predict(test_x)


# In[ ]:


print("Accuracy of Logistic Regression model is:",
metrics.accuracy_score(test_y, y_pred))


# In[ ]:


y_pred_df=pd.DataFrame({"actual":test_y,"predictedfrom_model":y_pred})
y_pred_df.sample(15,random_state=42)


# In[ ]:


print(metrics.classification_report( y_pred_df.actual, y_pred_df.predictedfrom_model ))


# Precision =  The ratio of how much of the predicted is correct.
# Recall   =   The ratio of how many of the actual labels were predicted.