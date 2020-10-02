#!/usr/bin/env python
# coding: utf-8

# ## HR Dataset with Demographic, Work Related and Behavioural aspects 

# ### Data Features Simulated
Columns - ID , Name, Gender, Marital Status, DOB, Email, Linkedin, Blogger, Articles, Tenure, Cos_Worked, Academics_Level, Sports_Level, Domains_Worked, Manager_OrNot, Span, Hierachy_Level, Prvs_WorkExp, Rated, Soft_skills, Pay_Level, Pay_Level_Peers, Avg_Promotion_Rate, Avg_Hike_Rate, Bonus Level, Redundancy_Possible, add_random_features

Leavers - Asked_to_Leave, Left_by_Volition, Cause
Joiners - Role_type, Recruited_through
# ### Description of Data for the Not so obvious feature set
Academics_Level - Phd/Tier1/ProAccredition, Specialization/Masters, Graduates
Sports_level - Professional, College_Level, Hobby
Hierachy_Level - Senior, Middle, Low
Rated - High, Average, Bottom. Equivalent of IQ/Performance. Ability to thrive in fixed mindset environment.
Soft_Skills - High, Average, Bottom. Equivalent of EQ/Value Behaviours. Ability to adopt a growth mindset in growth mindset environment.
Pay_Level - Market or Above, At Bargain, Requires Market Correction
Pay_Level_Peers - Above Par, At Par, Birdie
Bonus_Level - Bonus congruent to Rating. Small random Percentage of Rated Paid Low/high
Avg_Promotion_Rate - For each hierachy level - plausible promotion rates. Again, small random % of rated will be promoted - Low or High
Average Hike Rate - Assuming the business is in established in high growth country with average inflation
Roles - Revenue_Generation, Day_to_Day_Ops, Support, Innovation_Niche
Redundancy_Possible - Possibility of Redundancy - High in less than 3 years, Medium in less than 10 years, Low in less than 15 years
Cause - Non-Volition - Automation, Business Restructuring, Market Disruption, Performance Issues, Behavioural Issues; Volition - Retirement, Lack of Pay, Low growth Prospects, Cultural Issues, Restrictive Environment, Personal Issues at office, Personal Issues at home.
Role_type - Replaced for a leaver, New role due to business changes/expansion
add_random_features - added through scikit learn to account for other patterns other than behavioural, work related or demographic such as revenue, salary
# In[ ]:


import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import re

import pydbgen
from pydbgen import pydbgen as dbgen
myDB= dbgen.pydb()

from sklearn.datasets import make_classification

import random


# ### Simulating HR Data

# In[ ]:


size = 1000
#Dataframe
hr_data = pd.DataFrame()

np.random.seed(1)

hr_data["ID"] = np.arange(size)
hr_data["Name"] = myDB.gen_data_series(size,'name',seed=1)
#hr_data["Location"] = myDB.gen_data_series(size,'city',seed=1)
hr_data["Gender"] = np.random.choice(['Male','Female'],size = size, p= [0.7,0.3])
hr_data["Marital_Status"]=np.random.choice(['Married','Unmarried','Divorced'],size = size, p= [0.3,0.5,0.2])
hr_data["Age_Range"] = np.random.choice(['18-30','30-50','50-70'],size = size, p= [0.6,0.35,0.05])
hr_data["Blogger_yn"] = np.random.choice(['Yes','No'],size = size, p= [0.95,0.05])
hr_data["Tenure"] = np.random.choice(['0-3','4-8','8-15','15-30'],size = size, p= [0.4,0.3,0.25,0.05])
hr_data["Academics_Level"] = np.random.choice(['Phd/Tier1/ProAccredition','Specialization/Masters','Graduates'],size = size, p= [0.1,0.6,0.3])
hr_data["Sports_Level"] = np.random.choice(['Professional','College_Level','Hobby'],size = size, p= [0.05,0.25,0.7])
hr_data["Hierachy_Level"] = np.random.choice(['Senior','Middle','Low'],size = size, p= [0.05,0.25,0.7])
hr_data["Manager_OrNot"] = np.random.choice(['Yes','No'],size = size, p= [0.8,0.2])
hr_data["Rated"] = np.random.choice(['High','Average','Bottom'],size = size, p= [0.4,0.59,0.01])#High, Average, Bottom. Equivalent of IQ/Performance. Ability to thrive in fixed mindset environment.
hr_data["Soft_Skills"] = np.random.choice(['Example Behaviour','As Required','Temperamental'],size = size, p= [0.4,0.59,0.01])
hr_data["Roles"] = np.random.choice(['Revenue_Generation', 'Day_to_Day_Ops', 'Support', 'Innovation_Niche'],size = size, p= [0.2,0.3,0.3,0.2])#pareto ratio -  20% are the movers - revenue generator or innovation

