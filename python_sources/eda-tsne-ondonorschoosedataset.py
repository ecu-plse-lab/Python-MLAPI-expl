#!/usr/bin/env python
# coding: utf-8

# # DonorsChoose

# <p>
# DonorsChoose.org receives hundreds of thousands of project proposals each year for classroom projects in need of funding. Right now, a large number of volunteers is needed to manually screen each submission before it's approved to be posted on the DonorsChoose.org website.
# </p>
# <p>
#     Next year, DonorsChoose.org expects to receive close to 500,000 project proposals. As a result, there are three main problems they need to solve:
# <ul>
# <li>
#     How to scale current manual processes and resources to screen 500,000 projects so that they can be posted as quickly and as efficiently as possible</li>
#     <li>How to increase the consistency of project vetting across different volunteers to improve the experience for teachers</li>
#     <li>How to focus volunteer time on the applications that need the most assistance</li>
#     </ul>
# </p>    
# <p>
# The goal of the competition is to predict whether or not a DonorsChoose.org project proposal submitted by a teacher will be approved, using the text of project descriptions as well as additional metadata about the project, teacher, and school. DonorsChoose.org can then use this information to identify projects most likely to need further review before approval.
# </p>

# ## About the DonorsChoose Data Set
# 
# The `train.csv` data set provided by DonorsChoose contains the following features:
# 
# Feature | Description 
# ----------|---------------
# **`project_id`** | A unique identifier for the proposed project. **Example:** `p036502`   
# **`project_title`**    | Title of the project. **Examples:**<br><ul><li><code>Art Will Make You Happy!</code></li><li><code>First Grade Fun</code></li></ul> 
# **`project_grade_category`** | Grade level of students for which the project is targeted. One of the following enumerated values: <br/><ul><li><code>Grades PreK-2</code></li><li><code>Grades 3-5</code></li><li><code>Grades 6-8</code></li><li><code>Grades 9-12</code></li></ul>  
#  **`project_subject_categories`** | One or more (comma-separated) subject categories for the project from the following enumerated list of values:  <br/><ul><li><code>Applied Learning</code></li><li><code>Care &amp; Hunger</code></li><li><code>Health &amp; Sports</code></li><li><code>History &amp; Civics</code></li><li><code>Literacy &amp; Language</code></li><li><code>Math &amp; Science</code></li><li><code>Music &amp; The Arts</code></li><li><code>Special Needs</code></li><li><code>Warmth</code></li></ul><br/> **Examples:** <br/><ul><li><code>Music &amp; The Arts</code></li><li><code>Literacy &amp; Language, Math &amp; Science</code></li>  
#   **`school_state`** | State where school is located ([Two-letter U.S. postal code](https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations#Postal_codes)). **Example:** `WY`
# **`project_subject_subcategories`** | One or more (comma-separated) subject subcategories for the project. **Examples:** <br/><ul><li><code>Literacy</code></li><li><code>Literature &amp; Writing, Social Sciences</code></li></ul> 
# **`project_resource_summary`** | An explanation of the resources needed for the project. **Example:** <br/><ul><li><code>My students need hands on literacy materials to manage sensory needs!</code</li></ul> 
# **`project_essay_1`**    | First application essay<sup>*</sup>  
# **`project_essay_2`**    | Second application essay<sup>*</sup> 
# **`project_essay_3`**    | Third application essay<sup>*</sup> 
# **`project_essay_4`**    | Fourth application essay<sup>*</sup> 
# **`project_submitted_datetime`** | Datetime when project application was submitted. **Example:** `2016-04-28 12:43:56.245`   
# **`teacher_id`** | A unique identifier for the teacher of the proposed project. **Example:** `bdf8baa8fedef6bfeec7ae4ff1c15c56`  
# **`teacher_prefix`** | Teacher's title. One of the following enumerated values: <br/><ul><li><code>nan</code></li><li><code>Dr.</code></li><li><code>Mr.</code></li><li><code>Mrs.</code></li><li><code>Ms.</code></li><li><code>Teacher.</code></li></ul>  
# **`teacher_number_of_previously_posted_projects`** | Number of project applications previously submitted by the same teacher. **Example:** `2` 
# 
# <sup>*</sup> See the section <b>Notes on the Essay Data</b> for more details about these features.
# 
# Additionally, the `resources.csv` data set provides more data about the resources required for each project. Each line in this file represents a resource required by a project:
# 
# Feature | Description 
# ----------|---------------
# **`id`** | A `project_id` value from the `train.csv` file.  **Example:** `p036502`   
# **`description`** | Desciption of the resource. **Example:** `Tenor Saxophone Reeds, Box of 25`   
# **`quantity`** | Quantity of the resource required. **Example:** `3`   
# **`price`** | Price of the resource required. **Example:** `9.95`   
# 
# **Note:** Many projects require multiple resources. The `id` value corresponds to a `project_id` in train.csv, so you use it as a key to retrieve all resources needed for a project:
# 
# The data set contains the following label (the value you will attempt to predict):
# 
# Label | Description
# ----------|---------------
# `project_is_approved` | A binary flag indicating whether DonorsChoose approved the project. A value of `0` indicates the project was not approved, and a value of `1` indicates the project was approved.

# ### Notes on the Essay Data
# 
# <ul>
# Prior to May 17, 2016, the prompts for the essays were as follows:
# <li>__project_essay_1:__ "Introduce us to your classroom"</li>
# <li>__project_essay_2:__ "Tell us more about your students"</li>
# <li>__project_essay_3:__ "Describe how your students will use the materials you're requesting"</li>
# <li>__project_essay_4:__ "Close by sharing why your project will make a difference"</li>
# </ul>
# 
# 
# <ul>
# Starting on May 17, 2016, the number of essays was reduced from 4 to 2, and the prompts for the first 2 essays were changed to the following:<br>
# <li>__project_essay_1:__ "Describe your students: What makes your students special? Specific details about their background, your neighborhood, and your school are all helpful."</li>
# <li>__project_essay_2:__ "About your project: How will these materials make a difference in your students' learning and improve their school lives?"</li>
# <br>For all projects with project_submitted_datetime of 2016-05-17 and later, the values of project_essay_3 and project_essay_4 will be NaN.
# </ul>
# 

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
import warnings
warnings.filterwarnings("ignore")

import sqlite3
import pandas as pd
import numpy as np
import nltk
import string
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from sklearn.metrics import roc_curve, auc
from nltk.stem.porter import PorterStemmer

import re
# Tutorial about Python regular expressions: https://pymotw.com/2/re/
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import pickle

from tqdm import tqdm
import os

# replaced -- from plotly import plotly with below line. as it was giving exception 
#reference from https://github.com/plotly/plotly.py/issues/1660
from chart_studio.plotly import plot, iplot
import plotly.offline as offline
import plotly.graph_objs as go
offline.init_notebook_mode()
from collections import Counter


# ## 1.1 Reading Data

# In[ ]:


project_data = pd.read_csv('../input/donors-chose/train_data.csv')
resource_data = pd.read_csv('../input/donors-chose/resources.csv')


# In[ ]:


print(project_data.info())
print(resource_data.info())


# In[ ]:


print("Number of data points in train data", project_data.shape)
print('-'*50)
print("The attributes of data :", project_data.columns.values)


# In[ ]:


print("Number of data points in train data", resource_data.shape)
print(resource_data.columns.values)
resource_data.head(2)


# # 1.2 Data Analysis

# In[ ]:


# PROVIDE CITATIONS TO YOUR CODE IF YOU TAKE IT FROM ANOTHER WEBSITE.
# https://matplotlib.org/gallery/pie_and_polar_charts/pie_and_donut_labels.html#sphx-glr-gallery-pie-and-polar-charts-pie-and-donut-labels-py


y_value_counts = project_data['project_is_approved'].value_counts()
print("Number of projects thar are approved for funding ", y_value_counts[1], ", (", (y_value_counts[1]/(y_value_counts[1]+y_value_counts[0]))*100,"%)")
print("Number of projects thar are not approved for funding ", y_value_counts[0], ", (", (y_value_counts[0]/(y_value_counts[1]+y_value_counts[0]))*100,"%)")

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
recipe = ["Accepted", "Not Accepted"]

data = [y_value_counts[1], y_value_counts[0]]

wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    ax.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                 horizontalalignment=horizontalalignment, **kw)

ax.set_title("Nmber of projects that are Accepted and not accepted")

plt.show()


