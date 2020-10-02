#!/usr/bin/env python
# coding: utf-8

# # Best NBA Player per Draft Position
# ## Introduction
# In this notebook, I will try to analyze a controversial topic: who is the best/worst NBA player, per draft position? This is a controversial topic because, best/worst player is mainly about opinion and preference, and stats cannot simply justified the best/worst argument as basketball and sports in overall cannot be judged only by stats and number. 
# 
# Let's get started into it. For you who don't know what a draft is, it is a method for NBA teams to "recruit" new players from colleges or overseas. The recruitment process happened sequentially, so the team that get the first pick can recruit player first, and so on. With such method, it is expected that the first player drafted is the best player from the recruitment class. But sometimes, we got a highly picked player that doesn't meet the expectation or a lowly drafted player that overcome the expectation. Using this dataset, I will try to analyze which player that actually over/underacieved their draft position.   

# # EDA & Data cleansing
# First, let's do some EDA from this dataset. We can start by import useful libraries and load the data

# In[ ]:


import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


df = pd.read_csv("../input/nba-players-data/all_seasons.csv")


# Let's see some information about this dataset

# In[ ]:


df.info()


# We can see that we have 11145 players data across 23 seasons and 22 features.

# In[ ]:


df.describe()


# Here we got some descriptive statistics of numerical features. We can see that the dataset contain many single game appearence. While this not really affect many of the essential stats (points, assists, rebounds, etc.), single game appearence really disturb the net rating. For example, the max net rating recorded in the dataset is 300 while the lowest is -200. This is happens because in one of those single game appearence, that player maybe only played in garbage time thus the net rating deflated. 
# 
# To deal with this, we can use three approaches: drop the record of player who only played few number of games for every season, drop the record of player who only averaged few number of games overall, or simply removed this features from consideration. All of this approaches have their own pros and cons. In the first approach, we can drop some record of a player who actually has a decent career, but has one or two seasons with only one appearances due to injury/rough start. For example, let's see the career of Bruce Bowen:

# In[ ]:


test_feat = ['gp','net_rating']
df.loc[df.player_name=='Bruce Bowen',test_feat]


# Here we can see that Bruce start his first NBA season by only played one game with deflated net rating of 300, but after that he definitely has a legendary career with the San Antonio Spurs. If we choose the first approach, we will neglect his career start, but we can slightly alter his points per game for example, and can create some bias. If we choose the second approach, we will keep this deflated stats and affect our calculation. The third approach is more neutral, but I want to keep it as it can differentiate good player in good team or bad team. 
# 
# To decide my approach, I want to know how many records that contain this anomaly:

# In[ ]:


(df.loc[(df['gp']==1 )& (df['net_rating']>20)])


# It seems like there are many similar cases in the dataset. Therefore, my approach is to discard player who average less than 3 games for their entire career when we rank the players.
# 
# Then as we want to measure per draft number, we want to know how many draft class are there in the dataset

# In[ ]:


df.draft_year.unique()


# So, per 1996 season, there are 44 draft class and 1 class for undrafted player. In the case for undrafted player, we want to see whether majority of NBA players are undrafted. Since 1990, NBA draft consist of two rounds with 29 or 30 picks per round. thus around 60 new players become NBA player each season. If each team need 15-man roster for their team, for 30 NBA team around 450 players needed, which can be acquired from free agency of undrafted player. For some perspective, let's see 2018 season

# In[ ]:


sns.barplot(y=df.loc[df.season=='2018-19'].draft_year.value_counts().index,x=df.loc[df.season=='2018-19'].draft_year.value_counts())


# In[ ]:


total_player = len(df.loc[df.season=='2018-19'].player_name.unique())
undrafted_player = len(df.loc[(df.season=='2018-19')&(df.draft_year=='Undrafted')].player_name.unique())
prcntg  = 100*(undrafted_player/total_player)
print(prcntg)


# We can see that more than 24% of NBA players actually come undrafted per 2018 season.

# This dataset contains all of player records from 1996 season. We can't include all players in this list, as some of them maybe drafted far back beyond 1996 season, thus the record in this dataset does not count all of their accomplishment. For example, we only got around 5 season of Michael Jordan greatness with this dataset. Because of that, we need to discard players that drafted before 1995 season. Why 1995 season and not 1996? Because of my personal reference to include recent HOF Kevin Garnett in our analysis, so don't be mad.

# In[ ]:


df.drop(df[df.draft_year<'1995'].index, inplace=True)


# We also need to clean some weird number, such as a player that drafted in 82nd pick, and turn all of undrafted player to 61st pick for analytics purpose.

