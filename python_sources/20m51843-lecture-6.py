#!/usr/bin/env python
# coding: utf-8

# # 20M51843 Lecture 6 
# # Ahdyat Zain Athoillah
# # SINGAPORE COVID-19 CASES
# I decided to analyse COVID-19 cases in Singapore. This city-state had its first coronavirus on 23 January 2020. The first victim was a Chinese tourist who arrived from Wuhan [1]. On 12 June 2020 Singapore has the highest number of coronavirus confirmed cases among Southeast Asian countries after overtaking over Indonesia which many low wage worker from other countries have been infected [2]. However, now Indonesia overtook again the first place with more coronavirus cases as updated until 18 June 2020. The data is shown as below. 

# In[ ]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
np.set_printoptions(threshold=np.inf)

selected_country = 'Singapore'
df = pd.read_csv('../input/novel-corona-virus-2019-dataset/covid_19_data.csv', header = 0)
df = df[df['Country/Region']==selected_country]
df = df.groupby('ObservationDate').sum()
print(df)


# In[ ]:


df['daily_confirmed'] = df['Confirmed'].diff()
df['daily_deaths'] = df['Deaths'].diff()
df['daily_recovery'] = df['Recovered'].diff()
df['daily_confirmed'].plot()
df['daily_recovery'].plot()


# In[ ]:


print(df)


# # Interactive chart will be created
# From the chart shown below, it seems that the trend of coronavirus infection cases in Singapore has decreased. The highest jump in number of infection was recorded on 20 April 2020 with 830 new recorded confirmed cases. Since then, the trend seems to decrease continuously until this report is written.

# In[ ]:


from plotly.offline import iplot
import plotly.graph_objs as go

daily_confirmed_object = go.Scatter(x=df.index,y=df['daily_confirmed'].values,name='Daily confirmed')
daily_deaths_object = go.Scatter(x=df.index,y=df['daily_deaths'].values,name='Daily deaths')

layout_object = go.Layout(title='Singapore daily cases 20M51843',xaxis=dict(title='Date'),yaxis=dict(title='Number of people'))
fig = go.Figure(data=[daily_confirmed_object,daily_deaths_object],layout=layout_object)
iplot(fig)
fig.write_html('Singapore_daily_cases_20M51843.html')


# # Informative table will be created
# The low values has dark color and the high values has bright color.

# In[ ]:


df1 = df#[['daily_confirmed']]
df1 = df1.fillna(0.)
styled_object = df1.style.background_gradient(cmap='gnuplot2').highlight_max('daily_confirmed').set_caption('Daily Summaries')
display(styled_object)
f = open('table_20M51843.html','w')
f.write(styled_object.render())


# # Global ranking can be analyzed
# Currently Singapore is ranked 31 in the world with most coronavirus cases and the second in ASEAN region. The government has implemented several measures to minimize the infection in the country. Singapore has limited the number of foreign visitors by banning all short-term visitors arriving or transiting through Singapore from 23 March onwards, with only people in essential services like healthcare and transport allowed entry during this time [3].
# 
# Additionally, the government of Singapore has formed a special ministry taskforce to tackle this coronavirus cases [4]. This country has implemented a lockdown status which they call as a "circuit breaker" from 7 April until 1 June [5]. In economic aspect, the government has poured big amount of money as the economic stimulus. In total there are four economic stimulus called as Unity budget with 6.4 billion Singaporean Dollar to help the transport and tourism industry [6], Resilience budget with 17 billion Singaporean Dollar [7], Solidarity budget with 5.1 billion Singaporean Dollar [8] and Fortitude budget as the last stimuli with total amounting to 32 billion Singaporean Dollar [9]. These economic stimulus were used to revive the food and retail industry in the country by giving them 10,000 Singaporean Dollar as an effort to digitalize their business [10].
# 
# Global ranking of COVID-19 cases can be found using the code below.

# In[ ]:


data = pd.read_csv('../input/novel-corona-virus-2019-dataset/covid_19_data.csv')
data.head()
data.index=data['ObservationDate']
data = data.drop(['SNo','ObservationDate'],axis=1)
data.head()
data_Singapore = data[data['Country/Region']=='Singapore']
data_Singapore.tail()
latest = data[data.index=='06/18/2020']
latest = latest.groupby('Country/Region').sum()
latest = latest.sort_values(by='Confirmed',ascending=False).reset_index() 
print('Ranking of Singapore: ', latest[latest['Country/Region']=='Singapore'].index.values[0]+1)


# # REFERENCES
# * 1."Coronavirus: Should the world worry about Singapore's virus surge?" BBC. Retrieved 12 June 2020
# * 2."Singapore now has most coronavirus cases in SE Asia". Bangkok Post. Retrieved 12 June 2020.
# * 3."Coronavirus: All short-term visitors barred from entering and transiting in Singapore from Monday, 11.59pm". The Straits Times. Retrieved 12 June 2020.
# * 4."Wuhan virus: MOH sets up multi-ministry taskforce, advises against non-essential trips to Wuhan". The Straits Times. Retrieved 12 June 2020.
# * 5."COVID-19 (Temporary Measures) (Control Order) Regulations 2020". Singapore Statutes Online. Retrieved 12 June 2020.
# * 6."Government support for firms and workers in response to the 2019 Novel Coronavirus outbreak". MOF, MTI. Retrieved 12 June 2020.
# * 7."Coronavirus: DPM Heng to announce supplementary budget in Parliament on Thursday". The Straits Times. Retrieved 12 June 2020.
# * 8."Solidarity Budget to cost SS 5.1 billion, SS 4 billion more needed from reserves". CNA. Retrieved 12 June 2020.
# * 9."SS 31 billion to be drawn from reserves for Fortitude Budget". CNA. Retrieved 12 June 2020.
# * 10."F&B and retail businesses can get up to SS 10,000 under new digital transformation scheme". The Straits Times. Retrieved 12 June 2020.