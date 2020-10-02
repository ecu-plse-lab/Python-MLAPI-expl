#!/usr/bin/env python
# coding: utf-8

# # Introduction
# NCAA March Madness is a single-elimination tournament played each spring in the United States, currently featuring 68 college basketball teams from the Division I level of the National Collegiate Athletic Association (NCAA), to determine the national championship [1]. It is one of the very popular game in the USA. Because it is a single-elimination tournament if a team lose then that team eliminate from the tournament whether it has good seeds or points. This makes this tournament very exciting. 
# 
# This tournament first rank team by seeds. To learn how these seeds are calculated read the [wikipedia](https://en.wikipedia.org/wiki/NCAA_Division_I_Men%27s_Basketball_Tournament) article. The first round consists of play between higher-seeded teams with the lower-seeded team in a region. Because of single-elimination, often time unexpected things happen, underdogs become "cinderellas," and games that analysts expected to be blowouts become nail-biters through the final seconds. A team's competitiveness is what keeps games exciting and the tournament truly "mad." This notebook aims to find out characteristics that differentiate underdogs teams and create upsets in the tournament. 

# In[ ]:


import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np


# plotly imports
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)

import shap

# load JS visualization code to notebook
shap.initjs()


base_address = '../input/march-madness-analytics-2020/2020DataFiles/2020DataFiles/2020-Mens-Data'

m_teams = pd.read_csv(base_address + '/MDataFiles_Stage1/MTeams.csv')

# 2019 all tournament compat results, meaning each game score
# this file will be useful for getting overall birds eye view
tourn_compat_results = pd.read_csv(base_address + '/MDataFiles_Stage1/MNCAATourneyCompactResults.csv')
tourn_compat_results_2019 = tourn_compat_results.loc[tourn_compat_results.Season==2019]

tourn_detail_results = pd.read_csv(base_address + '/MDataFiles_Stage1/MNCAATourneyDetailedResults.csv')
tourn_detail_results_2019 = tourn_detail_results.loc[tourn_detail_results.Season==2019]


tourney_seeds = pd.read_csv(base_address + '/MDataFiles_Stage1/MNCAATourneySeeds.csv')


# ## Cinderella team
# Before we move on to the analysis of the Cinderella teams, first we have to understand what is Cinderella team. Although there is not an official definition of what constitutes a Cinderella team, there does seem to be a consensus that such teams represent small schools, are usually low-seeded in the tournament, and achieves at least one unexpected win in the tournament. A recent example of this is Florida Gulf Coast University, a relatively new school that held its first classes in 1997 and became Division I postseason eligible in 2011. They made their first appearance in the 2013 tournament, winning two games to become the first #15 seed to advance to the Sweet Sixteen [1].

# In[ ]:


############
# this cell process dataset, merge and calculate upsets game
###########

tourn_detail_results_merge = tourn_detail_results.merge(tourney_seeds, left_on=['Season', 'WTeamID'], right_on=['Season', 'TeamID'], how='inner')
tourn_detail_results_merge = tourn_detail_results_merge.loc[tourn_detail_results_merge.DayNum.isin([136, 137])]
tourn_detail_results_merge = tourn_detail_results_merge.rename(columns={'Seed': 'WSeed'})
tourn_detail_results_merge = tourn_detail_results_merge.drop(['TeamID'], 1)

tourn_detail_results_merge = tourn_detail_results_merge.merge(tourney_seeds, left_on=['Season', 'LTeamID'], right_on=['Season', 'TeamID'], how='inner')
tourn_detail_results_merge = tourn_detail_results_merge.loc[tourn_detail_results_merge.DayNum.isin([136, 137])]
tourn_detail_results_merge = tourn_detail_results_merge.rename(columns={'Seed': 'LSeed'})
tourn_detail_results_merge = tourn_detail_results_merge.drop(['TeamID'], 1)



tourn_detail_results_merge = tourn_detail_results_merge.merge(m_teams[['TeamID', 'TeamName']], left_on='WTeamID', right_on='TeamID',how='inner')
tourn_detail_results_merge = tourn_detail_results_merge.rename(columns={'TeamName': 'WTeamName'})
tourn_detail_results_merge = tourn_detail_results_merge.drop(['TeamID'], 1)

tourn_detail_results_merge = tourn_detail_results_merge.merge(m_teams[['TeamID', 'TeamName']], left_on='LTeamID', right_on='TeamID',how='inner')
tourn_detail_results_merge = tourn_detail_results_merge.rename(columns={'TeamName': 'LTeamName'})
tourn_detail_results_merge = tourn_detail_results_merge.drop(['TeamID'], 1)