# **Analysis --> from the above pie plot Number of Projects that are accepted are around 85% which much higher than number of projects which are rejected.**

# ### 1.2.1 Univariate Analysis: School State

# In[ ]:


# Pandas dataframe groupby count, mean: https://stackoverflow.com/a/19385591/4084039

#https://github.com/plotly/plotly.py/issues/1660

temp = pd.DataFrame(project_data.groupby("school_state")["project_is_approved"].apply(np.mean)).reset_index()
# if you have data which contain only 0 and 1, then the mean = percentage (think about it)
temp.columns = ['state_code', 'num_proposals']

# How to plot US state heatmap: https://datascience.stackexchange.com/a/9620

scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]

data = [ dict(
        type='choropleth',
        colorscale = scl,
        autocolorscale = False,
        locations = temp['state_code'],
        z = temp['num_proposals'].astype(float),
        locationmode = 'USA-states',
        text = temp['state_code'],
        marker = dict(line = dict (color = 'rgb(255,255,255)',width = 2)),
        colorbar = dict(title = "% of pro")
    ) ]

layout = dict(
        title = 'Project Proposals % of Acceptance Rate by US States',
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)',
        ),
    )

fig = go.Figure(data=data, layout=layout)
offline.iplot(fig, filename='us-map-heat-map')


# In[ ]:


temp.head(10)


# In[ ]:


# https://www.csi.cuny.edu/sites/default/files/pdf/administration/ops/2letterstabbrev.pdf
temp.sort_values(by=['num_proposals'], inplace=True)
print("States with lowest % approvals")
print(temp.head(5))
print('='*50)
print("States with highest % approvals")
print(temp.tail(5))


# if we look at the above summary we can colnclude two thing
# 
# 1). State Vermont has lowest Approval rate with 80% and Delaware has highest approval rate of around 90%
# 
# 2). even though our average approval rate is close to 85%, the variablity in approval rate lies between 80% to 90% which means 
# this feature plays a important role in deciding whether the project may or may not get approval

# In[ ]:


#stacked bar plots matplotlib: https://matplotlib.org/gallery/lines_bars_and_markers/bar_stacked.html
def stack_plot(data, xtick, col2='project_is_approved', col3='total'):
    ind = np.arange(data.shape[0])
    
    plt.figure(figsize=(20,5))
    p1 = plt.bar(ind, data[col3].values)
    p2 = plt.bar(ind, data[col2].values)

    plt.ylabel('Projects')
    plt.title('Number of projects aproved vs rejected')
    plt.xticks(ind, list(data[xtick].values))
    plt.legend((p1[0], p2[0]), ('total', 'accepted'))
    plt.show()


# In[ ]:


def univariate_barplots(data, col1, col2='project_is_approved', top=False):
    # Count number of zeros in dataframe python: https://stackoverflow.com/a/51540521/4084039
    temp = pd.DataFrame(project_data.groupby(col1)[col2].agg(lambda x: x.eq(1).sum())).reset_index()

    # Pandas dataframe grouby count: https://stackoverflow.com/a/19385591/4084039
    temp['total'] = pd.DataFrame(project_data.groupby(col1)[col2].agg({'total':'count'})).reset_index()['total']
    temp['Avg'] = pd.DataFrame(project_data.groupby(col1)[col2].agg({'Avg':'mean'})).reset_index()['Avg']
    
    temp.sort_values(by=['total'],inplace=True, ascending=False)
    #print(temp.head())
    if top:
        temp = temp[0:top]
    
    stack_plot(temp, xtick=col1, col2=col2, col3='total')
    print(temp.head(5))
    print("="*50)
    print(temp.tail(5))


# In[ ]:


univariate_barplots(project_data, 'school_state', 'project_is_approved', False)


# **__SUMMARY**
# 1) Every state has greater than 80% success rate in approval__
# 
# 2)highest number of Projects has been submitted from state  of California and lowest number of Projects has been Submitted from state of Vermont

# ### 1.2.2 Univariate Analysis: teacher_prefix

# In[ ]:


univariate_barplots(project_data, 'teacher_prefix', 'project_is_approved' , top=False)


# **Analysis from above plot**
# --> number of Unique prefix's are 5
# 
# --> teacher whose prefix are "Mrs." have higher number of Project Submission and also Higher Submission rate of 85%
# 
# --> Prefix "Ms." and "Mr." has alomost similar rate of Project approval but but slighlty low as compared to "Mrs."
# 
# --> Doctors have low approval rate of 69% as compared to "Mrs", "Mr" and "Ms.". but the project submitted by them is also very low. it just 14

# ### 1.2.3 Univariate Analysis: project_grade_category

# In[ ]:


univariate_barplots(project_data, 'project_grade_category', 'project_is_approved', top=False)


# **Summary**
# 
# --> grade level of students doesn't make much impact on Project approval rate. since all the grades has almost similar approval rate of around 83-85%
# 
# --> but the project submitted by Grade Prek-2 students are slightly higher
# 
# --> Student between grade 9 to 12 have submitted less projects as comared to Prek-2 and Grade 3-5 students

# ### 1.2.4 Univariate Analysis: project_subject_categories

# In[ ]:


catogories = list(project_data['project_subject_categories'].values)
# remove special characters from list of strings python: https://stackoverflow.com/a/47301924/4084039

# https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
# https://stackoverflow.com/questions/23669024/how-to-strip-a-specific-word-from-a-string
# https://stackoverflow.com/questions/8270092/remove-all-whitespace-in-a-string-in-python
cat_list = []
for i in catogories:
    temp = ""
    temp_list=[]
    temp_new=""
    # consider we have text like this "Math & Science, Warmth, Care & Hunger"
    for j in i.split(','): # it will split it in three parts ["Math & Science", "Warmth", "Care & Hunger"]
        if 'The' in j.split(): # this will split each of the catogory based on space "Math & Science"=> "Math","&", "Science"
            j=j.replace('The','') # if we have the words "The" we are going to replace it with ''(i.e removing 'The')
        j = j.replace(' ','') # we are placeing all the ' '(space) with ''(empty) ex:"Math & Science"=>"Math&Science"
        temp+=j.strip()+" " #" abc ".strip() will return "abc", remove the trailing spaces
        temp = temp.replace('&','_') # we are replacing the & value into 
        '''i have made a small change in the code while cleaning categories 
        for each project categories will now be listed in sorted order just to make sure we get unique combination for example
        if a project had Math_science and arts_music and other has arts_music and Math_science both should be included in a unique
        count i.e arts_music Math_science after sorting. this will give a unique result and will be good in analysis'''
    temp_list=sorted(temp.split(' '))
    for s in temp_list:
        temp_new+=s+" "
    cat_list.append(temp_new.strip())


# In[ ]:


project_data['clean_categories'] = cat_list
project_data.drop(['project_subject_categories'], axis=1, inplace=True)
project_data.head(2)


# In[ ]:


univariate_barplots(project_data, 'clean_categories', 'project_is_approved', top=20)


# **Analysis from Above plot**
# 
# --> there is lots of variability in number of project submmitted and approvd among different categories
# 
# --> the top three categories on which there is highest number of Project belongs to "Lietacy and Literature" , "Math and Science" or the combination og both categieries
# 
# --> most of the projects that have highest number of submission and approval have atleast two categories
# 
# --> even though there is less submission of project for "warmth" "care & Hunger" but the approval rate is around 93%
# 
# --> Health & sports with Literacy & language has very less number of submission

# In[ ]:


print(len(project_data['clean_categories']))


# In[ ]:


# count of all the words in corpus python: https://stackoverflow.com/a/22898595/4084039
from collections import Counter
my_counter = Counter()
for word in project_data['clean_categories'].values:
    my_counter.update(word.split())


# In[ ]:


print(type(my_counter))
print(my_counter)


# In[ ]:


# dict sort by value python: https://stackoverflow.com/a/613218/4084039
cat_dict = dict(my_counter)
sorted_cat_dict = dict(sorted(cat_dict.items(), key=lambda kv: kv[1]))

print("categories counter",cat_dict)
print("--"*10)
print("Sorted Catregories counter",sorted_cat_dict)

ind = np.arange(len(sorted_cat_dict))
plt.figure(figsize=(20,5))
p1 = plt.bar(ind, list(sorted_cat_dict.values()))

plt.ylabel('Projects')
plt.title('% of projects aproved category wise')
plt.xticks(ind, list(sorted_cat_dict.keys()))
plt.show()


# In[ ]:


for i, j in sorted_cat_dict.items():
    print("{:20} :{:10}".format(i,j))


