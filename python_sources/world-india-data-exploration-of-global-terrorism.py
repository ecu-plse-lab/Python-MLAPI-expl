#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import folium.plugins

# Input data files are available in the "../input/" directory.
terror_data = pd.read_csv('../input/globalterrorismdb_0718dist.csv',encoding='ISO-8859-1')


# Setting a limit on number of rows and columns to show by default.

# In[ ]:


#This will show only 20 columns when we print the data.
pd.set_option('display.max_columns',20)

#This will show only 20 rows when we print the data.
pd.set_option('display.max_rows',5)


# Name of All the Columns in the terror data.

# In[ ]:


#terror_data.columns only show some columns name while terror_data.columns.values show all the columns name.
print(terror_data.columns.values)


# Checking how many null values are there in the terror dataframe.

# In[ ]:


#This will Print the total number of Null Values in each Columns.
print(terror_data.isnull().sum())


# Renaming some columns for better and clearly understanding the data.

# In[ ]:


terror_data = terror_data.rename(columns = {'nkill':'Killed','nwound':'Wounded','iyear':'Year','imonth':'Month',
'iday':'Day','country':'country_no','country_txt':'Country','attacktype1_txt':'AttackType','region_txt':'Region',
'target1':'Target','summary':'Summary','gname':'Group','targtype1_txt':'Target_type','weaptype1_txt':'Weapon_type','motive':'Motive'})


# In[ ]:


terror_data['Casualities'] = terror_data['Killed'] + terror_data['Wounded']
column = ['Year','Month','Day','Country','Region','city','latitude','longitude','AttackType','Killed','Wounded','Target','Summary','Group','Target_type','Weapon_type','Motive','Casualities']


# In[ ]:


terror = pd.DataFrame(terror_data,columns = column)
print(terror)


# Checking how many nulls values are there in each column of the dataframe.

# In[ ]:


print(terror.isnull().sum())


# Countries with Maximum and Minimum Numbers of Terrorist Attacks.
# In Simple Words Top 5 Maximum Terrorist Prone Countries and Top 5 Most Peaceful Countries.

# In[ ]:


#Countries with Maximum number of Terrorist Attack
print(terror['Country'].value_counts().head(5))


# In[ ]:


#Countries with Minimum number of Terrorist Attack
print(terror['Country'].value_counts().sort_values(ascending = True).head(5))


# Figure Showing the Number of Terrorist Attacks happening every year.  

# In[ ]:


#Setting Figure SIZE
plt.figure(figsize= (25,16))

#Terrorist Attacks Happening Every Year.
sns.countplot('Year',data = terror , palette = 'RdYlGn', edgecolor = sns.color_palette('dark',3))
plt.title('Terrorist Attacks by Year', fontsize = 30)
plt.xlabel('Year', fontsize = 20)
plt.ylabel('No. of Attacks', fontsize = 20)
plt.show()


# Figure Showing the Number of Different Types of Attacks.

# In[ ]:


#Setting Figure SIZE
plt.figure(figsize= (25,16))

#Countplot of All types of Attack sorted by Highest Number of Times.
sns.countplot('AttackType',data=terror ,palette='Blues_d', order = terror['AttackType'].value_counts().index)
plt.title('Numbers of Attacks of Different types',fontsize = 30)
plt.xlabel('Attack Types',fontsize= 20)
plt.xticks(rotation = 80, fontsize = 16)
plt.yticks(fontsize = 16)
plt.ylabel('No. of Attacks',fontsize = 20)
plt.show()


# Naming all Different Types of Attacks

# In[ ]:


print(terror['AttackType'].unique())


# Numbers of Attacks by each Year.

# In[ ]:


print(terror['Year'].value_counts())


# Different Types of Targets Type.

# In[ ]:


print(terror['Target_type'].unique())


# This clearly shows there are around more than 20 types of target types like Military, Police, Educational Institution, NGO, and other militants attacks.

# In[ ]:


plt.figure(figsize = (25,16))
sns.countplot('Target_type', data = terror, palette = 'inferno', order = terror['Target_type'].value_counts().index)
plt.xticks(rotation = 90, fontsize = 16)
plt.yticks(fontsize = 16)
plt.xlabel('Different types of Target', fontsize = 20)
plt.ylabel('Number of Attacks', fontsize = 20)
plt.title('Number of Attacks on each type of Targets',fontsize = 30)
plt.show()


# Region that are most Prone to Terrorist Attacks.

# In[ ]:


print(terror['Region'].value_counts().sort_values(ascending = False))


# Plotting the Countplot related to terrorist Attacks by each Region in maximum to minimum order.

# In[ ]:


plt.figure(figsize = (25,16))
sns.countplot('Region', data = terror, palette = 'RdYlGn_r', order = terror['Region'].value_counts().index, 
     edgecolor = sns.color_palette('deep',3))
plt.title('Numbers of Terrorist Attacks by Region', fontsize = 30)
plt.xticks(rotation = 90, fontsize = 16)
plt.yticks(fontsize = 16)
plt.xlabel('Regions', fontsize = 20)
plt.ylabel('Numbers of Terrorist Attacks', fontsize = 20)
plt.show()