tourn_detail_results_merge['WSeedNum'] = tourn_detail_results_merge.WSeed.str.extract('(\d+)')
tourn_detail_results_merge['LSeedNum'] = tourn_detail_results_merge.LSeed.str.extract('(\d+)')
tourn_detail_results_merge['WSeedNum'] = tourn_detail_results_merge['WSeedNum'].astype(int)
tourn_detail_results_merge['LSeedNum'] = tourn_detail_results_merge['LSeedNum'].astype(int)


tourn_detail_results_merge_upset = tourn_detail_results_merge.loc[tourn_detail_results_merge.WSeedNum > 10]


# # Game level stats of Cinderella team
# To find characteristics of Cinderellas teams, let's start with game level statistics. Game level statistics that are calculated based on the whole game. For example, ```WFGA3``` is a stats feature which describes the number of fields 3 pointer goal attempted in the game by winning team. There are a lot of stats features provided in the dataset. We will analyze them to see any patterns. 

# In[ ]:


###############
# this cell caluclate adavance features and also it 
# seperate dataframe for loser and winners
###############

winner = tourn_detail_results_merge_upset[['WFGM', 'WFGA', 'WFGM3',
                                           'WFGA3', 'WFTM', 'WFTA',
                                           'WOR', 'WDR','WAst',
                                           'WTO', 'WStl',
                                           'WBlk', 'WPF', 'LDR', 'LOR']]
winner.columns = ['FGM', 'FGA', 'FGM3','FGA3', 'FTM', 'FTA',
                  'OR', 'DR','Ast','TO', 'Stl','Blk', 'PF', 'LDR', 'LOR']
winner['status'] = 'Winner'
winner['FGP'] = winner['FGM'] / winner['FGA']
winner['FGP2'] = (winner['FGM'] - winner['FGM3']) / (winner['FGA'] - winner['FGA3'])
winner['FGP3'] = winner['FGM3'] / winner['FGA3']
winner['FTP'] = winner['FTM'] / winner['FTA']
winner['ORP'] = winner['OR'] / (winner['OR']+winner['LDR'])
winner['DRP'] = winner['DR'] / (winner['DR']+winner['LOR'])
winner['POS'] = 0.96 * (winner['FGA'] + winner['TO'] + 0.44 * winner['FTA'] - winner['OR'])






looser = tourn_detail_results_merge_upset[['LFGM', 'LFGA', 'LFGM3', 'LFGA3',
       'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF', 'WDR', 'WOR']]

looser.columns = ['FGM', 'FGA', 'FGM3', 'FGA3',
       'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF', 'WDR', 'WOR']

looser['status'] = 'Looser'
looser['FGP'] = looser['FGM'] / looser['FGA']
looser['FGP2'] = (looser['FGM'] - looser['FGM3']) / (looser['FGA'] - looser['FGA3'])
looser['FGP3'] = looser['FGM3'] / looser['FGA3']
looser['FTP'] = looser['FTM'] / looser['FTA']
looser['ORP'] = looser['OR'] / (looser['OR']+looser['WDR'])
looser['DRP'] = looser['DR'] / (looser['DR']+looser['WOR'])
looser['POS'] = 0.96 * (looser['FGA'] + looser['TO'] + 0.44 * looser['FTA'] - looser['OR'])



basic_stats_features = ['FGM', 'FGA', 'FGM3', 'FGA3',
       'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']
advanced_stats_features = ['status', 'FGP', 'FGP2', 'FGP3',
                           'FTP', 'ORP', 'DRP', 'POS']


df_stats = pd.concat([winner[basic_stats_features+advanced_stats_features],
           looser[basic_stats_features+advanced_stats_features]])


# In[ ]:


temp = df_stats[basic_stats_features+ ['status']].groupby('status').mean()
temp = temp.rename_axis(None)
temp.style.background_gradient(cmap='Blues')


# We are seeing a very informative table, each game level stats for the winner(cinderella team) and losing team. The table itself is self-explanatory. Below is the main info from the table. 
# 
# * Cinderella team has higher FGM, FGM3, FTM, FTA compare to losing team. 
# * Cinderella team has higher defensive rebounds and less offensive rebounds compare to losing team. 
# * Cinderella team has a higher assist. 
# * Personal foul committed by losing team is higher. 

# ## Advanced statistics
# We previously have seen basic game level statistics of the cinderella team. Now we look to calculate more advanced stats for finding more meaningful info. Below is a list of new advanced features we will be calculating. 
# 
# WFGP(Field Goal Percentage) = WFGM/WFGA
# 
# WFGP2(2 Pointer Field Goal Percentage) = (WFGM - WFGM3) / (WFGA - WFGA3)
# 
# WFGP3(3 Pointer Field Goal Percentage) = WFGM3 / WFGA3
# 
# WFTP(Field Through Percentage) = WFTM / WFTA
# 
# WORP(Offensive Rebounds Percentage) = WOR / (WOR + LDR)
# 
# WDRP(Defensive Rebounds Percentage) = WDR / (WDR + LOR)
# 
# POS = 0.96 * (WFGA + WTO + 0.44 * WFTA - WOR)
# 
# Above advanced stats features also calculate for losing team. These features will help us to more clearly identify cinderella team characteristics. 