# **Analysis**
# 
# earlier we looked at projects with group of categories. but after calculating the word counter for each individual word/categories we found that there is too much variablity in the project with different unique categories
# 
# category Literacy & Language has been used 52239 times or we can say in 52239 Project whereas category "care & Hunger" has been used only in 1388 Projects
# 
# this can be one of the important feature to predict whether a Project will be approved or not

# ### 1.2.5 Univariate Analysis: project_subject_subcategories

# In[ ]:


sub_catogories = list(project_data['project_subject_subcategories'].values)
# remove special characters from list of strings python: https://stackoverflow.com/a/47301924/4084039

# https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
# https://stackoverflow.com/questions/23669024/how-to-strip-a-specific-word-from-a-string
# https://stackoverflow.com/questions/8270092/remove-all-whitespace-in-a-string-in-python

sub_cat_list = []
for i in sub_catogories:
    temp = ""
    temp_list=[]
    temp_new=""
    # consider we have text like this "Math & Science, Warmth, Care & Hunger"
    for j in i.split(','): # it will split it in three parts ["Math & Science", "Warmth", "Care & Hunger"]
        if 'The' in j.split(): # this will split each of the catogory based on space "Math & Science"=> "Math","&", "Science"
            j=j.replace('The','') # if we have the words "The" we are going to replace it with ''(i.e removing 'The')
        j = j.replace(' ','') # we are placeing all the ' '(space) with ''(empty) ex:"Math & Science"=>"Math&Science"
        temp +=j.strip()+" "#" abc ".strip() will return "abc", remove the trailing spaces
        temp = temp.replace('&','_')
    temp_list=sorted(temp.split(' '))
    for s in temp_list:
        temp_new+=s+" "
    
    sub_cat_list.append(temp_new.strip())


# In[ ]:


project_data['clean_subcategories'] = sub_cat_list
project_data.drop(['project_subject_subcategories'], axis=1, inplace=True)
project_data.head(2)


# In[ ]:


univariate_barplots(project_data, 'clean_subcategories', 'project_is_approved', top=50)


# **Analysis**
# 
# --> even in the subcategories there is lot og variablity in the data
# 
# --> the Subcategory "Literacy" have highest number of submission and approval and even the approval rate is arounf 88% percent
# 
# --> if you look at the top 5 subcategories which has highest submission and approval all are single or combination of "Literacy" , "Mathematics" and "Literature"
# 
# --> while the subcategories that have least submission ranges from 330 t0 389 project whixh is very less as compared to the highest subcategories Project. so the variance in the Project submission is high
# 

# In[ ]:


# count of all the words in corpus python: https://stackoverflow.com/a/22898595/4084039
from collections import Counter
my_counter = Counter()
for word in project_data['clean_subcategories'].values:
    my_counter.update(word.split())


# In[ ]:


# dict sort by value python: https://stackoverflow.com/a/613218/4084039
sub_cat_dict = dict(my_counter)
sorted_sub_cat_dict = dict(sorted(sub_cat_dict.items(), key=lambda kv: kv[1]))


ind = np.arange(len(sorted_sub_cat_dict))
plt.figure(figsize=(20,5))
p1 = plt.bar(ind, list(sorted_sub_cat_dict.values()))

plt.ylabel('Projects')
plt.title('% of projects aproved state wise')
plt.xticks(ind, list(sorted_sub_cat_dict.keys()))
plt.show()


# In[ ]:


print("total Distinct Subcategories :",len(sorted_sub_cat_dict))

#print(sorted_sub_cat_dict.head())

print("*"*20)

for i, j in sorted_sub_cat_dict.items():
    print("{:20} :{:10}".format(i,j),round(((j/sum(sorted_sub_cat_dict.values()))*100),2))    


# **Analysis**
# 
# --> there are total 30 distinct subcategories in the entire data sets
# 
# --> if we lokk at the list above, we find that there is too much variability in project submission and approval for distinct subcategories. 
# 
# --> the subcategory "Economics" has very less no of project as compared to "Literacy" Subcategory which has around 33700 Project which is around more than 100 times to that of "econmics"
# 
# --> only 0.15% of project submitted have "Economics" as Subcategories" while more than 19% of Project submitted has "Literacy" as Sub Category 

# ### 1.2.6 Univariate Analysis: Text features (Title)

# In[ ]:


#How to calculate number of words in a string in DataFrame: https://stackoverflow.com/a/37483537/4084039
word_count = project_data['project_title'].str.split().apply(len).value_counts()
word_dict = dict(word_count)

print(word_dict)

word_dict = dict(sorted(word_dict.items(), key=lambda kv: kv[1]))


ind = np.arange(len(word_dict))
plt.figure(figsize=(20,5))
p1 = plt.bar(ind, list(word_dict.values()))

plt.ylabel('Number of projects')
plt.xlabel('Number words in project title')
plt.title('Words for each title of the project')
plt.xticks(ind, list(word_dict.keys()))
plt.show()


# **Analysis**
# 
# from the above plot we can find that there is lot of variance in the total word count in Project title. project title with 1 word and more than 10 words are very very less or alomost negligible. wherease most of the project submission belongs to project which has project title between 3-7 words 

# In[ ]:


approved_title_word_count = project_data[project_data['project_is_approved']==1]['project_title'].str.split().apply(len)
approved_title_word_count = approved_title_word_count.values

rejected_title_word_count = project_data[project_data['project_is_approved']==0]['project_title'].str.split().apply(len)
rejected_title_word_count = rejected_title_word_count.values


# In[ ]:


# https://glowingpython.blogspot.com/2012/09/boxplot-with-matplotlib.html
plt.boxplot([approved_title_word_count, rejected_title_word_count])
plt.xticks([1,2],('Approved Projects','Rejected Projects'))
plt.ylabel('Words in project title')
plt.grid()
plt.show()


# **Analysis**
# 
# if we look at the box plot of project distributions for feature "Word count in Title", we find that median of both the Approved and Rejected Projects are almost same i.e. close to 5
# 
# but box plot of approved project is slightly high as Compared to Rejected Proeject class which indicates that number of words in Project title is slightly more than number of words in Project title for Rejected Projects

# In[ ]:


plt.figure(figsize=(10,3))
sns.kdeplot(approved_title_word_count,label="Approved Projects", bw=0.6)
sns.kdeplot(rejected_title_word_count,label="Not Approved Projects", bw=0.6)
plt.legend()
plt.show()


# **Analysis**
# --> the PDF plot and Boxplot indticates almost similar thing i.e.
# 
# since the plot of Approved project is slightly ahead of Rejected Projectes, which means word count in Approved projects are slighlty higher than word count in rejected Proijects

# ### 1.2.7 Univariate Analysis: Text features (Project Essay's)

# In[ ]:


# merge two column text dataframe: 
project_data["essay"] = project_data["project_essay_1"].map(str) +                        project_data["project_essay_2"].map(str) +                         project_data["project_essay_3"].map(str) +                         project_data["project_essay_4"].map(str)


# In[ ]:


approved_word_count = project_data[project_data['project_is_approved']==1]['essay'].str.split().apply(len)
approved_word_count = approved_word_count.values

rejected_word_count = project_data[project_data['project_is_approved']==0]['essay'].str.split().apply(len)
rejected_word_count = rejected_word_count.values


# In[ ]:


# https://glowingpython.blogspot.com/2012/09/boxplot-with-matplotlib.html
plt.boxplot([approved_word_count, rejected_word_count])
plt.title('Words for each essay of the project')
plt.xticks([1,2],('Approved Projects','Rejected Projects'))
plt.ylabel('Words in project essays')
plt.grid()
plt.show()


# **Analysis**
# 
# --> even though the median of Rejected and Approved Projects are almost similar ,we can see that box of Approve Projects are
# 
# --> 75% percents of approved projects have word count less or equal to 295 words while 75% of rejected projects have word count less than or equal to 275 words
# 
# --> higher than that of rejeced Projects which says projects with higher number of word counnts have higher chances of getting approved

# In[ ]:


plt.figure(figsize=(10,3))
sns.distplot(approved_word_count, hist=False, label="Approved Projects")
sns.distplot(rejected_word_count, hist=False, label="Not Approved Projects")
plt.title('Words for each essay of the project')
plt.xlabel('Number of words in each eassay')
plt.legend()
plt.show()


# **Analysis**
# 
# the above plot shows almost similar analysis to that of Box plot
# 
# --> the plot of Approved Projects is slightly ahead of Rejected Projects which says projects whose Word Count in the essay is higher has high chances of geeting approved