#dependent columns
hr_data["Articles"] = hr_data.Blogger_yn.apply(lambda x: np.random.randint(0,10) if x=="Yes" else "NA")
hr_data["Cos_Worked"] = hr_data.Tenure.apply(lambda x: np.random.randint(0,2) if x=="0-3" else np.random.randint(0,8))
hr_data["people_reporting_count"] = hr_data.Manager_OrNot.apply(lambda x: np.random.randint(0,10) if x=="Yes" else "NA")

#Salary data
hr_data["Fixed_Salary"] = np.random.weibull(1,size)*200000


# In[ ]:


def high_paying_job(academics,sports,roles):
    """
    the company is ready to pay top dollar for those people who are top in academics or sports 
    provided that they are part of revenue generation or innovation niche roles
    """
    if re.match("Phd*",academics) or re.match("Pro*",sports):
            if re.match("[(Rev*)|(Inno*)]",roles):
                        return True


# In[ ]:


hr_data['Pay_Level'] = hr_data.apply(lambda x: "Market or above" 
                                     if high_paying_job(x["Academics_Level"],x["Sports_Level"],x["Roles"]) 
                                     else np.random.choice(["On Average","Birdie"], p=[0.7,0.3]),axis = 1 )


# In[ ]:


hr_data.Pay_Level.value_counts()
#hr_data[["Academics_Level","Sports_Level","Roles"]][hr_data.Pay_Level=="Market or above"]


# > Adding Leavers to primary hr data with additional Base Feautures to aid modeling

# In[ ]:


# Imbalance = two class with 70% negative, 30% positive
# clusters = 2 
# n_informative = 2 unique features
# n_redundant = 1 redundant features
# flip y for adding noise

X,y = make_classification(n_samples=1000, n_features=3, n_informative=2, n_redundant=1, n_repeated=0, n_classes=2, 
                          n_clusters_per_class=2,class_sep=2,flip_y=0.2,weights=[0.7,0.3], random_state=17)


# In[ ]:


generated = pd.DataFrame(X,columns = ['add_feature_1','add_feature_2','add_feature_3'])
generated["Leavers"] = y

#hr_data added with leavers
hr_data = pd.concat([hr_data,generated],axis=1)


# In[ ]:


hr_data.to_csv('/kaggle/working/hr_data_comprehensive.csv')


# Appendix
# 
Weibull distribution is a continuous probability distribution. It is unlike the normal distribution which is more balanced. Weibull can be used to create skewed distributions. In this case, we are using to create salary where majority are paid at the lower range. Below shows two scenarios of skewed salary payouts. The first one with a scale of 2 is more skewed to the right. The second with scale of 5 gets closer to ideal payouts where still select group of people are paid per their contribution but, largely the discrimination or gap between rich and poor is narrowed.
# In[ ]:


plt.hist(np.random.weibull(2,1000))
plt.hist(np.random.weibull(5,1000))


# > Loading dataset within a kernel - Sample code

# In[ ]:


import pandas as pd
hr_data_comprehensive = pd.read_csv("../input/hr_data_comprehensive.csv")