# This Graph clearly shows that Middle East, North Africa and South Asia Region are most Prone to terrorist attacks, and also East Asia, Central Asia and Oceania region are among the Most Peaceful Region.

# Terrorism and Terrorist Attacks in TOP Countries.

# In[ ]:


plt.figure(figsize = (25,16))
index_ = terror['Country'].value_counts()[:15].index
value_ = terror['Country'].value_counts()[:15].values
sns.barplot(index_ , value_ , palette = 'inferno')
plt.xticks(fontsize = 14)
plt.yticks(fontsize = 16)
plt.xlabel('Country', fontsize = 20)
plt.ylabel('Numbers of Attacks', fontsize = 20)
plt.title('Numbers of Attacks by Each Country ( Ranked by Top )', fontsize = 30)
plt.show()


# Terrorist Attack of Different Types in Different Regions.

# In[ ]:


pd.crosstab(terror.Region, terror.AttackType).plot.bar(stacked = True, color = sns.color_palette('RdYlBu',3))
fig = plt.gcf()
fig.set_size_inches(12,8)
plt.title('All Types of Attacks stacked over each other')
plt.show()


# This shows that Bombing/Explosion are most famous attack type in the Middle-East and South Asia. While in Sub-Saharan Africa both Armed Assault and Bombing are equally famous attack types. And In Almost All regions have Bombing/Explosion are the main types of Attacks.
# One Thing we can do to stop the terrorist attacks is to identify the source of the explosives terrorist use.

# Biggest Terrorist Group in the World. Most of the Attacks are Unknowns so I remove the Unknown Value.

# In[ ]:


plt.figure(figsize = (25,16))
index_2 = terror['Group'].value_counts()[1:16].index
value_2 = terror['Group'].value_counts()[1:16].values
sns.barplot(index_2, value_2 , palette = 'Blues_d')
plt.xticks(rotation = 90, fontsize = 16)
plt.yticks(fontsize = 16)
plt.xlabel('Terrorist Organisations', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Terrorist Attacks by Top 15 Terrorist Organisation', fontsize = 24 )
plt.show()


# This shows for most of the terrorist attacks, terrorist organisation don't get responsiblity. After that Taliban and ISIS are the most responsible for terrorist attacks all over the world.

# All terrorist attacks done by major terrorist organisations from 1970 till 2017.

# In[ ]:


top_groups = terror[terror['Group'].isin(terror['Group'].value_counts()[1:11].index)]
pd.crosstab(top_groups.Year, top_groups.Group).plot(color = sns.color_palette('bright',9))
fig = plt.gcf()
fig.set_size_inches(20,8)
plt.show()


# This clearly shows the Rise in Numbers of Attacks by several Terrorist Organisations.

# Terrorist Attacks in Top 10 Countries Over Time.

# In[ ]:


top_country = terror[terror['Country'].isin(terror['Country'].value_counts()[:10].index)]
pd.crosstab(top_country.Year, top_country.Country).plot(color = sns.color_palette('bright',10))
fig = plt.gcf()
fig.set_size_inches(20,6)
plt.show()


# Terrorist Attacks in the Different Regions Over Time.

# In[ ]:


top_region = terror[terror['Region'].isin(terror['Region'].value_counts()[:10].index)]
pd.crosstab(top_region.Year , top_region.Region).plot(color = sns.color_palette('bright',10))
fig = plt.gcf()
fig.set_size_inches(20,6)
plt.xlabel('Year', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Terrorist Attack in Different Region over time from 1970 to 2017', fontsize = 30)
plt.show()


# In[ ]:


count_terror = terror['Country'].value_counts()[:15].to_frame()
count_terror.columns = ['Attack']
count_killed = terror.groupby('Country')[['Killed','Wounded']].sum()
count_terror.merge(count_killed, left_index = True, right_index = True, how = 'left').plot.bar(width = 0.9,
  color = sns.color_palette('RdYlGn',3))
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.title('Combine Bar Chart of Country with Total Attacks, People Killed and People Wounded', fontsize = 30)
plt.xlabel('Country', fontsize = 20)
plt.ylabel('Attacks, Killed & Wounded', fontsize = 20)
fig = plt.gcf()
fig.set_size_inches(25,16)
plt.show()


# In[ ]:


count_terror = terror['Country'].value_counts()[:15].to_frame()
count_terror.columns = ['Attacks']
count_Casual = terror.groupby('Country')['Casualities'].sum().to_frame()
count_terror.merge(count_Casual , left_index =True, right_index= True , how = 'left').plot.bar(width = 0.8, color = sns.color_palette('Blues_d',3))
fig = plt.gcf()
fig.set_size_inches(25,16)
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.title('Combine Bar Chart of Country with Total Attacks and People Casualities', fontsize = 30)
plt.xlabel('Country', fontsize = 20)
plt.ylabel('Attacks Vs Casualties', fontsize = 20)
plt.show()


# **Now Some Terrorist Attacks in India.**

# First Creating a new India Dataframe and then creating a countplotof attacks in top 15 Indian Cities.

# In[ ]:


#Creating another dataframe related to only India.
terror_india = terror[terror['Country'] == 'India']

#Setting figure size and creating a coundplot of attacks in top 15 cities of India.
plt.figure(figsize = (25,16))
sns.countplot(terror_india['city'], palette = 'RdYlGn', order = terror_india['city'].value_counts()[:15].index)
plt.xticks(rotation = 90, fontsize = 16)
plt.yticks(fontsize = 16)
plt.xlabel('Cities in India', fontsize = 20)
plt.ylabel('Numbers of Attack', fontsize = 20)
plt.title( 'Numbers of Attack in Different Cities of India', fontsize = 30 )
plt.show()


# Creating a Bar Plot of Numbers of Attacks by Terrorist in India. 

# In[ ]:


#Creating Barplot of Groups Attacks
plt.figure(figsize = (25,16))
index_2 = terror_india['Group'].value_counts()[1:11].index
value_2 = terror_india['Group'].value_counts()[1:11].values
sns.barplot(index_2 , value_2 )
plt.xticks(rotation = 80, fontsize = 14)
plt.yticks(fontsize = 16)
plt.xlabel('Terrorist Organisations', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Terrorist Attacks done by each top Terrorist Organisation in India')
plt.show()


# Creating Time Graph of Terrorist Attack done by different Organisaton over Years.

# In[ ]:


#Creating Time Frame Graph of Terrorist Attack by each organisation over Years
top_group = terror_india[terror_india['Group'].isin(terror_india['Group'].value_counts()[1:11].index)]
pd.crosstab(top_group.Year, top_group.Group).plot(color= sns.color_palette('bright',7))
fig = plt.gcf()
fig.set_size_inches(16,5)
plt.xlabel('Organisation', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Terrorist Attack by Terrorist Organisations over Time', fontsize= 30)
plt.show()


# This clearly shows that Sikh Extremists were mostly active in 1980-1990 time period, But Over the Period India sees a increase in the Numbers of Attacks by Maoists Group and CPI Maoists.

# Creating Time Frame Graph of Terrorist Attacks by each Cities over Year.

# In[ ]:


#Creating Time Frame Graph of Terrorist Attacks by each Cities over Year.
top_cities = terror_india[terror_india['city'].isin(terror_india['city'].value_counts()[:10].index)]
pd.crosstab(top_cities.Year, top_cities.city).plot(color = sns.color_palette('Set1',8))
fig = plt.gcf()
fig.set_size_inches(18,6)
plt.xlabel('Year', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Terrorist Attack in Cities Over Time', fontsize= 30)
plt.show()



# This shows that Terrorist attack in all the cities show a decline except New Delhi where attack show a rise.

# This clearly shows the Each type of Attacks on a Particular City.

# In[ ]:


top_attack = terror_india[terror_india['city'].isin(terror_india['city'].value_counts()[:10].index)]
pd.crosstab(top_attack.city, top_attack.AttackType).plot.bar(stacked = True, color = sns.color_palette('dark',5))
fig = plt.gcf()
fig.set_size_inches(16,10)
plt.xticks(rotation = 0, fontsize = 16)
plt.xlabel('Cities', fontsize = 20)
plt.ylabel('Attacks', fontsize = 20)
plt.title('Number of Attacks with Each Type of Attack in Top 10 Cities', fontsize = 24)
plt.show()


# In[ ]:


terror_india=terror[terror['Country']=='India']
terror_india_fol=terror_india.copy()
terror_india_fol.dropna(subset=['latitude','longitude'],inplace=True)
location_ind=terror_india_fol[['latitude','longitude']][:5000]
city_ind=terror_india_fol['city'][:5000]
killed_ind=terror_india_fol['Killed'][:5000]
wound_ind=terror_india_fol['Wounded'][:5000]
target_ind=terror_india_fol['Target_type'][:5000]
def color_point(x):
    if x>=30:
        color='red'
    elif ((x>0 and x<30)):
        color='blue'
    else:
        color='green'
    return color   
def point_size(x):
    if (x>30 and x<100):
        size=2
    elif (x>=100 and x<500):
        size=8
    elif x>=500:
        size=16
    else:
        size=0.5
    return size

map1 = folium.Map(location=[20.59, 78.96],tiles='Stamen Terrain',zoom_start=4.5)
for point in location_ind.index:
    folium.CircleMarker(list(location_ind.loc[point].values),popup='<b>City: </b>'+str(city_ind[point])+'<br><b>Killed: </b>'+str(killed_ind[point])+                        '<br><b>Injured: </b>'+str(wound_ind[point])+'<br><b>Target: </b>'+str(target_ind[point]),radius=point_size(killed_ind[point]),color=color_point(killed_ind[point]),fill_color=color_point(killed_ind[point])).add_to(map1)
map1