# ### 1.2.8 Univariate Analysis: Cost per project

# In[ ]:


# we get the cost of the project using resource.csv file
resource_data.head(2)


# In[ ]:


# https://stackoverflow.com/questions/22407798/how-to-reset-a-dataframes-indexes-for-all-groups-in-one-step
price_data = resource_data.groupby('id').agg({'price':'sum', 'quantity':'sum'}).reset_index()
price_data.head(2)


# In[ ]:


# join two dataframes in python: 
project_data = pd.merge(project_data, price_data, on='id', how='left')


# In[ ]:


approved_price = project_data[project_data['project_is_approved']==1]['price'].values

rejected_price = project_data[project_data['project_is_approved']==0]['price'].values


# In[ ]:


# https://glowingpython.blogspot.com/2012/09/boxplot-with-matplotlib.html
plt.boxplot([approved_price, rejected_price])
plt.title('Box Plots of Cost per approved and not approved Projects')
plt.xticks([1,2],('Approved Projects','Rejected Projects'))
plt.ylabel('Price')
plt.grid()
plt.show()


# **Analysis**
# 
# the box plots for "COst of Project" is quite messy and gives no idea about the impace of cost of project on the whether the project was approved or not

# In[ ]:


plt.figure(figsize=(10,3))
sns.distplot(approved_price, hist=False, label="Approved Projects")
sns.distplot(rejected_price, hist=False, label="Not Approved Projects")
plt.title('Cost per approved and not approved Projects')
plt.xlabel('Cost of a project')
plt.legend()
plt.show()


# **Analysis*
# 
# just like Box Plot, even the pdf plot don't tell anything much about the impace of cost on Project Approval or rejection since it override each other at post of the part of plot
# 
# --> but if you look at the end part, tail of rejected project is slightly ahead of approved projects ,which says if the cst of project is high afyer certain price level, the rejections are more

# In[ ]:


# http://zetcode.com/python/prettytable/
from prettytable import PrettyTable

#If you get a ModuleNotFoundError error , install prettytable using: pip3 install prettytable

x = PrettyTable()
x.field_names = ["Percentile", "Approved Projects", "Not Approved Projects","Price Difference"]

for i in range(0,101,5):
    x.add_row([i,np.round(np.percentile(approved_price,i), 3), np.round(np.percentile(rejected_price,i), 3),round((np.round(np.percentile(rejected_price,i), 3)-np.round(np.percentile(approved_price,i), 3)),3)])
print(x)


# **Analysis**
# 
# if we look at the above Percentile table, we would come to know that for all the Percentils the Cost of rejected Projects is Higher than the Cost of Rejeced Projects which means project with large cost are tends to get rejected
# 
# as will move from 0 Percentile to 95% the price difference is getting increased between Approved and Rejected Projects. 
# 
# if we look at the 95 percentild of Approved project, the value is \\$801.59 which says even if the highest cost can be \\$9999.00 but 95% of Approve projects only have cosrt less than \\$801.59 and only 5% of approve projecrts has cost between \\$802.00 to \\$9999.00
# 

# <h3><font color='red'>1.2.9 Univariate Analysis: teacher_number_of_previously_posted_projects</font></h3>

# In[ ]:


univariate_barplots(project_data, 'teacher_number_of_previously_posted_projects', 'project_is_approved', top=25)


# **Analysis from above bar plots**
# 
# --> most of the Project that has been Submitted is being submitted first time by any teacher
# 
# -->there are good chunks of number of Projects submitted lies between range 1 to 4. which says a good number of projects has been submitted by teacher who has submitted 1 to 4 projects in the past
# 
# --> even though the number of projects submitted by teacher who has previously submitted project is very low , but if you look at the number it tells that teacher who has submitted more than 15 projects earlier. the acceptance rate is more than 86% and it increases as the number of fearture valriable increase. 
# it says that this feature plays good role in deciding whether the project will be approved or not

# In[ ]:


approved_previouslyPostedProjectcount= project_data[project_data['project_is_approved']==1]['teacher_number_of_previously_posted_projects'].values

rejected_previouslyPostedProjectcount = project_data[project_data['project_is_approved']==0]['teacher_number_of_previously_posted_projects'].values


# In[ ]:


plt.boxplot([approved_previouslyPostedProjectcount,rejected_previouslyPostedProjectcount])
plt.title('Box Plots of projects count for number of previously Submitted Projects')
plt.xticks([1,2],('Approved Projects','Rejected Projects'))
plt.ylabel('teacher_number_of_prevnuiously_posted_projects')
plt.grid()
plt.show()


# **Analysis**
# 
# --> boxplot don't depict much about the relation of Approvals and rejection of projects  with "number of project submitted by teacher earlier" because the number of projects which is submitted by teacher who has never submitted any projects before or have submitted only 1 or 2 projects before are much much higher

# In[ ]:


plt.figure(figsize=(10,3))
sns.distplot(approved_previouslyPostedProjectcount, hist=False, label="Approved Projects")
sns.distplot(rejected_previouslyPostedProjectcount, hist=False, label="Not Approved Projects")
plt.title('PDF of teacher number of previously posted projects for Approved and Rejected Projects')
plt.xlabel('teacher number of previously posted projects')
plt.legend()
plt.show()


# **Analysis**
# 
# the pdf for Approved projects move slightly ahead against rejected projects which says that teachers who have submiited the Projects earlier before current submission, the acceptance rate of such project is higher

# <h3><font color='red'>1.2.10 Univariate Analysis: project_resource_summary</font></h3>

# In[ ]:


project_data.head(5)


# In[ ]:


#How to calculate number of words in a string in DataFrame: https://stackoverflow.com/a/37483537/4084039
word_count = project_data['project_resource_summary'].str.split().apply(len).value_counts()
word_dict = dict(word_count)

print(word_dict)

word_dict = dict(sorted(word_dict.items(), key=lambda kv: kv[1]))


ind = np.arange(len(word_dict))
plt.figure(figsize=(20,5))
p1 = plt.bar(ind, list(word_dict.values()))

plt.ylabel('Number of projects')
plt.xlabel('Number words in project resource summary')
plt.title('Words in each project resource summary')
plt.xticks(ind, list(word_dict.keys()))
plt.show()


# **Analysis**
# 
# => the minimum number of word that a project resource summary has is 4 while the maximum word in any summary is 137
# 
# => even though the variance in the word count is from 4 to 137 but majority of project has word count between 11-15
# 
# => more than 10000 projects has word count of 11
# 
# ==> Majority of Project have word count between 11 to 31

# In[ ]:


approved_projectresourcesummarycount = project_data[project_data['project_is_approved']==1]['project_resource_summary'].str.split().apply(len)
approved_projectresourcesummarycount = approved_projectresourcesummarycount.values

rejected_projectresourcesummarycount = project_data[project_data['project_is_approved']==0]['project_resource_summary'].str.split().apply(len)
rejected_projectresourcesummarycount = rejected_projectresourcesummarycount.values


# In[ ]:


x = PrettyTable()
x.field_names = ["Percentile", "Approved Projects", "Not Approved Projects","word Difference"]

for i in range(0,101,5):
    x.add_row([i,np.round(np.percentile(approved_projectresourcesummarycount,i), 3), np.round(np.percentile(rejected_projectresourcesummarycount,i), 3),round((np.round(np.percentile(approved_projectresourcesummarycount,i), 3)-np.round(np.percentile(rejected_projectresourcesummarycount,i), 3)),3)])
print(x)


# **Analysis**
# 
# from the above percentile table we can see that all the percentiles has almost similar word counts in both approved and rejected categiories 
# 
# but if we look at the 75% percentile, the 75% of approved projects have word count less than equal to 26

# ### checking the prsence of mumerical digit in Project Resource Summary

# In[ ]:


#resource https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number

def contains_Numbers(inputString):
    x=0
    if (any(char.isdigit() for char in inputString)):
        x=1
    else:
        x=0
    return x    


# In[ ]:


res_summary = list(project_data['project_resource_summary'].values)
res_summary
IsSummaryhasDigit_list = []
for i in res_summary:
    IsSummaryhasDigit_list.append(contains_Numbers(i))


# In[ ]:


project_data['numericdigit_summary_flag'] = IsSummaryhasDigit_list
project_data.head(5)


# In[ ]:


project_data['numericdigit_summary_flag'].value_counts(normalize=True)