# In[ ]:


df['draft_number'].replace('Undrafted','82',inplace=True)
df['draft_number'].replace('82','61',inplace=True)
df['draft_number'] = pd.to_numeric(df['draft_number'])


# Then we want to discard some players that only played few games for their entire career. First we need to list them then drop them from the original dataframe

# In[ ]:


df_player = df[['player_name','gp']].groupby('player_name').sum().reset_index()
df_player = df_player.loc[df_player['gp'] < 5]
for p in df_player['player_name']:
    df.drop(df[df.player_name==p].index, inplace=True)


# Next, we create two dataframe: average stats per draft pick and average stats per player. Average stats per draft pick means the average stats for each draft pick. For stat, we will used 'gp', 'pts', 'reb', 'ast', 'net_rating', 'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct'.

# In[ ]:


stats = ['gp', 'pts', 'reb', 'ast', 'net_rating',
       'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct']
avg_per_pick = df.groupby(['draft_number'])[stats].mean().reset_index()
avg_per_player = df.groupby(['player_name','draft_number'])[stats].mean().reset_index()


# First, let's see the trend of traditional stats (points, assists, rebounds) against the draft position

# In[ ]:


sns.regplot(x='draft_number',y='pts',data=avg_per_pick,order=3)
plt.show()


# In[ ]:


sns.regplot(x='draft_number',y='ast',data=avg_per_pick,order=3)
plt.show()


# In[ ]:


sns.regplot(x='draft_number',y='reb',data=avg_per_pick,order=3)
plt.show()


# It's seems that the overall trend shows that higher draft pick gives better number. But let's see the the actual number as we can see many outliers in the graph

# In[ ]:


ax = sns.lineplot(x='draft_number',y='pts',data=avg_per_pick, label='pts')
ax = sns.lineplot(x='draft_number',y='ast',data=avg_per_pick, label='ast')
ax = sns.lineplot(x='draft_number',y='reb',data=avg_per_pick, label='reb')
ax.set(ylabel = 'avg')
ax.legend()
plt.show()


# In[ ]:


avg_per_pick[['draft_number','pts','reb','ast']][:15]


# In[ ]:


avg_per_pick[['draft_number','pts','reb','ast']][-5:]


# We can see some interesting trend here. For example, we can see that the 2nd overall pick actually has lowest ppg and apg among the top 5 picks. Well, historically not many successful 2nd pick since 1995 with some notable names are Derrick Williams, Hasheem Thabeet, and Darko Milicic, which are considered as the draft bust. Then we got 11th pick, which notoriously has lowest ppg, apg, and rpg among lottery pick and even to late round pick. Sure Klay Thompson, Myles Turner, and Domantas Sabonis were picked at this position, but other than that we only got some decent NBA players.
# 
# We also got interesting things in the late draft pick, where there are some spike in 57th and 60th pick. Let's see some details about players in this position

# In[ ]:


avg_per_player[avg_per_player.draft_number==57]


# In[ ]:


avg_per_player[avg_per_player.draft_number==60]


# So, we can see two names that create this spike: Manu Ginobili and Isaiah Thomas. IT create the spike in ppg due to his inprobable all-star form in Boston Celtics and Manu just being Manu. Seeing the downhill of IT is a sad story though

# In[ ]:


ax = sns.lineplot(x='season',y='pts',data=df.loc[df['player_name'] == 'Isaiah Thomas'], label='pts')
ax = sns.lineplot(x='season',y='ast',data=df.loc[df['player_name'] == 'Isaiah Thomas'], label='ast')
ax = sns.lineplot(x='season',y='reb',data=df.loc[df['player_name'] == 'Isaiah Thomas'], label='reb')
ax.set(ylabel = 'avg')
ax.legend()
plt.show()


# Although his apg and rpg basically stays the same, his ppg drop significantly from almost 30.0 ppg to mere 10.0 ppg since his trade to Cavs and hip injury.

# In[ ]:


ax = sns.lineplot(x='season',y='pts',data=df.loc[df['player_name'] == 'Manu Ginobili'], label='pts')
ax = sns.lineplot(x='season',y='ast',data=df.loc[df['player_name'] == 'Manu Ginobili'], label='ast')
ax = sns.lineplot(x='season',y='reb',data=df.loc[df['player_name'] == 'Manu Ginobili'], label='reb')
ax.set(ylabel = 'avg')
ax.legend()
plt.show()


# Manu's stat actually looks like a decent player with some all star number in his prime, given the facts that he was picked 57th in the draft.

# # Rank the best player for each pick
# Now we move to the tricky part: rank the best/worst player. Obviously we cannot use traditional stats only to make our consideration. We must use all the stats available to rank the players. How do we do it?
# 
# I create a metrics called 'score', which measure the difference between sum of player's stat with the average stat in his draft position. Sounds simple right? I create this metrics based on the facts that in basketball stat that we analyzed, the higher the number, the better the player was. In other hands, if the difference of sum of player stats to the sum of average stat is equal/approaching zero, the player is an average player in his draft position. if the difference is positive, he is overachieving and vice versa. First let's create the function to measure the 'score'

# In[ ]:


def score(a, b):
    #function to calculate score
    sum = 0.0
    for i in range(1,len(a)):
        sum += (b[i+1]-a[i])
    return (sum)


# Then we applied it to our dataset 

# In[ ]:


dist = []
for p in range(avg_per_player.shape[0]):
    val = score(avg_per_pick.loc[avg_per_player.loc[p][1]-1],avg_per_player.loc[p])
    dist.append(val)
avg_per_player['score'] = dist


# Let's see the score for example 1st draft pick

# In[ ]:


avg_per_player.loc[avg_per_player.draft_number==1].sort_values('score')


# As we can see, LeBron actually is the best 1st pick since 1995, whatever the haters say, and Anthony Bennett is truly the biggest bust for a 1st pick. Zion get negative score as this is still his first season. We also see that the number of games played affected the metric. Kyrie, who actually has great stats has lower score than John Wall and Andrew Wiggins as he played less game per season. Net rating, as I mentioned earlier, gives difference between star in bad team and good team. Tim Duncan has similar stats with Karl-Anthony Towns, but as he has superior net rating, he has higher metric in the end. Now let's see which player has the highest score per draft position

# In[ ]:


avg_per_player.loc[avg_per_player.groupby('draft_number')['score'].idxmax()]


# Here's the complete list of best player for each draft pick, measured by the 'score' metrics. We'll see some of great players that we expect is the best on his draft position. Now I want to mention some interesting results. 
# 
# - First, the 'OKC trio' actually was the best 2nd, 3rd, and 4th draft pick since 1995 and all of them have become league MVP. With the addition of Steven Adams (12th pick) and Serge Ibaka (24th pick), OKC drafted 5 players that become the best in their pick (CMIIW). OKC scouts really have good eyes on sleeper player.
# - GSW drafted 3 players (Steph, Klay, and Draymond) that are the best in their respective draft pick position. 
# - As we expect, Bruce Bowen has the highest 'score' due to his inflated net rating. If we not consider him, Nikola Jokic has the highest 'score', thus the most overachieve player since 1995. 
# - The 59th pick does not give any sleeper players so far. The best of 59th pick is DJ Strawberry with a score of 7.6.
# - In the case of 8th pick, the best player is Andre Miller. Among the top 10 pick, only 8th pick that actually has a non all-star player as their best player. But it is reasonable as beside Miller, other notable players are KCP, Rudy Gay, and Jamal Crawford.

# In[ ]:


avg_per_player.loc[avg_per_player.draft_number==8].sort_values('score')


# - One of questionable result: where is Kobe Bryant? Instead of Kobe, the best player in 13th pick is Donovan Mitchell. This is happened most likely because: Mitchell average more games per season and has higher net rating than Kobe. In his old days, Kobe suffer many harsh injuries and mediocre teammate that affect his total stats

# In[ ]:


avg_per_player.loc[avg_per_player.draft_number==13].sort_values('score')


# Ok, now what about the underachiever? In this regard, let limit it to the lottery picks as we expect a great player drafted in that position.

# In[ ]:


avg_per_player.loc[avg_per_player.groupby('draft_number')['score'].idxmin()][:15]


# We can see many bust name: Anthony Bennett, Hasheem Thabeet, Eddy Curry. The lowest underachiever is Aleksandar Radojevic, that actually only player 2 NBA seasons.
# 
# The case of 7th pick, Wendell Carter Jr. is particularly interesting as he only enter his sophomore season. But as we see in the table below, it is mostly because he played less game than others in a bad Bulls team. His overall stats actually not so bad as he has the highest ppg and rpg among other 'busts'.

# In[ ]:


avg_per_player.loc[avg_per_player.draft_number==7].sort_values('score')


# ## Conclusion
# We have see the best/worst NBA player per their draft position and analyze why the results happened. Well it is not the most objective results, as we use many assumption for our analysis. We also only use a simple metric to rank the players. For the future, I want to use more advanced machine learning method to classify players 'tier', which also become one of the most debatable topic among NBA fans. I welcome any suggestion about my method/analysis. Cheers!