# In[ ]:


temp = df_stats[advanced_stats_features].groupby('status').mean()
temp = temp.rename_axis(None)
temp.style.background_gradient(cmap='Blues')


# We are seeing that 
# * FGP, FGP2, FGP3, FTP are all higher in Cinderella teams. 
# * ORP and DRP are slightly higher in losing team.
# * POS is slightly higher in losing team though it mostly the same in both teams. 
# 
# 
# After analysing game level data, We find that possession is mostly the same between cinderella teams and the losing team. But we find that Cinderella teams have a higher percentage in those events that generate points (FGM, FGM3, FTM, FTA). Also, cinderella teams have lower fowl rate which helps them to win despite they have lower seed. 

# # Cinderella teams stats from Play-By-Play data
# We previously saw Cinderella teams game level stats features and how they are different for cinderella teams. And find out some characteristics of cinderellas team. Now we are going to move ahead and try to find patterns of cinderellas teams from play by play data. This will help us to get more detailed characteristics of cinderella teams. 

# In[ ]:


mens_events = []
for year in [2015, 2016, 2017, 2018, 2019]:
    mens_events.append(pd.read_csv(f'../input/march-madness-analytics-2020/2020DataFiles/2020DataFiles/2020-Mens-Data/MEvents{year}.csv'))
MEvents = pd.concat(mens_events)



MEvents_upset = MEvents.merge(tourn_detail_results_merge_upset[['Season', 'DayNum', 'WTeamID', 'WScore',
                                                'LTeamID','WSeed', 'LSeed', 'WTeamName', 
                                                'LTeamName', 'WSeedNum', 'LSeedNum']],
             on=['Season', 'DayNum', 'WTeamID', 'LTeamID'], how='inner')

MEvents_upset.loc[MEvents_upset.EventTeamID == MEvents_upset.WTeamID, 'event_team_status'] = 'Winner'
MEvents_upset['event_team_status'] = MEvents_upset['event_team_status'].fillna('Looser')


# ## Popular Events in games for cinderella teams
# In play-by-play data, we have data that describes the event between plays. There are different kinds of events in basketball. Assist, sub, steal and others. This event is really useful for identifying characteristics of cinderella teams. Let's see what we can find! 

# In[ ]:


temp = MEvents_upset.groupby(['Season', 'WTeamID', 'LTeamID','event_team_status'])['EventType'].value_counts().reset_index(name='count')
temp2 = temp.groupby(['event_team_status', 'EventType'])['count'].mean().reset_index()
fig = px.bar(temp2, x='EventType', y='count', color='event_team_status', barmode='group')
for axis in fig.layout:
    if type(fig.layout[axis]) == go.layout.YAxis:
        fig.layout[axis].title.text = ''
fig.show()


# We are seeing very important results. Let's spent some time with just what we have found. 
# 
# * Cinderella teams have a higher assist, fouled, made1, made2, made3, miss1, steal, sub
# * Losing teams have higher foul, jump, miss2, miss3
# 
# As we previously saw, game level stats that cinderella teams often perform more those events that produce points. Additionally, we are seeing in here those movements that help getting points like steal and sub. These are very informative findings but the above chart gives full game time overview. Next, we will see events in different segments of the game. 

# ## Popular Events in games for cinderella teams by time segments
# NCAA Basketball consists of two half, each one is 20 minutes and lastly extra time. Now we will see is there any differences in playing by cinderella team in different time quarter. We will split play-by-play data into three segments. First-quarter, second quarter, extra. And then we will try to find popular event types in each of these quadrants. 

# In[ ]:


MEvents_upset.loc[MEvents_upset.ElapsedSeconds <= 1200, 'time_quadrent'] = 'first quarter'
MEvents_upset.loc[(MEvents_upset.ElapsedSeconds > 1200) & (MEvents_upset.ElapsedSeconds <=2400), 'time_quadrent'] = 'second quarter'
MEvents_upset.loc[MEvents_upset.ElapsedSeconds > 2400, 'time_quadrent'] = 'extra'




temp = MEvents_upset.groupby(['Season', 'WTeamID', 'LTeamID','event_team_status', 'time_quadrent'])['EventType'].value_counts().reset_index(name='count')
temp2 = temp.groupby(['event_team_status', 'EventType', 'time_quadrent'])['count'].mean().reset_index()
fig = px.bar(temp2, x='EventType', y='count', color='event_team_status', barmode='group', facet_row='time_quadrent')