# Analysis --> 85% of projects does not have any numeric digit in the resource summary while the rest 85% have numneric digit

# In[ ]:


univariate_barplots(project_data, 'numericdigit_summary_flag', 'project_is_approved')


# **Analysis**
# project which doesn't have numeric value in the resource field 84 % approval rate 
# 
# project which has numeric value in the resource summry hase 89% approaval rate which is 5% higher than project without any numeric field in resource_summary column which somehow indicates that project with numeric value in resource_summary field has hgiher chances of approval

# ## 1.3 Text preprocessing

# ### 1.3.1 Essay Text

# In[ ]:


project_data.head(2)


# In[ ]:


# printing some random essays.
print(project_data['essay'].values[0])
print("="*50)
print(project_data['essay'].values[150])
print("="*50)
print(project_data['essay'].values[1000])
print("="*50)
print(project_data['essay'].values[20000])
print("="*50)
print(project_data['essay'].values[99999])
print("="*50)


# In[ ]:


# https://stackoverflow.com/a/47091490/4084039
import re

def decontracted(phrase):
    # specific
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase


# In[ ]:


sent = decontracted(project_data['essay'].values[20000])
print(sent)
print("="*50)


# In[ ]:


# \r \n \t remove from string python: http://texthandler.com/info/remove-line-breaks-python/
sent = sent.replace('\\r', ' ')
sent = sent.replace('\\"', ' ')
sent = sent.replace('\\n', ' ')
print(sent)


# In[ ]:


#remove spacial character: https://stackoverflow.com/a/5843547/4084039
sent = re.sub('[^A-Za-z0-9]+', ' ', sent)
print(sent)


# In[ ]:


# https://gist.github.com/sebleier/554280
# we are removing the words from the stop words list: 'no', 'nor', 'not'
stopwords= ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",            "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',             'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their',            'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',             'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',             'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',             'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very',             's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're',             've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',            "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',            "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't",             'won', "won't", 'wouldn', "wouldn't"]


# In[ ]:


# Combining all the above statemennts 
from tqdm import tqdm
preprocessed_essays = []
# tqdm is for printing the status bar
for sentance in tqdm(project_data['essay'].values):
    sent = decontracted(sentance)
    sent = sent.replace('\\r', ' ')
    sent = sent.replace('\\"', ' ')
    sent = sent.replace('\\n', ' ')
    sent = re.sub('[^A-Za-z0-9]+', ' ', sent)
    # https://gist.github.com/sebleier/554280
    sent = ' '.join(e for e in sent.split() if e not in stopwords)
    preprocessed_essays.append(sent.lower().strip())


# In[ ]:


# after preprocesing
preprocessed_essays[20000]


# <h3><font color='red'>1.3.2 Project title Text</font></h3>

# In[ ]:


# similarly you can preprocess the titles also

# Combining all the above statemennts 
from tqdm import tqdm
preprocessed_projecttitle = []
# tqdm is for printing the status bar
for sentance in tqdm(project_data['project_title'].values):
    sent = decontracted(sentance)
    sent = sent.replace('\\r', ' ')
    sent = sent.replace('\\"', ' ')
    sent = sent.replace('\\n', ' ')
    sent = re.sub('[^A-Za-z0-9]+', ' ', sent)
    # https://gist.github.com/sebleier/554280
    sent = ' '.join(e for e in sent.split() if e not in stopwords)
    preprocessed_projecttitle.append(sent.lower().strip())


# In[ ]:


print(preprocessed_projecttitle[2000])
print("*"*50)
print(preprocessed_projecttitle[3100])

print(preprocessed_projecttitle[20000])


# ## 1. 4 Preparing data for models

# In[ ]:


project_data.columns


# we are going to consider
# 
#        - school_state : categorical data
#        - clean_categories : categorical data
#        - clean_subcategories : categorical data
#        - project_grade_category : categorical data
#        - teacher_prefix : categorical data
#        
#        - project_title : text data
#        - text : text data
#        - project_resource_summary: text data
#        
#        - quantity : numerical
#        - teacher_number_of_previously_posted_projects : numerical
#        - price : numerical

# ### 1.4.1 Vectorizing Categorical data

# - https://www.appliedaicourse.com/course/applied-ai-course-online/lessons/handling-categorical-and-numerical-features/

# In[ ]:


list(sorted_cat_dict.keys())


# In[ ]:


# we use count vectorizer to convert the values into one hot encoded features
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(vocabulary=list(sorted_cat_dict.keys()), lowercase=False, binary=True)
vectorizer.fit(project_data['clean_categories'].values)
print(vectorizer.get_feature_names())


categories_one_hot = vectorizer.transform(project_data['clean_categories'].values)
print("Shape of matrix after one hot encodig ",categories_one_hot.shape)


# In[ ]:


# we use count vectorizer to convert the values into one hot encoded features
vectorizer = CountVectorizer(vocabulary=list(sorted_sub_cat_dict.keys()), lowercase=False, binary=True)
vectorizer.fit(project_data['clean_subcategories'].values)
print(vectorizer.get_feature_names())


sub_categories_one_hot = vectorizer.transform(project_data['clean_subcategories'].values)
print("Shape of matrix after one hot encodig ",sub_categories_one_hot.shape)


# ### 3.1 one Hot Encoding of School State

# In[ ]:


my_counter_state = Counter()
for word in project_data['school_state'].values:
    my_counter_state.update(word.split())


# In[ ]:


# dict sort by value python: https://stackoverflow.com/a/613218/4084039
state_dict = dict(my_counter_state)
sorted_state_dict = dict(sorted(my_counter_state.items(), key=lambda kv: kv[1]))


# In[ ]:


# we use count vectorizer to convert the values into one hot encoded features
vectorizer = CountVectorizer(vocabulary=list(sorted_state_dict.keys()), lowercase=False, binary=True)
vectorizer.fit(project_data['school_state'].values)
print(vectorizer.get_feature_names())


state_one_hot = vectorizer.transform(project_data['school_state'].values)
print("Shape of matrix after one hot encodig ",state_one_hot.shape)


# ### 3.4 one Hot Encoding of Teacher Prefix

# In[ ]:


my_counter_TeacherPrefix = Counter()
for word in project_data['teacher_prefix'].values:
    word_str=str(word)
    my_counter_TeacherPrefix.update(word_str.split())


# In[ ]:


# dict sort by value python: https://stackoverflow.com/a/613218/4084039
teacher_prefix_dict = dict(my_counter_TeacherPrefix)
sorted_teacher_prefix_dict = dict(sorted(teacher_prefix_dict.items(), key=lambda kv: kv[1]))


# In[ ]:


# we use count vectorizer to convert the values into one hot encoded features
vectorizer = CountVectorizer(vocabulary=list(sorted_teacher_prefix_dict.keys()), lowercase=False, binary=True)
#vectorizer.fit(project_data['teacher_prefix'].values)
# the above line was showing error "np.nan is an invalid document, expected byte or unicode string."
#resource : https://stackoverflow.com/questions/39303912/tfidfvectorizer-in-scikit-learn-valueerror-np-nan-is-an-invalid-document

vectorizer.fit(project_data['teacher_prefix'].values.astype('U'))

print(vectorizer.get_feature_names())

print("*"*50)
teacher_prefix_one_hot = vectorizer.transform(project_data['teacher_prefix'].values.astype('U'))
print("Shape of matrix after one hot encodig ",teacher_prefix_one_hot.shape)


# ### 3.5 one Hot Encoding of project_grade_category

# In[ ]:


my_counter_projgradcat = Counter()
for word in project_data['project_grade_category'].values:
    my_counter_projgradcat.update(word.split())


# In[ ]:


# dict sort by value python: https://stackoverflow.com/a/613218/4084039
projgrade_dict = dict(my_counter_projgradcat)
sorted_projgrade_dict = dict(sorted(projgrade_dict.items(), key=lambda kv: kv[1]))

sorted_projgrade_dict


# In[ ]:


# we use count vectorizer to convert the values into one hot encoded features
vectorizer = CountVectorizer(vocabulary=list(sorted_projgrade_dict.keys()), lowercase=False, binary=True)
vectorizer.fit(project_data['project_grade_category'].values)
print(vectorizer.get_feature_names())


project_grade_category_one_hot = vectorizer.transform(project_data['project_grade_category'].values)
print("Shape of matrix after one hot encodig ",project_grade_category_one_hot.shape)


# ### 1.4.2 Vectorizing Text data

# #### 1.4.2.1 Bag of words

