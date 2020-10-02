#!/usr/bin/env python
# coding: utf-8

# # Pokemon - Exploratory Data Analysis
# Growing up with Pokemon, I find that this dataset is interesting to be explored. Also taking this opportunity to practice the usage of different visualizations.
# Any feedback is most welcome! :)

# In[ ]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
from pandas import set_option
import squarify
import warnings
warnings.filterwarnings("ignore")

plt.rcParams['patch.force_edgecolor'] = True
plt.rcParams['patch.facecolor'] = 'b'


# In[ ]:


# getting colors to be used in charts

# rainbow colors
rb = []
colors = plt.cm.rainbow(np.linspace(0,1,18))
for c in colors:
    rb.append(c)
rb = reversed(rb)
rb = list(rb)

# viridis colors
vd = []
colors = plt.cm.GnBu(np.linspace(0,1,6))
for c in colors:
    vd.append(c)
vd = list(vd)


# In[ ]:


pokemon = pd.read_csv("../input/pokemon.csv")
pokemon.head(3) # glimpse of how the dataset looks


# In[ ]:


# Adding "total points" feature as an estimate of overall strength
pokemon['total_points']=pokemon['hp']+pokemon['attack']+pokemon['defense']+pokemon['speed']+pokemon['sp_attack']+pokemon['sp_defense']


# # 1. Pokemon Overview

# In[ ]:


fig, ax = plt.subplots(3,2, figsize=(18,18))

########## ax[0,0] Number of pokemon by generation
ax[0,0].bar(np.arange(7)+1, pokemon.groupby('generation')['name'].count(), color='cadetblue')
ax[0,0].set_title('Number of Pokemon by generation')
ax[0,0].set_xlabel('generation')
ax[0,0].set_ylabel('number of pokemon')

# Inserting text of total number of pokemon
props = dict(boxstyle='round', facecolor='gold', alpha=0.4)
ax[0,0].text(5.8,140, 'Total Pokemon:\n         801',fontsize=14, bbox=props)

########## ax[0,1] Pokemon by type
square = pokemon['type1'].value_counts() # Preparing subset of data for chart
squarify.plot(sizes=square.values, label=square.index, alpha=0.5, color=rb, value=square.values, ax=ax[0,1])
        # "rb" is a list of colors extracted from a standard cmap - codes at "start of notebook
ax[0,1].axis('off')
ax[0,1].set_title('Number of Pokemon by Type 1')

########## ax[1,0] Pokemon Type 2 distribution
sns.barplot(x='type2', y='index', data = pokemon['type2'].value_counts().reset_index(), ax=ax[1,0])
ax[1,0].set_title('Number of pokemon by Type 2')
ax[1,0].set_ylabel('Pokemon Type1')
ax[1,0].set_xlabel('Number of Pokemon')

########## ax[1,1] Percentage of pokemon with one type and two types
pokemon['type_count'] = ~pokemon['type2'].isnull() # Preparing subset of data for chart
pokemon['type_count'] = pokemon['type_count'].map({True:'two types',False:'one type'})

x = pokemon['type_count'].value_counts()
labels = pokemon['type_count'].value_counts().index

ax[1,1].pie(x, shadow=False, labels=labels, autopct='%1.1f%%', startangle=180, 
            colors=['powderblue','lightcoral'],wedgeprops={'linewidth':4,'edgecolor':'white'},pctdistance=0.8)

white_circle=plt.Circle( (0,0), 0.6, color='white') # adding white space to create donut chart
p=plt.gcf()
ax[1,1].add_artist(white_circle)

ax[1,1].axis('equal')
ax[1,1].text(-0.45,0, 'How many Pokemon\nhas two types?', fontsize=12)

########## ax[2,0] Distribution of Pokemon with 1 type and 2 types
type_heat = pokemon[['type1','type2']] # Preparing subset of data for chart
type_heat['n'] = 1
type_heat = type_heat.groupby(['type1','type2'], as_index=True)['n'].count().unstack()
sns.heatmap(type_heat, annot=True, cmap=plt.cm.magma_r, ax=ax[2,0], cbar=False, linewidths=0.3)
ax[2,0].set_title('Pokemon type1 & type2 combination')

########## ax[2,1] Total points: Pokemon with one type vs two types
sns.boxplot(x='type_count', y='total_points', data=pokemon, showfliers=False, showmeans=True, palette='Blues',
           ax=ax[2,1])
ax[2,1].set_title('Strength comparison: One type vs Two types')

plt.tight_layout()
plt.show()