for axis in fig.layout:
    if type(fig.layout[axis]) == go.layout.YAxis:
        fig.layout[axis].title.text = ''

for annotation in fig.layout.annotations:
    annotation.text = annotation.text.split("=")[1]
    
fig.show()


# We are seeing that in the second quarter the cinderella team achieve higher points compare to the first quarter of the game because it has a higher rate of made1, made2, made3, sub. So we can say that the second quarter is very important for the cinderella team. But how the score changes with time? Next, we will find how cinderella team score changes with time. 

# # Changes in score in games by cinderella team
# We previously found the characteristics of cinderellas teams. Now let's find out how the score changes with time. In play-by-play data, for 2019 we have elapsed time feature column. We can use that to find out how WCurrentScore and LCurrentScore moving along with time in games. We will create a new column where we will subtract these two columns. If subtraction is below zero then losing team score is higher and if it is above higher then the cinderella team score is higher. 

# In[ ]:


temp = (MEvents_upset.loc[MEvents_upset.Season > 2018]).sort_values(['Season', 'WTeamID', 'LTeamID','ElapsedSeconds'])
temp['score_diff'] = temp['WCurrentScore'] - temp['LCurrentScore']

fig = px.line(temp, x="ElapsedSeconds", y="score_diff", facet_row='LSeed')
fig.show()


# We are seeing very interesting results. The above chart shows 4 cinderella teams winning match's score difference distribution along time elapsed. The blue line below 0 is when the losing team score is the higher and blue line above 0 is when cinderella team score is higher. 
# 
# We can see cinderella team plays very competitively in full time of the game. Whenever the score opposing team score higher, cinderella team often get back and score more points. These plots show us how competitively cinderella teams play to win. 

# # Using ML to distinguish Cinderella team wins vs regular wins
# We previously saw different characteristics of cinderella teams. How these characteristics help cinderella teams become cinderella(win against higher seed though they have low seed). Those are very important information and pattern. Now we will move towards a more important topic. 
# 
# From game level data, we will select games where the winner is the lower-seeded team(cinderella) and another set of data where the winner is higher seeded team meaning regular game. Using this data we will build a decision tree model that predicts whether the game is cinderella wins or not based on previous features we discuss. After that, we will use ML explainability to understand what features contributes to cinderella team winning and also regular winning. 

# In[ ]:


##########
# this cell train a randomtreeclassifier and used for model explainability
#########

tourn_detail_results_merge_regular = tourn_detail_results_merge.loc[tourn_detail_results_merge.WSeedNum < 5]
tourn_detail_results_merge_regular = tourn_detail_results_merge_regular.head(83)

tourn_detail_results_merge_regular['winning_term'] = '0'

tourn_detail_results_merge_upset['winning_term'] = '1'




train_col = ['WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR',
       'WAst', 'WTO', 'WStl', 'WBlk', 'WPF', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3',
       'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']


train = pd.concat([tourn_detail_results_merge_upset, tourn_detail_results_merge_regular])
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier

X = train[train_col]
Y = train['winning_term']
clf = RandomForestClassifier(random_state=0)
clf = clf.fit(X, Y)


# In[ ]:


explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X.iloc[4])

shap.force_plot(explainer.expected_value[1], shap_values[1], X.iloc[4])


# After training our model using randomtreeclassifier we finally plotted our feature contribution in decision making. This plot needs a little bit of description. 
# 
# What we are seeing is the logic of our model to classify our 4th row of train dataset as cinderella win. 0.86 in bold represent the probability that 4th row in train dataset is cinderella team win based win stats features. Red colour features are those features that drive our predicted outcome higher and blue colour is the opposite of that. 
# 
# 
# We are seeing from the plot that Cinderella team's Blocking, defensive rebounds, field goal made and winner assist drive cinderella team to win the game. This is very important info for us. This plot and technique can be used for more findings and research in future. 

# # Conclusion
# Finally, we have come to an end. Thank you very much for reading this notebook. Hope we together learn something new. Learned how why upsets happened, characteristics of cinderella teams and lot more. Thanks Again!

# [1. https://en.wikipedia.org/wiki/NCAA_Division_I_Men%27s_Basketball_Tournament](https://en.wikipedia.org/wiki/NCAA_Division_I_Men%27s_Basketball_Tournament)
# 
# [2. https://www.kaggle.com/dansbecker/shap-values](https://www.kaggle.com/dansbecker/shap-values)
# 
# [3. https://github.com/slundberg/shap](https://github.com/slundberg/shap)