# In[ ]:


# We are considering only the words which appeared in at least 10 documents(rows or projects).
vectorizer = CountVectorizer(min_df=10)
text_bow = vectorizer.fit_transform(preprocessed_essays)
print("Shape of matrix after one hot encodig ",text_bow.shape)


# <h4><font color='red'> 1.4.2.2 Bag of Words on `project_title`</font></h4>

# In[ ]:


# you can vectorize the title also 
# before you vectorize the title make sure you preprocess it
# Similarly you can vectorize for title also
vectorizer = CountVectorizer(min_df=10)
projtitle_bow = vectorizer.fit_transform(preprocessed_projecttitle)
print("Shape of matrix after one hot encodig ",projtitle_bow.shape)


# #### 1.4.2.3 TFIDF vectorizer

# In[ ]:


from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(min_df=10)
text_tfidf = vectorizer.fit_transform(preprocessed_essays)
print("Shape of matrix after one hot encodig ",text_tfidf.shape)


# <h4><font color='red'> 1.4.2.4 TFIDF Vectorizer on `project_title`</font></h4>

# In[ ]:


# Similarly you can vectorize for title also
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(min_df=10)
projecttitle_tfidf = vectorizer.fit_transform(preprocessed_projecttitle)
print("Shape of matrix after one hot encodig ",projecttitle_tfidf.shape)


# #### 1.4.2.5 Using Pretrained Models: Avg W2V

# In[ ]:


'''
# Reading glove vectors in python: https://stackoverflow.com/a/38230349/4084039
def loadGloveModel(gloveFile):
    print ("Loading Glove Model")
    f = open(gloveFile,'r', encoding="utf8")
    model = {}
    for line in tqdm(f):
        splitLine = line.split()
        word = splitLine[0]
        embedding = np.array([float(val) for val in splitLine[1:]])
        model[word] = embedding
    print ("Done.",len(model)," words loaded!")
    return model
model = loadGloveModel(r'E:\Applied-AI\assignment-2-comp\glove.42B.300d\glove.42B.300d.txt')

# ============================
#Output:
    
#Loading Glove Model
#1917495it [06:32, 4879.69it/s]
#Done. 1917495  words loaded!

# ============================

words = []
for i in preprocessed_essays:
    words.extend(i.split(' '))

for i in preprocessed_projecttitle:
    words.extend(i.split(' '))
print("all the words in the coupus", len(words))
words = set(words)
print("the unique words in the coupus", len(words))

inter_words = set(model.keys()).intersection(words)
print("The number of words that are present in both glove vectors and our coupus", \
      len(inter_words),"(",np.round(len(inter_words)/len(words)*100,3),"%)")

words_courpus = {}
words_glove = set(model.keys())
for i in words:
    if i in words_glove:
        words_courpus[i] = model[i]
print("word 2 vec length", len(words_courpus))


# stronging variables into pickle files python: http://www.jessicayung.com/how-to-use-pickle-to-save-and-load-variables-in-python/

import pickle
with open('glove_vectors', 'wb') as f:
    pickle.dump(words_courpus, f)
'''


# In[ ]:



# stronging variables into pickle files python: http://www.jessicayung.com/how-to-use-pickle-to-save-and-load-variables-in-python/
# make sure you have the glove_vectors file
with open('../input/donors-chose/glove_vectors', 'rb') as f:
    model = pickle.load(f)
    glove_words =  set(model.keys())    


# In[ ]:


# average Word2Vec
# compute average word2vec for each review.
avg_w2v_vectors = []; # the avg-w2v for each sentence/review is stored in this list
for sentence in tqdm(preprocessed_essays): # for each review/sentence
    vector = np.zeros(300) # as word vectors are of zero length
    cnt_words =0; # num of words with a valid vector in the sentence/review
    for word in sentence.split(): # for each word in a review/sentence
        if word in glove_words:
            vector += model[word]
            cnt_words += 1
    if cnt_words != 0:
        vector /= cnt_words
    avg_w2v_vectors.append(vector)

print(len(avg_w2v_vectors))
print(len(avg_w2v_vectors[0]))


# <h4><font color='red'> 1.4.2.6 Using Pretrained Models: AVG W2V on `project_title`</font></h4>

# In[ ]:


# Similarly you can vectorize for title also
# average Word2Vec
# compute average word2vec for each review.
avg_w2v_vectors_projtitles = []; # the avg-w2v for each sentence/review is stored in this list
for sentence in tqdm(preprocessed_projecttitle): # for each review/sentence
    vector = np.zeros(300) # as word vectors are of zero length
    cnt_words =0; # num of words with a valid vector in the sentence/review
    for word in sentence.split(): # for each word in a review/sentence
        if word in glove_words:
            vector += model[word]
            cnt_words += 1
    if cnt_words != 0:
        vector /= cnt_words
    avg_w2v_vectors_projtitles.append(vector)

print(len(avg_w2v_vectors_projtitles))
print(len(avg_w2v_vectors_projtitles[0]))


# #### 1.4.2.7 Using Pretrained Models: TFIDF weighted W2V

# In[ ]:


# S = ["abc def pqr", "def def def abc", "pqr pqr def"]
tfidf_model = TfidfVectorizer()
tfidf_model.fit(preprocessed_essays)
# we are converting a dictionary with word as a key, and the idf as a value
dictionary = dict(zip(tfidf_model.get_feature_names(), list(tfidf_model.idf_)))
tfidf_words = set(tfidf_model.get_feature_names())


# In[ ]:


# average Word2Vec
# compute average word2vec for each review.
tfidf_w2v_vectors = []; # the avg-w2v for each sentence/review is stored in this list
for sentence in tqdm(preprocessed_essays): # for each review/sentence
    vector = np.zeros(300) # as word vectors are of zero length
    tf_idf_weight =0; # num of words with a valid vector in the sentence/review
    for word in sentence.split(): # for each word in a review/sentence
        if (word in glove_words) and (word in tfidf_words):
            vec = model[word] # getting the vector for each word
            # here we are multiplying idf value(dictionary[word]) and the tf value((sentence.count(word)/len(sentence.split())))
            tf_idf = dictionary[word]*(sentence.count(word)/len(sentence.split())) # getting the tfidf value for each word
            vector += (vec * tf_idf) # calculating tfidf weighted w2v
            tf_idf_weight += tf_idf
    if tf_idf_weight != 0:
        vector /= tf_idf_weight
    tfidf_w2v_vectors.append(vector)

print(len(tfidf_w2v_vectors))
print(len(tfidf_w2v_vectors[0]))


# <h4><font color='red'> 1.4.2.9 Using Pretrained Models: TFIDF weighted W2V on `project_title`</font></h4>

# In[ ]:


# Similarly you can vectorize for title also
# S = ["abc def pqr", "def def def abc", "pqr pqr def"]
tfidf_model = TfidfVectorizer()
tfidf_model.fit(preprocessed_projecttitle)
# we are converting a dictionary with word as a key, and the idf as a value
dictionary = dict(zip(tfidf_model.get_feature_names(), list(tfidf_model.idf_)))
tfidf_words_projtitle = set(tfidf_model.get_feature_names())


# In[ ]:


# average Word2Vec
# compute average word2vec for each review.
tfidf_w2v_vectors_projtitle = []; # the avg-w2v for each sentence/review is stored in this list
for sentence in tqdm(preprocessed_projecttitle): # for each review/sentence
    vector = np.zeros(300) # as word vectors are of zero length
    tf_idf_weight =0; # num of words with a valid vector in the sentence/review
    for word in sentence.split(): # for each word in a review/sentence
        if (word in glove_words) and (word in tfidf_words):
            vec = model[word] # getting the vector for each word
            # here we are multiplying idf value(dictionary[word]) and the tf value((sentence.count(word)/len(sentence.split())))
            tf_idf = dictionary[word]*(sentence.count(word)/len(sentence.split())) # getting the tfidf value for each word
            vector += (vec * tf_idf) # calculating tfidf weighted w2v
            tf_idf_weight += tf_idf
    if tf_idf_weight != 0:
        vector /= tf_idf_weight
    tfidf_w2v_vectors_projtitle.append(vector)

print(len(tfidf_w2v_vectors_projtitle))
print(len(tfidf_w2v_vectors_projtitle[0]))


# ### 1.4.3 Vectorizing Numerical features

# In[ ]:


# check this one: https://www.youtube.com/watch?v=0HOqOcln3Z4&t=530s
# standardization sklearn: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
from sklearn.preprocessing import StandardScaler