# #### Pokemon overview observations:
# 1. There are a total of 801 pokemon across 7 generations. Generation 1, 3 and 5 have relatively higher number of Pokemon introduced
# 2. The most common pokemon types are "water", "normal", "grass" and "bug"
# 3. All pokemon has a primary type but only 52% of pokemon has a primary and secondary type (e.g.  primary: bug, secondary: flying)
# 4. "normal + flying", "grass + poison", "bug + flying" and "bug + poison" are the most common type 1&2 combination
# 5. There is no significant strength differences between pokemon with only 1 type and pokemon with 2 types

# # 2. Pokemon capture and growth

# Note: 
# 1. The lower the capture_rate indicates increasing difficulty in capturing pokemon (e.g. 3 = most difficult)
# 2. The higher the hp during time of capture, the more difficult it is for the pokemon to be captured

# In[ ]:


from IPython.display import display_html
# creating function to display df side by side
# reference https://stackoverflow.com/questions/38783027/jupyter-notebook-display-two-pandas-tables-side-by-side
def display_side_by_side(*args):
    html_str=''
    for df in args:
        html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)

cap = pokemon.loc[pokemon['capture_rate']!='30 (Meteorite)255 (Core)'] # removing irregular capture_rate
cap['capture_rate'] = cap['capture_rate'].map(lambda x: int(x)) # converting capture_rate to integer

df1 = cap[['name','capture_rate','hp']].sort_values(by=['capture_rate','hp'], ascending=[True,False]).head(10)
df2 = cap[['name','capture_rate','hp']].sort_values(by=['capture_rate','hp'], ascending=[False,True]).head(10)

df1.set_index('name', inplace=True)
df1.index.rename('10 most difficult to capture', inplace=True)
df2.set_index('name', inplace=True)
df2.index.rename('10 easiest to capture', inplace=True)

display_side_by_side(df1,df2)


# In[ ]:


fig, ax = plt.subplots(1,2, figsize=(18,6))

########## ax[0] Steps to hatch egg
egg_s = pokemon.groupby('base_egg_steps')['name'].count() # Preparing subset of data for chart
x = egg_s.index.map(lambda x: str(x))
y = egg_s.values

sns.barplot(x,y, order=x, palette='viridis',ax=ax[0])
ax[0].set_xlabel('Steps required to hatch base egg')
ax[0].set_ylabel('number of pokemon')
ax[0].set_title('Steps required to hatch base egg')

########## ax[1] Experience required to grow
exp_g = pokemon.groupby('experience_growth')['name'].count() # Preparing subset of data for chart
labels = ['600k', '800k', '1000k', '1060k', '1250k', '1640k']

ax[1].pie(exp_g.values, labels=labels, autopct='%1.1f%%',colors=vd, wedgeprops={'linewidth':4,'edgecolor':'white'},pctdistance=0.8, startangle=180)
        # "vd" is a list of colors extracted from a standard cmap - codes at start of notebook
my_circle=plt.Circle( (0,0), 0.6, color='white') # adding white space to create donut chart
p=plt.gcf()
ax[1].add_artist(my_circle)

ax[1].text(-0.45,-0.05, 'Experience required\nfor Pokemon growth', fontsize=12)
ax[1].axis('equal')

plt.tight_layout()
plt.show()


# #### Pokemon capture and growth observations:
# 1. Majority of eggs are hatched with 5,120 steps, followed by 3,840 steps
# 2. 67% of pokemon requires between 1-1.06 million experience points to grow
# 3. Only a small percentage (1.7%) of pokemon requires more than 1.6 million experience point to grow

# # 3. Pokemon strengths analysis

# In[ ]:


fig, ax = plt.subplots(2,2, figsize=(18,12))

######## ax[0,0] Legendary pokemon within different types
legendary = pokemon.groupby(['type1','is_legendary'])['name'].count().unstack() # creating subset data for chart
legendary = legendary.fillna(0)

legendary.columns = ['not_legend','legend']
n = pokemon['type1'].nunique()

totals = [i+j for i,j in zip(legendary['not_legend'], legendary['legend'])] # counting total for each 'type1'
legend = [i / j * 100 for i,j in zip(legendary['legend'], totals)] # calculating % of legend in each 'type1'
not_legend = [i / j * 100 for i,j in zip(legendary['not_legend'], totals)] # calculating % of non-legend in 'type1'

width = 0.85
ax[0,0].bar(np.arange(n), not_legend, color='lightcoral', edgecolor='white', width=width)
ax[0,0].bar(np.arange(n), legend, bottom=not_legend, color='gold', edgecolor='white', width=width)
ax[0,0].set_xticks(np.arange(n))
ax[0,0].set_xticklabels(np.sort(pokemon['type1'].unique()))
ax[0,0].set_title('% of legendary Pokemon within Type1')

######## ax[0,1] hp distribution among type1
sns.boxplot(x='hp', y='type1', data=pokemon, showfliers=False, showmeans=True, ax=ax[0,1])
ax[0,1].set_title('hp distribution of different Type1')

######## ax[1,0] attack & defense of pokemon based on type1
att_def = pokemon.groupby('type1')[['attack','defense','hp']].mean() # creating subset data for chart

labels_max = att_def.sort_values(by='attack', ascending=False).head(7) # find label for top 7 types for attack
labels_min = att_def.sort_values(by='attack', ascending=True).head(3) # find label for last 3 types for attack
label_high = labels_max.index.tolist()
label_low = labels_min.index.tolist()

ax[1,0].scatter(x=att_def['attack'], y=att_def['defense'],s=200,label=att_def.index, c=rb, alpha=0.7)

for label, x, y in zip(label_high, labels_max['attack'], labels_max['defense']):
    ax[1,0].annotate(
        label, xy=(x, y), xytext=(-20, -5), textcoords='offset points', ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', fc='gold', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
for label, a, b in zip(label_low, labels_min['attack'], labels_min['defense']):
    ax[1,0].annotate(
        label, xy=(a, b), xytext=(14, 40), textcoords='offset points', ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', fc='gold', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
ax[1,0].set_title('Pokemon attack & defense by Type 1')

######## ax[1,1] Correlations between size, health and power
power = pokemon[['height_m','weight_kg','hp','attack','defense','speed','sp_attack','sp_defense']]
sns.heatmap(power.corr(), annot=True, cmap='GnBu', ax=ax[1,1], cbar=False)
ax[1,1].set_title('Correlations between size, health and power')

plt.tight_layout()
plt.show()


# #### Pokemon strengths observation:
# 1. dragon, flying, psychic and steel have relatively larger percentage of legendary pokemon
# 2. ghost, electric and bug pokemon tend to have lower hp whereas fairy and flying pokemon types tend to have higher hp
# 3. On average, dragon type has the highest attack and steel type has significantly higher defense
# 4. With reference to the combination of attack and defense:
#     - dragon, steel, rock and ground are among the strongest pokemon type
#     - fairy, psychic and flying are among the weakest pokemon type
# 5.  There is no strong linear correlation between pokemon size (height & weight) to hp, attack and defense

# # 4. Pokemon battle advantage

# In[ ]:


against = pokemon.iloc[:,1:19] # creating subset data for chart
against = pd.concat([pokemon[['type1','type2']],against], axis=1)
against['type2'].loc[against['type2'].isnull()]='None'
against['type_combo'] = against['type1']+'-'+against['type2']

fig, ax = plt.subplots(2,1,figsize=(18,18))

sns.heatmap(against.groupby('type1').mean(), cmap='RdYlGn_r', annot=True, linewidths=0.3, fmt='.2g', ax=ax[0])
ax[0].set_title('Battle advantage among pokemon types')

selection = against.groupby('type1').mean()
sns.heatmap(selection.mask(selection<=1.5, np.nan),linewidths=0.3, cmap='RdYlGn_r', annot=True, fmt='.2g', linecolor='gainsboro', ax=ax[1])
ax[1].set_title('Which pokemon type to use in specific battles?')

print('Note: Figures indicates amount of damage taken against a particular type, with 1 being normal amount of damage')
plt.tight_layout()
plt.show()


# In[ ]:


# manual selection based on chart above
d = {'oponent pokemon':['bug','dark','dragon','electric','fairy','fighting','fire','flying','ghost','grass','ground','ice','normal','poison',
                        'psychic','rock','steel','water'],
     'selection1':['rock','fairy','ice','ground','steel','fairy','water','ice','ghost','fire','ice','rock','fighting','psychic','ghost','grass',
                   'ground','grass'],
     'selection2':['fire','fighting','fairy','fighting','poison','flying','rock','rock','dark','ice','water','steel','ice','ground','dark','water',
                   'fire','electric'],
     'selection3':['flying','bug','dragon','fire','ice','psychic','ground','fairy','ice','flying','grass','fire','electric','flying','bug','steel',
                   'fighting','rock']}

print('Top 3 best pokemon selection against specific pokemon type')
pd.DataFrame(d)


# # Back up

# In[ ]:


pokemon.info()
# Observation: 801 records and 41 features with mixture of object, float and int. Some missing data in...
#...height, weight, type2 and percentage male