# price_standardized = standardScalar.fit(project_data['price'].values)
# this will rise the error
# ValueError: Expected 2D array, got 1D array instead: array=[725.05 213.03 329.   ... 399.   287.73   5.5 ].
# Reshape your data either using array.reshape(-1, 1)

price_scalar = StandardScaler()
price_scalar.fit(project_data['price'].values.reshape(-1,1)) # finding the mean and standard deviation of this data
print(f"Mean : {price_scalar.mean_[0]}, Standard deviation : {np.sqrt(price_scalar.var_[0])}")

# Now standardize the data with above maen and variance.
price_standardized = price_scalar.transform(project_data['price'].values.reshape(-1, 1))


# In[ ]:


price_standardized


# **Analysis** 
# 
# Mean Cost per Project is around \\$298.00 and Standered deviation is \\$367.5

# In[ ]:


PrevPostedPorjects_scalar = StandardScaler()
PrevPostedPorjects_scalar.fit(project_data['teacher_number_of_previously_posted_projects'].values.reshape(-1,1)) # finding the mean and standard deviation of this data
print(f"Mean : {PrevPostedPorjects_scalar.mean_[0]}, Standard deviation : {np.sqrt(PrevPostedPorjects_scalar.var_[0])}")

# Now standardize the data with above maen and variance.
PrevPostedPorjects_standardized = PrevPostedPorjects_scalar.transform(project_data['teacher_number_of_previously_posted_projects'].values.reshape(-1, 1))


# In[ ]:


PrevPostedPorjects_standardized


# ### 1.4.4 Merging all the above features

# - we need to merge all the numerical vectors i.e catogorical, text, numerical vectors

# In[ ]:


print(categories_one_hot.shape)
print(sub_categories_one_hot.shape)
print(state_one_hot.shape)
print(project_grade_category_one_hot.shape)
print(teacher_prefix_one_hot.shape)
print(projtitle_bow.shape)
print(projecttitle_tfidf.shape)
#print(avg_w2v_vectors_projtitles.shape)
#print(tfidf_w2v_vectors_projtitle.shape)
print(price_standardized.shape)
print(PrevPostedPorjects_standardized.shape)


# In[ ]:


# merge two sparse matrices: https://stackoverflow.com/a/19710648/4084039
from scipy.sparse import hstack
# with the same hstack function we are concatinating a sparse matrix and a dense matirx :)
X = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot, projtitle_bow,projecttitle_tfidf,avg_w2v_vectors_projtitles,tfidf_w2v_vectors_projtitle, price_standardized,PrevPostedPorjects_standardized))
X.shape


# <h1><font color='red'>Assignment 2: Apply TSNE<font></h1>

#  <font color=#F4274F>If you are using any code snippet from the internet, you have to provide the reference/citations, as we did in the above cells. Otherwise, it will be treated as plagiarism without citations.</font>

# <ol> 
#     <li> In the above cells we have plotted and analyzed many features. Please observe the plots and write the observations in markdown cells below every plot.</li>
#     <li> EDA: Please complete the analysis of the feature: teacher_number_of_previously_posted_projects</li>
#     <li>
#         <ul>Build the data matrix using these features 
#             <li>school_state : categorical data (one hot encoding)</li>
#             <li>clean_categories : categorical data (one hot encoding)</li>
#             <li>clean_subcategories : categorical data (one hot encoding)</li>
#             <li>teacher_prefix : categorical data (one hot encoding)</li>
#             <li>project_grade_category : categorical data (one hot encoding)</li>
#             <li>project_title : text data (BOW, TFIDF, AVG W2V, TFIDF W2V)</li>
#             <li>price : numerical</li>
#             <li>teacher_number_of_previously_posted_projects : numerical</li>
#          </ul>
#     </li>
#     <li> Now, plot FOUR t-SNE plots with each of these feature sets.
#         <ol>
#             <li>categorical, numerical features + project_title(BOW)</li>
#             <li>categorical, numerical features + project_title(TFIDF)</li>
#             <li>categorical, numerical features + project_title(AVG W2V)</li>
#             <li>categorical, numerical features + project_title(TFIDF W2V)</li>
#         </ol>
#     </li>
#     <li> Concatenate all the features and Apply TNSE on the final data matrix </li>
#     <li> <font color='blue'>Note 1: The TSNE accepts only dense matrices</font></li>
#     <li> <font color='blue'>Note 2: Consider only 5k to 6k data points to avoid memory issues. If you run into memory error issues, reduce the number of data points but clearly state the number of datat-poins you are using</font></li>
# </ol>

# In[ ]:


# this is the example code for TSNE
import numpy as np
from sklearn.manifold import TSNE
from sklearn import datasets
import pandas as pd
import matplotlib.pyplot as plt

iris = datasets.load_iris()
x = iris['data']
y = iris['target']

tsne = TSNE(n_components=2, perplexity=30, learning_rate=200)

X_embedding = tsne.fit_transform(x)
# if x is a sparse matrix you need to pass it as X_embedding = tsne.fit_transform(x.toarray()) , .toarray() will convert the sparse matrix into dense matrix

for_tsne = np.hstack((X_embedding, y.reshape(-1,1)))
for_tsne_df = pd.DataFrame(data=for_tsne, columns=['Dimension_x','Dimension_y','Score'])
colors = {0:'red', 1:'blue', 2:'green'}
plt.scatter(for_tsne_df['Dimension_x'], for_tsne_df['Dimension_y'], c=for_tsne_df['Score'].apply(lambda x: colors[x]))
plt.show()


# <h2> 2.1 TSNE with `BOW` encoding of `project_title` feature (10k) recrods </h2>

# In[ ]:


# please write all of the code with proper documentation and proper titles for each subsection
# when you plot any graph make sure you use 
    # a. Title, that describes your plot, this will be very helpful to the reader
    # b. Legends if needed
    # c. X-axis label
    # d. Y-axis label
    
from sklearn.manifold import TSNE
from sklearn import datasets

    
x = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot, projtitle_bow, price_standardized,PrevPostedPorjects_standardized),format='csr').toarray()
x = x[0:10000]
y = project_data['project_is_approved']
y = y[0:10000]

tsne = TSNE(n_components=2, perplexity=100, random_state=0)

tsne_data_bow = tsne.fit_transform(x)
tsne_data_bow= np.vstack((tsne_data_bow.T, y)).T
tsne_df_bow = pd.DataFrame(data=tsne_data_bow, columns=("Dimension_x", "Dimension_y", "Approved"))
sns.FacetGrid(tsne_df_bow, hue="Approved", height=6).map(plt.scatter, 'Dimension_x', 'Dimension_y').add_legend()
plt.title('TSNE with all Numerical, categorical feature and BOW encoding of PROJECT_TITLE feature')
plt.show()    


# <h2> 2.2 TSNE with `TFIDF` encoding of `project_title` feature (6k) records [Commented] </h2>

# In[ ]:


'''
#please write all the code with proper documentation, and proper titles for each subsection
# when you plot any graph make sure you use 
    # a. Title, that describes your plot, this will be very helpful to the reader
    # b. Legends if needed
    # c. X-axis label
    # d. Y-axis label
    
x = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot,projecttitle_tfidf,price_standardized,PrevPostedPorjects_standardized),format='csr').toarray()
x = x[0:6000]
y = project_data['project_is_approved']
y = y[0:6000]

tsne = TSNE(n_components=2, perplexity=100, random_state=0)

tsne_data_bow = tsne.fit_transform(x)
tsne_data_bow= np.vstack((tsne_data_bow.T, y)).T
tsne_df_bow = pd.DataFrame(data=tsne_data_bow, columns=("Dimension_x", "Dimension_y", "Approved"))
sns.FacetGrid(tsne_df_bow, hue="Approved", height=6).map(plt.scatter, 'Dimension_x', 'Dimension_y').add_legend()
plt.title('TSNE with all Numerical, categorical feature and TFIDF encoding of PROJECT_TITLE feature')
plt.show()  
'''


# **Analysis**
# 
# since the points overlapping both classes and class "0" is not visibile, we cannot analayse anything from the t-SNE plot
# 
# taking larger sets of data for the plot might work

# <h2> 2.3 TSNE with `AVG W2V` encoding of `project_title` feature (15k) records [commented] </h2>

# In[ ]:


'''
# please write all the code with proper documentation, and proper titles for each subsection
# when you plot any graph make sure you use 
    # a. Title, that describes your plot, this will be very helpful to the reader
    # b. Legends if needed
    # c. X-axis label
    # d. Y-axis label
#categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot, projtitle_bow,projecttitle_tfidf,avg_w2v_vectors_projtitles,tfidf_w2v_vectors_projtitle, price_standardized,PrevPostedPorjects_standardized

x = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot,avg_w2v_vectors_projtitles,price_standardized,PrevPostedPorjects_standardized),format='csr').toarray()
x = x[0:15000]
y = project_data['project_is_approved']
y = y[0:15000]

tsne = TSNE(n_components=2, perplexity=100, random_state=0)

tsne_data_bow = tsne.fit_transform(x)
tsne_data_bow= np.vstack((tsne_data_bow.T, y)).T
tsne_df_bow = pd.DataFrame(data=tsne_data_bow, columns=("Dimension_x", "Dimension_y", "Approved"))
sns.FacetGrid(tsne_df_bow, hue="Approved", height=6).map(plt.scatter, 'Dimension_x', 'Dimension_y').add_legend()
plt.title('TSNE with all Numerical, categorical feature and AVG W2V encoding of PROJECT_TITLE feature')
plt.show()   
'''


# **Analysis**
# 
# since the points overlapping both classes and class "0" is not visibile, we cannot analayse anything from the t-SNE plot
# 
# taking larger sets of data for the plot might work

# <h2> 2.4 TSNE with `TFIDF Weighted W2V` encoding of `project_title` feature (15k) records [commented] </h2>

# In[ ]:


'''
# please write all the code with proper documentation, and proper titles for each subsection
# when you plot any graph make sure you use 
    # a. Title, that describes your plot, this will be very helpful to the reader
    # b. Legends if needed
    # c. X-axis label
    # d. Y-axis label
x = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot, tfidf_w2v_vectors_projtitle, price_standardized,PrevPostedPorjects_standardized),format='csr').toarray()
x = x[0:15000]
y = project_data['project_is_approved']
y = y[0:15000]

tsne = TSNE(n_components=2, perplexity=100, random_state=0)

tsne_data_bow = tsne.fit_transform(x)
tsne_data_bow= np.vstack((tsne_data_bow.T, y)).T
tsne_df_bow = pd.DataFrame(data=tsne_data_bow, columns=("Dimension_x", "Dimension_y", "Approved"))
sns.FacetGrid(tsne_df_bow, hue="Approved", height=6).map(plt.scatter, 'Dimension_x', 'Dimension_y').add_legend()
plt.title('TSNE with all Numerical, categorical feature and TFIDF Weighted W2V encoding of PROJECT_TITLE feature')
plt.show()   
'''  


# **Analysis**
# 
# since the points overlapping both classes and class "0" is not visibile, we cannot analayse anything from the t-SNE plot
# 
# taking larger sets of data for the plot might work

# <h2> 2.5 TSNE with all the Vectors `project_title` feature 15k records </h2>

# In[ ]:


# please write all the code with proper documentation, and proper titles for each subsection
# when you plot any graph make sure you use 
    # a. Title, that describes your plot, this will be very helpful to the reader
    # b. Legends if needed
    # c. X-axis label
    # d. Y-axis label
x = hstack((categories_one_hot, sub_categories_one_hot,state_one_hot,project_grade_category_one_hot,teacher_prefix_one_hot,projtitle_bow,projecttitle_tfidf,avg_w2v_vectors_projtitles,tfidf_w2v_vectors_projtitle,price_standardized,PrevPostedPorjects_standardized),format='csr').toarray()
x = x[0:5000]
y = project_data['project_is_approved']
y = y[0:5000]

tsne = TSNE(n_components=2, perplexity=100, random_state=0)

tsne_data_bow = tsne.fit_transform(x)
tsne_data_bow= np.vstack((tsne_data_bow.T, y)).T
tsne_df_bow = pd.DataFrame(data=tsne_data_bow, columns=("Dimension_x", "Dimension_y", "Approved"))
sns.FacetGrid(tsne_df_bow, hue="Approved", height=6).map(plt.scatter, 'Dimension_x', 'Dimension_y').add_legend()
plt.title('TSNE with all Numerical, categorical feature and all verctors of PROJECT_TITLE feature')
plt.show()  


# **Analysis**
# 
# even after combing all the numberical and Categoriacal features with all diffferent vectors of Project_title we cann see much difference in the plot. only "approved" labels are visibile. 
# 
# also since we have taken only 15k points for the plots and the truth that only 15% of our actual data sets are negative. 
# there are high chances that most of the records in our selected data are "Approved" class. hence the tSNE plot might not shows "rejected" labels that are way from "Approved" labels"

# <h2> 2.5 Summary </h2>

# 
# 1) there are total of 109248 Data Points out of which 92706 i.e. nearly 85% of belongs to Positive class (Approved Project) and remaining 15% belongs to "Rejected" Projects
# 
# 2) state Vermont,District of Columbia, Texas , Monotana, Los Angles have minimal approval rate within 80-83 % approval rate. on the other side state New Hampshire, Ohio, Washington, North Dakota, Delaware are top 5 states where approval rates are high
# 
# 3). every state has more than 80% of Approval rate. 
# 
# 4). highest nukber of Project has been submitted from California with project count of 15388 followed by Texas from where 7396 project has been submitted.
# 
# 5) state of Vermont lies at the bottom of the list both in the terms of number of Project and Approval rate. only 80 pojects has been submitted from the state and has approval rate of around 80%
# 
# 6) Teacher with Prefix "Mrs" has submitted heighest number of project i.e. 57269 with approval rating of 85.5% whereas Teacher with prefix Doctor "Dr." has submitted just 13 projects with approval rate of 69% percent
# 
# 7).project approval rate among all the grade range of student is almost same i.e arround 83-86% percent. Student between grade 9 to 12 have submitted less projects as comared to Prek-2 and Grade 3-5 students
# 
# 8) there is lots of variability in number of project submmitted and approvd among different categories. the top three categories on which there is highest number of Project belongs to "Lietacy and Literature" , "Math and Science" or the combination og both categieries. while Health & sports with Literacy & language has very less number of submission
# 
# 9). category Literacy & Language has been used 52239 times or we can say in 52239 Project whereas category "care & Hunger" has been used only in 1388 Projects. this can be one of the important feature to predict whether a Project will be approved or not
# 
# 10).if you look at the top 5 subcategories which has highest submission and approval all are single or combination of "Literacy" , "Mathematics" and "Literature"
# 
# 11). there are total 30 distinct subcategories in the entire data sets
# 
# 12). the subcategory "Economics" has very less no of project as compared to "Literacy" Subcategory which has around 33700 Project which is around more than 100 times to that of "econmics". only 0.15% of project submitted have "Economics" as Subcategories" while more than 19% of Project submitted has "Literacy" as Sub Category
# 
# 13).for all the Percentils the Cost of rejected Projects is Higher than the Cost of Rejeced Projects which means project with large cost are tends to get rejected also as will move from 0 Percentile to 95% the price difference is getting increased between Approved and Rejected Projects.
# 
# 14).most of the Project that has been Submitted is being submitted first time by any teacher.even though the number of projects submitted by teacher who has previously submitted project is very low , but if you look at the number it tells that teacher who has submitted more than 15 projects earlier. the acceptance rate is more than 86% and it increases as the number of fearture valriable increase. it says that this feature plays good role in deciding whether the project will be approved or not
# 
# 15)the minimum number of word that a project resource summary has is 4 while the maximum word in any summary is 137. more than 10000 projects has word count of 11. Majority of Project have word count between 11 to 31
# 
# 16). project which has numeric value in the resource summry hase 89% approaval rate which is 5% higher than project without any numeric field in resource_summary column which somehow indicates that project with numeric value in resource_summary field has hgiher chances of approval
# 
# 17). there are total 5 features which are categorical, 3 columns {price, teacher_number_of_previously_posted_projects} which are numerical and 2 text columns {essays,Project_title} which we have considered in tSNE Plot
# 
# 18) after convertinf all the features to numerical vector we have created tSNE plot using all the Categorical and Numerical feature along with differnet numerical vector {BOW, TFIDF, avg-W2v and TFIDF W2v} individually with all the numerical and Categorical feature we didn't find much sense from the tSNE plot. we have considered 15k Data Points for TSNE plot
# 
# 19). later we combined all the vector together and plotted tSNE, but still not find any plot that could help us in diffentiating between the class lables since the plots are overlapping

# In[ ]:



